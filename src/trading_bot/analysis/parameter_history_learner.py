#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史数据学习模块 - Parameter History Learner

从历史交易数据中学习最优参数组合
支持市场环境分类和参数相似度匹配

作者: MT5 Trading Bot Team
创建时间: 2026-02-21
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from collections import defaultdict
import json
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
class ParameterHistoryLearner:
    """
    参数历史学习器
    
    核心功能:
    1. 从历史数据中学习最优参数
    2. 识别不同市场环境
    3. 参数组合相似度匹配
    4. 市场状态聚类
    """
    
    def __init__(self,
                 param_names: List[str],
                 market_feature_names: List[str] = None,
                 n_clusters: int = 5):
        """
        初始化参数历史学习器
        
        Args:
            param_names: 参数名称列表
            market_feature_names: 市场特征名称列表
            n_clusters: 市场状态聚类数
        """
        self.param_names = param_names
        self.market_feature_names = market_feature_names or [
            'trend_strength', 'volatility', 'volume_ratio',
            'sentiment', 'momentum', 'choppiness_index'
        ]
        self.n_clusters = n_clusters
        
        # 数据存储
        self.parameter_history = []  # 参数历史
        self.performance_history = []  # 性能历史
        self.market_state_history = []  # 市场状态历史
        self.timestamps = []  # 时间戳
        
        # 聚类模型
        self.cluster_model = None
        self.scaler = StandardScaler()
        self.cluster_labels = None
        self.cluster_centers = None
        
        # 按聚类存储的最优参数
        self.cluster_best_params = {}
        self.cluster_best_performance = {}
        
        # 市场状态相似度缓存
        self.similarity_cache = {}
        
        # 统计信息
        self.stats = {
            'total_records': 0,
            'unique_market_states': 0,
            'best_performing_cluster': None,
            'last_learn_time': None
        }
        
        logger.info("参数历史学习器初始化完成")
    
    def add_record(self,
                   params: Dict[str, float],
                   performance: Dict[str, float],
                   market_state: Dict[str, float],
                   timestamp: datetime = None):
        """
        添加历史记录
        
        Args:
            params: 参数字典
            performance: 性能指标
            market_state: 市场状态
            timestamp: 时间戳
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # 存储数据
        self.parameter_history.append(params)
        self.performance_history.append(performance)
        self.market_state_history.append(market_state)
        self.timestamps.append(timestamp)
        
        # 清除缓存
        self.similarity_cache.clear()
        
        # 更新统计
        self.stats['total_records'] += 1
        self.stats['last_learn_time'] = datetime.now()
        
        logger.debug(f"添加历史记录，总记录数: {self.stats['total_records']}")
    
    def learn(self, force_retrain: bool = False):
        """
        从历史数据中学习
        
        Args:
            force_retrain: 是否强制重新训练
        """
        if not self.market_state_history:
            logger.warning("没有历史数据可供学习")
            return
        
        if len(self.market_state_history) < self.n_clusters:
            logger.warning(f"历史数据不足（{len(self.market_state_history)} < {self.n_clusters}），无法聚类")
            return
        
        # 检查是否需要重新训练
        if not force_retrain and self.cluster_model is not None:
            if len(self.parameter_history) - self.stats.get('last_train_size', 0) < 10:
                logger.info("数据变化不大，跳过重新训练")
                return
        
        # 执行聚类
        self._perform_clustering()
        
        # 分析每个聚类
        self._analyze_clusters()
        
        # 更新统计
        self.stats['last_train_size'] = len(self.parameter_history)
        
        logger.info("学习完成")
    
    def _perform_clustering(self):
        """执行市场状态聚类"""
        # 提取市场特征
        feature_vectors = []
        for state in self.market_state_history:
            vector = [state.get(feat, 0) for feat in self.market_feature_names]
            feature_vectors.append(vector)
        
        feature_vectors = np.array(feature_vectors)
        
        # 标准化
        feature_vectors_scaled = self.scaler.fit_transform(feature_vectors)
        
        # 聚类
        self.cluster_model = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.cluster_labels = self.cluster_model.fit_predict(feature_vectors_scaled)
        self.cluster_centers = self.cluster_model.cluster_centers_
        
        # 更新统计
        unique_labels = len(set(self.cluster_labels))
        self.stats['unique_market_states'] = unique_labels
        
        logger.info(f"聚类完成，识别出 {unique_labels} 个市场状态")
    
    def _analyze_clusters(self):
        """分析每个聚类的最优参数"""
        # 初始化
        self.cluster_best_params = {}
        self.cluster_best_performance = {}
        
        # 按聚类分组
        cluster_records = defaultdict(list)
        for i, label in enumerate(self.cluster_labels):
            cluster_records[label].append(i)
        
        # 对每个聚类找最优参数
        for label, indices in cluster_records.items():
            # 计算该聚类内所有记录的综合得分
            scores = []
            for idx in indices:
                perf = self.performance_history[idx]
                score = self._calculate_combined_score(perf)
                scores.append(score)
            
            # 找最优记录
            best_idx = indices[np.argmax(scores)]
            
            # 保存最优参数和性能
            self.cluster_best_params[label] = self.parameter_history[best_idx]
            self.cluster_best_performance[label] = self.performance_history[best_idx]
            
            logger.debug(f"聚类 {label}: 最优得分={max(scores):.4f}")
        
        # 找最佳聚类
        best_cluster_score = max(
            self._calculate_combined_score(self.cluster_best_performance[label])
            for label in self.cluster_best_performance
        )
        for label, perf in self.cluster_best_performance.items():
            if self._calculate_combined_score(perf) >= best_cluster_score:
                self.stats['best_performing_cluster'] = label
    
    def _calculate_combined_score(self, performance: Dict[str, float]) -> float:
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
    
    def predict_best_params(self,
                           market_state: Dict[str, float],
                           top_k: int = 3) -> List[Tuple[Dict[str, float], float]]:
        """
        预测当前市场状态下的最优参数
        
        Args:
            market_state: 当前市场状态
            top_k: 返回top_k个候选参数
        
        Returns:
            候选参数列表及其相似度得分
        """
        if not self.parameter_history:
            logger.warning("没有历史数据，无法预测")
            return []
        
        # 找到相似的聚类
        cluster_candidates = self._find_similar_clusters(market_state, top_k)
        
        if not cluster_candidates:
            return []
        
        # 合并候选参数
        candidates = []
        for cluster_label, similarity in cluster_candidates:
            if cluster_label in self.cluster_best_params:
                params = self.cluster_best_params[cluster_label]
                candidates.append((params, similarity))
        
        return candidates
    
    def _find_similar_clusters(self,
                               market_state: Dict[str, float],
                               top_k: int) -> List[Tuple[int, float]]:
        """
        找到与当前市场状态相似的聚类
        
        Args:
            market_state: 当前市场状态
            top_k: 返回top_k个聚类
        
        Returns:
            聚类标签和相似度列表
        """
        if self.cluster_centers is None:
            return []
        
        # 提取特征向量
        feature_vector = [market_state.get(feat, 0) for feat in self.market_feature_names]
        feature_vector = np.array(feature_vector).reshape(1, -1)
        
        # 标准化
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # 计算到各聚类中心的距离
        distances = euclidean_distances(feature_vector_scaled, self.cluster_centers)[0]
        
        # 转换为相似度
        max_dist = np.max(distances)
        if max_dist > 0:
            similarities = 1 - distances / max_dist
        else:
            similarities = np.ones_like(distances)
        
        # 排序并取top_k
        sorted_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(int(idx), similarities[idx]) for idx in sorted_indices]
    
    def find_similar_records(self,
                            market_state: Dict[str, float],
                            top_k: int = 5,
                            min_days_back: int = 30) -> List[Tuple[int, float]]:
        """
        找到历史中相似的记录
        
        Args:
            market_state: 当前市场状态
            top_k: 返回top_k个记录
            min_days_back: 最少回溯天数
        
        Returns:
            记录索引和相似度列表
        """
        if not self.market_state_history:
            return []
        
        # 提取特征向量
        current_vector = [market_state.get(feat, 0) for feat in self.market_feature_names]
        current_vector = np.array(current_vector)
        
        # 计算时间过滤
        now = datetime.now()
        min_time = now - timedelta(days=min_days_back)
        
        # 计算相似度
        similarities = []
        for i, historical_state in enumerate(self.market_state_history):
            # 时间过滤
            if self.timestamps[i] < min_time:
                continue
            
            # 计算相似度
            hist_vector = [historical_state.get(feat, 0) for feat in self.market_feature_names]
            hist_vector = np.array(hist_vector)
            
            sim = cosine_similarity([current_vector], [hist_vector])[0][0]
            similarities.append((i, sim))
        
        # 排序并取top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def calculate_parameter_similarity(self,
                                     params1: Dict[str, float],
                                     params2: Dict[str, float]) -> float:
        """
        计算两组参数的相似度
        
        Args:
            params1: 参数组合1
            params2: 参数组合2
        
        Returns:
            相似度分数 (0-1)
        """
        # 归一化参数
        vec1 = []
        vec2 = []
        
        for name in self.param_names:
            if name in params1 and name in params2:
                vec1.append(params1[name])
                vec2.append(params2[name])
        
        if not vec1:
            return 0.0
        
        # 余弦相似度
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        return cosine_similarity([vec1], [vec2])[0][0]
    
    def get_parameter_statistics(self, cluster_label: int = None) -> Dict[str, Dict[str, float]]:
        """
        获取参数统计信息
        
        Args:
            cluster_label: 聚类标签，None表示所有数据
        
        Returns:
            参数统计信息
        """
        # 过滤数据
        if cluster_label is not None:
            if self.cluster_labels is None:
                return {}
            indices = [i for i, label in enumerate(self.cluster_labels) if label == cluster_label]
        else:
            indices = range(len(self.parameter_history))
        
        # 计算统计
        stats = {}
        for name in self.param_names:
            values = [self.parameter_history[i][name] for i in indices if name in self.parameter_history[i]]
            
            if values:
                stats[name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'median': float(np.median(values))
                }
        
        return stats
    
    def export_data(self, filepath: str):
        """
        导出学习数据到文件
        
        Args:
            filepath: 保存路径
        """
        data = {
            'parameter_history': self.parameter_history,
            'performance_history': self.performance_history,
            'market_state_history': self.market_state_history,
            'timestamps': [ts.isoformat() for ts in self.timestamps],
            'cluster_labels': self.cluster_labels.tolist() if self.cluster_labels is not None else None,
            'cluster_centers': self.cluster_centers.tolist() if self.cluster_centers is not None else None,
            'cluster_best_params': self.cluster_best_params,
            'cluster_best_performance': self.cluster_best_performance,
            'stats': self.stats
        }
        
        # 处理非序列化对象
        def default_serializer(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return str(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=default_serializer)
        
        logger.info(f"数据已导出到: {filepath}")
    
    def load_data(self, filepath: str):
        """
        从文件加载学习数据
        
        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.parameter_history = data.get('parameter_history', [])
            self.performance_history = data.get('performance_history', [])
            self.market_state_history = data.get('market_state_history', [])
            
            # 恢复时间戳
            self.timestamps = [
                datetime.fromisoformat(ts) for ts in data.get('timestamps', [])
            ]
            
            # 恢复聚类模型
            self.cluster_labels = np.array(data.get('cluster_labels'))
            self.cluster_centers = np.array(data.get('cluster_centers'))
            
            # 恢复最优参数
            self.cluster_best_params = data.get('cluster_best_params', {})
            self.cluster_best_performance = data.get('cluster_best_performance', {})
            
            # 恢复统计
            self.stats = data.get('stats', {})
            
            logger.info(f"数据已加载，记录数: {len(self.parameter_history)}")
            
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
    
    def get_learning_report(self) -> Dict[str, Any]:
        """
        获取学习报告
        
        Returns:
            学习报告字典
        """
        report = {
            'stats': self.stats,
            'cluster_analysis': {},
            'parameter_statistics': self.get_parameter_statistics(),
            'recent_performance': self._get_recent_performance()
        }
        
        # 聚类分析
        if self.cluster_labels is not None:
            unique_labels = set(self.cluster_labels)
            for label in unique_labels:
                cluster_stats = self.get_parameter_statistics(label)
                report['cluster_analysis'][f'cluster_{label}'] = {
                    'size': int(np.sum(self.cluster_labels == label)),
                    'best_performance': self.cluster_best_performance.get(label, {}),
                    'parameter_stats': cluster_stats
                }
        
        return report
    
    def _get_recent_performance(self, n_days: int = 30) -> Dict[str, float]:
        """获取最近n天的性能"""
        now = datetime.now()
        min_time = now - timedelta(days=n_days)
        
        recent_indices = [
            i for i, ts in enumerate(self.timestamps) if ts >= min_time
        ]
        
        if not recent_indices:
            return {}
        
        scores = [
            self._calculate_combined_score(self.performance_history[i])
            for i in recent_indices
        ]
        
        return {
            'avg_score': float(np.mean(scores)),
            'max_score': float(np.max(scores)),
            'min_score': float(np.min(scores)),
            'n_trades': len(recent_indices)
        }
    
    def reset(self):
        """重置学习器"""
        self.parameter_history = []
        self.performance_history = []
        self.market_state_history = []
        self.timestamps = []
        
        self.cluster_model = None
        self.cluster_labels = None
        self.cluster_centers = None
        
        self.cluster_best_params = {}
        self.cluster_best_performance = {}
        
        self.similarity_cache.clear()
        
        self.stats = {
            'total_records': 0,
            'unique_market_states': 0,
            'best_performing_cluster': None,
            'last_learn_time': None
        }
        
        logger.info("学习器已重置")
