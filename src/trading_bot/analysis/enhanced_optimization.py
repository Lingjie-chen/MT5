#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强参数优化系统 - Enhanced Optimization Module

集成大模型优化器与传统优化算法
支持混合优化策略和智能模式切换

作者: MT5 Trading Bot Team
创建时间: 2026-02-21
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 导入项目模块
from .optimization import WOAm, TETA
from .llm_parameter_optimizer import LLMParameterOptimizer
from .bayesian_llm_optimizer import BayesianLLMOptimizer
from .parameter_history_learner import ParameterHistoryLearner
from .adaptive_parameter_tuner import AdaptiveParameterTuner

logger = logging.getLogger(__name__)
class EnhancedOptimizationEngine:
    """
    增强优化引擎
    
    集成多种优化方法:
    1. 传统算法 (WOAm, TETA)
    2. 大模型优化 (LLMParameterOptimizer)
    3. 贝叶斯优化 (BayesianLLMOptimizer)
    4. 历史学习 (ParameterHistoryLearner)
    5. 自适应调整 (AdaptiveParameterTuner)
    """
    
    def __init__(self,
                 param_bounds: Dict[str, Tuple[float, float]],
                 optimization_mode: str = 'hybrid',
                 model_type: str = 'qwen',
                 objective_metrics: List[str] = ['return', 'sharpe', 'max_drawdown']):
        """
        初始化增强优化引擎
        
        Args:
            param_bounds: 参数边界
            optimization_mode: 优化模式 ('traditional', 'llm', 'bayesian', 'hybrid', 'adaptive')
            model_type: 大模型类型
            objective_metrics: 优化目标指标
        """
        self.param_bounds = param_bounds
        self.param_names = list(param_bounds.keys())
        self.optimization_mode = optimization_mode
        self.model_type = model_type
        self.objective_metrics = objective_metrics
        
        # 初始化各种优化器
        self.llm_optimizer = None
        self.bayesian_optimizer = None
        self.history_learner = None
        self.adaptive_tuner = None
        self.traditional_optimizers = {}
        
        # 初始化优化器
        self._initialize_optimizers()
        
        # 优化历史
        self.optimization_history = []
        self.best_params = None
        self.best_performance = None
        
        # 配置
        self.config = {
            'hybrid_weight': {
                'traditional': 0.3,
                'llm': 0.4,
                'bayesian': 0.3
            },
            'switch_threshold': 0.1,  # 性能下降超过此值时切换方法
            'min_history_size': 10,  # 最小历史记录数
            'adaptive_window': 20    # 自适应窗口
        }
        
        logger.info(f"增强优化引擎初始化完成，模式: {optimization_mode}")
    
    def _initialize_optimizers(self):
        """初始化所有优化器"""
        # 初始化大模型优化器
        try:
            self.llm_optimizer = LLMParameterOptimizer(
                param_bounds=self.param_bounds,
                objective_metrics=self.objective_metrics,
                model_type=self.model_type
            )
            logger.info("LLM优化器初始化成功")
        except Exception as e:
            logger.warning(f"LLM优化器初始化失败: {e}")
        
        # 初始化贝叶斯优化器
        try:
            self.bayesian_optimizer = BayesianLLMOptimizer(
                param_bounds=self.param_bounds,
                objective_metrics=self.objective_metrics,
                use_llm=True
            )
            logger.info("贝叶斯优化器初始化成功")
        except Exception as e:
            logger.warning(f"贝叶斯优化器初始化失败: {e}")
        
        # 初始化历史学习器
        try:
            self.history_learner = ParameterHistoryLearner(
                param_names=self.param_names
            )
            logger.info("历史学习器初始化成功")
        except Exception as e:
            logger.warning(f"历史学习器初始化失败: {e}")
        
        # 初始化自适应调整器（稍后设置当前参数）
        self.adaptive_tuner = None
        logger.info("自适应调整器延迟初始化")
    
    def set_current_params(self, params: Dict[str, float]):
        """设置当前参数（用于自适应调整器）"""
        if self.adaptive_tuner is None:
            self.adaptive_tuner = AdaptiveParameterTuner(
                current_params=params,
                param_bounds=self.param_bounds
            )
        else:
            self.adaptive_tuner.current_params = params.copy()
    
    def optimize(self,
                objective_function: Callable[[Dict[str, float]], Dict[str, float]],
                n_iterations: int = 50,
                market_data: Optional[Dict] = None,
                use_hybrid: bool = True) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        执行优化
        
        Args:
            objective_function: 目标函数
            n_iterations: 迭代次数
            market_data: 市场数据
            use_hybrid: 是否使用混合优化
        
        Returns:
            (最优参数, 最优性能)
        """
        logger.info(f"开始优化，模式: {self.optimization_mode}, 迭代次数: {n_iterations}")
        
        # 选择优化方法
        if self.optimization_mode == 'traditional':
            return self._traditional_optimize(objective_function, n_iterations)
        
        elif self.optimization_mode == 'llm':
            return self._llm_optimize(objective_function, n_iterations, market_data)
        
        elif self.optimization_mode == 'bayesian':
            return self._bayesian_optimize(objective_function, n_iterations)
        
        elif self.optimization_mode == 'hybrid' and use_hybrid:
            return self._hybrid_optimize(objective_function, n_iterations, market_data)
        
        elif self.optimization_mode == 'adaptive':
            return self._adaptive_optimize(objective_function, n_iterations)
        
        else:
            logger.warning(f"未知优化模式: {self.optimization_mode}，使用混合模式")
            return self._hybrid_optimize(objective_function, n_iterations, market_data)
    
    def _traditional_optimize(self,
                              objective_function: Callable,
                              n_iterations: int) -> Tuple[Dict, Dict]:
        """传统算法优化（WOAm）"""
        if 'woam' not in self.traditional_optimizers:
            self.traditional_optimizers['woam'] = WOAm(pop_size=200)
        
        optimizer = self.traditional_optimizers['woam']
        
        # 转换边界
        bounds = [self.param_bounds[name] for name in self.param_names]
        
        # 执行优化
        best_solution, best_score = optimizer.optimize(
            objective_function=self._wrap_objective_function(objective_function),
            bounds=bounds,
            epochs=n_iterations
        )
        
        # 转换结果
        best_params = {}
        for i, name in enumerate(self.param_names):
            best_params[name] = float(best_solution[i])
        
        # 评估最优参数
        best_performance = objective_function(best_params)
        
        logger.info(f"传统优化完成，得分: {best_score:.4f}")
        return best_params, best_performance
    
    def _llm_optimize(self,
                      objective_function: Callable,
                      n_iterations: int,
                      market_data: Optional[Dict]) -> Tuple[Dict, Dict]:
        """大模型优化"""
        if self.llm_optimizer is None:
            logger.error("LLM优化器未初始化")
            return self._get_fallback_params(objective_function)
        
        # 如果有市场数据，推荐参数
        if market_data and len(self.llm_optimizer.param_history) > 0:
            best_params = self.llm_optimizer.recommend_params(market_data)
        else:
            best_params = self.llm_optimizer._get_random_params()
        
        # 迭代优化
        for i in range(n_iterations):
            # 评估参数
            performance = objective_function(best_params)
            
            # 更新学习器
            if market_data:
                self.llm_optimizer.update_performance(
                    best_params, performance, market_data
                )
            
            # 生成新参数
            if market_data:
                best_params = self.llm_optimizer.recommend_params(market_data)
            else:
                best_params = self.llm_optimizer._get_random_params()
        
        # 评估最终参数
        best_performance = objective_function(best_params)
        
        logger.info(f"LLM优化完成，综合得分: {self.llm_optimizer.best_performance}")
        return best_params, best_performance
    
    def _bayesian_optimize(self,
                          objective_function: Callable,
                          n_iterations: int) -> Tuple[Dict, Dict]:
        """贝叶斯优化"""
        if self.bayesian_optimizer is None:
            logger.error("贝叶斯优化器未初始化")
            return self._get_fallback_params(objective_function)
        
        # 执行优化
        best_params, best_performance = self.bayesian_optimizer.optimize(
            objective_function=objective_function,
            n_iterations=n_iterations
        )
        
        logger.info(f"贝叶斯优化完成")
        return best_params, best_performance
    
    def _hybrid_optimize(self,
                         objective_function: Callable,
                         n_iterations: int,
                         market_data: Optional[Dict]) -> Tuple[Dict, Dict]:
        """混合优化"""
        # 分配迭代次数
        n_traditional = int(n_iterations * self.config['hybrid_weight']['traditional'])
        n_llm = int(n_iterations * self.config['hybrid_weight']['llm'])
        n_bayesian = n_iterations - n_traditional - n_llm
        
        logger.info(f"混合优化: 传统={n_traditional}, LLM={n_llm}, 贝叶斯={n_bayesian}")
        
        # 传统优化
        if n_traditional > 0:
            trad_params, trad_perf = self._traditional_optimize(
                objective_function, n_traditional
            )
            self._record_optimization_result(trad_params, trad_perf, 'traditional')
        else:
            trad_params = self._get_random_params()
            trad_perf = objective_function(trad_params)
        
        # LLM优化
        if n_llm > 0 and self.llm_optimizer:
            llm_params, llm_perf = self._llm_optimize(
                objective_function, n_llm, market_data
            )
            self._record_optimization_result(llm_params, llm_perf, 'llm')
        else:
            llm_params = self._get_random_params()
            llm_perf = objective_function(llm_params)
        
        # 贝叶斯优化
        if n_bayesian > 0 and self.bayesian_optimizer:
            bayes_params, bayes_perf = self._bayesian_optimize(
                objective_function, n_bayesian
            )
            self._record_optimization_result(bayes_params, bayes_perf, 'bayesian')
        else:
            bayes_params = self._get_random_params()
            bayes_perf = objective_function(bayes_params)
        
        # 合并结果
        best_params = self._merge_results([
            (trad_params, trad_perf, self.config['hybrid_weight']['traditional']),
            (llm_params, llm_perf, self.config['hybrid_weight']['llm']),
            (bayes_params, bayes_perf, self.config['hybrid_weight']['bayesian'])
        ])
        
        # 评估最终结果
        best_performance = objective_function(best_params)
        
        logger.info(f"混合优化完成")
        return best_params, best_performance
    
    def _adaptive_optimize(self,
                          objective_function: Callable,
                          n_iterations: int) -> Tuple[Dict, Dict]:
        """自适应优化"""
        if self.adaptive_tuner is None:
            logger.error("自适应调整器未初始化")
            return self._get_fallback_params(objective_function)
        
        # 执行自动调参
        result = self.adaptive_tuner.auto_tune(
            objective_function=objective_function,
            n_iterations=n_iterations
        )
        
        if result['success']:
            best_params = result['best_params']
            best_performance = result['best_params']
            logger.info(f"自适应优化完成，得分: {result['best_score']:.4f}")
        else:
            best_params = self.adaptive_tuner.current_params
            best_performance = objective_function(best_params)
            logger.warning(f"自适应优化失败，使用当前参数")
        
        return best_params, best_performance
    
    def _wrap_objective_function(self, 
                                 objective_function: Callable) -> Callable:
        """包装目标函数以适配传统优化器"""
        def wrapper(params_array):
            # 转换参数
            params_dict = {}
            for i, name in enumerate(self.param_names):
                params_dict[name] = float(params_array[i])
            
            # 调用原函数
            performance = objective_function(params_dict)
            
            # 计算得分
            score = 0.0
            if 'return' in performance:
                score += performance['return'] * 0.3
            if 'sharpe' in performance:
                score += performance['sharpe'] * 0.4
            if 'max_drawdown' in performance:
                normalized_dd = max(0, min(1, performance['max_drawdown'] / 0.5))
                score += (1 - normalized_dd) * 0.3
            
            return score
        
        return wrapper
    
    def _get_fallback_params(self,
                             objective_function: Callable) -> Tuple[Dict, Dict]:
        """获取回退参数"""
        params = {}
        for name, (min_val, max_val) in self.param_bounds.items():
            params[name] = np.random.uniform(min_val, max_val)
        
        performance = objective_function(params)
        return params, performance
    
    def _get_random_params(self) -> Dict[str, float]:
        """生成随机参数"""
        params = {}
        for name, (min_val, max_val) in self.param_bounds.items():
            params[name] = np.random.uniform(min_val, max_val)
        return params
    
    def _record_optimization_result(self,
                                   params: Dict[str, float],
                                   performance: Dict[str, float],
                                   method: str):
        """记录优化结果"""
        # 记录历史
        if self.history_learner:
            self.history_learner.add_record(
                params=params,
                performance=performance,
                market_state={'optimization_method': method},
                timestamp=datetime.now()
            )
        
        # 记录优化历史
        self.optimization_history.append({
            'timestamp': datetime.now(),
            'params': params,
            'performance': performance,
            'method': method
        })
        
        # 更新最优解
        if self.best_performance is None or \
           self._calculate_score(performance) > self._calculate_score(self.best_performance):
            self.best_params = params.copy()
            self.best_performance = performance.copy()
    
    def _merge_results(self,
                      results: List[Tuple[Dict, Dict, float]]) -> Dict[str, float]:
        """合并多个优化结果"""
        merged_params = {}
        
        for name in self.param_names:
            # 加权平均
            weighted_sum = 0.0
            total_weight = 0.0
            
            for params, performance, weight in results:
                if name in params:
                    score = self._calculate_score(performance)
                    weighted_sum += params[name] * score * weight
                    total_weight += score * weight
            
            if total_weight > 0:
                merged_params[name] = weighted_sum / total_weight
            else:
                merged_params[name] = self._get_random_params()[name]
        
        return merged_params
    
    def _calculate_score(self, performance: Dict[str, float]) -> float:
        """计算综合得分"""
        score = 0.0
        
        if 'return' in performance:
            score += performance['return'] * 0.3
        if 'sharpe' in performance:
            score += performance['sharpe'] * 0.4
        if 'max_drawdown' in performance:
            normalized_dd = max(0, min(1, performance['max_drawdown'] / 0.5))
            score += (1 - normalized_dd) * 0.3
        
        return score
    
    def recommend_parameters(self,
                           market_data: Optional[Dict] = None,
                           top_k: int = 3) -> List[Dict[str, float]]:
        """
        推荐参数
        
        Args:
            market_data: 市场数据
            top_k: 返回top_k个候选
        
        Returns:
            候选参数列表
        """
        recommendations = []
        
        # 1. LLM推荐
        if self.llm_optimizer and market_data:
            llm_params = self.llm_optimizer.recommend_params(market_data)
            recommendations.append({
                'params': llm_params,
                'source': 'llm',
                'score': 0.8
            })
        
        # 2. 历史学习推荐
        if self.history_learner and market_data:
            history_candidates = self.history_learner.predict_best_params(
                market_data, top_k
            )
            for params, similarity in history_candidates:
                recommendations.append({
                    'params': params,
                    'source': 'history',
                    'score': similarity
                })
        
        # 3. 最优参数
        if self.best_params:
            recommendations.append({
                'params': self.best_params,
                'source': 'best',
                'score': 0.9
            })
        
        # 排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回top_k
        return [r['params'] for r in recommendations[:top_k]]
    
    def monitor_and_adjust(self,
                           current_performance: Dict[str, float],
                           market_data: Optional[Dict] = None):
        """
        监控性能并调整参数
        
        Args:
            current_performance: 当前性能
            market_data: 市场数据
        """
        # 更新自适应调整器
        if self.adaptive_tuner:
            self.adaptive_tuner.monitor_performance(current_performance)
            
            # 如果检测到性能下降，尝试调整
            if self.adaptive_tuner.drift_detected:
                logger.warning("检测到参数漂移，尝试自动调整")
                
                # 获取推荐参数
                recommendations = self.recommend_parameters(market_data, top_k=1)
                
                if recommendations:
                    success, msg = self.adaptive_tuner.adjust_parameters(
                        recommendations[0],
                        force=False
                    )
                    
                    if success:
                        logger.info(f"参数自动调整成功: {msg}")
        
        # 记录到历史学习器
        if self.history_learner and self.adaptive_tuner:
            self.history_learner.add_record(
                params=self.adaptive_tuner.current_params,
                performance=current_performance,
                market_state=market_data or {},
                timestamp=datetime.now()
            )
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        report = {
            'optimization_mode': self.optimization_mode,
            'best_params': self.best_params,
            'best_performance': self.best_performance,
            'optimization_history_length': len(self.optimization_history),
            'config': self.config
        }
        
        # 添加各优化器的统计
        if self.llm_optimizer:
            report['llm_stats'] = self.llm_optimizer.get_optimization_stats()
        
        if self.bayesian_optimizer:
            report['bayesian_report'] = self.bayesian_optimizer.get_optimization_report()
        
        if self.history_learner:
            report['history_learner_report'] = self.history_learner.get_learning_report()
        
        if self.adaptive_tuner:
            report['adaptive_tuner_status'] = self.adaptive_tuner.get_status()
        
        return report
    
    def export_optimization_data(self, filepath: str):
        """
        导出优化数据
        
        Args:
            filepath: 保存路径
        """
        import json
        
        data = {
            'best_params': self.best_params,
            'best_performance': self.best_performance,
            'optimization_history': self.optimization_history,
            'config': self.config,
            'export_time': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"优化数据已导出到: {filepath}")
    
    def reset(self):
        """重置优化引擎"""
        self.optimization_history = []
        self.best_params = None
        self.best_performance = None
        
        if self.llm_optimizer:
            self.llm_optimizer.reset()
        
        if self.history_learner:
            self.history_learner.reset()
        
        if self.adaptive_tuner:
            self.adaptive_tuner.reset()
        
        logger.info("优化引擎已重置")
