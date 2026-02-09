import sys
import os
import logging
import pandas as pd
from unittest.mock import MagicMock

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Mock MT5
sys.modules['MetaTrader5'] = MagicMock()

from trading_bot.analysis.trade_performance_analyzer import TradePerformanceAnalyzer
from trading_bot.analysis.advanced_analysis import AdvancedMarketAnalysis

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def verify_optimization():
    print("=== 验证大模型交易策略全面优化模块 ===\n")

    # 1. 验证交易记录分析系统 (Trade Performance Analyzer)
    print("[1] 验证交易记录分析系统...")
    analyzer = TradePerformanceAnalyzer()
    
    # 模拟历史交易数据
    mock_trades = [
        {'profit': 50, 'type': 'buy', 'reason': 'Trend', 'open_time': '2023-10-01 10:00:00'},
        {'profit': -20, 'type': 'buy', 'reason': 'Trend', 'open_time': '2023-10-01 14:00:00'}, # Loss at 14:00
        {'profit': -30, 'type': 'sell', 'reason': 'Reversal', 'open_time': '2023-10-02 14:30:00'}, # Loss at 14:00
        {'profit': 100, 'type': 'buy', 'reason': 'SMC', 'open_time': '2023-10-03 09:00:00'}
    ]
    
    analysis = analyzer.analyze_trades(mock_trades)
    
    print(f"   - Win Rate: {analysis['metrics']['win_rate']}%")
    print(f"   - Risky Hours Identified: {analysis['loss_analysis'].get('risky_hours')}")
    
    if analysis['metrics']['win_rate'] == 50.0 and 14 in analysis['loss_analysis']['risky_hours']:
        print("   ✅ 交易分析逻辑验证通过")
    else:
        print("   ❌ 交易分析逻辑异常")

    # 2. 验证价格区间评估模型 (Optimal Entry Zones)
    print("\n[2] 验证价格区间评估模型 (OEZ)...")
    ama = AdvancedMarketAnalysis()
    
    # 模拟 M15 数据 (构造一个简单的摆动结构)
    # 扩展数据长度到 60 以通过 len(df) < 50 检查
    close_prices = [100 + i%10 for i in range(60)] # Dummy
    df = pd.DataFrame({
        'close': close_prices,
        'high': [c + 2 for c in close_prices],
        'low': [c - 2 for c in close_prices],
        'open': close_prices,
        'volume': [100]*60
    })
    
    # Mock SMC Data
    smc_data = {
        'details': {
            'ob': {'active_obs': [{'type': 'bullish', 'top': 102, 'bottom': 100}]},
            'fvg': {'active_fvgs': []}
        }
    }
    
    # 注入 detect_structure_points 的 Mock 返回 (因为 df 太短，真实算法可能算不出)
    ama.detect_structure_points = MagicMock(return_value=[
        {'type': 'SL', 'price': 100},
        {'type': 'SH', 'price': 115}
    ])
    
    oez = ama.identify_optimal_entry_zones(df, smc_data)
    
    zones = oez.get('zones', [])
    print(f"   - Identified Zones: {len(zones)}")
    for z in zones:
        print(f"     * {z['name']} ({z['type']}): {z['bottom']} - {z['top']}")
        
    has_golden = any(z['name'] == 'Golden Pocket' for z in zones)
    has_ob = any(z['name'] == 'Order Block' for z in zones)
    
    if has_golden and has_ob:
        print("   ✅ 价格区间评估模型验证通过")
    else:
        print("   ❌ 未能识别出预期的 Golden Pocket 或 Order Block")

if __name__ == "__main__":
    verify_optimization()
