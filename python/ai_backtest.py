#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI交易策略回测脚本

支持使用历史数据测试AI交易策略的表现，输出详细的回测报告。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import logging
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processor import MT5DataProcessor
from ai_client_factory import initialize_ai_clients
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_backtest.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIBacktester:
    """
    AI交易策略回测器
    """
    
    def __init__(self, initial_capital=100000.0, risk_per_trade=1.0):
        """
        初始化回测器
        
        Args:
            initial_capital (float): 初始资金
            risk_per_trade (float): 每笔交易风险百分比
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.position = 0  # 持仓状态：1=多头，-1=空头，0=空仓
        self.entry_price = 0.0
        self.trades = []
        self.equity_curve = []
        self.data_processor = MT5DataProcessor()
        
        # 初始化AI客户端 - 使用硅基流动API服务，基于ValueCell的模型工厂模式
        ai_clients = initialize_ai_clients()
        
        self.deepseek_client = ai_clients.get('deepseek')
        self.qwen_client = ai_clients.get('qwen')
        
        # 验证客户端初始化成功
        if not self.deepseek_client or not self.qwen_client:
            logger.error("AI客户端初始化失败，使用模拟数据进行回测")
        
        logger.info(f"AIBacktester初始化完成，初始资金: {initial_capital}, 每笔风险: {risk_per_trade}%")
    
    def get_historical_data(self, symbol, start_date, end_date, timeframe='H1'):
        """
        获取历史数据
        
        Args:
            symbol (str): 交易品种
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
            timeframe (str): 时间周期
        
        Returns:
            pd.DataFrame: 历史数据
        """
        logger.info(f"获取{symbol}的历史数据，时间范围: {start_date} 至 {end_date}")
        df = self.data_processor.get_historical_data(symbol, None, start_date, end_date)
        logger.info(f"获取到{len(df)}条历史数据")
        return df
    
    def get_ai_signal(self, df):
        """
        获取AI交易信号
        
        Args:
            df (pd.DataFrame): 市场数据
        
        Returns:
            str: 交易信号 (buy, sell, none)
            int: 信号强度 (0-100)
        """
        # 检查AI客户端是否初始化成功
        if not self.deepseek_client or not self.qwen_client:
            logger.error("AI客户端未初始化，无法生成交易信号")
            return "none", 50
        
        # 生成特征
        df_with_features = self.data_processor.generate_features(df)
        
        # 准备模型输入
        df_tail = df_with_features.tail(20)
        df_tail_reset = df_tail.reset_index()
        df_tail_reset['time'] = df_tail_reset['time'].astype(str)
        model_input = df_tail_reset.to_dict(orient='records')
        
        try:
            # 使用DeepSeek分析市场结构
            deepseek_analysis = self.deepseek_client.analyze_market_structure(model_input)
            
            # 使用Qwen3优化策略
            optimized_strategy = self.qwen_client.optimize_strategy_logic(deepseek_analysis, model_input)
            
            # 生成信号
            signal = "none"
            if optimized_strategy["signal_strength"] > 70:
                if df_with_features['ema_fast'].iloc[-1] > df_with_features['ema_slow'].iloc[-1]:
                    signal = "buy"
                else:
                    signal = "sell"
            
            return signal, optimized_strategy["signal_strength"]
        except Exception as e:
            logger.error(f"AI信号生成失败: {e}")
            return "none", 50
    
    def calculate_position_size(self, atr):
        """
        计算仓位大小
        
        Args:
            atr (float): 平均真实波动幅度
        
        Returns:
            float: 仓位大小
        """
        if atr <= 0:
            return 0.0
        
        # 计算风险金额
        risk_amount = self.current_capital * (self.risk_per_trade / 100.0)
        
        # 假设每手价值为100000（根据实际情况调整）
        # 这里简化处理，实际应该根据交易品种的点值计算
        position_size = risk_amount / (atr * 100000)
        
        # 限制最小和最大仓位
        position_size = max(0.01, min(1.0, position_size))
        
        return round(position_size, 2)
    
    def run_backtest(self, symbol, start_date, end_date):
        """
        运行回测
        
        Args:
            symbol (str): 交易品种
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
        """
        logger.info(f"开始回测 {symbol}, 时间范围: {start_date} 至 {end_date}")
        
        # 获取历史数据
        df = self.get_historical_data(symbol, start_date, end_date)
        
        # 生成特征
        df = self.data_processor.generate_features(df)
        
        # 初始化回测
        self.current_capital = self.initial_capital
        self.position = 0
        self.entry_price = 0.0
        self.trades = []
        self.equity_curve = [self.current_capital]
        
        # 遍历数据进行回测
        for i in range(20, len(df)):
            # 获取当前数据
            current_data = df.iloc[i]
            
            # 计算ATR
            atr = current_data['atr']
            
            # 获取AI信号
            window_df = df.iloc[i-20:i+1]
            signal, signal_strength = self.get_ai_signal(window_df)
            
            # 处理交易信号
            if signal == "buy" and self.position != 1:
                # 平仓现有仓位
                if self.position == -1:
                    self.close_position(current_data['close'])
                
                # 开多仓
                self.position = 1
                self.entry_price = current_data['close']
                position_size = self.calculate_position_size(atr)
                
                self.trades.append({
                    'date': current_data.name,
                    'signal': 'buy',
                    'price': self.entry_price,
                    'position_size': position_size,
                    'signal_strength': signal_strength,
                    'status': 'open'
                })
                
                logger.info(f"开多仓: {symbol}, 价格: {self.entry_price:.5f}, 仓位: {position_size}, 信号强度: {signal_strength}")
            
            elif signal == "sell" and self.position != -1:
                # 平仓现有仓位
                if self.position == 1:
                    self.close_position(current_data['close'])
                
                # 开空仓
                self.position = -1
                self.entry_price = current_data['close']
                position_size = self.calculate_position_size(atr)
                
                self.trades.append({
                    'date': current_data.name,
                    'signal': 'sell',
                    'price': self.entry_price,
                    'position_size': position_size,
                    'signal_strength': signal_strength,
                    'status': 'open'
                })
                
                logger.info(f"开空仓: {symbol}, 价格: {self.entry_price:.5f}, 仓位: {position_size}, 信号强度: {signal_strength}")
            
            # 更新权益曲线
            self.update_equity_curve(current_data['close'])
        
        # 回测结束，平仓所有仓位
        if self.position != 0:
            self.close_position(df.iloc[-1]['close'])
        
        logger.info("回测完成")
        
        # 生成回测报告
        self.generate_report(symbol, start_date, end_date)
    
    def close_position(self, exit_price):
        """
        平仓
        
        Args:
            exit_price (float): 平仓价格
        """
        if self.position == 0:
            return
        
        # 获取当前持仓的交易记录
        for trade in reversed(self.trades):
            if trade['status'] == 'open':
                # 计算盈亏
                if trade['signal'] == 'buy':
                    profit = (exit_price - trade['price']) * trade['position_size'] * 100000
                else:
                    profit = (trade['price'] - exit_price) * trade['position_size'] * 100000
                
                # 更新交易记录
                trade['exit_date'] = datetime.now()
                trade['exit_price'] = exit_price
                trade['profit'] = profit
                trade['status'] = 'closed'
                
                # 更新资金
                self.current_capital += profit
                
                logger.info(f"平仓: 信号: {trade['signal']}, 入场: {trade['price']:.5f}, 出场: {exit_price:.5f}, 盈亏: {profit:.2f}, 资金: {self.current_capital:.2f}")
                break
        
        # 重置持仓状态
        self.position = 0
        self.entry_price = 0.0
    
    def update_equity_curve(self, current_price):
        """
        更新权益曲线
        
        Args:
            current_price (float): 当前价格
        """
        # 如果持仓，计算浮动盈亏
        if self.position != 0:
            if self.position == 1:
                unrealized_profit = (current_price - self.entry_price) * self.trades[-1]['position_size'] * 100000
            else:
                unrealized_profit = (self.entry_price - current_price) * self.trades[-1]['position_size'] * 100000
            
            equity = self.current_capital + unrealized_profit
        else:
            equity = self.current_capital
        
        self.equity_curve.append(equity)
    
    def generate_report(self, symbol, start_date, end_date):
        """
        生成回测报告
        
        Args:
            symbol (str): 交易品种
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
        """
        logger.info("生成回测报告")
        
        # 计算回测指标
        total_trades = len(self.trades)
        winning_trades = sum(1 for trade in self.trades if trade['profit'] > 0)
        losing_trades = sum(1 for trade in self.trades if trade['profit'] < 0)
        total_profit = sum(trade['profit'] for trade in self.trades if trade['status'] == 'closed')
        max_drawdown = self.calculate_max_drawdown()
        
        # 计算胜率
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
        
        # 计算平均盈亏比
        avg_win = sum(trade['profit'] for trade in self.trades if trade['profit'] > 0) / winning_trades if winning_trades > 0 else 0
        avg_loss = abs(sum(trade['profit'] for trade in self.trades if trade['profit'] < 0) / losing_trades) if losing_trades > 0 else 1
        risk_reward_ratio = avg_win / avg_loss
        
        # 计算总收益率
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital * 100
        
        # 输出回测报告
        report = f"""===== AI交易策略回测报告 =====
交易品种: {symbol}
时间范围: {start_date} 至 {end_date}
初始资金: {self.initial_capital:.2f}
最终资金: {self.current_capital:.2f}
总收益率: {total_return:.2f}%
总交易次数: {total_trades}
盈利交易: {winning_trades}
亏损交易: {losing_trades}
胜率: {win_rate:.2f}%
平均盈利: {avg_win:.2f}
平均亏损: {avg_loss:.2f}
风险回报比: {risk_reward_ratio:.2f}
最大回撤: {max_drawdown:.2f}%
==========================="""
        
        print(report)
        logger.info(report)
        
        # 保存回测报告
        with open(f"ai_backtest_report_{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.txt", 'w') as f:
            f.write(report)
        
        # 绘制权益曲线
        self.plot_equity_curve(symbol, start_date, end_date)
    
    def calculate_max_drawdown(self):
        """
        计算最大回撤
        
        Returns:
            float: 最大回撤百分比
        """
        if not self.equity_curve:
            return 0.0
        
        peak = self.equity_curve[0]
        max_drawdown = 0.0
        
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    def plot_equity_curve(self, symbol, start_date, end_date):
        """
        绘制权益曲线
        
        Args:
            symbol (str): 交易品种
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
        """
        logger.info("绘制权益曲线")
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve, label='Equity Curve')
        plt.title(f'AI Trading Strategy - Equity Curve ({symbol})')
        plt.xlabel('Time Steps')
        plt.ylabel('Equity')
        plt.grid(True)
        plt.legend()
        
        # 保存图表
        plt.savefig(f"ai_backtest_equity_{symbol}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.png", dpi=300)
        plt.close()
        
        logger.info(f"权益曲线已保存")

def main():
    """
    主函数
    """
    # 配置回测参数
    symbol = "GOLD"
    start_date = datetime.now() - timedelta(days=30)  # 回测最近30天
    end_date = datetime.now()
    initial_capital = 100000.0
    risk_per_trade = 1.0
    
    # 创建回测器
    backtester = AIBacktester(initial_capital, risk_per_trade)
    
    # 运行回测
    backtester.run_backtest(symbol, start_date, end_date)

if __name__ == "__main__":
    main()
