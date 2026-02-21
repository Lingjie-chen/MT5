import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiPatternRecognizer:
    """
    多模式识别系统
    整合传统技术分析与机器学习模型，识别9种核心交易模式。
    """
    
    PATTERN_TYPES = [
        'trend_up', 'trend_down', 'range', 
        'breakout_up', 'breakout_down',
        'fake_breakout_up', 'fake_breakout_down',
        'reversal_up', 'reversal_down', 'consolidation'
    ]
    
    def __init__(self, model_type: str = 'ensemble'):
        self.scaler = StandardScaler()
        self.model_type = model_type
        
        # 初始化模型
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.mlp_model = MLPClassifier(hidden_layer_sizes=(50, 25), max_iter=500, random_state=42)
        
        self.pattern_history = []
        self.transition_matrix = np.zeros((len(self.PATTERN_TYPES), len(self.PATTERN_TYPES)))
        
    def extract_pattern_features(self, df: pd.DataFrame) -> np.ndarray:
        """提取25+维模式识别特征"""
        features = pd.DataFrame(index=df.index)
        
        # 调用各特征提取器
        features = pd.concat([
            features,
            self._extract_trend_features(df),
            self._extract_breakout_features(df),
            self._extract_reversal_features(df),
            self._extract_range_features(df),
            self._extract_volume_features(df),
            self._extract_volatility_features(df),
            self._extract_pattern_features(df)
        ], axis=1)
        
        return features.replace([np.inf, -np.inf], np.nan).fillna(0).values

    def _extract_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = pd.DataFrame()
        feats['adx'] = self._calculate_adx(df)
        feats['sar_dist'] = (df['close'] - self._calculate_psar(df)) / df['close']
        feats['ichimoku_signal'] = self._calculate_ichimoku(df)
        feats['ma_cross_5_20'] = (df['close'].rolling(5).mean() > df['close'].rolling(20).mean()).astype(int)
        feats['ma_cross_10_50'] = (df['close'].rolling(10).mean() > df['close'].rolling(50).mean()).astype(int)
        feats['slope_20'] = self._calculate_slope(df['close'], 20)
        feats['slope_50'] = self._calculate_slope(df['close'], 50)
        feats['higher_highs'] = self._count_higher_highs(df)
        return feats

    def _extract_breakout_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = pd.DataFrame()
        window = 20
        feats['price_vs_high'] = df['close'] / df['high'].rolling(window).max() - 1
        feats['price_vs_low'] = df['close'] / df['low'].rolling(window).min() - 1
        feats['range_position'] = (df['close'] - df['low'].rolling(window).min()) / \
                                  (df['high'].rolling(window).max() - df['low'].rolling(window).min() + 1e-6)
        feats['bb_width'] = self._calculate_bb_width(df)
        feats['squeeze'] = feats['bb_width'].rolling(10).min() == feats['bb_width']
        feats['volume_spike'] = df['volume'] > df['volume'].rolling(window).mean() * 2
        feats['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        return feats

    def _extract_reversal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = pd.DataFrame()
        feats['rsi_14'] = self._calculate_rsi(df['close'], 14)
        feats['stoch_k'] = self._calculate_stoch(df)
        feats['cci'] = self._calculate_cci(df)
        feats['divergence'] = self._detect_divergence(df) # 简化
        feats['candle_hammer'] = self._detect_hammer(df)
        feats['candle_shooting'] = self._detect_shooting_star(df)
        return feats

    def _extract_range_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = pd.DataFrame()
        feats['choppy_index'] = self._calculate_chop(df)
        feats['adx_low'] = (self._calculate_adx(df) < 20).astype(int)
        feats['range_pct'] = (df['high'].rolling(20).max() - df['low'].rolling(20).min()) / df['close'].rolling(20).mean()
        return feats

    def _extract_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = pd.DataFrame()
        feats['vol_ma_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        feats['obv_trend'] = self._calculate_slope((df['volume'] * (df['close'].diff().apply(np.sign))).cumsum())
        feats['vpt'] = self._calculate_vpt(df) # 量价趋势
        return feats

    def _extract_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = pd.DataFrame()
        feats['atr'] = self._calculate_atr(df)
        feats['atr_ratio'] = feats['atr'] / df['close']
        feats['hist_vol'] = df['close'].pct_change().rolling(20).std()
        feats['vol_ratio'] = feats['hist_vol'] / feats['hist_vol'].rolling(50).mean()
        return feats
    
    def _extract_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feats = pd.DataFrame()
        feats['doji'] = self._detect_doji(df)
        feats['engulfing'] = self._detect_engulfing(df)
        # ... 其他形态
        return feats

    def recognize_patterns(self, df: pd.DataFrame, use_model: bool = True) -> Dict:
        """主模式识别函数"""
        features = self.extract_pattern_features(df)
        
        # 规则基础识别
        rule_patterns = self._rule_based_recognition(df)
        
        model_patterns = []
        if use_model and hasattr(self.rf_model, 'classes_'):
            # 模型预测
            scaled_feats = self.scaler.transform(features)
            rf_pred = self.rf_model.predict(scaled_feats)
            mlp_pred = self.mlp_model.predict(scaled_feats)
            
            # 投票集成
            final_preds = []
            for r, m in zip(rf_pred, mlp_pred):
                final_preds.append(r if r == m else r) # 简单策略
                
            model_patterns = [self.PATTERN_TYPES[i] for i in final_preds]
        
        # 融合逻辑 (此处简化，优先模型)
        detected_patterns = model_patterns if model_patterns else rule_patterns
        
        # 更新历史和转换矩阵
        if detected_patterns:
            self._update_pattern_history(detected_patterns[-1])
        
        return {
            'current_pattern': detected_patterns[-1] if detected_patterns else None,
            'pattern_sequence': detected_patterns,
            'confidence': self._calculate_pattern_confidence(features[-1], detected_patterns[-1])
        }

    def _rule_based_recognition(self, df: pd.DataFrame) -> List[str]:
        """基于规则的模式识别"""
        patterns = []
        last = df.iloc[-1]
        
        # 趋势判断
        adx = self._calculate_adx(df).iloc[-1]
        slope = self._calculate_slope(df['close']).iloc[-1]
        
        if adx > 25 and slope > 0:
            patterns.append('trend_up')
        elif adx > 25 and slope < 0:
            patterns.append('trend_down')
        elif adx < 20:
            patterns.append('range')
            
        # ... 更多规则
        
        return patterns

    def _calculate_pattern_confidence(self, feature_vec: np.ndarray, pattern: str) -> float:
        """计算模式置信度"""
        # 简化：如果是模型预测，返回概率；如果是规则，返回固定值
        if hasattr(self.rf_model, 'predict_proba'):
            probs = self.rf_model.predict_proba([feature_vec])[0]
            idx = self.PATTERN_TYPES.index(pattern)
            return probs[idx]
        return 0.75

    def train_models(self, X: np.ndarray, y: np.ndarray):
        """训练模型"""
        X_scaled = self.scaler.fit_transform(X)
        self.rf_model.fit(X_scaled, y)
        self.mlp_model.fit(X_scaled, y)
        logger.info("Models trained successfully.")

    def _update_pattern_history(self, current_pattern: str):
        if self.pattern_history:
            last_pattern = self.pattern_history[-1]
            i = self.PATTERN_TYPES.index(last_pattern)
            j = self.PATTERN_TYPES.index(current_pattern)
            self.transition_matrix[i][j] += 1
        self.pattern_history.append(current_pattern)

    def get_pattern_summary(self) -> Dict:
        return {
            'history': self.pattern_history,
            'transition_matrix': self.transition_matrix
        }

    # --- 辅助计算函数 (部分复用PatternDiscovery，实际开发中应提取为公共Utils) ---
    def _calculate_slope(self, series: pd.Series, window: int = 5) -> pd.Series:
        slopes = series.rolling(window).apply(lambda x: np.polyfit(np.arange(window), x, 1)[0], raw=True)
        return slopes

    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        # 完整实现参考PatternDiscovery
        return pd.Series(25, index=df.index) # Placeholder

    def _calculate_psar(self, df: pd.DataFrame) -> pd.Series:
        return df['close'].rolling(5).mean() # Placeholder

    def _calculate_ichimoku(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(0, index=df.index) # Placeholder
    
    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _calculate_stoch(self, df: pd.DataFrame) -> pd.Series:
        low_min = df['low'].rolling(14).min()
        high_max = df['high'].rolling(14).max()
        return 100 * (df['close'] - low_min) / (high_max - low_min + 1e-6)

    def _calculate_bb_width(self, df: pd.DataFrame) -> pd.Series:
        ma = df['close'].rolling(20).mean()
        std = df['close'].rolling(20).std()
        upper = ma + 2 * std
        lower = ma - 2 * std
        return (upper - lower) / ma

    # ... 其他辅助函数省略实现细节 ...
    def _calculate_cci(self, df): return pd.Series(0, index=df.index)
    def _detect_divergence(self, df): return pd.Series(0, index=df.index)
    def _detect_hammer(self, df): return pd.Series(0, index=df.index)
    def _detect_shooting_star(self, df): return pd.Series(0, index=df.index)
    def _calculate_chop(self, df): return pd.Series(0, index=df.index)
    def _calculate_atr(self, df): return pd.Series(0, index=df.index)
    def _calculate_vpt(self, df): return pd.Series(0, index=df.index)
    def _detect_doji(self, df): return pd.Series(0, index=df.index)
    def _detect_engulfing(self, df): return pd.Series(0, index=df.index)
    def _count_higher_highs(self, df): return pd.Series(0, index=df.index)
