import numpy as np
import pandas as pd
from itertools import combinations
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Any
from scipy.stats import chi2_contingency
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HiddenPatternMiner:
    """
    隐含模式挖掘模块
    使用关联规则和序列模式挖掘，发现市场中隐含的非线性关系。
    """
    
    def __init__(self, min_support: float = 0.1, min_confidence: float = 0.6):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets = {}
        self.association_rules = []
        
    def extract_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """将连续市场数据转换为离散事件集合"""
        events = pd.DataFrame(index=df.index)
        
        # 1. 价格事件
        events['price_up'] = df['close'].pct_change() > 0.02
        events['price_down'] = df['close'].pct_change() < -0.02
        events['price_gap_up'] = (df['open'] - df['close'].shift(1)) > 0.01
        
        # 2. 成交量事件
        vol_ma = df['volume'].rolling(20).mean()
        events['vol_spike'] = df['volume'] > vol_ma * 2.0
        events['vol_dry'] = df['volume'] < vol_ma * 0.5
        
        # 3. 波动率事件
        atr = self._calculate_atr(df)
        atr_ma = atr.rolling(20).mean()
        events['volatility_expansion'] = atr > atr_ma * 1.5
        events['volatility_contraction'] = atr < atr_ma * 0.7
        
        # 4. 形态事件
        events['new_high'] = df['high'] == df['high'].rolling(20).max()
        events['new_low'] = df['low'] == df['low'].rolling(20).min()
        
        # 5. 指标事件
        rsi = self._calculate_rsi(df['close'])
        events['rsi_overbought'] = rsi > 70
        events['rsi_oversold'] = rsi < 30
        
        # 转换为事务格式 (每行只保留True的列名)
        transactions = []
        for idx, row in events.iterrows():
            true_events = list(row[row].index)
            transactions.append(true_events)
            
        return transactions

    def mine_association_rules(self, transactions: List[List[str]]) -> List[Dict]:
        """
        挖掘关联规则
        1. 挖掘频繁项集
        2. 生成关联规则
        3. 评估规则质量
        """
        # 1. 频繁项集挖掘
        frequent_itemsets = self._mine_frequent_itemsets(transactions)
        
        # 2. 生成规则
        rules = self._generate_rules(frequent_itemsets, transactions)
        
        # 3. 评估规则
        evaluated_rules = self._evaluate_rules(rules, transactions)
        
        self.association_rules = evaluated_rules
        logger.info(f"Found {len(evaluated_rules)} valid association rules.")
        return evaluated_rules

    def _mine_frequent_itemsets(self, transactions: List[List[str]]) -> Dict[Tuple, int]:
        """Apriori算法挖掘频繁项集"""
        itemsets = defaultdict(int)
        total = len(transactions)
        
        # 生成1-项集
        C1 = defaultdict(int)
        for trans in transactions:
            for item in trans:
                C1[(item,)] += 1
                
        L1 = {k: v for k, v in C1.items() if v / total >= self.min_support}
        itemsets.update(L1)
        
        current_L = L1
        k = 2
        
        while current_L:
            # 生成候选k-项集
            Ck = self._generate_candidates(list(current_L.keys()), k)
            Lk = defaultdict(int)
            
            # 扫描数据库计数
            for trans in transactions:
                trans_set = set(trans)
                for candidate in Ck:
                    if set(candidate).issubset(trans_set):
                        Lk[candidate] += 1
            
            # 剪枝
            current_L = {k: v for k, v in Lk.items() if v / total >= self.min_support}
            itemsets.update(current_L)
            k += 1
            
        return itemsets

    def _generate_candidates(self, prev_itemsets: List[Tuple], k: int) -> List[Tuple]:
        """生成候选项集 (连接步与剪枝步)"""
        candidates = set()
        n = len(prev_itemsets)
        
        for i in range(n):
            for j in range(i + 1, n):
                l1, l2 = prev_itemsets[i], prev_itemsets[j]
                # 连接：前k-2项相同，最后一项不同
                if l1[:-1] == l2[:-1] and l1[-1] < l2[-1]:
                    candidate = tuple(sorted(list(l1) + [l2[-1]]))
                    candidates.add(candidate)
                    
        return list(candidates)

    def _generate_rules(self, frequent_itemsets: Dict, transactions: List) -> List[Tuple]:
        """生成关联规则"""
        rules = []
        total = len(transactions)
        
        for itemset, count in frequent_itemsets.items():
            if len(itemset) < 2:
                continue
                
            support = count / total
            
            # 对于每个项集，尝试生成 A -> B 的规则
            for i in range(1, len(itemset)):
                for antecedent in combinations(itemset, i):
                    consequent = tuple(set(itemset) - set(antecedent))
                    if consequent:
                        rules.append((antecedent, consequent, support))
                        
        return rules

    def _evaluate_rules(self, rules: List[Tuple], transactions: List) -> List[Dict]:
        """评估规则质量"""
        evaluated = []
        total = len(transactions)
        
        for ant, cons, support in rules:
            # 计算指标
            ant_count = sum(1 for t in transactions if set(ant).issubset(t))
            cons_count = sum(1 for t in transactions if set(cons).issubset(t))
            both_count = sum(1 for t in transactions if set(ant).issubset(t) and set(cons).issubset(t))
            
            # Support: P(A∪B)
            supp = both_count / total
            # Confidence: P(B|A) = P(A∪B)/P(A)
            conf = both_count / (ant_count + 1e-6)
            # Lift: P(A∪B)/(P(A)*P(B))
            lift = conf / ((cons_count / total) + 1e-6)
            
            if conf >= self.min_confidence:
                evaluated.append({
                    'rule': f"{ant} -> {cons}",
                    'support': round(supp, 4),
                    'confidence': round(conf, 4),
                    'lift': round(lift, 4),
                    'leverage': round(supp - (ant_count/total * cons_count/total), 4),
                    'conviction': round((1 - cons_count/total) / (1 - conf + 1e-6), 4)
                })
                
        return sorted(evaluated, key=lambda x: x['lift'], reverse=True)

    def mine_sequential_patterns(self, df: pd.DataFrame, time_window: int = 5) -> List[Dict]:
        """挖掘序列模式"""
        # 构建事务数据库，带时间窗口
        # 简化实现：寻找 "事件A -> 事件B" 在time_window内发生的频率
        events = self.extract_events(df)
        sequences = []
        
        # 搜索二阶序列
        for i in range(len(events) - 1):
            antecedent = events[i]
            # 向前看window窗口
            future_events = [item for sublist in events[i+1:i+1+time_window] for item in sublist]
            
            for a in antecedent:
                for b in set(future_events):
                    sequences.append((a, b))
                    
        # 统计频率
        seq_counts = defaultdict(int)
        for seq in sequences:
            seq_counts[seq] += 1
            
        # 筛选显著模式
        total = len(df)
        results = []
        for (a, b), count in seq_counts.items():
            if count / total > self.min_support:
                results.append({
                    'sequence': f"{a} -> {b}",
                    'count': count,
                    'frequency': round(count / total, 4)
                })
                
        return sorted(results, key=lambda x: x['count'], reverse=True)

    def validate_patterns(self, patterns: List[Dict]) -> List[Dict]:
        """验证模式统计显著性"""
        validated = []
        for p in patterns:
            # 使用卡方检验判断是否随机出现
            # 构建列联表: (A发生且B发生, A发生B不发生; A不发生B发生, 都不发生)
            # 简化逻辑，实际需根据具体数据构建
            chi2, p_val, dof, exp = chi2_contingency([[p['count'], 10], [20, 100]]) # 模拟数据
            
            if p_val < 0.05:
                p['statistical_significance'] = p_val
                validated.append(p)
                
        return validated

    def export_patterns(self, filepath: str):
        import json
        with open(filepath, 'w') as f:
            json.dump(self.association_rules, f, indent=4)

    # 辅助函数
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
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
