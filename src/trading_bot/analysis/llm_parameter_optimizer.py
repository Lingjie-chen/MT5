#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型参数优化器 - LLM Parameter Optimizer

基于大模型学习的参数优化系统，替代传统遗传算法
支持在线学习、参数动态调整和市场状态自适应

作者: MT5 Trading Bot Team
创建时间: 2026-02-21
"""

import numpy as np
import pandas as pd
import logging
import json
import time
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
import warnings
warnings.filterwarnings('ignore')

# 导入项目模块
try:
    from ai.ai_client_factory import AIClientFactory
    from utils.robust_json_parser import RobustJSONParser
except ImportError:
    # 用于独立测试
    AIClientFactory = None
    RobustJSONParser = None

logger = logging.getLogger(__name__)
class LLMParameterOptimizer:
    """
    大模型参数优化器核心类
    
    核心功能:
    1. 使用大模型学习历史最优参数组合
    2. 支持在线学习和参数动态调整
    3. 基于市场状态的参数推荐系统
    4. 多目标优化支持
    """
    
    def __init__(self, 
                 param_bounds: Dict[str, Tuple[float, float]],
                 objective_metrics: List[str] = ['return', 'sharpe', 'max_drawdown'],
                 model_type: str = 'qwen',
                 learning_rate: float = 0.1,
                 exploration_rate: float = 0.3):
        """
        初始化大模型参数优化器
        
        Args:
            param_bounds: 参数边界字典 {参数名: (最小值, 最大值)}
            objective_metrics: 优化目标指标列表
            model_type: 大模型类型 ('qwen' 或 'deepseek')
            learning_rate: 学习率，控制参数调整幅度
            exploration_rate: 探索率，控制随机探索比例
        """
        self.param_bounds = param_bounds
        self.param_names = list(param_bounds.keys())
        self.n_params = len(self.param_names)
        
        self.objective_metrics = objective_metrics
        self.model_type = model_type
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        
        # 初始化AI客户端
        self.ai_client = None
        self.json_parser = RobustJSONParser() if RobustJSONParser else None
        
        # 历史数据存储
        self.param_history = []  # 参数历史
        self.performance_history = []  # 性能历史
        self.market_state_history = []  # 市场状态历史
        
        # 当前最优参数
        self.best_params = self._get_random_params()
        self.best_performance = None
        self.best_market_state = None
        
        # 参数重要性权重
        self.param_importance = {name: 1.0 / self.n_params for name in self.param_names}
        
        # 统计信息
        self.optimization_stats = {
            'total_evaluations': 0,
            'improvements': 0,
            'last_update_time': None,
            'convergence_rate': 0.0
        }
        
        logger.info(f"LLM参数优化器初始化完成，参数数量: {self.n_params}, 优化目标: {objective_metrics}")
    
    def _initialize_ai_client(self):
        """初始化AI客户端"""
        if self.ai_client is None and AIClientFactory:
            try:
                factory = AIClientFactory()
                self.ai_client = factory.create_client(self.model_type)
                logger.info(f"AI客户端初始化成功: {self.model_type}")
            except Exception as e:
                logger.error(f"AI客户端初始化失败: {e}")
                self.ai_client = None
    
    def _get_random_params(self) -> Dict[str, float]:
        """生成随机参数"""
        params = {}
        for name, (min_val, max_val) in self.param_bounds.items():
            params[name] = np.random.uniform(min_val, max_val)
        return params
    
    def _normalize_params(self, params: Dict[str, float]) -> np.ndarray:
        """将参数归一化到[0,1]区间"""
        normalized = np.zeros(self.n_params)
        for i, name in enumerate(self.param_names):
            min_val, max_val = self.param_bounds[name]
            normalized[i] = (params[name] - min_val) / (max_val - min_val)
        return normalized
    
    def _denormalize_params(self, normalized: np.ndarray) -> Dict[str, float]:
        """将归一化参数还原"""
        params = {}
        for i, name in enumerate(self.param_names):
            min_val, max_val = self.param_bounds[name]
            params[name] = normalized[i] * (max_val - min_val) + min_val
        return params
    
    def _calculate_market_state_vector(self, market_data: Dict) -> np.ndarray:
        """
        计算市场状态向量
        
        考虑因素:
        - 趋势强度
        - 波动率
        - 成交量
        - 市场情绪
        """
        features = [
            market_data.get('trend_strength', 0),
            market_data.get('volatility', 0),
            market_data.get('volume_ratio', 1.0),
            market_data.get('sentiment', 0),
            market_data.get('momentum', 0),
            market_data.get('choppiness_index', 0)
        ]
        
        # 归一化
        features = np.array(features)
        features = (features - features.min()) / (features.max() - features.min() + 1e-8)
        return features
    
    def _find_similar_market_states(self, 
                                    current_state: np.ndarray,
                                    top_k: int = 5) -> List[Tuple[int, float]]:
        """
        找到与当前市场状态最相似的历史状态
        
        Args:
            current_state: 当前市场状态向量
            top_k: 返回最相似的top_k个状态
        
        Returns:
            相似状态索引列表及其相似度
        """
        if len(self.market_state_history) == 0:
            return []
        
        similarities = []
        for i, historical_state in enumerate(self.market_state_history):
            # 使用余弦相似度
            sim = cosine_similarity([current_state], [historical_state])[0][0]
            similarities.append((i, sim))
        
        # 按相似度排序，取top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def _combine_params_with_importance(self, 
                                        params_list: List[Dict[str, float]],
                                        weights: List[float]) -> Dict[str, float]:
        """
        基于参数重要性权重合并多个参数组合
        
        Args:
            params_list: 参数组合列表
            weights: 每个参数组合的权重
        
        Returns:
            合并后的参数字典
        """
        combined = {}
        
        for param_name in self.param_names:
            # 加权平均
            weighted_sum = 0.0
            weight_sum = 0.0
            
            for params, weight in zip(params_list, weights):
                weighted_sum += params[param_name] * weight * self.param_importance[param_name]
                weight_sum += weight * self.param_importance[param_name]
            
            if weight_sum > 0:
                combined[param_name] = weighted_sum / weight_sum
            else:
                combined[param_name] = self._get_random_params()[param_name]
        
        return combined
    
    def recommend_params(self, market_data: Dict, 
                       use_exploration: bool = True) -> Dict[str, float]:
        """
        基于市场状态推荐参数
        
        Args:
            market_data: 市场数据字典
            use_exploration: 是否使用探索策略
        
        Returns:
            推荐的参数字典
        """
        # 计算当前市场状态
        current_state = self._calculate_market_state_vector(market_data)
        
        # 找到相似的历史状态
        similar_states = self._find_similar_market_states(current_state)
        
        if not similar_states or len(similar_states) == 0:
            # 没有历史数据，返回随机参数
            logger.info("无历史数据，返回随机参数")
            return self._get_random_params()
        
        # 提取相似状态的参数和性能
        params_list = []
        weights = []
        
        for idx, similarity in similar_states:
            if idx < len(self.param_history):
                params_list.append(self.param_history[idx])
                # 性能越好，权重越大
                performance = self.performance_history[idx]
                # 综合考虑相似度和性能
                weight = similarity * performance.get('combined_score', 0.5)
                weights.append(weight)
        
        if not params_list:
            return self._get_random_params()
        
        # 归一化权重
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(weights)] * len(weights)
        
        # 合并参数
        recommended_params = self._combine_params_with_importance(params_list, weights)
        
        # 探索策略: 随机扰动
        if use_exploration and np.random.random() < self.exploration_rate:
            logger.info("使用探索策略，添加随机扰动")
            recommended_params = self._add_exploration_noise(recommended_params)
        
        # 使用大模型优化（如果可用）
        if self.ai_client and np.random.random() < 0.5:
            recommended_params = self._optimize_with_llm(recommended_params, market_data)
        
        # 确保参数在边界内
        recommended_params = self._clip_params(recommended_params)
        
        logger.info(f"推荐参数: {recommended_params}")
        return recommended_params
    
    def _add_exploration_noise(self, params: Dict[str, float]) -> Dict[str, float]:
        """添加探索噪声"""
        noisy_params = {}
        for name, value in params.items():
            min_val, max_val = self.param_bounds[name]
            # 添加高斯噪声
            noise_scale = (max_val - min_val) * 0.1 * self.learning_rate
            noise = np.random.normal(0, noise_scale)
            noisy_params[name] = value + noise
        return noisy_params
    
    def _clip_params(self, params: Dict[str, float]) -> Dict[str, float]:
        """确保参数在边界内"""
        clipped = {}
        for name, value in params.items():
            min_val, max_val = self.param_bounds[name]
            clipped[name] = np.clip(value, min_val, max_val)
        return clipped
    
    def _optimize_with_llm(self, 
                          current_params: Dict[str, float],
                          market_data: Dict) -> Dict[str, float]:
        """
        使用大模型优化参数
        
        Args:
            current_params: 当前参数
            market_data: 市场数据
        
        Returns:
            优化后的参数
        """
        self._initialize_ai_client()
        if not self.ai_client:
            return current_params
        
        try:
            # 构建提示词
            prompt = self._build_optimization_prompt(current_params, market_data)
            
            # 调用大模型
            response = self.ai_client.generate(prompt, temperature=0.7)
            
            # 解析响应
            if self.json_parser:
                optimized_params = self.json_parser.parse(response)
            else:
                # 简单解析
                optimized_params = self._simple_parse_json(response)
            
            if optimized_params and self._validate_params(optimized_params):
                logger.info("大模型优化成功")
                return self._clip_params(optimized_params)
            else:
                logger.warning("大模型优化结果无效，使用原参数")
                return current_params
                
        except Exception as e:
            logger.error(f"大模型优化失败: {e}")
            return current_params
    
    def _build_optimization_prompt(self, 
                                   params: Dict[str, float],
                                   market_data: Dict) -> str:
        """构建优化提示词"""
        prompt = f"""
你是专业的交易策略参数优化专家。

当前市场状态:
- 趋势强度: {market_data.get('trend_strength', 0):.2f}
- 波动率: {market_data.get('volatility', 0):.2f}
- 成交量比率: {market_data.get('volume_ratio', 1.0):.2f}
- 市场情绪: {market_data.get('sentiment', 0):.2f}
- 动量: {market_data.get('momentum', 0):.2f}
- 震荡指数: {market_data.get('choppiness_index', 0):.2f}

当前参数:
{json.dumps(params, indent=2)}

请根据当前市场状态，优化这些参数以提高策略表现。
考虑:
1. 趋势市场应该调整哪些参数
2. 震荡市场应该调整哪些参数
3. 高波动环境下如何调整
4. 保持参数在合理范围内

请以JSON格式返回优化后的参数，格式:
{{
  "参数名1": 数值1,
  "参数名2": 数值2,
  ...
}}

参数边界:
{json.dumps(self.param_bounds, indent=2)}
"""
        return prompt
    
    def _simple_parse_json(self, text: str) -> Optional[Dict]:
        """简单JSON解析"""
        try:
            # 查找JSON块
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass
        return None
    
    def _validate_params(self, params: Dict) -> bool:
        """验证参数有效性"""
        if not isinstance(params, dict):
            return False
        
        for name, value in params.items():
            if name not in self.param_bounds:
                continue
            min_val, max_val = self.param_bounds[name]
            if not (min_val <= value <= max_val):
                return False
        
        return True
    
    def update_performance(self,
                          params: Dict[str, float],
                          performance: Dict[str, float],
                          market_data: Dict):
        """
        更新性能数据和参数历史
        
        Args:
            params: 使用的参数
            performance: 性能指标
            market_data: 市场数据
        """
        # 计算综合得分
        combined_score = self._calculate_combined_score(performance)
        performance['combined_score'] = combined_score
        
        # 存储历史
        self.param_history.append(params)
        self.performance_history.append(performance)
        self.market_state_history.append(self._calculate_market_state_vector(market_data))
        
        # 更新最优参数
        if self.best_performance is None or combined_score > self.best_performance['combined_score']:
            self.best_performance = performance
            self.best_params = params
            self.best_market_state = market_data
            self.optimization_stats['improvements'] += 1
            logger.info(f"发现新的最优参数，综合得分: {combined_score:.4f}")
        
        # 更新参数重要性
        self._update_param_importance(performance, params)
        
        # 更新统计信息
        self.optimization_stats['total_evaluations'] += 1
        self.optimization_stats['last_update_time'] = datetime.now()
        
        # 计算收敛率
        if len(self.performance_history) > 10:
            recent_scores = [p['combined_score'] for p in self.performance_history[-10:]]
            self.optimization_stats['convergence_rate'] = np.std(recent_scores)
    
    def _calculate_combined_score(self, performance: Dict[str, float]) -> float:
        """
        计算综合得分
        
        综合考虑多个优化目标:
        - 收益率 (正向)
        - 夏普比率 (正向)
        - 最大回撤 (负向)
        """
        score = 0.0
        
        # 收益率权重 0.3
        if 'return' in performance:
            score += performance['return'] * 0.3
        
        # 夏普比率权重 0.4
        if 'sharpe' in performance:
            score += performance['sharpe'] * 0.4
        
        # 最大回撤权重 0.3 (负向，所以用1-归一化值)
        if 'max_drawdown' in performance:
            # 回撤越小越好，所以转换为正向指标
            normalized_dd = max(0, min(1, performance['max_drawdown'] / 0.5))  # 假设50%回撤为最大
            score += (1 - normalized_dd) * 0.3
        
        return score
    
    def _update_param_importance(self, 
                               performance: Dict,
                               params: Dict):
        """
        更新参数重要性权重
        
        基于参数变化对性能的影响
        """
        if len(self.param_history) < 2:
            return
        
        # 获取最近两次的性能和参数
        prev_params = self.param_history[-2]
        prev_perf = self.performance_history[-2]
        curr_params = params
        curr_perf = performance
        
        # 计算性能变化
        perf_change = curr_perf.get('combined_score', 0) - prev_perf.get('combined_score', 0)
        
        # 计算参数变化
        for param_name in self.param_names:
            param_change = abs(curr_params[param_name] - prev_params[param_name])
            
            # 参数变化越大，且性能提升越大，该参数重要性越高
            if param_change > 0:
                importance_delta = (perf_change / param_change) * self.learning_rate
                self.param_importance[param_name] += importance_delta
        
        # 归一化重要性权重
        total_importance = sum(self.param_importance.values())
        if total_importance > 0:
            for name in self.param_names:
                self.param_importance[name] /= total_importance
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        stats = self.optimization_stats.copy()
        
        # 添加额外统计信息
        if len(self.performance_history) > 0:
            scores = [p['combined_score'] for p in self.performance_history]
            stats['avg_score'] = np.mean(scores)
            stats['max_score'] = max(scores)
            stats['min_score'] = min(scores)
            stats['score_std'] = np.std(scores)
        
        stats['param_importance'] = self.param_importance
        stats['history_length'] = len(self.param_history)
        
        return stats
    
    def export_history(self, filepath: str):
        """
        导出历史数据到文件
        
        Args:
            filepath: 保存路径
        """
        history_data = {
            'param_history': self.param_history,
            'performance_history': self.performance_history,
            'optimization_stats': self.optimization_stats,
            'param_importance': self.param_importance,
            'best_params': self.best_params,
            'best_performance': self.best_performance
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"历史数据已导出到: {filepath}")
    
    def load_history(self, filepath: str):
        """
        从文件加载历史数据
        
        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            self.param_history = history_data.get('param_history', [])
            self.performance_history = history_data.get('performance_history', [])
            self.optimization_stats = history_data.get('optimization_stats', {})
            self.param_importance = history_data.get('param_importance', {})
            self.best_params = history_data.get('best_params')
            self.best_performance = history_data.get('best_performance')
            
            # 如果有历史数据，重建市场状态向量
            self.market_state_history = []
            for i in range(len(self.param_history)):
                if i < len(self.performance_history):
                    # 简化的市场状态重建
                    state_vector = np.array([
                        self.performance_history[i].get('trend_strength', 0),
                        self.performance_history[i].get('volatility', 0),
                        1.0,
                        self.performance_history[i].get('sentiment', 0),
                        self.performance_history[i].get('momentum', 0),
                        self.performance_history[i].get('choppiness_index', 0)
                    ])
                    self.market_state_history.append(state_vector)
            
            logger.info(f"历史数据已加载，历史记录数: {len(self.param_history)}")
            
        except Exception as e:
            logger.error(f"加载历史数据失败: {e}")
    
    def reset(self):
        """重置优化器状态"""
        self.param_history = []
        self.performance_history = []
        self.market_state_history = []
        
        self.best_params = self._get_random_params()
        self.best_performance = None
        self.best_market_state = None
        
        self.param_importance = {name: 1.0 / self.n_params for name in self.param_names}
        
        self.optimization_stats = {
            'total_evaluations': 0,
            'improvements': 0,
            'last_update_time': None,
            'convergence_rate': 0.0
        }
        
        logger.info("优化器状态已重置")
