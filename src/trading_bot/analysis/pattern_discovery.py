import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Optional, Any
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatternDiscovery:
    """
    模式发现核心类
    基于无监督学习技术，实现市场特征的提取、聚类分析与模式发现。
    核心理论依据：通过聚类将相似市场状态分组，发现潜在结构，无需预先定义标签。
    """
    
    def __init__(self, n_clusters: int = 5, clustering_method: str = 'kmeans', 
                 use_pca: bool = True, n_components: int = 10, llm_client: Any = None):
        """
        初始化模式发现器
        
        Args:
            n_clusters: 聚类簇数
            clustering_method: 聚类方法
            use_pca: 是否使用PCA降维
            n_components: PCA降维后的维度
            llm_client: 大模型客户端接口
        """
        self.n_clusters = n_clusters
        self.clustering_method = clustering_method
        self.use_pca = use_pca
        self.n_components = n_components
        self.llm_client = llm_client
        
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components) if use_pca else None
        self.cluster_model = self._init_cluster_model()
        self.anomaly_detector = IsolationForest(contamination=0.05, random_state=42)
        self.pattern_store = {}  # 存储发现的模式中心点
        
        logger.info(f"PatternDiscovery initialized with {clustering_method} method.")

    def _init_cluster_model(self):
        """初始化聚类模型"""
        if self.clustering_method == 'kmeans':
            return KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        elif self.clustering_method == 'dbscan':
            return DBSCAN(eps=0.5, min_samples=5)
        elif self.clustering_method == 'hierarchical':
            return AgglomerativeClustering(n_clusters=self.n_clusters)
        else:
            raise ValueError(f"Unsupported clustering method: {self.clustering_method}")

    def extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        提取30+维市场特征
        包含价格、成交量、波动率、趋势、动量、形态六大类特征
        """
        features = pd.DataFrame(index=df.index)
        
        # 1. 价格特征 (8维)
        price_feats = self._extract_price_features(df)
        features = pd.concat([features, price_feats], axis=1)
        
        # 2. 成交量特征 (4维)
        volume_feats = self._extract_volume_features(df)
        features = pd.concat([features, volume_feats], axis=1)
        
        # 3. 波动率特征 (5维)
        volatility_feats = self._extract_volatility_features(df)
        features = pd.concat([features, volatility_feats], axis=1)
        
        # 4. 趋势特征 (8维)
        trend_feats = self._extract_trend_features(df)
        features = pd.concat([features, trend_feats], axis=1)
        
        # 5. 动量特征 (3维)
        momentum_feats = self._extract_momentum_features(df)
        features = pd.concat([features, momentum_feats], axis=1)
        
        # 6. 形态特征 (5维)
        pattern_feats = self._extract_pattern_features(df)
        features = pd.concat([features, pattern_feats], axis=1)
        
        # 数据清洗
        features = features.replace([np.inf, -np.inf], np.nan).dropna()
        
        return features.values

    def _extract_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取价格相关特征"""
        feats = pd.DataFrame()
        feats['pct_change'] = df['close'].pct_change()
        feats['oc_ratio'] = (df['close'] - df['open']) / df['open'] # 实体相对大小
        feats['hl_ratio'] = (df['high'] - df['low']) / df['low'] # 振幅
        feats['upper_shadow'] = (df['high'] - df[['open', 'close']].max(axis=1)) / (df['high'] - df['low'] + 1e-6)
        feats['lower_shadow'] = (df[['open', 'close']].min(axis=1) - df['low']) / (df['high'] - df['low'] + 1e-6)
        feats['ma5_dist'] = df['close'] / df['close'].rolling(5).mean() - 1
        feats['ma20_dist'] = df['close'] / df['close'].rolling(20).mean() - 1
        feats['price_position'] = (df['close'] - df['low'].rolling(20).min()) / \
                                  (df['high'].rolling(20).max() - df['low'].rolling(20).min() + 1e-6)
        return feats

    def _extract_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取成交量特征"""
        feats = pd.DataFrame()
        feats['vol_change'] = df['volume'].pct_change()
        feats['vol_ma_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        feats['obv_slope'] = self._calculate_slope((df['volume'] * (df['close'].diff().apply(np.sign))).cumsum())
        feats['vol_price_trend'] = df['volume'].rolling(5).corr(df['close'].rolling(5))
        return feats

    def _extract_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取波动率特征"""
        feats = pd.DataFrame()
        feats['atr'] = self._calculate_atr(df)
        feats['atr_ratio'] = feats['atr'] / df['close']
        feats['volatility_20'] = df['close'].pct_change().rolling(20).std()
        feats['parkinson_vol'] = np.sqrt((1 / (4 * 20 * np.log(2))) * 
                                         (np.log(df['high'] / df['low'])**2).rolling(20).sum())
        feats['garman_klass'] = np.sqrt((0.5 * (np.log(df['high']/df['low'])**2).rolling(20).mean()) - 
                                        ((2*np.log(2)-1) * (np.log(df['close']/df['open'])**2).rolling(20).mean()))
        return feats

    def _extract_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取趋势特征"""
        feats = pd.DataFrame()
        # ADX相关计算简化处理
        feats['adx'] = self._calculate_adx(df)
        feats['plus_di'] = self._calculate_di(df, '+')
        feats['minus_di'] = self._calculate_di(df, '-')
        feats['aro_up'] = (df['high'].rolling(14).max() - df['close']) / (df['high'].rolling(14).max() - df['low'].rolling(14).min() + 1e-6)
        feats['aro_down'] = (df['close'] - df['low'].rolling(14).min()) / (df['high'].rolling(14).max() - df['low'].rolling(14).min() + 1e-6)
        feats['trend_strength'] = np.abs(df['close'] - df['close'].shift(10)) / (feats['atr'] * 10 + 1e-6)
        feats['mass_index'] = self._calculate_mass_index(df)
        feats['choppy'] = self._calculate_chop(df)
        return feats

    def _extract_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取动量特征"""
        feats = pd.DataFrame()
        feats['rsi_14'] = self._calculate_rsi(df['close'], 14)
        feats['cci'] = self._calculate_cci(df)
        feats['mfi'] = self._calculate_mfi(df)
        return feats

    def _extract_pattern_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """提取形态特征"""
        feats = pd.DataFrame()
        # 简单的K线形态识别特征
        feats['is_doji'] = (np.abs(df['close'] - df['open']) / (df['high'] - df['low'] + 1e-6) < 0.1).astype(int)
        feats['is_hammer'] = ((df['close'] > df['open']) & 
                              ((df['open'] - df['low']) > 2 * (df['close'] - df['open'])) & 
                              ((df['high'] - df['close']) < (df['close'] - df['open']))).astype(int)
        feats['gap'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
        feats['higher_high'] = (df['high'] > df['high'].shift(1)).rolling(3).sum()
        feats['lower_low'] = (df['low'] < df['low'].shift(1)).rolling(3).sum()
        return feats

    def discover_patterns(self, df: pd.DataFrame) -> Dict:
        """
        发现交易模式的核心流程
        1. 特征提取 -> 2. 标准化 -> 3. 降维 -> 4. 聚类 -> 5. 异常检测 -> 6. LLM增强
        """
        # 1. 特征提取
        raw_features = self.extract_features(df)
        if len(raw_features) < self.n_clusters:
            return {"status": "error", "message": "数据量不足以进行聚类分析"}

        # 2. 标准化
        scaled_features = self.scaler.fit_transform(raw_features)
        
        # 3. 降维
        reduced_features = self.pca.fit_transform(scaled_features) if self.use_pca else scaled_features
        
        # 4. 聚类分析
        labels = self._cluster_features(reduced_features)
        
        # 5. 异常检测
        anomaly_labels = self._detect_anomalies(scaled_features)
        
        # 6. 模式分析与存储
        pattern_info = self._analyze_patterns(df, labels, reduced_features)
        
        # 7. LLM增强解释 (如果提供了客户端)
        if self.llm_client:
            pattern_info = self._enhance_with_llm(pattern_info, df)
            
        return {
            "labels": labels,
            "anomaly_labels": anomaly_labels,
            "pattern_details": pattern_info,
            "scores": {
                "silhouette": silhouette_score(reduced_features, labels) if len(set(labels)) > 1 else -1,
                "calinski_harabasz": calinski_harabasz_score(reduced_features, labels) if len(set(labels)) > 1 else 0
            }
        }

    def _cluster_features(self, features: np.ndarray) -> np.ndarray:
        """执行聚类"""
        return self.cluster_model.fit_predict(features)

    def _detect_anomalies(self, features: np.ndarray) -> np.ndarray:
        """检测异常模式"""
        return self.anomaly_detector.fit_predict(features)

    def _analyze_patterns(self, df: pd.DataFrame, labels: np.ndarray, features: np.ndarray) -> Dict:
        """分析聚类结果，生成模式描述"""
        unique_labels = set(labels)
        pattern_details = {}
        
        # 过滤掉原始数据中因特征计算产生的NaN行索引
        valid_indices = df.index[-len(labels):]
        
        for label in unique_labels:
            if label == -1: continue # 忽略噪声点(DBSCAN)
            
            mask = (labels == label)
            cluster_center = features[mask].mean(axis=0)
            
            # 存储模式中心
            self.pattern_store[label] = {
                "center": cluster_center,
                "count": mask.sum(),
                "avg_return": df.loc[valid_indices[mask], 'close'].pct_change().mean()
            }
            pattern_details[label] = self.pattern_store[label]
            
        return pattern_details

    def _enhance_with_llm(self, pattern_info: Dict, df: pd.DataFrame) -> Dict:
        """使用大模型增强模式理解"""
        prompt = f"""
        基于当前市场数据聚类结果：
        - 发现了{len(pattern_info)}种主要市场状态。
        - 各状态样本分布：{[(k, v['count']) for k, v in pattern_info.items()]}。
        - 各状态平均收益：{[(k, v['avg_return']) for k, v in pattern_info.items()]}。
        
        请分析这些状态可能代表的市场微观结构含义（如吸筹、派发、震荡、趋势启动），
        并给出简短的交易建议。
        """
        # 调用LLM的伪代码
        # response = self.llm_client.generate(prompt)
        # pattern_info['llm_analysis'] = response.text
        pattern_info['llm_analysis'] = "LLM analysis placeholder: Trend detected in Cluster 0."
        return pattern_info

    def classify_pattern(self, new_data: pd.DataFrame) -> Tuple[int, float]:
        """分类新模式，返回簇标签和置信度"""
        new_features = self.extract_features(new_data)
        scaled_new = self.scaler.transform(new_features)
        reduced_new = self.pca.transform(scaled_new) if self.use_pca else scaled_new
        
        # 计算与已有模式中心的相似度
        best_label = -1
        best_sim = -1
        
        for label, data in self.pattern_store.items():
            sim = cosine_similarity([reduced_new[0]], [data['center']])[0][0]
            if sim > best_sim:
                best_sim = sim
                best_label = label
                
        return best_label, best_sim

    # 辅助计算函数
    def _calculate_slope(self, series: pd.Series, window: int = 5) -> pd.Series:
        """计算序列斜率"""
        slopes = series.rolling(window).apply(lambda x: np.polyfit(np.arange(window), x, 1)[0], raw=True)
        return slopes

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """计算ATR"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def _calculate_rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """简化ADX计算"""
        plus_dm = df['high'].diff()
        minus_dm = df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr = self._calculate_atr(df, 1) * 1 # ATR计算需要修正，这里简化
        atr = self._calculate_atr(df, period)
        
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (abs(minus_dm).rolling(period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di + 1e-6)
        return dx.rolling(period).mean()
    
    def _calculate_di(self, df: pd.DataFrame, direction: str) -> pd.Series:
        # 简化处理
        return pd.Series(0, index=df.index)

    def _calculate_cci(self, df: pd.DataFrame, period: int = 20) -> pd.Series:
        TP = (df['high'] + df['low'] + df['close']) / 3
        return (TP - TP.rolling(period).mean()) / (0.015 * TP.rolling(period).std())

    def _calculate_mfi(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        TP = (df['high'] + df['low'] + df['close']) / 3
        MF = TP * df['volume']
        delta = TP.diff()
        positive = MF.where(delta > 0, 0).rolling(period).sum()
        negative = MF.where(delta < 0, 0).rolling(period).sum()
        return 100 - (100 / (1 + positive / (negative + 1e-6)))

    def _calculate_mass_index(self, df: pd.DataFrame) -> pd.Series:
        ratio = df['high'] / df['low']
        return ratio.rolling(9).mean().rolling(25).sum()

    def _calculate_chop(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        atr = self._calculate_atr(df, 1)
        high_max = df['high'].rolling(period).max()
        low_min = df['low'].rolling(period).min()
        return 100 * np.log10(atr.rolling(period).sum() / (high_max - low_min + 1e-6)) / np.log10(period)

    def get_pattern_report(self) -> Dict:
        return self.pattern_store

    def export_patterns(self, filepath: str):
        import joblib
        joblib.dump({
            'scaler': self.scaler,
            'pca': self.pca,
            'model': self.cluster_model,
            'store': self.pattern_store
        }, filepath)

    def load_patterns(self, filepath: str):
        import joblib
        data = joblib.load(filepath)
        self.scaler = data['scaler']
        self.pca = data['pca']
        self.cluster_model = data['model']
        self.pattern_store = data['store']
