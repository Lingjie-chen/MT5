
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
    # Make it a clear range setter, avoiding "Long Wick" filter (limit 500*0.01 = 5.0)
    # High - BodyHigh <= 5.0, BodyLow - Low <= 5.0
    # Open 100, Close 100. BodyHigh 100, BodyLow 100.
    # Max High 105, Min Low 95.
    df.iloc[4] = [100, 105, 95, 100, 100] # High 105, Low 95. Range 95-105.
    
    # Subsequent candles inside range (95-105)
    df.iloc[5] = [100, 104, 96, 102, 100] # Inside
    df.iloc[6] = [102, 103, 97, 98, 100]  # Inside
    df.iloc[7] = [98, 102, 98, 100, 100]  # Inside -> Count should be 3 -> Finalized?
    
    # Create Strategy
    strategy = GoldORBStrategy('GOLD', open_hour=1, consolidation_candles=3)
    
    print("Testing Range Finalization...")
    # Pass data up to 2:00 (index 8)
    subset = df.iloc[:9] 
    high, low, is_final = strategy.calculate_orb_levels(subset)
    
    print(f"High: {high}, Low: {low}, Final: {is_final}")
    print(f"Stats: Mean={strategy.range_mean}, Std={strategy.range_std}")
    
    assert is_final == True
    assert high == 105
    assert low == 95
    assert strategy.range_mean != 0
    
    # Test Breakout
    print("\nTesting Breakout Signal...")
    # Candle 9: Breakout Up
    # Previous High 105. We need Close > 105.
    breakout_candle = pd.Series({'open': 104, 'high': 110, 'low': 103, 'close': 108}, name=dates[9])
    
    # Append breakout candle to DF at index 9 (2:15 AM)
    df.iloc[8] = [104, 110, 103, 108, 100] 
    
    # check_signal looks at the second to last candle of the passed DF (assuming it's the last CLOSED candle).
    # If we want to check signal for the candle at index 8, we need to pass a DF that goes up to index 9 (current open candle).
    # Or simply pass the DF ending at index 8, but check_signal logic is: last_closed_candle = target_df.iloc[-2]
    # So if we want to signal on index 8, we need target_df to have index 8 at iloc[-2]. So target_df must have index 9.
    
    # Let's add a dummy "current open" candle at index 9
    df.iloc[9] = [108, 108, 108, 108, 100] # Current running candle
    
    subset_breakout = df.iloc[:10] # 0..9. iloc[-2] is 8 (Breakout Candle).
    
    signal, stats = strategy.check_signal(108, subset_breakout)
    print(f"Signal: {signal}")
    print(f"Stats: {stats}")
    
    if signal:
        print("Breakout Detected!")
    else:
        print("No Signal (Check logic)")

if __name__ == "__main__":
    test_orb_logic()
