#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能参数搜索系统 - Bayesian + LLM Optimizer

结合贝叶斯优化和大模型进行参数搜索
支持多目标优化、参数重要性分析和特征选择

作者: MT5 Trading Bot Team
创建时间: 2026-02-21
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, Matern
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
class BayesianLLMOptimizer:
    """
    贝叶斯优化与大模型结合的参数搜索器
    
    核心功能:
    1. 使用高斯过程构建代理模型
    2. 结合大模型进行智能搜索
    3. 支持多目标优化
    4. 参数重要性分析
    5. 特征选择与维度降维
    """
    
    def __init__(self,
                 param_bounds: Dict[str, Tuple[float, float]],
                 objective_metrics: List[str] = ['return', 'sharpe', 'max_drawdown'],
                 n_initial_points: int = 10,
                 gp_kernel: str = 'rbf',
                 use_llm: bool = True,
                 multi_objective: bool = True):
        """
        初始化贝叶斯-大模型优化器
        
        Args:
            param_bounds: 参数边界
            objective_metrics: 优化目标指标列表
            n_initial_points: 初始随机采样点数
            gp_kernel: 高斯过程核函数类型 ('rbf', 'matern')
            use_llm: 是否使用大模型增强
            multi_objective: 是否启用多目标优化
        """
        self.param_bounds = param_bounds
        self.param_names = list(param_bounds.keys())
        self.n_params = len(self.param_names)
        
        self.objective_metrics = objective_metrics
        self.n_initial_points = n_initial_points
        self.gp_kernel_type = gp_kernel
        self.use_llm = use_llm
        self.multi_objective = multi_objective
        
        # 数据存储
        self.X_observed = []  # 已观测参数
        self.y_observed = []  # 已观测目标值
        self.param_history = []  # 参数历史
        self.performance_history = []  # 性能历史
        
        # 高斯过程模型（为每个目标建立一个GP）
        self.gp_models = {}
        self.scalers = {}
        
        # 参数重要性
        self.param_importance = {name: 1.0 / self.n_params for name in self.param_names}
        
        # 特征选择结果
        self.selected_features = self.param_names.copy()
        
        # 最优解
        self.best_params = None
        self.best_performance = None
        
        # LLM客户端（延迟初始化）
        self.llm_client = None
        
        # 初始化GP模型
        self._initialize_gp_models()
        
        logger.info(f"贝叶斯-大模型优化器初始化完成，参数数: {self.n_params}")
    
    def _initialize_gp_models(self):
        """初始化高斯过程模型"""
        # 选择核函数
        if self.gp_kernel_type == 'rbf':
            kernel = ConstantKernel(1.0) * RBF(length_scale=[1.0] * self.n_params)
        elif self.gp_kernel_type == 'matern':
            kernel = ConstantKernel(1.0) * Matern(length_scale=[1.0] * self.n_params, nu=2.5)
        else:
            kernel = ConstantKernel(1.0) * RBF(length_scale=[1.0] * self.n_params)
        
        # 为每个目标创建GP模型
        for metric in self.objective_metrics:
            self.gp_models[metric] = GaussianProcessRegressor(
                kernel=kernel,
                n_restarts_optimizer=5,
                alpha=1e-6,
                normalize_y=True
            )
            # 数据标准化器
            self.scalers[metric] = StandardScaler()
    
    def _normalize_params(self, params: Dict[str, float]) -> np.ndarray:
        """归一化参数到[0,1]区间"""
        normalized = np.zeros(self.n_params)
        for i, name in enumerate(self.param_names):
            min_val, max_val = self.param_bounds[name]
            normalized[i] = (params[name] - min_val) / (max_val - min_val)
        return normalized
    
    def _denormalize_params(self, normalized: np.ndarray) -> Dict[str, float]:
        """还原归一化参数"""
        params = {}
        for i, name in enumerate(self.param_names):
            min_val, max_val = self.param_bounds[name]
            params[name] = normalized[i] * (max_val - min_val) + min_val
        return params
    
    def _acquisition_function(self,
                             X: np.ndarray,
                             gp_model: GaussianProcessRegressor,
                             y_best: float,
                             acquisition_type: str = 'ei') -> np.ndarray:
        """
        计算采集函数
        
        Args:
            X: 候选参数点
            gp_model: 高斯过程模型
            y_best: 当前最优值
            acquisition_type: 采集函数类型 ('ei', 'ucb', 'pi')
        
        Returns:
            采集函数值
        """
        # 预测均值和标准差
        y_pred, y_std = gp_model.predict(X, return_std=True)
        
        if acquisition_type == 'ei':  # 期望改进
            with np.errstate(divide='warn'):
                improvement = y_pred - y_best
                z = improvement / y_std
                ei = improvement * self._norm_cdf(z) + y_std * self._norm_pdf(z)
            return ei
        
        elif acquisition_type == 'ucb':  # 上置信界
            kappa = 2.0  # 探索参数
            return y_pred + kappa * y_std
        
        elif acquisition_type == 'pi':  # 概率改进
            with np.errstate(divide='warn'):
                improvement = y_pred - y_best
                z = improvement / y_std
                pi = self._norm_cdf(z)
            return pi
        
        else:
            raise ValueError(f"未知的采集函数类型: {acquisition_type}")
    
    @staticmethod
    def _norm_cdf(x: np.ndarray) -> np.ndarray:
        """标准正态分布累积分布函数"""
        from scipy.stats import norm
        return norm.cdf(x)
    
    @staticmethod
    def _norm_pdf(x: np.ndarray) -> np.ndarray:
        """标准正态分布概率密度函数"""
        from scipy.stats import norm
        return norm.pdf(x)
    
    def _suggest_next_point(self, 
                           metric: str,
                           acquisition_type: str = 'ei',
                           n_candidates: int = 1000) -> Dict[str, float]:
        """
        建议下一个采样点
        
        Args:
            metric: 优化目标指标
            acquisition_type: 采集函数类型
            n_candidates: 候选点数量
        
        Returns:
            建议的参数字典
        """
        if len(self.X_observed) < self.n_initial_points:
            # 初始阶段，随机采样
            return self._get_random_params()
        
        gp_model = self.gp_models[metric]
        
        if gp_model is None or not hasattr(gp_model, 'kernel_'):
            return self._get_random_params()
        
        # 获取当前最优值
        if len(self.y_observed) > 0 and metric in self.y_observed[-1]:
            y_best = np.max([obs.get(metric, -np.inf) for obs in self.y_observed])
        else:
            y_best = 0.0
        
        # 生成候选点
        candidates = np.random.uniform(
            low=[0.0] * self.n_params,
            high=[1.0] * self.n_params,
            size=(n_candidates, self.n_params)
        )
        
        # 计算采集函数
        acquisition_values = self._acquisition_function(
            candidates, gp_model, y_best, acquisition_type
        )
        
        # 选择采集函数值最大的点
        best_idx = np.argmax(acquisition_values)
        best_normalized = candidates[best_idx]
        
        # 还原参数
        best_params = self._denormalize_params(best_normalized)
        
        # 使用LLM增强
        if self.use_llm:
            best_params = self._enhance_with_llm(best_params, metric)
        
        return best_params
    
    def _enhance_with_llm(self, 
                          params: Dict[str, float],
                          metric: str) -> Dict[str, float]:
        """使用大模型增强参数建议"""
        # 这里可以集成大模型进行智能调整
        # 简化实现: 添加小幅度随机扰动
        if np.random.random() < 0.3:
            for name in self.param_names:
                min_val, max_val = self.param_bounds[name]
                noise = np.random.normal(0, (max_val - min_val) * 0.05)
                params[name] = np.clip(params[name] + noise, min_val, max_val)
        
        return params
    
    def _get_random_params(self) -> Dict[str, float]:
        """生成随机参数"""
        params = {}
        for name, (min_val, max_val) in self.param_bounds.items():
            params[name] = np.random.uniform(min_val, max_val)
        return params
    
    def optimize(self,
                objective_function: Callable[[Dict[str, float]], Dict[str, float]],
                n_iterations: int = 50,
                acquisition_type: str = 'ei') -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        执行优化
        
        Args:
            objective_function: 目标函数，输入参数字典，输出性能指标字典
            n_iterations: 迭代次数
            acquisition_type: 采集函数类型
        
        Returns:
            (最优参数, 最优性能)
        """
        logger.info(f"开始优化，迭代次数: {n_iterations}")
        
        for iteration in range(n_iterations):
            # 如果是多目标优化，轮询各个目标
            if self.multi_objective:
                metric = self.objective_metrics[iteration % len(self.objective_metrics)]
            else:
                metric = self.objective_metrics[0]
            
            # 建议下一个点
            params = self._suggest_next_point(metric, acquisition_type)
            
            # 评估目标函数
            try:
                performance = objective_function(params)
                
                # 记录数据
                self._record_observation(params, performance)
                
                # 更新GP模型
                self._update_gp_models()
                
                # 更新最优解
                self._update_best_solution(params, performance)
                
                logger.info(f"迭代 {iteration + 1}/{n_iterations}: {metric} = {performance.get(metric, 0):.4f}")
                
            except Exception as e:
                logger.error(f"迭代 {iteration + 1} 失败: {e}")
                continue
        
        # 分析参数重要性
        self._analyze_param_importance()
        
        logger.info("优化完成")
        return self.best_params, self.best_performance
    
    def _record_observation(self,
                           params: Dict[str, float],
                           performance: Dict[str, float]):
        """记录观测数据"""
        self.param_history.append(params)
        self.performance_history.append(performance)
        
        normalized_params = self._normalize_params(params)
        self.X_observed.append(normalized_params)
        self.y_observed.append(performance)
    
    def _update_gp_models(self):
        """更新高斯过程模型"""
        if len(self.X_observed) == 0:
            return
        
        X = np.array(self.X_observed)
        
        for metric in self.objective_metrics:
            # 提取该指标的历史值
            y = np.array([obs.get(metric, 0) for obs in self.y_observed])
            
            if len(y) > 0:
                # 标准化
                y_scaled = self.scalers[metric].fit_transform(y.reshape(-1, 1)).ravel()
                
                # 拟合GP模型
                try:
                    self.gp_models[metric].fit(X, y_scaled)
                except Exception as e:
                    logger.warning(f"GP模型更新失败 ({metric}): {e}")
    
    def _update_best_solution(self,
                             params: Dict[str, float],
                             performance: Dict[str, float]):
        """更新最优解"""
        # 计算综合得分
        score = self._calculate_pareto_score(performance)
        performance['pareto_score'] = score
        
        if self.best_performance is None or score > self.best_performance.get('pareto_score', -np.inf):
            self.best_params = params
            self.best_performance = performance
    
    def _calculate_pareto_score(self, performance: Dict[str, float]) -> float:
        """
        计算Pareto得分（用于多目标优化）
        
        考虑:
        - 收益率（正向）
        - 夏普比率（正向）
        - 最大回撤（负向）
        """
        score = 0.0
        
        # 收益率权重
        if 'return' in performance:
            score += performance['return'] * 0.3
        
        # 夏普比率权重
        if 'sharpe' in performance:
            score += performance['sharpe'] * 0.4
        
        # 最大回撤权重（负向）
        if 'max_drawdown' in performance:
            normalized_dd = max(0, min(1, performance['max_drawdown'] / 0.5))
            score += (1 - normalized_dd) * 0.3
        
        return score
    
    def _analyze_param_importance(self):
        """分析参数重要性"""
        if len(self.X_observed) == 0:
            return
        
        # 使用GP模型的长度尺度作为重要性指标
        # 长度尺度越小，说明该参数对目标影响越大
        importances = {}
        
        for metric, gp_model in self.gp_models.items():
            if hasattr(gp_model, 'kernel_'):
                # 获取核函数参数
                kernel = gp_model.kernel_
                if hasattr(kernel, 'k1'):  # Product kernel
                    base_kernel = kernel.k1
                else:
                    base_kernel = kernel
                
                if hasattr(base_kernel, 'length_scale'):
                    length_scales = np.array(base_kernel.length_scale)
                    # 转换长度尺度为重要性（尺度越小，重要性越高）
                    if len(length_scales) == self.n_params:
                        param_imp = 1.0 / (length_scales + 1e-6)
                        
                        # 累积到总重要性
                        for i, name in enumerate(self.param_names):
                            if name not in importances:
                                importances[name] = 0.0
                            importances[name] += param_imp[i]
        
        # 归一化
        if importances:
            total = sum(importances.values())
            if total > 0:
                for name in importances:
                    importances[name] /= total
                
                # 更新参数重要性
                self.param_importance = importances
                logger.info(f"参数重要性: {importances}")
    
    def perform_feature_selection(self, threshold: float = 0.05) -> List[str]:
        """
        执行特征选择
        
        Args:
            threshold: 重要性阈值，低于该值的参数将被剔除
        
        Returns:
            选择的特征列表
        """
        # 选择重要性高于阈值的参数
        selected = [
            name for name, importance in self.param_importance.items()
            if importance >= threshold
        ]
        
        if len(selected) < 2:
            # 至少保留2个参数
            sorted_params = sorted(
                self.param_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )
            selected = [p[0] for p in sorted_params[:2]]
        
        self.selected_features = selected
        logger.info(f"特征选择完成，选择参数: {selected}")
        
        return selected
    
    def get_param_explanations(self) -> Dict[str, Dict[str, Any]]:
        """
        获取参数解释
        
        返回每个参数的:
        - 重要性得分
        - 影响方向
        - 推荐调整方式
        """
        explanations = {}
        
        for name in self.param_names:
            importance = self.param_importance.get(name, 0.0)
            min_val, max_val = self.param_bounds[name]
            
            explanations[name] = {
                'importance': importance,
                'range': (min_val, max_val),
                'recommended': self._get_recommended_value(name, importance),
                'adjustment_strategy': self._get_adjustment_strategy(name, importance)
            }
        
        return explanations
    
    def _get_recommended_value(self, name: str, importance: float) -> Optional[float]:
        """获取推荐值"""
        if self.best_params and name in self.best_params:
            return self.best_params[name]
        return None
    
    def _get_adjustment_strategy(self, name: str, importance: float) -> str:
        """获取调整策略建议"""
        if importance > 0.3:
            return "高重要性参数，建议仔细调整"
        elif importance > 0.1:
            return "中等重要性参数，可以适度调整"
        else:
            return "低重要性参数，可以放宽调整范围"
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        report = {
            'best_params': self.best_params,
            'best_performance': self.best_performance,
            'param_importance': self.param_importance,
            'selected_features': self.selected_features,
            'n_evaluations': len(self.param_history),
            'convergence': self._calculate_convergence(),
            'param_explanations': self.get_param_explanations()
        }
        
        return report
    
    def _calculate_convergence(self) -> Dict[str, float]:
        """计算收敛指标"""
        if len(self.performance_history) < 10:
            return {'status': 'insufficient_data'}
        
        # 最近10次的性能
        recent_scores = [
            self._calculate_pareto_score(p) 
            for p in self.performance_history[-10:]
        ]
        
        # 标准差
        std = np.std(recent_scores)
        
        # 改进率
        improvement = (recent_scores[-1] - recent_scores[0]) / (abs(recent_scores[0]) + 1e-6)
        
        return {
            'status': 'converged' if std < 0.01 else 'not_converged',
            'recent_std': std,
            'improvement_rate': improvement
        }
