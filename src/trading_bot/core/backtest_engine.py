import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, Any, List
from datetime import datetime

class BacktestEngine:
    """
    回测引擎，用于策略历史数据回测和性能评估
    """
    def __init__(self, initial_capital: float = 100000.0):
        """
        初始化回测引擎
        
        Args:
            initial_capital (float): 初始资金，默认为100,000.0
        """
        self.initial_capital = initial_capital
        self.data = None
        self.strategy = None
        self.results = None
        self.trades = None
    
    def load_data(self, data: pd.DataFrame):
        """
        加载历史数据
        
        Args:
            data (pd.DataFrame): 包含OHLCV和特征的数据
        """
        self.data = data.copy()
    
    def set_strategy(self, strategy_func):
        """
        设置回测策略
        
        Args:
            strategy_func: 策略函数，接受数据和回测引擎实例，返回信号
        """
        self.strategy = strategy_func
    
    def run_backtest(self, risk_per_trade: float = 0.01):
        """
        执行回测
        
        Args:
            risk_per_trade (float): 每笔交易风险占比，默认为1%
        """
        if self.data is None:
            raise ValueError("No data loaded. Please call load_data() first.")
        
        if self.strategy is None:
            raise ValueError("No strategy set. Please call set_strategy() first.")
        
        # 初始化回测变量
        capital = self.initial_capital
        position = 0  # 持仓量，正数为多，负数为空
        trades = []
        equity_curve = [capital]
        
        # 遍历数据，执行策略
        for i in range(len(self.data)):
            # 获取当前数据
            current_data = self.data.iloc[i]
            
            # 调用策略函数生成信号
            signal = self.strategy(self.data.iloc[:i+1], self)
            
            # 计算ATR用于止损
            atr = current_data['atr']
            
            # 计算每笔交易的风险金额
            risk_amount = capital * risk_per_trade
            
            # 计算仓位大小（假设1手=100000单位）
            if atr > 0:
                position_size = int(risk_amount / (atr * 100000))
            else:
                position_size = 1
            
            # 执行交易
            if signal == 1 and position <= 0:  # 买入信号
                # 平仓（如果有空头仓位）
                if position < 0:
                    exit_price = current_data['close']
                    pnl = (exit_price - current_data['open']) * abs(position) * 100000
                    capital += pnl
                    trades.append({
                        'entry_time': entry_time,
                        'entry_price': entry_price,
                        'exit_time': current_data.name,
                        'exit_price': exit_price,
                        'signal': 'sell',
                        'pnl': pnl,
                        'capital': capital
                    })
                
                # 开仓
                position = position_size
                entry_time = current_data.name
                entry_price = current_data['open']
            
            elif signal == -1 and position >= 0:  # 卖出信号
                # 平仓（如果有多头仓位）
                if position > 0:
                    exit_price = current_data['close']
                    pnl = (exit_price - entry_price) * position * 100000
                    capital += pnl
                    trades.append({
                        'entry_time': entry_time,
                        'entry_price': entry_price,
                        'exit_time': current_data.name,
                        'exit_price': exit_price,
                        'signal': 'buy',
                        'pnl': pnl,
                        'capital': capital
                    })
                
                # 开仓
                position = -position_size
                entry_time = current_data.name
                entry_price = current_data['open']
            
            # 更新权益曲线
            if position != 0:
                # 计算未实现盈亏
                current_price = current_data['close']
                unrealized_pnl = (current_price - entry_price) * position * 100000
                current_capital = capital + unrealized_pnl
            else:
                current_capital = capital
            
            equity_curve.append(current_capital)
        
        # 保存结果
        self.results = {
            'equity_curve': equity_curve,
            'final_capital': equity_curve[-1],
            'initial_capital': self.initial_capital
        }
        
        self.trades = pd.DataFrame(trades)
        if not self.trades.empty:
            self.trades.set_index('entry_time', inplace=True)
        
        # 计算性能指标
        self.calculate_metrics()
    
    def calculate_metrics(self):
        """
        计算回测性能指标
        """
        if self.results is None:
            raise ValueError("No backtest results available. Please run_backtest() first.")
        
        equity = pd.Series(self.results['equity_curve'][1:], index=self.data.index)
        returns = equity.pct_change().dropna()
        
        # 计算基本指标
        total_return = (self.results['final_capital'] - self.results['initial_capital']) / self.results['initial_capital']
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1  # 假设252个交易日
        
        # 计算风险指标
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 计算最大回撤
        drawdowns = []
        peak = equity.iloc[0]
        
        for value in equity:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            drawdowns.append(drawdown)
        
        max_drawdown = max(drawdowns)
        
        # 计算胜率
        winning_trades = 0
        total_trades = len(self.trades) if self.trades is not None and not self.trades.empty else 0
        
        if total_trades > 0:
            winning_trades = len(self.trades[self.trades['pnl'] > 0])
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 计算平均盈亏比
        avg_win = self.trades[self.trades['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = abs(self.trades[self.trades['pnl'] < 0]['pnl'].mean()) if (total_trades - winning_trades) > 0 else 0
        risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # 保存指标
        self.results.update({
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'risk_reward_ratio': risk_reward_ratio,
            'total_trades': total_trades,
            'winning_trades': winning_trades
        })
    
    def generate_report(self, report_path: str = None):
        """
        生成回测报告
        
        Args:
            report_path (str): 报告保存路径，默认为None（不保存）
        
        Returns:
            Dict[str, Any]: 回测报告
        """
        if self.results is None:
            raise ValueError("No backtest results available. Please run_backtest() first.")
        
        report = {
            '回测参数': {
                '初始资金': self.initial_capital,
                '回测周期': f"{self.data.index[0]} 至 {self.data.index[-1]}",
                '数据周期': str(self.data.index.freq),
                '交易品种': 'GOLD'
            },
            '性能指标': {
                '总收益率': f"{self.results['total_return']:.2%}",
                '年化收益率': f"{self.results['annual_return']:.2%}",
                '波动率': f"{self.results['volatility']:.2%}",
                '夏普比率': f"{self.results['sharpe_ratio']:.2f}",
                '最大回撤': f"{self.results['max_drawdown']:.2%}",
                '胜率': f"{self.results['win_rate']:.2%}",
                '风险回报比': f"{self.results['risk_reward_ratio']:.2f}",
                '总交易次数': self.results['total_trades'],
                '盈利交易次数': self.results['winning_trades']
            }
        }
        
        # 如果有交易记录，添加交易详情
        if self.trades is not None and not self.trades.empty:
            report['交易记录'] = self.trades.to_dict('records')
        
        # 保存报告
        if report_path:
            import json
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        return report
    
    def plot_results(self, save_path: str = None):
        """
        可视化回测结果
        
        Args:
            save_path (str): 图表保存路径，默认为None（不保存）
        """
        if self.results is None:
            raise ValueError("No backtest results available. Please run_backtest() first.")
        
        equity = pd.Series(self.results['equity_curve'][1:], index=self.data.index)
        
        # 创建画布
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # 绘制权益曲线
        ax1.plot(equity.index, equity, label='Equity Curve', color='blue')
        ax1.set_title('Backtest Results - Equity Curve')
        ax1.set_ylabel('Capital')
        ax1.grid(True)
        ax1.legend()
        
        # 绘制最大回撤
        drawdowns = []
        peak = equity.iloc[0]
        for value in equity:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            drawdowns.append(drawdown)
        
        ax2.plot(equity.index, drawdowns, label='Drawdown', color='red')
        ax2.set_title('Backtest Results - Drawdown')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Drawdown')
        ax2.grid(True)
        ax2.legend()
        
        # 格式化日期
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()
        
        # 保存图表
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.tight_layout()
        plt.show()


def example_strategy(data, engine):
    """
    示例策略：EMA交叉策略
    
    Args:
        data (pd.DataFrame): 历史数据
        engine (BacktestEngine): 回测引擎实例
    
    Returns:
        int: 信号，1=买入，-1=卖出，0=持有
    """
    if len(data) < 26:  # 确保有足够的数据计算指标
        return 0
    
    # 简单的EMA交叉策略
    if data['ema_fast'].iloc[-1] > data['ema_slow'].iloc[-1] and data['ema_fast'].iloc[-2] <= data['ema_slow'].iloc[-2]:
        return 1  # 金叉，买入信号
    elif data['ema_fast'].iloc[-1] < data['ema_slow'].iloc[-1] and data['ema_fast'].iloc[-2] >= data['ema_slow'].iloc[-2]:
        return -1  # 死叉，卖出信号
    else:
        return 0  # 无信号


def main():
    """
    主函数用于测试回测引擎
    """
    from src.trading_bot.data.mt5_data_processor import MT5DataProcessor
    
    # 初始化数据处理器
    processor = MT5DataProcessor()
    
    # 获取历史数据
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 注意：这里使用模拟数据，因为MT5可能没有连接
    # 生成模拟数据
    dates = pd.date_range(start=start_date, end=end_date, freq='H')
    n = len(dates)
    
    # 生成模拟价格数据
    np.random.seed(42)
    close = 1900 + np.cumsum(np.random.randn(n) * 2)
    high = close + np.random.rand(n) * 3
    low = close - np.random.rand(n) * 3
    open_price = close.shift(1).fillna(1900)
    volume = np.random.randint(100000, 1000000, n)
    
    # 创建模拟DataFrame
    df = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    # 生成特征
    df = processor.generate_features(df)
    
    # 初始化回测引擎
    engine = BacktestEngine(initial_capital=100000.0)
    
    # 加载数据
    engine.load_data(df)
    
    # 设置策略
    engine.set_strategy(example_strategy)
    
    # 运行回测
    engine.run_backtest(risk_per_trade=0.01)
    
    # 生成报告
    report = engine.generate_report()
    print("回测报告:")
    for section, content in report.items():
        print(f"\n{section}:")
        if isinstance(content, dict):
            for key, value in content.items():
                print(f"  {key}: {value}")
        else:
            print(content)
    
    # 绘制结果
    engine.plot_results(save_path="/Users/lenovo/tmp/quant_trading_strategy/backtest_reports/example_backtest.png")

if __name__ == "__main__":
    main()
