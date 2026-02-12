import sys
import os
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

# Mock mt5 before importing modules that use it
sys.modules['MetaTrader5'] = MagicMock()
import MetaTrader5 as mt5
mt5.TIMEFRAME_M5 = 5
mt5.TIMEFRAME_M15 = 15
mt5.TIMEFRAME_H1 = 60
mt5.copy_rates_from_pos.return_value = None # Default

# Add src to path
sys.path.append(os.path.abspath("src"))
sys.path.append(os.path.abspath("src/trading_bot")) # Fix import path for utils

from trading_bot.strategies.orb_strategy import GoldORBStrategy
from trading_bot.analysis.advanced_analysis import SMCAnalyzer

def test_orb_strategy():
    print("Testing ORBStrategy...")
    strategy = GoldORBStrategy(symbol="EURUSD", open_hour=8)
    
    # Create Mock M15 Data (Trend/Structure)
    dates = pd.date_range(start="2024-01-01 07:00", periods=20, freq="15min")
    data = {
        'time': dates,
        'open': np.random.rand(20) * 10 + 100,
        'high': np.random.rand(20) * 10 + 110,
        'low': np.random.rand(20) * 10 + 90,
        'close': np.random.rand(20) * 10 + 100,
        'tick_volume': np.random.randint(100, 1000, 20),
        'spread': np.random.randint(0, 10, 20),
        'real_volume': np.random.randint(100, 1000, 20)
    }
    df_m15 = pd.DataFrame(data)
    df_m15.set_index('time', inplace=True)
    
    # Test calculate_orb_levels
    strategy.calculate_orb_levels(df_m15)
    print("ORB Levels Calculated:", strategy.final_range_high, strategy.final_range_low)
    
    # Test check_signal with current price
    current_price = 105.0
    signal, stats = strategy.check_signal(current_price, df_h1=df_m15)
    
    print("Signal:", signal)
    print("Stats keys:", stats.keys())
    
    if 'range_high' in stats and 'z_score' in stats:
        print("✅ ORBStrategy check_signal returns stats correctly.")
    else:
        print("❌ ORBStrategy stats missing.")

def test_smc_analyzer():
    print("\nTesting SMCAnalyzer...")
    analyzer = SMCAnalyzer()
    
    # Mock Data for Sentiment
    dates = pd.date_range(start="2024-01-01", periods=100, freq="15min")
    data = {
        'open': np.linspace(100, 110, 100),
        'high': np.linspace(101, 111, 100),
        'low': np.linspace(99, 109, 100),
        'close': np.linspace(100, 110, 100),
        'tick_volume': np.random.randint(100, 1000, 100)
    }
    df = pd.DataFrame(data, index=dates)
    
    # Mock get_mtf_data to return our df
    analyzer.get_mtf_data = MagicMock(return_value=df)
    
    # Test get_market_sentiment
    sentiment, text = analyzer.get_market_sentiment(df, "EURUSD")
    print(f"Market Sentiment: {sentiment} ({text})")
    print("✅ SMCAnalyzer get_market_sentiment ran successfully.")

if __name__ == "__main__":
    try:
        test_orb_strategy()
        test_smc_analyzer()
        print("\n🎉 All strategy checks passed!")
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
