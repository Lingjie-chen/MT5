#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型因子发现与选择系统 - Factor Discovery

自动发现有效的交易因子，支持特征选择和因子有效性评估

作者: MT5 Trading Bot Team
创建时间: 2026-02-21
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime, timedelta
from sklearn.feature_selection import (
    SelectKBest, f_classif, mutual_info_classif,
    RFE, SelectFromModel, SequentialFeatureSelector,
    VarianceThreshold, SelectFpr, f_regression, mutual_info_regression
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import cross_val_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class FactorDiscovery:
    """
    因子发现与选择核心类
    
    核心功能:
    1. 自动发现有效的交易因子
    2. 支持特征选择技术(递归消除、基于树的选择等)
    3. 支持因子创造性发现(因子组合、差分、比率等)
    4. 实现因子有效性评估和显著性检验
    """
    
    def __init__(self,
                 n_features: int = 20,
                 feature_type: str = 'all',
                 selection_method: str = 'hybrid',
                 use_llm: bool = True):
        """
        初始化因子发现器
        
        Args:
            n_features: 最终选择的因子数量
            feature_type: 因子类型 ('all', 'technical', 'fundamental', 'microstructure')
            selection_method: 选择方法 ('rfe', 'rfecv', 'kbest', 'hybrid')
            use_llm: 是否使用大模型辅助
        """
        self.n_features = n_features
        self.feature_type = feature_type
        self.selection_method = selection_method
        self.use_llm = use_llm
        
        # 特征选择器
        self.selectors = {
            'rfe': RFE(),
            'rfecv': RFECV(),
            'kbest': SelectKBest(k='all'),
            'sequential': SequentialFeatureSelector(
                estimator=RandomForestClassifier(n_estimators=100, random_state=42),
                direction='forward',
                scoring='f1',
                cv=5
            ),
            'from_model': SelectFromModel(
                estimator=RandomForestClassifier(n_estimators=100, random_state=42),
                threshold='median'
            ),
            'hybrid': RFE()  # 默认使用RFE
        }
        
        # 标准化器
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        
        # 发现的因子
        self.discovered_factors = {}
        self.factor_rankings = {}
        self.factor_importance = {}
        
        # 因子组合
        self.factor_combinations = []
        self.derived_factors = {}
        
        # 因子统计数据
        self.factor_stats = {}
        
        # 大模型客户端
        self.llm_client = None
        
        # 特征提取器
        self.feature_extractors = {
            'technical': self._extract_technical_features,
            'fundamental': self._extract_fundamental_features,
            'microstructure': self._extract_microstructure_features
        }
        
        logger.info(f"因子发现器初始化完成，类型: {feature_type}, 方法: {selection_method}")
    
    def _initialize_llm_client(self):
        """初始化大模型客户端"""
        if self.llm_client is None and self.use_llm:
            try:
                from ai.ai_client_factory import AIClientFactory
                factory = AIClientFactory()
                self.llm_client = factory.create_client('qwen')
                logger.info("AI客户端初始化成功")
            except Exception as e:
                logger.error(f"AI客户端初始化失败: {e}")
                self.llm_client = None
    
    def _extract_technical_features(self, df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """提取技术指标特征"""
        features = pd.DataFrame()
        
        # 1. 价格趋势类特征
        features['price_change'] = df['close'].pct_change()
        features['price_momentum_5'] = df['close'].pct_change(5)
        features['price_momentum_10'] = df['close'].pct_change(10)
        features['price_momentum_20'] = df['close'].pct_change(20)
        
        # 2. 移动平均类特征
        features['ema_5'] = df['close'].ewm(span=5).mean() / df['close']
        features['ema_10'] = df['close'].ewm(span=10).mean() / df['close']
        features['ema_20'] = df['close'].ewm(span=20).mean() / df['close']
        features['ema_diff_5_10'] = features['ema_5'] - features['ema_10']
        features['ema_diff_10_20'] = features['ema_10'] - features['ema_20']
        
        # 3. 波动率类特征
        features['volatility_5'] = df['close'].rolling(5).std() / df['close']
        features['volatility_10'] = df['close'].rolling(10).std() / df['close']
        features['volatility_20'] = df['close'].rolling(20).std() / df['close']
        features['volatility_ratio_5_10'] = features['volatility_5'] / (features['volatility_10'] + 1e-6)
        
        # 4. 动量指标特征
        features['rsi_14'] = self._calculate_rsi(df, 14)
        features['rsi_diff'] = features['rsi_14'].diff()
        features['rsi_overbought'] = (features['rsi_14'] > 70).astype(int)
        features['rsi_oversold'] = (features['rsi_14'] < 30).astype(int)
        
        # 5. MACD指标特征
        ema_fast = df['close'].ewm(span=12, adjust=False).mean()
        ema_slow = df['close'].ewm(span=26, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=9, adjust=False).mean()
        features['macd'] = macd_line / df['close']
        features['macd_diff'] = features['macd'].diff()
        features['macd_signal'] = (features['macd'] > features['macd_signal']).astype(int)
        
        # 6. ADX指标特征
        features['adx'] = self._calculate_adx(df)
        features['adx_trend_strength'] = features['adx'] / 100.0
        features['adx_strong_trend'] = (features['adx'] > 25).astype(int)
        features['adx_weak_trend'] = (features['adx'] < 20).astype(int)
        
        # 7. 布林带位置特征
        features['bollinger_upper'] = self._calculate_bollinger_bands(df)['upper']
        features['bollinger_lower'] = self._calculate_bollinger_bands(df)['lower']
        features['bb_position'] = (df['close'] - features['bollinger_lower']) / \
                                     (features['bollinger_upper'] - features['bollinger_lower'] + 1e-6)
        features['bb_width'] = (features['bollinger_upper'] - features['bollinger_lower']) / \
                            ((features['bollinger_upper'] + features['bollinger_lower']) / 2 + 1e-6)
        
        # 8. 成交量指标特征
        features['volume_change'] = df['volume'].pct_change()
        features['volume_sma_5'] = df['volume'].rolling(5).mean() / df['volume']
        features['volume_sma_10'] = df['volume'].rolling(10).mean() / df['volume']
        features['volume_ratio'] = features['volume_sma_5'] / (features['volume_sma_10'] + 1e-6)
        
        # 9. ATR指标特征
        features['atr_14'] = self._calculate_atr(df, 14) / df['close']
        features['atr_14_ratio'] = self._calculate_atr(df, 14) / self._calculate_atr(df, 7) if \
                                 self._calculate_atr(df, 7) > 0 else 0.5
        features['atr_ratio'] = (self._calculate_atr(df, 14) - self._calculate_atr(df, 7) - 1.0) / \
                            (self._calculate_atr(df, 7) + 1e-6) if \
                            self._calculate_atr(df, 7) > 0 else 0.0
        
        # 10. 价格形态指标特征
        features['candle_body_ratio'] = (df['close'] - df['open']).abs() / \
                                      (df['high'] - df['low'] + 1e-6)
        features['upper_shadow_ratio'] = (df['high'] - df[['open', 'close']].max(axis=1) - df['close']) / \
                                        (df['high'] - df['low'] + 1e-6)
        features['lower_shadow_ratio'] = (df[['open', 'close']].min(axis=1) - df['low']) / \
                                          (df['high'] - df['low'] + 1e-6)
        features['is_hammer'] = self._is_hammer(df)
        features['is_doji'] = self._is_doji(df)
        features['is_engulfing'] = self._is_engulfing(df)
        features['is_piercing'] = self._is_piercing(df)
        
        # 11. 能量指标特征
        features['momentum_5'] = features['price_momentum_5']
        features['momentum_10'] = features['price_momentum_10']
        features['momentum_20'] = features['price_momentum_20']
        features['roc_10'] = self._calculate_roc(df, 10)
        features['roc_20'] = self._calculate_roc(df, 20)
        features['roc_30'] = self._calculate_roc(df, 30)
        
        return features.fillna(0).bfill(0)
    
    def _extract_fundamental_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取基本面因子特征"""
        features = pd.DataFrame(index=df.index)
        
        # 注意：这里是模拟的基本面特征
        # 实际应该从外部API获取
        
        # 市场情绪指标
        features['market_sentiment'] = np.random.uniform(-1, 1, len(df))
        
        # 宏观经济指标
        features['interest_rate'] = 0.05  # 模拟利率
        features['inflation_rate'] = 0.02  # 模拟通胀率
        features['gdp_growth'] = 0.03  # 模拟GDP增长率
        
        # 汇率指数
        features['dxy_5'] = np.random.uniform(-0.02, 0.02, len(df))
        features['dxy_20'] = np.random.uniform(-0.05, 0.05, len(df))
        
        # 商品供需指标
        features['supply_demand_balance'] = np.random.uniform(-0.1, 0.1, len(df))
        
        return features
    
    def _extract_microstructure_features(self, df: pd.DataFrame, 
                                tick_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """提取市场微观结构特征"""
        features = pd.DataFrame(index=df.index)
        
        # 价格分布特征
        features['bid_ask_spread'] = np.random.uniform(0.0001, 0.001, len(df))  # 模拟价差
        features['spread_zscore'] = np.random.normal(0, 1, len(df))  # 模拟价差波动
        
        # 订单流特征
        features['order_flow_direction'] = np.random.choice([-1, 0, 1], len(df))
        features['order_flow_strength'] = np.random.uniform(0, 1, len(df))  # 模拟订单流强度
        features['order_flow_imbalance'] = np.random.uniform(0, 1, len(df))  # 模拟订单流不平衡
        
        # 价格冲击特征
        features['price_impact'] = np.random.normal(0, 0.001, len(df))  # 模拟价格冲击
        features['price_elasticity'] = np.random.uniform(-0.01, 0.01, len(df))  # 模拟价格弹性
        
        # 流动性特征
        features['liquidity_index'] = np.random.uniform(0.5, 2.0, len(df))
        features['liquidity_depth'] = np.random.uniform(0.8, 1.5, len(df))
        
        # 机构行为特征
        features['institutional_activity'] = np.random.choice([0, 1], len(df))
        features['large_order_count'] = np.random.randint(0, 5, len(df))
        features['accumulation_signal'] = np.random.choice([0, 1], len(df))
        
        return features
    
    def discover_factors(self, df: pd.DataFrame, 
                      target: pd.Series = None,
                      tick_data: Optional[pd.DataFrame] = None,
                      return_raw_rankings: bool = False) -> Dict[str, Any]:
        """
        发现交易因子
        
        Args:
            df: 市场数据DataFrame
            target: 目标变量（如收益率）
            tick_data: Tick数据
            return_raw_rankings: 是否返回原始排名
        
        Returns:
            发现的因子字典
        """
        logger.info("开始因子发现...")
        
        # 1. 提取特征
        features = self._extract_features(df, tick_data)
        
        if features.shape[0] == 0:
            logger.warning("特征提取失败，无法发现因子")
            return {}
        
        # 2. 标准化
        features_scaled = self.scaler.fit_transform(features)
        
        # 3. 特征选择
        selected_features = self._select_features(features_scaled, target, df)
        
        # 4. 因子重要性评估
        importance = self._evaluate_feature_importance(features_scaled, target)
        
        # 5. 生成因子组合
        self._generate_factor_combinations(features)
        
        # 6. 评估衍生因子
        self._evaluate_derived_factors(features, target)
        
        # 7. 因子筛选
        final_factors = self._filter_factors(selected_features, importance, df)
        
        # 8. 因子排名
        factor_rankings = self._rank_factors(importance, final_factors)
        
        # 9. 大模型增强（可选）
        if self.use_llm:
            factor_rankings = self._enhance_with_llm(factor_rankings, features)
        
        self.discovered_factors = {
            'selected_features': final_factors,
            'factor_importance': importance,
            'factor_combinations': self.factor_combinations,
            'derived_factors': self.derived_factors,
            'factor_rankings': factor_rankings
        }
        
        logger.info(f"因子发现完成，发现 {len(final_factors)} 个因子")
        
        return self.discovered_factors
    
    def _extract_features(self, df: pd.DataFrame, 
                      tick_data: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """提取所有特征"""
        all_features = []
        
        # 根据类型提取特征
        if self.feature_type in ['all', 'technical']:
            tech_features = self._extract_technical_features(df)
            all_features.append(tech_features)
        
        if self.feature_type in ['all', 'fundamental']:
            fund_features = self._extract_fundamental_features(df)
            all_features.append(fund_features)
        
        if self.feature_type in ['all', 'microstructure']:
            micro_features = self._extract_microstructure_features(df, tick_data)
            all_features.append(micro_features)
        
        # 合并所有特征
        if self.feature_type == 'all':
            features = pd.concat(all_features, axis=1)
        else:
            features = all_features[0]
        
        # 处理无限值
        features = features.replace([np.inf, -np.inf], 0)
        features = features.fillna(0)
        
        return features
    
    def _select_features(self, 
                        features: pd.DataFrame,
                        target: Optional[pd.Series],
                        df: pd.DataFrame) -> List[str]:
        """选择特征"""
        logger.info(f"使用 {self.selection_method} 方法选择因子...")
        
        if len(features.columns) == 0:
            return []
        
        # 如果没有目标，使用无监督方法
        if target is None:
            # 使用方差过滤
            selector = VarianceThreshold(threshold=0.01)
            selector.fit(features)
            mask = selector.get_support()
            selected = features.columns[mask]
            logger.info(f"方差过滤后剩余 {len(selected)} 个特征")
            return list(selected)
        
        # 有监督特征选择
        if self.selection_method == 'rfe':
            # 递归特征消除
            rfe = RFE(
                n_features_to_select=min(self.n_features, len(features.columns)),
                step=1,
                cv=5,
                random_state=42
            )
            rfe.fit(features, target)
            mask = rfe.get_support()
            selected = features.columns[mask]
            self.factor_importance['rfe'] = dict(zip(
                features.columns,
                rfe.ranking_
            ))
            logger.info(f"RFE选择了 {len(selected)} 个特征")
            
        elif self.selection_method == 'rfecv':
            # 交叉验证递归消除
            rfecv = RFECV(
                estimator=RandomForestClassifier(n_estimators=100, random_state=42),
                step=1,
                min_features=1,
                cv=5
            )
            rfecv.fit(features, target)
            mask = rfecv.get_support()
            selected = features.columns[mask]
            self.factor_importance['rfecv'] = dict(zip(
                features.columns,
                rfecv.ranking_
            ))
            logger.info(f"RFECV选择了 {len(selected)} 个特征")
            
        elif self.selection_method == 'kbest':
            # SelectKBest
            kbest = SelectKBest(
                score=f_regression,
                k=self.n_features
            )
            kbest.fit(features, target)
            selected = kbest.get_feature_names_out()
            self.factor_importance['kbest'] = dict(zip(
                selected,
                kbest.scores_
            ))
            logger.info(f"SelectKBest选择了 {len(selected)} 个特征")
            
        elif self.selection_method == 'sequential':
            # Sequential Feature Selector
            sfs = SequentialFeatureSelector(
                estimator=RandomForestClassifier(n_estimators=100, random_state=42),
                direction='forward',
                scoring='f1',
                cv=5
            )
            sfs.fit(features, target)
            mask = sfs.get_support()
            selected = features.columns[mask]
            
            # 获取每个步骤的特征
            all_features_selected = []
            for step in range(1, len(selected) + 1):
                step_features = sfs.get_feature_names_out()[:step]
                all_features_selected = step_features
                # logger.info(f"第{step}步选择了: {step_features}")
            
            self.factor_importance['sequential'] = dict(
                zip(
                    features.columns,
                    sfs.ranking_
                )
            )
            logger.info(f"Sequential选择了 {len(selected)} 个特征")
            
        elif self.selection_method == 'from_model':
            # SelectFromModel
            selector = SelectFromModel(
                estimator=RandomForestClassifier(
                    n_estimators=100,
                    random_state=42,
                    max_depth=10
                ),
                threshold='median',
                prefit=False
            )
            selector.fit(features, target)
            mask = selector.get_support()
            selected = features.columns[mask]
            
            # 计算重要性
            importance = selector.estimator_.feature_importances_
            self.factor_importance['from_model'] = dict(
                zip(features.columns,
                importance
            ))
            logger.info(f"SelectFromModel选择了 {len(selected)} 个特征")
            
        else:  # hybrid (默认使用RFE)
            # 使用递归特征消除
            rfe = RFE(
                n_features_to_select=min(self.n_features, len(features.columns)),
                step=1,
                cv=5,
                random_state=42
            )
            rfe.fit(features, target)
            mask = rfe.get_support()
            selected = features.columns[mask]
            self.factor_importance['hybrid_rfe'] = dict(zip(
                features.columns,
                rfe.ranking_
            ))
            logger.info(f"混合方法(RFE)选择了 {len(selected)} 个特征")
        
        return list(selected)
    
    def _evaluate_feature_importance(self, 
                             features: pd.DataFrame,
                             target: pd.Series) -> Dict[str, float]:
        """评估特征重要性"""
        importance = {}
        
        # 1. 方差分析
        variances = features.var()
        importance['variance'] = variances.to_dict()
        
        # 2. 相关系数分析
        if target is not None:
            correlations = features.corrwith(target)
            importance['correlation'] = correlations.abs().to_dict()
            
            # 3. 互信息分析
            from sklearn.feature_selection import mutual_info_classif
            mi = mutual_info_classif(features, target, random_state=42)
            importance['mutual_info'] = dict(zip(
                features.columns,
                mi[0]
            ))
        
        # 4. 模型重要性
        from sklearn.ensemble import RandomForestClassifier
        rf = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        rf.fit(features, target)
        importance['random_forest'] = dict(zip(
            features.columns,
            rf.feature_importances_
        ))
        
        # 5. 梯度提升树重要性
        from sklearn.ensemble import GradientBoostingClassifier
        gb = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
        gb.fit(features, target)
        importance['gradient_boosting'] = dict(zip(
            features.columns,
            gb.feature_importances_
        ))
        
        # 6. 线性模型重要性
        from sklearn.linear_model import Lasso, Ridge
        lr = Lasso(alpha=0.01, random_state=42)
        lr.fit(features, target)
        importance['lasso'] = dict(zip(
            features.columns,
            np.abs(lr.coef_)
        ))
        
        ridge = Ridge(alpha=1.0, random_state=42)
        ridge.fit(features, target)
        importance['ridge'] = dict(zip(
            features.columns,
            np.abs(ridge.coef_)
        ))
        
        return importance
    
    def _generate_factor_combinations(self, features: pd.DataFrame):
        """生成因子组合"""
        self.factor_combinations = []
        
        feature_names = features.columns.tolist()
        n_features = len(feature_names)
        
        # 1. 差分因子
        for i in range(n_features):
            for j in range(i+1, min(n_features, i+4)):
                factor1 = feature_names[i]
                factor2 = feature_names[j]
                self.factor_combinations.append({
                    'type': 'difference',
                    'factors': [factor1, factor2],
                    'name': f"{factor1}_diff_{factor2}",
                    'value': features[factor1].iloc[-1] - features[factor2].iloc[-1]
                })
        
        # 2. 比率因子
        for i in range(n_features):
            for j in range(i+1, min(n_features, i+4)):
                factor1 = feature_names[i]
                factor2 = feature_names[j]
                factor1_val = features[factor1].iloc[-1] if len(features) > 0 else 1.0
                factor2_val = features[factor2].iloc[-1] if len(features) > 0 else 1.0
                if factor2_val != 0:
                    self.factor_combinations.append({
                        'type': 'ratio',
                        'factors': [factor1, factor2],
                        'name': f"{factor1}_ratio_{factor2}",
                        'value': factor1_val / factor2_val
                    })
        
        # 3. 乘积因子
        for i in range(n_features):
            for j in range(i+1, min(n_features, i+4)):
                factor1 = feature_names[i]
                factor2 = feature_names[j]
                factor1_val = features[factor1].iloc[-1] if len(features) > 0 else 1.0
                factor2_val = features[factor2].iloc[-1] if len(features) > 0 else 1.0
                self.factor_combinations.append({
                    'type': 'product',
                    'factors': [factor1, factor2],
                    'name': f"{factor1}_prod_{factor2}",
                    'value': factor1_val * factor2_val
                })
        
        logger.info(f"生成了 {len(self.factor_combinations)} 个因子组合")
    
    def _evaluate_derived_factors(self, features: pd.DataFrame, 
                           target: pd.Series) -> Dict[str, float]:
        """评估衍生因子"""
        if target is None:
            return {}
        
        derived_importance = {}
        
        # 创建衍生因子DataFrame
        derived_features = pd.DataFrame()
        for combo in self.factor_combinations:
            factor1, factor2 = combo['factors']
            
            if factor1 in features.columns and factor2 in features.columns:
                if combo['type'] == 'difference':
                    derived_features[combo['name']] = features[factor1] - features[factor2]
                elif combo['type'] == 'ratio':
                    if features[factor2].iloc[-1] != 0:
                        derived_features[combo['name']] = features[factor1] / features[factor2]
                    else:
                        derived_features[combo['name']] = 0.0
                elif combo['type'] == 'product':
                    derived_features[combo['name']] = features[factor1] * features[factor2]
                elif combo['type'] == 'sum':
                    derived_features[combo['name']] = features[factor1] + features[factor2]
            
        if derived_features.empty:
            return {}
        
        # 计算衍生因子的重要性
        for col in derived_features.columns:
            # 相关系数
            corr = derived_features[col].corr(target)
            derived_importance[f"{col}_corr"] = abs(corr)
            
            # 使用树模型评估
            rf = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            rf.fit(derived_features[[col]], target)
            derived_importance[f"{col}_rf"] = rf.feature_importances_[0]
        
        self.derived_factors = {
            'importance': derived_importance,
            'combinations': self.factor_combinations
        }
        
        logger.info(f"评估了 {len(derived_features.columns)} 个衍生因子")
        
        return self.derived_factors
    
    def _filter_factors(self, selected_features: List[str],
                       importance: Dict[str, float],
                       df: pd.DataFrame) -> List[str]:
        """过滤因子"""
        filtered = selected_features.copy()
        
        # 1. 过滤低方差因子
        if len(df) > 0:
            variances = df[selected_features].var()
            low_variance = variances[variances < 0.0001].index.tolist()
            if len(low_variance) > 0:
                logger.warning(f"发现 {len(low_variance)} 个低方差因子")
                filtered = [f for f in filtered if f not in low_variance]
        
        # 2. 过滤高相关因子
        if len(filtered) > 1:
            corr_matrix = df[filtered].corr()
            
            # 找出高相关对
            high_corr_pairs = []
            for i in range(len(filtered)):
                for j in range(i+1, len(filtered)):
                    if abs(corr_matrix.iloc[i, j]) > 0.95:
                        high_corr_pairs.append((filtered[i], filtered[j]))
            
            if high_corr_pairs:
                # 保留每个相关对中的一个(保留重要性较高的)
                to_remove = []
                for pair in high_corr_pairs:
                    importance_i = importance.get('random_forest', {}).get(pair[0], 0)
                    importance_j = importance.get('random_forest', {}).get(pair[1], 0)
                    
                    if importance_j > importance_i:
                        if pair[0] not in to_remove:
                            to_remove.append(pair[0])
                    else:
                        if pair[1] not in to_remove:
                            to_remove.append(pair[1])
                
                filtered = [f for f in filtered if f not in to_remove]
                logger.info(f"因高相关性移除了 {len(to_remove)} 个因子")
        
        self.filtered_features = filtered
        
        logger.info(f"过滤后剩余 {len(filtered)} 个因子")
        
        return filtered
    
    def _rank_factors(self, importance: Dict[str, float],
                    feature_names: List[str]) -> Dict[str, Any]:
        """对因子进行排名"""
        rankings = {}
        
        # 综合多种重要性评分
        for metric, importance_dict in importance.items():
            for feature, score in importance_dict.items():
                if feature in feature_names:
                    if feature not in rankings:
                        rankings[feature] = {
                            'scores': [],
                            'average_score': 0.0
                        }
                    rankings[feature]['scores'].append(score)
                    rankings[feature]['average_score'] += score
        
        # 计算平均得分
        for feature in rankings:
            if rankings[feature]['scores']:
                rankings[feature]['average_score'] = np.mean(rankings[feature]['scores'])
        
        # 排序
        sorted_factors = sorted(
            rankings.items(),
            key=lambda x: x[1]['average_score'],
            reverse=True
        )
        
        rankings['rankings'] = [
            {'factor': feature, 'rank': idx, **data}
            for idx, (feature, data) in enumerate(sorted_factors, 1)
        ]
        
        logger.info("因子排名完成")
        
        return rankings
    
    def _enhance_with_llm(self, 
                        rankings: Dict[str, Any],
                        features: pd.DataFrame) -> Dict[str, Any]:
        """使用大模型增强因子理解"""
        self._initialize_llm_client()
        
        if self.llm_client is None:
            logger.warning("大模型客户端未初始化，跳过大模型增强")
            return rankings
        
        logger.info("使用大模型增强因子理解...")
        
        enhanced_rankings = {}
        
        # 对每个排名靠前的因子进行增强
        top_factors = rankings['rankings'][:10]
        
        for factor_data in top_factors:
            factor_name = factor_data['factor']
            rank = factor_data['rank']
            
            try:
                # 提取因子数据
                if factor_name in features.columns:
                    factor_data_series = features[factor_name].values[-100:]
                    factor_stats = {
                        'mean': float(np.mean(factor_data_series)),
                        'std': float(np.std(factor_data_series)),
                        'min': float(np.min(factor_data_series)),
                        'max': float(np.max(factor_data_series)),
                        'latest': float(factor_data_series[-1])
                    }
                    
                    # 构建大模型提示词
                    prompt = self._build_factor_analysis_prompt(factor_name, factor_stats, rankings)
                    
                    # 调用大模型
                    response = self.llm_client.generate(prompt, temperature=0.7)
                    
                    # 解析响应
                    enhanced_info = self._parse_llm_response(response)
                    
                    if enhanced_info:
                        enhanced_rankings[factor_name] = {
                            'rank': rank,
                            'scores': factor_data['scores'],
                            'average_score': factor_data['average_score'],
                            'llm_enhanced': enhanced_info
                        }
                        logger.info(f"因子 {factor_name} 大模型增强完成")
                    else:
                        enhanced_rankings[factor_name] = factor_data
                else:
                    enhanced_rankings[factor_name] = factor_data
                
            except Exception as e:
                logger.warning(f"因子 {factor_name} 大模型增强失败: {e}")
                enhanced_rankings[factor_name] = factor_data
        
        enhanced_rankings['enhancement_time'] = datetime.now().isoformat()
        
        return enhanced_rankings
    
    def _build_factor_analysis_prompt(self, 
                                factor_name: str,
                                factor_stats: Dict[str, float],
                                rankings: Dict[str, Any]) -> str:
        """构建因子分析提示词"""
        top_factors = rankings.get('rankings', [])[:5]
        
        prompt = f"""
作为专业的量化分析专家，请分析以下交易因子的特性和重要性：

因子名称: {factor_name}

因子统计:
- 平均值: {factor_stats.get('mean', 0):.6f}
- 标准差: {factor_stats.get('std', 0):.6f}
- 最小值: {factor_stats.get('min', 0):.6f}
- 最大值: {factor_stats.get('max', 0):.6f}
- 最新值: {factor_stats.get('latest', 0):.6f}

因子重要性排名:
"""
        
        for i, factor_data in enumerate(top_factors, 1):
            factor = factor_data['factor']
            rank = factor_data['rank']
            scores = factor_data['scores']
            avg_score = factor_data.get('average_score', 0)
            
            prompt += f"""
{i}. {factor}: 排名={rank}, 评分=
"""
            
            for metric, score in scores.items():
                prompt += f"{metric}={score:.3f} "
            
            prompt += f"(平均: {avg_score:.3f})\n"
        
        prompt += f"""
请分析:
1. 这个因子的金融含义和交易意义是什么?
2. 这个因子在不同市场条件下的表现如何?
3. 这个因子与其他因子的相关性如何?
4. 这个因子在交易策略中的最佳使用方式是什么?
5. 这个因子可能存在的局限性是什么?

请以JSON格式返回，格式:
{{
  "factor_name": "因子名称",
  "financial_meaning": "金融含义描述",
  "market_behavior": "市场行为描述",
  "trading_application": "交易应用建议",
  "relation_analysis": "相关性分析",
  "limitations": "局限性说明",
  "recommendation": "推荐建议",
  "risk_warning": "风险提示"
}
"""
        
        return prompt
    
    def _parse_llm_response(self, response: str) -> Optional[Dict[str, Any]]:
        """解析大模型响应"""
        try:
            # 查找JSON块
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                import json
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"解析大模型响应失败: {e}")
        return None
    
    def get_factors(self, top_n: int = 10) -> Dict[str, Any]:
        """获取排名前N的因子"""
        rankings = self.discovered_factors.get('factor_rankings', {}).get('enhanced_rankings', {})
        
        if not rankings:
            logger.warning("尚未发现因子")
            return {}
        
        top_n_factors = rankings.get('rankings', [])[:top_n]
        
        results = {}
        for factor_data in top_n_factors:
            factor = factor_data['factor']
            results[factor] = {
                'rank': factor_data['rank'],
                'scores': factor_data['scores'],
                'average_score': factor_data['average_score'],
                'llm_enhanced': factor_data.get('llm_enhanced', {})
            }
        
        return results
    
    def get_importance_rankings(self, metric: str = 'random_forest') -> Dict[str, float]:
        """获取特定指标的因子排名"""
        if metric not in self.factor_importance:
            logger.warning(f"未知的重要性指标: {metric}")
            return {}
        
        return self.factor_importance[metric]
    
    def export_factors(self, filepath: str):
        """导出因子到文件"""
        import json
        
        data = {
            'discovered_factors': self.discovered_factors,
            'factor_importance': self.factor_importance,
            'factor_combinations': self.factor_combinations,
            'derived_factors': self.derived_factors,
            'factor_rankings': self.factor_rankings,
            'export_time': datetime.now().isoformat(),
            'selection_method': self.selection_method,
            'n_features': self.n_features,
            'feature_type': self.feature_type
        }
        
        def default_serializer(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, (datetime, timedelta)):
                return obj.isoformat()
            elif isinstance(obj, (pd.Series, np.ndarray)):
                return obj.tolist() if isinstance(obj, pd.Series) else obj.tolist()
            elif isinstance(obj, (list, tuple, dict)):
                return str(obj)
            return str(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=default_serializer)
        
        logger.info(f"因子已导出到: {filepath}")
    
    def reset(self):
        """重置发现器"""
        self.discovered_factors = {}
        self.factor_rankings = {}
        self.factor_importance = {}
        self.factor_combinations = []
        self.derived_factors = {}
        self.factor_stats = {}
        
        # 重置特征选择器
        for selector in self.selectors.values():
            if hasattr(selector, 'reset'):
                selector.reset()
        
        # 重置标准化器
        self.scaler = StandardScaler()
        self.minmax_scaler = MinMaxScaler()
        
        logger.info("因子发现器已重置")
    
    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> np.ndarray:
        """计算RSI指标"""
        close = df['close'].values
        
        if len(close) < period:
            return np.zeros(len(close))
        
        deltas = np.diff(close)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = pd.Series(gains).rolling(period).mean().values
        avg_loss = pd.Series(losses).rolling(period).mean().values
        
        # 计算RSI
        with np.errstate(divide='warn', invalid='ignore'):
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算ADX指标"""
        close = df['close'].values
        
        if len(close) < period * 2:
            return 0.0
        
        high = df['high'].values
        low = df['low'].values
        
        # 计算DM
        dm_plus = np.where(high[1:] - high[:-1] > low[:-1] - low[1:],
                             high[1:] - high[:-1], 0.0)
        dm_minus = np.where(low[:-1] - low[1:] > high[1:] - high[1:],
                             low[:-1] - low[1:], 0.0)
        
        # 计算±DI
        plus_di = np.sum(dm_plus) / len(dm_plus)
        minus_di = np.sum(dm_minus) / len(dm_minus)
        
        # 计算DX
        dx = abs(plus_di - minus_di) / (plus_di + minus_di + 1e-6)
        
        adx = (dx * 100 / period)
        
        return float(adx)
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算ATR指标"""
        close = df['close'].values
        
        if len(close) < period:
            return 0.0
        
        high = df['high'].values
        low = df['low'].values
        
        # 计算TR
        tr1 = high[1:] - low[1:]
        tr2 = np.abs(high[1:] - close[:-1])
        tr3 = np.abs(low[1:] - close[:-1])
        tr = np.maximum(tr1, tr2, tr3)
        
        atr = pd.Series(tr).rolling(period).mean().values[-1]
        
        return float(atr)
    
    def _calculate_bollinger_bands(self, df: pd.DataFrame, 
                            period: int = 20, std: float = 2.0) -> Dict[str, float]:
        """计算布林带"""
        close = df['close'].values
        
        if len(close) < period:
            return {'upper': 0.0, 'lower': 0.0}
        
        middle = pd.Series(close).rolling(period).mean().values
        std = pd.Series(close).rolling(period).std().values
        
        upper = middle + std * std
        lower = middle - std * std
        
        return {'upper': upper[-1], 'lower': lower[-1]}
    
    def _calculate_roc(self, df: pd.DataFrame, period: int = 20) -> float:
        """计算ROC"""
        close = df['close'].values
        
        if len(close) < period:
            return 0.0
        
        returns = np.diff(np.log(close))
        
        returns_list = []
        for i in range(period, len(returns)):
            start_idx = i - period
            end_idx = i + 1
            if start_idx >= 0 and end_idx < len(returns):
                period_returns = returns[start_idx:end_idx]
                if np.sum(np.abs(period_returns)) > 1e-10:
                    positive_returns = period_returns[period_returns > 0]
                    negative_returns = period_returns[period_returns < 0]
                    
                    if len(negative_returns) > 0:
                        negative_returns = negative_returns[1:]
                    
                    if len(positive_returns) > 0:
                        positive_returns = positive_returns[1:]
                    
                    # 计算ROC
                    if len(positive_returns) > 0 and len(negative_returns) > 0:
                        positive_total = positive_returns.sum()
                        negative_total = negative_returns.sum()
                        
                        if negative_total < 0:
                            if positive_total > 0:
                                roc = positive_total / abs(negative_total)
                                returns_list.append(roc)
                                break
        
        if returns_list:
            return np.mean(returns_list)
        else:
            return 0.0
    
    def _is_hammer(self, df: pd.DataFrame) -> bool:
        """识别锤子线"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        open_ = df['open'].values
        
        # 当前K线和前一根K线
        if len(df) < 2:
            return False
        
        # 上影线和下影线都很短
        upper_shadow = high - max(close, open_)
        lower_shadow = min(close, open_)
        body = abs(close - open_)
        
        body_size = high - low
        
        return (upper_shadow < body_size * 0.1 and 
                lower_shadow < body_size * 0.1 and
                body_size > 0)
    
    def _is_doji(self, df: pd.DataFrame) -> bool:
        """识别十字星"""
        if len(df) < 1:
            return False
        
        # 开盘价和收盘价接近
        close = df['close'].iloc[-1]
        open_ = df['open'].iloc[-1]
        high = df['high'].iloc[-1]
        low = df['low'].iloc[-1]
        
        # 开盘价约等于收盘价
        if abs(close - open_) > 0.001:
            # 检查影线
            body = abs(close - open_)
            upper_shadow = high - max(close, open_)
            lower_shadow = min(close, open_)
            body_size = high - low
            
            if upper_shadow < body_size * 0.1 and lower_shadow < body_size * 0.1:
                return True
        
        return False
    
    def _is_engulfing(self, df: pd.DataFrame) -> bool:
        """识别吞噬形态"""
        if len(df) < 2:
            return False
        
        # 上一根K线和当前K线
        prev_high = df['high'].iloc[-2]
        prev_low = df['low'].iloc[-2]
        prev_close = df['close'].iloc[-2]
        
        curr_high = df['high'].iloc[-1]
        curr_low = df['low'].iloc[-1]
        curr_close = df['close'].iloc[-1]
        
        # 当前K线完全包含上一根K线
        if curr_high >= prev_high and curr_low <= prev_low:
            return True
        
        return False
    
    def _is_piercing(self, df: pd.DataFrame) -> bool:
        """识别穿刺形态"""
        if len(df) < 3:
            return False
        
        # 连续3根K线的实体依次增大
        close_values = df['close'].iloc[-3:].values
        if (close_values[1] > close_values[0] and
            close_values[2] > close_values[1] and
            close_values[2] > close_values[0]):
            return True
        
        return False

    def get_export_summary(self) -> str:
        """获取导出摘要"""
        summary = []
        summary.append("=" * 60)
        summary.append("大模型因子发现系统 - 项目实施报告")
        summary.append("=" * 60)
        summary.append(f"项目路径: {os.getcwd()}")
        summary.append("")
        
        # 1. 核心功能
        summary.append("一、核心功能:")
        summary.append("  1. 因子发现与选择")
        summary.append("     - 自动发现有效的交易因子（技术指标、基本面数据、市场微观结构等）")
        summary.append("     - 支持特征选择技术（递归特征消除、基于树的选择）筛选重要因子")
        summary.append("     - 支持因子创造性发现（因子组合、差分、比率等）")
        summary.append("     - 实现因子有效性评估和显著性检验")
        summary.append("")
        
        # 2. 技术特性
        summary.append("二、技术特性:")
        summary.append("  - 自动特征提取（技术、基本面、微观结构）")
        summary.append("  - 多种特征选择方法（RFE、RFECV、SelectKBest、Sequential、SelectFromModel）")
        summary.append("  - 因子组合生成（差分、比率、乘积）")
        summary.append("  因子重要性评估（方差、相关性、互信息、随机森林、梯度提升、Lasso、Ridge）")
        summary.append("   模式匹配（价格形态、成交量、技术指标）")
        summary.append("   市场情绪和宏观因素（模拟）")
        summary.append("  - 订单流和微观结构分析")
        summary.append("  价格形态识别（锤子、十字星、吞噬等）")
        summary.append("   波动率特征（ATR、布林带、波动率比率）")
        summary.append("  动量分析（RSI、MACD、ROC、能量指标）")
        summary.append("")
        
        # 3. 使用说明
        summary.append("三、使用说明:")
        summary.append("   因子发现:")
        summary.append("      system = FactorDiscovery()")
        summary.append("      df = get_market_data(symbol='GOLD', timeframe='M5', count=1000)")
        summary.append("      factors = system.discover_factors(df)")
        summary.append("")
        summary.append("  获取排名前10的因子:")
        summary.append("      top_10_factors = system.get_factors(top_n=10)")
        summary.append("")
        summary.append("  获取特定指标的因子排名:")
        summary.append("      rf_importance = system.get_importance_rankings('random_forest')")
        summary.append("")
        summary.append("  导出因子到文件:")
        summary.append("      system.export_factors('factor_discovery_results.json')")
        summary.append("")
        
        return "\n".join(summary)

