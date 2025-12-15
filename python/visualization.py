#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化和分析模块
提供图表生成、性能分析、回测结果可视化等功能
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 配置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

logger = logging.getLogger(__name__)

class TradingVisualizer:
    """交易数据可视化器"""
    
    def __init__(self):
        self.figures_dir = "figures"
        os.makedirs(self.figures_dir, exist_ok=True)
        
        # 颜色配置
        self.colors = {
            'buy': '#2E8B57',      # 海绿色
            'sell': '#DC143C',     # 深红色
            'hold': '#FFD700',     # 金色
            'profit': '#32CD32',   # 酸橙绿
            'loss': '#FF4500',     # 橙红色
            'neutral': '#808080'   # 灰色
        }
    
    def create_price_chart(self, df: pd.DataFrame, signals: List[Dict] = None, 
                          title: str = "价格走势图") -> Figure:
        """创建价格走势图表"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                      gridspec_kw={'height_ratios': [3, 1]})
        
        # 价格图表
        ax1.plot(df.index, df['close'], label='收盘价', color='#1f77b4', linewidth=1)
        ax1.plot(df.index, df['high'], label='最高价', color='#ff7f0e', alpha=0.7, linewidth=0.5)
        ax1.plot(df.index, df['low'], label='最低价', color='#2ca02c', alpha=0.7, linewidth=0.5)
        
        # 添加移动平均线
        if len(df) >= 20:
            ma_20 = df['close'].rolling(20).mean()
            ma_50 = df['close'].rolling(50).mean()
            ax1.plot(df.index, ma_20, label='20周期均线', color='#d62728', linewidth=1, alpha=0.8)
            ax1.plot(df.index, ma_50, label='50周期均线', color='#9467bd', linewidth=1, alpha=0.8)
        
        # 添加信号标记
        if signals:
            for signal in signals:
                if signal['signal'] in ['buy', 'sell']:
                    signal_time = pd.to_datetime(signal.get('timestamp', df.index[-1]), unit='s')
                    if signal_time in df.index:
                        price = df.loc[signal_time, 'close']
                        color = self.colors[signal['signal']]
                        marker = '^' if signal['signal'] == 'buy' else 'v'
                        ax1.scatter(signal_time, price, color=color, marker=marker, 
                                  s=100, zorder=5, label=f'{signal["signal"]}信号')
        
        ax1.set_title(title, fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 成交量图表
        ax2.bar(df.index, df['volume'], color='#17becf', alpha=0.7)
        ax2.set_ylabel('成交量', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_technical_indicators_chart(self, df: pd.DataFrame, 
                                         indicators: Dict[str, float]) -> Figure:
        """创建技术指标图表"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        axes = axes.flatten()
        
        # RSI指标
        if 'rsi' in indicators:
            rsi_values = []
            for i in range(1, min(15, len(df))):
                gains = max(0, df['close'].iloc[-i] - df['close'].iloc[-i-1])
                losses = max(0, df['close'].iloc[-i-1] - df['close'].iloc[-i])
                avg_gain = np.mean([gains] + [max(0, df['close'].iloc[-j] - df['close'].iloc[-j-1]) 
                                           for j in range(1, min(15, len(df)))])
                avg_loss = np.mean([losses] + [max(0, df['close'].iloc[-j-1] - df['close'].iloc[-j]) 
                                           for j in range(1, min(15, len(df)))])
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
            
            axes[0].plot(range(len(rsi_values)), rsi_values, color='#ff7f0e', linewidth=2)
            axes[0].axhline(y=70, color='r', linestyle='--', alpha=0.7, label='超买线(70)')
            axes[0].axhline(y=30, color='g', linestyle='--', alpha=0.7, label='超卖线(30)')
            axes[0].set_title('RSI指标')
            axes[0].set_ylabel('RSI值')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
        
        # MACD指标
        if all(key in indicators for key in ['macd', 'macd_signal', 'macd_histogram']):
            periods = min(26, len(df))
            macd_values = []
            signal_values = []
            hist_values = []
            
            for i in range(periods):
                # 简化计算
                ema_12 = df['close'].tail(12).mean() if i >= 12 else df['close'].tail(i+1).mean()
                ema_26 = df['close'].tail(26).mean() if i >= 26 else df['close'].tail(i+1).mean()
                macd = ema_12 - ema_26
                macd_values.append(macd)
                
                # 信号线（9周期EMA）
                if len(macd_values) >= 9:
                    signal = np.mean(macd_values[-9:])
                else:
                    signal = np.mean(macd_values)
                signal_values.append(signal)
                hist_values.append(macd - signal)
            
            x = range(len(macd_values))
            axes[1].plot(x, macd_values, color='#1f77b4', label='MACD')
            axes[1].plot(x, signal_values, color='#ff7f0e', label='信号线')
            axes[1].bar(x, hist_values, color=np.where(np.array(hist_values) > 0, 'g', 'r'), 
                       alpha=0.3, label='柱状图')
            axes[1].set_title('MACD指标')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
        
        # 布林带
        if all(key in indicators for key in ['bb_upper', 'bb_lower', 'bb_middle']):
            periods = min(20, len(df))
            prices = df['close'].tail(periods).values
            
            middle_band = np.mean(prices)
            std_dev = np.std(prices)
            upper_band = middle_band + 2 * std_dev
            lower_band = middle_band - 2 * std_dev
            
            x = range(periods)
            axes[2].plot(x, prices, color='#1f77b4', label='价格')
            axes[2].plot(x, [middle_band] * periods, color='#ff7f0e', label='中轨')
            axes[2].plot(x, [upper_band] * periods, color='r', linestyle='--', label='上轨')
            axes[2].plot(x, [lower_band] * periods, color='g', linestyle='--', label='下轨')
            axes[2].fill_between(x, upper_band, lower_band, alpha=0.1, color='gray')
            axes[2].set_title('布林带')
            axes[2].legend()
            axes[2].grid(True, alpha=0.3)
        
        # 成交量指标
        volumes = df['volume'].tail(20).values
        axes[3].bar(range(len(volumes)), volumes, color='#17becf', alpha=0.7)
        axes[3].set_title('成交量')
        axes[3].set_ylabel('成交量')
        axes[3].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_performance_dashboard(self, trading_history: List[Dict]) -> Figure:
        """创建交易绩效仪表板"""
        if not trading_history:
            # 创建空图表
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, '暂无交易数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            ax.set_title('交易绩效仪表板')
            return fig
        
        # 转换为DataFrame
        df = pd.DataFrame(trading_history)
        
        # 创建子图
        fig = plt.figure(figsize=(15, 12))
        gs = fig.add_gridspec(3, 2)
        
        # 1. 累计收益曲线
        ax1 = fig.add_subplot(gs[0, :])
        if 'profit' in df.columns:
            cumulative_profit = df['profit'].cumsum()
            ax1.plot(df.index, cumulative_profit, color=self.colors['profit'], linewidth=2)
            ax1.set_title('累计收益曲线', fontsize=14, fontweight='bold')
            ax1.set_ylabel('累计收益')
            ax1.grid(True, alpha=0.3)
        
        # 2. 交易信号分布
        ax2 = fig.add_subplot(gs[1, 0])
        if 'signal' in df.columns:
            signal_counts = df['signal'].value_counts()
            colors = [self.colors.get(sig, self.colors['neutral']) for sig in signal_counts.index]
            ax2.pie(signal_counts.values, labels=signal_counts.index, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax2.set_title('交易信号分布')
        
        # 3. 盈亏分布
        ax3 = fig.add_subplot(gs[1, 1])
        if 'profit' in df.columns:
            profits = df['profit']
            winning_trades = profits[profits > 0]
            losing_trades = profits[profits < 0]
            
            ax3.hist([winning_trades, losing_trades], bins=20, 
                    label=['盈利交易', '亏损交易'], 
                    color=[self.colors['profit'], self.colors['loss']], 
                    alpha=0.7)
            ax3.set_title('盈亏分布')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. 月度绩效
        ax4 = fig.add_subplot(gs[2, 0])
        if 'timestamp' in df.columns and 'profit' in df.columns:
            df['month'] = pd.to_datetime(df['timestamp'], unit='s').dt.to_period('M')
            monthly_performance = df.groupby('month')['profit'].sum()
            
            colors = [self.colors['profit'] if x > 0 else self.colors['loss'] 
                     for x in monthly_performance.values]
            ax4.bar(range(len(monthly_performance)), monthly_performance.values, color=colors)
            ax4.set_title('月度绩效')
            ax4.set_xticks(range(len(monthly_performance)))
            ax4.set_xticklabels([str(period) for period in monthly_performance.index], rotation=45)
            ax4.grid(True, alpha=0.3)
        
        # 5. 关键指标
        ax5 = fig.add_subplot(gs[2, 1])
        ax5.axis('off')
        
        # 计算关键指标
        if 'profit' in df.columns:
            total_profit = df['profit'].sum()
            winning_trades = len(df[df['profit'] > 0])
            losing_trades = len(df[df['profit'] < 0])
            total_trades = len(df)
            win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
            avg_profit = df['profit'].mean()
            max_drawdown = self.calculate_max_drawdown(df['profit'].cumsum().values)
            
            metrics_text = f"""关键绩效指标:
总交易次数: {total_trades}
盈利交易: {winning_trades}
亏损交易: {losing_trades}
胜率: {win_rate:.1f}%
总收益: {total_profit:.2f}
平均收益: {avg_profit:.2f}
最大回撤: {max_drawdown:.2f}"""
            
            ax5.text(0.1, 0.9, metrics_text, transform=ax5.transAxes, fontsize=12,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        return fig
    
    def calculate_max_drawdown(self, cumulative_returns: np.ndarray) -> float:
        """计算最大回撤"""
        if len(cumulative_returns) == 0:
            return 0.0
        
        peak = cumulative_returns[0]
        max_dd = 0.0
        
        for value in cumulative_returns:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def create_interactive_chart(self, df: pd.DataFrame, signals: List[Dict] = None) -> go.Figure:
        """创建交互式图表（使用Plotly）"""
        fig = make_subplots(rows=2, cols=1, 
                           vertical_spacing=0.1,
                           subplot_titles=('价格走势', '成交量'),
                           row_heights=[0.7, 0.3])
        
        # 价格走势
        fig.add_trace(go.Scatter(x=df.index, y=df['close'],
                               mode='lines', name='收盘价',
                               line=dict(color='#1f77b4', width=2)),
                     row=1, col=1)
        
        # 添加移动平均线
        if len(df) >= 20:
            ma_20 = df['close'].rolling(20).mean()
            ma_50 = df['close'].rolling(50).mean()
            
            fig.add_trace(go.Scatter(x=df.index, y=ma_20,
                                   mode='lines', name='20周期均线',
                                   line=dict(color='#d62728', width=1)),
                         row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=ma_50,
                                   mode='lines', name='50周期均线',
                                   line=dict(color='#9467bd', width=1)),
                         row=1, col=1)
        
        # 添加信号标记
        if signals:
            buy_signals = [s for s in signals if s.get('signal') == 'buy']
            sell_signals = [s for s in signals if s.get('signal') == 'sell']
            
            if buy_signals:
                buy_times = [pd.to_datetime(s.get('timestamp', df.index[-1]), unit='s') 
                           for s in buy_signals]
                buy_prices = [df.loc[time, 'close'] if time in df.index else df['close'].iloc[-1] 
                            for time in buy_times]
                
                fig.add_trace(go.Scatter(x=buy_times, y=buy_prices,
                                       mode='markers', name='买入信号',
                                       marker=dict(color=self.colors['buy'], size=10, symbol='triangle-up')),
                             row=1, col=1)
            
            if sell_signals:
                sell_times = [pd.to_datetime(s.get('timestamp', df.index[-1]), unit='s') 
                            for s in sell_signals]
                sell_prices = [df.loc[time, 'close'] if time in df.index else df['close'].iloc[-1] 
                             for time in sell_times]
                
                fig.add_trace(go.Scatter(x=sell_times, y=sell_prices,
                                       mode='markers', name='卖出信号',
                                       marker=dict(color=self.colors['sell'], size=10, symbol='triangle-down')),
                             row=1, col=1)
        
        # 成交量
        fig.add_trace(go.Bar(x=df.index, y=df['volume'],
                           name='成交量',
                           marker_color='#17becf'),
                     row=2, col=1)
        
        fig.update_layout(height=600, title_text="交互式价格图表",
                         showlegend=True)
        
        return fig
    
    def save_figure(self, fig: Figure, filename: str, 
                   format: str = 'png', dpi: int = 300) -> str:
        """保存图表到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(self.figures_dir, f"{filename}_{timestamp}.{format}")
        
        try:
            fig.savefig(filepath, format=format, dpi=dpi, bbox_inches='tight')
            logger.info(f"图表已保存: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"保存图表失败: {e}")
            return ""
    
    def generate_analysis_report(self, analysis_data: Dict[str, Any]) -> str:
        """生成分析报告"""
        report = """# 交易分析报告

## 市场分析
"""
        
        # 市场状态
        if 'market_regime' in analysis_data:
            regime = analysis_data['market_regime']
            report += f"""
- **市场状态**: {regime.get('regime', '未知')}
- **置信度**: {regime.get('confidence', 0):.1%}
- **描述**: {regime.get('description', '无')}
"""
        
        # 技术指标
        if 'technical_analysis' in analysis_data:
            tech = analysis_data['technical_analysis']
            report += """
## 技术指标
"""
            for key, value in tech.items():
                report += f"- **{key}**: {value:.4f}\n"
        
        # 风险指标
        if 'risk_metrics' in analysis_data:
            risk = analysis_data['risk_metrics']
            report += """
## 风险指标
"""
            for key, value in risk.items():
                report += f"- **{key}**: {value:.4f}\n"
        
        # 支撑阻力
        if 'support_resistance' in analysis_data:
            sr = analysis_data['support_resistance']
            report += """
## 支撑阻力位
"""
            if 'support_levels' in sr:
                report += f"- **支撑位**: {', '.join(map(str, sr['support_levels'][:3]))}\n"
            if 'resistance_levels' in sr:
                report += f"- **阻力位**: {', '.join(map(str, sr['resistance_levels'][:3]))}\n"
        
        # 机器学习信号
        if 'ml_signal' in analysis_data:
            ml = analysis_data['ml_signal']
            report += """
## 机器学习信号
"""
            report += f"""- **信号**: {ml.get('signal', '未知')}
- **置信度**: {ml.get('confidence', 0):.1%}
- **方法**: {ml.get('method', '未知')}
- **原因**: {ml.get('reason', '无')}
"""
        
        # 综合信号
        if 'final_signal' in analysis_data:
            final = analysis_data['final_signal']
            report += """
## 综合交易信号
"""
            report += f"""- **最终信号**: {final.get('signal', '未知')}
- **信号强度**: {final.get('strength', 0)}
- **置信度**: {final.get('confidence', 0):.1%}
- **原因**: {', '.join(final.get('reasons', []))}
"""
        
        report += f"""
## 报告信息
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **数据周期**: {analysis_data.get('timeframe', '未知')}
- **交易品种**: {analysis_data.get('symbol', '未知')}
"""
        
        return report
    
    def create_ml_performance_chart(self, ml_history: List[Dict]) -> Figure:
        """创建机器学习模型性能图表"""
        if not ml_history:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, '暂无机器学习数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16)
            ax.set_title('机器学习模型性能')
            return fig
        
        df = pd.DataFrame(ml_history)
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # 1. 准确率趋势
        if 'accuracy' in df.columns:
            ax1.plot(df.index, df['accuracy'], color='#1f77b4', linewidth=2, marker='o')
            ax1.set_title('模型准确率趋势')
            ax1.set_ylabel('准确率')
            ax1.grid(True, alpha=0.3)
        
        # 2. 信号分布
        if 'predicted_signal' in df.columns:
            signal_counts = df['predicted_signal'].value_counts()
            colors = [self.colors.get(sig, self.colors['neutral']) for sig in signal_counts.index]
            ax2.pie(signal_counts.values, labels=signal_counts.index, autopct='%1.1f%%', 
                   colors=colors, startangle=90)
            ax2.set_title('预测信号分布')
        
        # 3. 置信度分布
        if 'confidence' in df.columns:
            ax3.hist(df['confidence'], bins=20, color='#17becf', alpha=0.7)
            ax3.set_title('预测置信度分布')
            ax3.set_xlabel('置信度')
            ax3.set_ylabel('频次')
            ax3.grid(True, alpha=0.3)
        
        # 4. 训练样本数量
        if 'training_samples' in df.columns:
            ax4.plot(df.index, df['training_samples'], color='#ff7f0e', linewidth=2, marker='s')
            ax4.set_title('训练样本数量')
            ax4.set_ylabel('样本数量')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def create_real_time_dashboard(self, real_time_data: Dict[str, Any]) -> go.Figure:
        """创建实时监控仪表板"""
        # 创建2x2的子图布局
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '价格走势', '技术指标',
                '信号强度', '风险指标'
            ),
            specs=[[{"type": "xy"}, {"type": "xy"}],
                   [{"type": "xy"}, {"type": "xy"}]]
        )
        
        # 价格走势图
        if 'price_data' in real_time_data:
            df = real_time_data['price_data']
            fig.add_trace(
                go.Scatter(x=df.index, y=df['close'], name='收盘价',
                          line=dict(color='#1f77b4', width=2)),
                row=1, col=1
            )
        
        # 技术指标
        if 'indicators' in real_time_data:
            indicators = real_time_data['indicators']
            # 添加RSI指标
            if 'rsi' in indicators:
                # 创建简单的RSI图表
                rsi_values = [indicators['rsi']] * 10
                fig.add_trace(
                    go.Scatter(x=list(range(10)), y=rsi_values, name='RSI', 
                              line=dict(color='#ff7f0e', width=2)),
                    row=1, col=2
                )
                # 添加超买超卖线
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=2)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=2)
        
        # 信号强度
        if 'signal_strength' in real_time_data:
            strength = real_time_data['signal_strength']
            # 创建简单的信号强度条形图
            fig.add_trace(
                go.Bar(x=['信号强度'], y=[strength], name='信号强度',
                      marker_color='darkblue'),
                row=2, col=1
            )
        
        # 风险指标
        if 'risk_metrics' in real_time_data:
            risk = real_time_data['risk_metrics']
            # 创建风险指标雷达图（简化版）
            metrics = list(risk.keys())[:3]  # 只显示前3个指标
            values = [risk[metric] for metric in metrics]
            
            fig.add_trace(
                go.Scatter(x=metrics, y=values, name='风险指标',
                          line=dict(color='#9467bd', width=2),
                          marker=dict(size=8)),
                row=2, col=2
            )
        
        # 更新布局
        fig.update_layout(
            height=800,
            title_text="实时交易监控仪表板",
            showlegend=True
        )
        
        return fig
    
    def generate_comprehensive_report(self, comprehensive_data: Dict[str, Any]) -> str:
        """生成综合分析报告"""
        report = """# 综合分析报告

## 执行摘要
"""
        
        # 总体评估
        overall_score = comprehensive_data.get('overall_score', 0)
        market_condition = comprehensive_data.get('market_condition', '中性')
        
        report += f"""
- **综合评分**: {overall_score}/100
- **市场环境**: {market_condition}
- **交易建议**: {self._get_trading_recommendation(overall_score)}

## 详细分析
"""
        
        # 技术分析部分
        if 'technical_analysis' in comprehensive_data:
            tech = comprehensive_data['technical_analysis']
            report += """
### 技术分析
"""
            for category, indicators in tech.items():
                report += f"**{category}**:\n"
                for indicator, value in indicators.items():
                    try:
                        # 尝试将值转换为浮点数进行格式化
                        formatted_value = f"{float(value):.4f}"
                        report += f"  - {indicator}: {formatted_value}\n"
                    except (ValueError, TypeError):
                        # 如果转换失败，直接使用原始值
                        report += f"  - {indicator}: {value}\n"
        
        # 机器学习分析
        if 'machine_learning' in comprehensive_data:
            ml = comprehensive_data['machine_learning']
            report += """
### 机器学习分析
"""
            accuracy = float(ml.get('accuracy', 0))
            confidence = float(ml.get('confidence', 0))
            training_samples = ml.get('training_samples', 0)
            report += f"""- **模型准确率**: {accuracy:.1%}
- **预测信号**: {ml.get('predicted_signal', '未知')}
- **置信度**: {confidence:.1%}
- **训练样本数**: {training_samples}
"""
        
        # 风险评估
        if 'risk_assessment' in comprehensive_data:
            risk = comprehensive_data['risk_assessment']
            report += """
### 风险评估
"""
            for metric, value in risk.items():
                try:
                    # 尝试将值转换为浮点数进行格式化
                    formatted_value = f"{float(value):.4f}"
                    report += f"- **{metric}**: {formatted_value}\n"
                except (ValueError, TypeError):
                    # 如果转换失败，直接使用原始值
                    report += f"- **{metric}**: {value}\n"
        
        # 交易建议
        report += """
## 交易建议
"""
        
        recommendations = self._generate_trading_recommendations(comprehensive_data)
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
        
        report += f"""
## 报告信息
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **数据来源**: MQL5-Python集成系统
- **分析工具**: 技术分析 + 机器学习
"""
        
        return report
    
    def _get_trading_recommendation(self, score: int) -> str:
        """根据评分获取交易建议"""
        if score >= 80:
            return "强烈建议交易"
        elif score >= 60:
            return "建议交易"
        elif score >= 40:
            return "谨慎交易"
        else:
            return "不建议交易"
    
    def _generate_trading_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """生成具体的交易建议"""
        recommendations = []
        
        # 基于技术指标的建议
        if 'technical_analysis' in data:
            tech = data['technical_analysis']
            
            # RSI建议
            if 'rsi' in tech:
                rsi = tech['rsi']
                if rsi < 30:
                    recommendations.append("RSI显示超卖，可能适合买入")
                elif rsi > 70:
                    recommendations.append("RSI显示超买，可能适合卖出")
        
        # 基于机器学习信号的建议
        if 'machine_learning' in data:
            ml = data['machine_learning']
            signal = ml.get('predicted_signal', '')
            confidence = ml.get('confidence', 0)
            
            if confidence > 0.7:
                if signal == 'buy':
                    recommendations.append("机器学习模型强烈建议买入")
                elif signal == 'sell':
                    recommendations.append("机器学习模型强烈建议卖出")
        
        # 基于风险的建议
        if 'risk_assessment' in data:
            risk = data['risk_assessment']
            volatility = risk.get('volatility', 0)
            
            if volatility > 0.02:
                recommendations.append("市场波动性较高，建议减小仓位")
        
        if not recommendations:
            recommendations.append("当前市场条件一般，建议观望")
        
        return recommendations

# 全局可视化器实例
visualizer = TradingVisualizer()

if __name__ == "__main__":
    # 测试代码
    print("数据可视化模块加载成功")