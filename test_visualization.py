#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据可视化模块
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from python.visualization import TradingVisualizer

def create_test_data():
    """创建测试数据"""
    # 创建价格数据
    dates = pd.date_range(start='2024-01-01', periods=100, freq='H')
    np.random.seed(42)
    
    # 生成随机价格数据
    prices = []
    current_price = 1.1000
    for i in range(100):
        change = np.random.normal(0, 0.001)
        current_price *= (1 + change)
        prices.append(current_price)
    
    df = pd.DataFrame({
        'time': dates,
        'open': [p - np.random.uniform(0.0001, 0.0005) for p in prices],
        'high': [p + np.random.uniform(0.0001, 0.0005) for p in prices],
        'low': [p - np.random.uniform(0.0001, 0.0005) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 5000, 100)
    })
    df.set_index('time', inplace=True)
    
    # 创建交易信号数据
    signals = []
    for i in range(10):
        signal_time = dates[i * 10]
        signal_type = 'buy' if i % 3 == 0 else 'sell' if i % 3 == 1 else 'hold'
        signals.append({
            'timestamp': int(signal_time.timestamp()),
            'signal': signal_type,
            'strength': np.random.randint(20, 100),
            'price': df.loc[signal_time, 'close'] if signal_time in df.index else df['close'].iloc[-1]
        })
    
    # 创建交易历史数据
    trading_history = []
    for i in range(20):
        trade_time = dates[i * 5]
        profit = np.random.normal(0, 10)
        trading_history.append({
            'timestamp': int(trade_time.timestamp()),
            'signal': 'buy' if profit > 0 else 'sell',
            'profit': profit,
            'symbol': 'EURUSD'
        })
    
    # 创建机器学习历史数据
    ml_history = []
    for i in range(50):
        ml_history.append({
            'timestamp': int(dates[i * 2].timestamp()),
            'accuracy': np.random.uniform(0.6, 0.9),
            'predicted_signal': np.random.choice(['buy', 'sell', 'hold']),
            'confidence': np.random.uniform(0.5, 0.95),
            'training_samples': np.random.randint(100, 1000)
        })
    
    # 创建分析数据
    analysis_data = {
        'market_regime': {
            'regime': 'trending',
            'confidence': 0.75,
            'description': '明显的上升趋势'
        },
        'technical_analysis': {
            'rsi': 65.5,
            'macd': 0.0023,
            'macd_signal': 0.0018,
            'macd_histogram': 0.0005,
            'ema_12': 1.1056,
            'ema_26': 1.1042,
            'bb_upper': 1.1089,
            'bb_lower': 1.1012,
            'bb_middle': 1.1050
        },
        'risk_metrics': {
            'volatility': 0.015,
            'max_drawdown': 2.3,
            'sharpe_ratio': 1.2,
            'var_95': 15.6
        },
        'support_resistance': {
            'support_levels': [1.1020, 1.1005, 1.0990],
            'resistance_levels': [1.1075, 1.1090, 1.1105]
        },
        'ml_signal': {
            'signal': 'buy',
            'confidence': 0.82,
            'method': 'random_forest',
            'reason': '模型预测买入信号'
        },
        'final_signal': {
            'signal': 'buy',
            'strength': 78,
            'confidence': 0.75,
            'reasons': ['RSI超买', 'MACD金叉', '价格突破阻力位']
        },
        'symbol': 'EURUSD',
        'timeframe': 'H1'
    }
    
    # 创建综合分析数据
    comprehensive_data = {
        'overall_score': 72,
        'market_condition': '看涨',
        'technical_analysis': {
            '趋势指标': {'ema_12': 1.1056, 'ema_26': 1.1042, '趋势方向': '上升'},
            '动量指标': {'rsi': 65.5, 'macd': 0.0023, '动量': '中等'},
            '波动指标': {'atr': 0.0012, 'bb_width': 0.0077, '波动率': '中等'}
        },
        'machine_learning': {
            'accuracy': 0.78,
            'predicted_signal': 'buy',
            'confidence': 0.82,
            'training_samples': 856
        },
        'risk_assessment': {
            'volatility': 0.015,
            'max_drawdown': 2.3,
            'sharpe_ratio': 1.2
        }
    }
    
    return {
        'price_data': df,
        'signals': signals,
        'trading_history': trading_history,
        'ml_history': ml_history,
        'analysis_data': analysis_data,
        'comprehensive_data': comprehensive_data
    }

def test_visualization_functions():
    """测试所有可视化功能"""
    print("开始测试数据可视化模块...")
    
    # 创建可视化器实例
    visualizer = TradingVisualizer()
    
    # 生成测试数据
    test_data = create_test_data()
    
    # 测试价格图表
    print("1. 测试价格图表...")
    try:
        price_fig = visualizer.create_price_chart(
            test_data['price_data'], 
            test_data['signals'],
            title="测试价格走势图"
        )
        price_file = visualizer.save_figure(price_fig, "test_price_chart")
        print(f"   价格图表保存成功: {price_file}")
    except Exception as e:
        print(f"   价格图表测试失败: {e}")
    
    # 测试技术指标图表
    print("2. 测试技术指标图表...")
    try:
        indicators = test_data['analysis_data']['technical_analysis']
        tech_fig = visualizer.create_technical_indicators_chart(
            test_data['price_data'], 
            indicators
        )
        tech_file = visualizer.save_figure(tech_fig, "test_technical_indicators")
        print(f"   技术指标图表保存成功: {tech_file}")
    except Exception as e:
        print(f"   技术指标图表测试失败: {e}")
    
    # 测试绩效仪表板
    print("3. 测试绩效仪表板...")
    try:
        performance_fig = visualizer.create_performance_dashboard(
            test_data['trading_history']
        )
        performance_file = visualizer.save_figure(performance_fig, "test_performance_dashboard")
        print(f"   绩效仪表板保存成功: {performance_file}")
    except Exception as e:
        print(f"   绩效仪表板测试失败: {e}")
    
    # 测试机器学习性能图表
    print("4. 测试机器学习性能图表...")
    try:
        ml_fig = visualizer.create_ml_performance_chart(test_data['ml_history'])
        ml_file = visualizer.save_figure(ml_fig, "test_ml_performance")
        print(f"   机器学习性能图表保存成功: {ml_file}")
    except Exception as e:
        print(f"   机器学习性能图表测试失败: {e}")
    
    # 测试分析报告生成
    print("5. 测试分析报告生成...")
    try:
        analysis_report = visualizer.generate_analysis_report(test_data['analysis_data'])
        report_file = os.path.join(visualizer.figures_dir, f"test_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(analysis_report)
        print(f"   分析报告保存成功: {report_file}")
        print("   报告内容预览:")
        print("   " + "="*50)
        for line in analysis_report.split('\n')[:10]:
            print(f"   {line}")
        print("   " + "="*50)
    except Exception as e:
        print(f"   分析报告测试失败: {e}")
    
    # 测试综合分析报告
    print("6. 测试综合分析报告...")
    try:
        comprehensive_report = visualizer.generate_comprehensive_report(test_data['comprehensive_data'])
        comp_report_file = os.path.join(visualizer.figures_dir, f"test_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(comp_report_file, 'w', encoding='utf-8') as f:
            f.write(comprehensive_report)
        print(f"   综合分析报告保存成功: {comp_report_file}")
        print("   报告内容预览:")
        print("   " + "="*50)
        for line in comprehensive_report.split('\n')[:15]:
            print(f"   {line}")
        print("   " + "="*50)
    except Exception as e:
        print(f"   综合分析报告测试失败: {e}")
    
    # 测试交互式图表
    print("7. 测试交互式图表...")
    try:
        interactive_fig = visualizer.create_interactive_chart(
            test_data['price_data'], 
            test_data['signals']
        )
        # 保存为HTML文件
        html_file = os.path.join(visualizer.figures_dir, f"test_interactive_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        interactive_fig.write_html(html_file)
        print(f"   交互式图表保存成功: {html_file}")
    except Exception as e:
        print(f"   交互式图表测试失败: {e}")
    
    # 测试实时仪表板
    print("8. 测试实时仪表板...")
    try:
        real_time_data = {
            'price_data': test_data['price_data'].tail(20),
            'indicators': test_data['analysis_data']['technical_analysis'],
            'signal_strength': 78
        }
        dashboard_fig = visualizer.create_real_time_dashboard(real_time_data)
        dashboard_file = os.path.join(visualizer.figures_dir, f"test_realtime_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        dashboard_fig.write_html(dashboard_file)
        print(f"   实时仪表板保存成功: {dashboard_file}")
    except Exception as e:
        print(f"   实时仪表板测试失败: {e}")
    
    print("\n所有可视化功能测试完成！")
    print("生成的图表和报告保存在 'figures' 目录中")

if __name__ == "__main__":
    test_visualization_functions()