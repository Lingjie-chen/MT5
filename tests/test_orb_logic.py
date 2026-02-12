
import pandas as pd
import numpy as np
import logging
from src.trading_bot.strategies.orb_strategy import GoldORBStrategy

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_orb_logic():
    # Create synthetic M15 data
    # 1:00 AM Open Candle
    dates = pd.date_range(start='2023-10-27 00:00', periods=20, freq='15min')
    data = {
        'open': [100]*20,
        'high': [105]*20,
        'low': [95]*20,
        'close': [100]*20,
        'tick_volume': [100]*20
    }
    df = pd.DataFrame(data, index=dates)
    
    # 1:00 AM candle (index 4)
    # Make it a clear range setter
    df.iloc[4] = [100, 110, 90, 100, 100] # High 110, Low 90
    
    # Subsequent candles inside range
    df.iloc[5] = [100, 105, 95, 102, 100] # Inside
    df.iloc[6] = [102, 108, 92, 98, 100]  # Inside
    df.iloc[7] = [98, 104, 96, 100, 100]  # Inside -> Count should be 3 -> Finalized?
    
    # Create Strategy
    strategy = GoldORBStrategy('GOLD', open_hour=1, consolidation_candles=3)
    
    print("Testing Range Finalization...")
    # Pass data up to 2:00 (index 8)
    subset = df.iloc[:9] 
    high, low, is_final = strategy.calculate_orb_levels(subset)
    
    print(f"High: {high}, Low: {low}, Final: {is_final}")
    print(f"Stats: Mean={strategy.range_mean}, Std={strategy.range_std}")
    
    assert is_final == True
    assert high == 110
    assert low == 90
    assert strategy.range_mean != 0
    
    # Test Breakout
    print("\nTesting Breakout Signal...")
    # Candle 9: Breakout Up
    breakout_candle = pd.Series({'open': 105, 'high': 115, 'low': 100, 'close': 112}, name=dates[9])
    
    # Check signal needs dataframe passed or stored
    # We pass the full DF including the breakout candle as "current data" context? 
    # check_signal takes current_price.
    # But it looks at the last closed candle of the DF passed.
    
    # Append breakout candle to DF
    df.iloc[8] = [105, 115, 100, 112, 100] # Breakout at 2:00
    
    # We need to pass the DF where the last candle is the breakout candle
    # And check_signal checks the second to last candle?
    # No, check_signal: last_closed_candle = target_df.iloc[-2]
    # So if we pass DF with 9 candles, it checks candle 7 (1:45).
    # If we pass DF with 10 candles (up to 2:15), it checks candle 8 (2:00).
    
    subset_breakout = df.iloc[:10] # 0..9. iloc[-2] is 8 (2:00).
    
    signal, stats = strategy.check_signal(112, subset_breakout)
    print(f"Signal: {signal}")
    print(f"Stats: {stats}")
    
    if signal:
        print("Breakout Detected!")
    else:
        print("No Signal (Check logic)")

if __name__ == "__main__":
    test_orb_logic()
