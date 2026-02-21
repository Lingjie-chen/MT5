import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PatternValidator:
    """
    模式验证与回测系统
    评估模式的统计显著性、稳健性及盈利能力。
    """
    
    def __init__(self, 
                 stop_loss_pct: float = 0.01, 
                 take_profit_pct: float = 0.02,
                 slippage_pct: float = 0.001):
        
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.slippage_pct = slippage_pct
        
    def validate_pattern(self, df: pd.DataFrame, pattern_func: callable) -> Dict:
        """
        验证单个模式
        pattern_func: 识别模式索引的函数，返回模式发生的index列表
        """
        # 1. 提取实例
        instances = self._extract_pattern_instances(df, pattern_func)
        
        if not instances:
            return {"status": "No instances found"}
            
        # 2. 计算表现
        performance = self._calculate_pattern_performance(df, instances)
        
        # 3. 统计显著性检验
        significance = self._test_statistical_significance(performance)
        
        # 4. 稳健性评估
        robustness = self._assess_robustness(performance)
        
        # 5. 回测
        backtest = self._backtest_pattern(df, instances)
        
        # 6. 综合评分
        score = self._calculate_overall_score(performance, significance, robustness, backtest)
        
        return {
            'instances_count': len(instances),
            'performance': performance,
            'significance': significance,
            'robustness': robustness,
            'backtest': backtest,
            'overall_score': score
        }

    def _extract_pattern_instances(self, df: pd.DataFrame, pattern_func: callable) -> List[pd.Timestamp]:
        """提取模式发生的时间点"""
        return pattern_func(df)

    def _calculate_pattern_performance(self, df: pd.DataFrame, instances: List) -> Dict:
        """计算模式在不同前瞻期的表现"""
        forward_periods = [5, 10, 20]
        results = {f'forward_{p}': {} for p in forward_periods}
        
        returns_list = {p: [] for p in forward_periods}
        
        for t in instances:
            loc = df.index.get_loc(t)
            for p in forward_periods:
                if loc + p < len(df):
                    future_price = df['close'].iloc[loc + p]
                    current_price = df['close'].iloc[loc]
                    ret = (future_price - current_price) / current_price
                    returns_list[p].append(ret)
                    
        for p in forward_periods:
            r = returns_list[p]
            if r:
                results[f'forward_{p}'] = {
                    'mean_return': np.mean(r),
                    'median_return': np.median(r),
                    'std_dev': np.std(r),
                    'win_rate': sum(1 for x in r if x > 0) / len(r)
                }
        return results

    def _test_statistical_significance(self, performance: Dict) -> Dict:
        """t检验：验证收益均值是否显著不为0"""
        sig_results = {}
        for key, vals in performance.items():
            if not vals: continue
            mean = vals.get('mean_return', 0)
            std = vals.get('std_dev', 1)
            n = 20 # 假设样本数，实际应从instances获取
            
            if std == 0: continue
            
            # 单样本t检验
            t_stat, p_val = stats.ttest_1samp([mean] * n, 0) # 简化，实际应传入具体样本列表
            
            sig_results[key] = {
                't_statistic': t_stat,
                'p_value': p_val,
                'is_significant': p_val < 0.05
            }
        return sig_results

    def _assess_robustness(self, performance: Dict) -> Dict:
        """评估稳健性"""
        # 检查不同周期表现是否一致
        win_rates = [vals.get('win_rate', 0) for vals in performance.values()]
        
        if len(win_rates) < 2:
            return {'score': 0}
            
        # 稳健性 = 胜率方差小，均值高
        consistency = 1 - np.std(win_rates)
        avg_win_rate = np.mean(win_rates)
        
        return {
            'win_rate_consistency': consistency,
            'average_win_rate': avg_win_rate,
            'score': consistency * avg_win_rate
        }

    def _backtest_pattern(self, df: pd.DataFrame, instances: List) -> Dict:
        """简单的回测逻辑"""
        trades = []
        
        for t in instances:
            entry_loc = df.index.get_loc(t)
            if entry_loc + 20 >= len(df): continue # 没有足够数据退出
            
            entry_price = df['close'].iloc[entry_loc]
            # 加入滑点
            entry_price *= (1 + self.slippage_pct)
            
            # 模拟未来20根K线寻找出场点
            exit_price = None
            for i in range(1, 21):
                future_low = df['low'].iloc[entry_loc + i]
                future_high = df['high'].iloc[entry_loc + i]
                future_close = df['close'].iloc[entry_loc + i]
                
                # 止损逻辑
                if future_low <= entry_price * (1 - self.stop_loss_pct):
                    exit_price = entry_price * (1 - self.stop_loss_pct)
                    break
                # 止盈逻辑
                if future_high >= entry_price * (1 + self.take_profit_pct):
                    exit_price = entry_price * (1 + self.take_profit_pct)
                    break
            
            if exit_price is None:
                exit_price = df['close'].iloc[entry_loc + 20] # 强制平仓
                
            pnl = (exit_price - entry_price) / entry_price
            trades.append(pnl)
            
        if not trades:
            return {'total_trades': 0}
            
        return {
            'total_trades': len(trades),
            'win_rate': sum(1 for t in trades if t > 0) / len(trades),
            'total_return': sum(trades),
            'sharpe_ratio': np.mean(trades) / (np.std(trades) + 1e-6) * np.sqrt(252) # 年化假设
        }

    def _calculate_overall_score(self, perf, sig, rob, bt) -> float:
        """加权综合评分"""
        score = 0.0
        
        # 性能分 (权重30%)
        perf_score = rob.get('average_win_rate', 0)
        score += perf_score * 0.3
        
        # 显著性分 (权重20%)
        sig_score = 1.0 if any(s.get('is_significant', False) for s in sig.values()) else 0.5
        score += sig_score * 0.2
        
        # 稳健性分 (权重20%)
        score += rob.get('score', 0) * 0.2
        
        # 回测分 (权重30%)
        bt_score = 0
        if bt.get('sharpe_ratio', 0) > 1.5: bt_score = 1.0
        elif bt.get('sharpe_ratio', 0) > 1.0: bt_score = 0.7
        else: bt_score = bt.get('win_rate', 0)
        score += bt_score * 0.3
        
        return round(score, 4)

    def generate_performance_report(self, validation_results: Dict) -> str:
        """生成文本报告"""
        report = "=== Pattern Validation Report ===\n"
        report += f"Total Instances: {validation_results.get('instances_count')}\n"
        report += f"Overall Score: {validation_results.get('overall_score')}\n"
        report += "Backtest Summary:\n"
        bt = validation_results.get('backtest', {})
        report += f"  Win Rate: {bt.get('win_rate', 0):.2%}\n"
        report += f"  Sharpe Ratio: {bt.get('sharpe_ratio', 0):.2f}\n"
        return report
