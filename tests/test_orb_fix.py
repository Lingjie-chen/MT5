
import sys
import os
import pandas as pd
import logging
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from trading_bot.strategies.orb_strategy import GoldORBStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestORBFix")

def test_orb_fixes():
    logger.info("Starting ORB Fix Verification...")
    
    orb = GoldORBStrategy(symbol="XAUUSD")
    # Assume Open Hour is 1 (01:00)
    orb.open_hour = 1
    
    # --- Test Case 1: Data Slicing Logic ---
    logger.info("\n[Test Case 1] Verifying Data Slicing Logic (Single Row)")
    
    # Create a DataFrame with ONLY the open candle (simulating data just arrived)
    # 2026-02-13 01:00:00
    date_str = "2026-02-13 01:00:00"
    df_single = pd.DataFrame({
        'time': [pd.to_datetime(date_str)],
        'open': [2000.0],
        'high': [2010.0],
        'low': [1990.0],
        'close': [2005.0],
        'tick_volume': [100]
    })
    
    # The fix should prevent iloc[:-1] from killing this single row
    # We expect calculate_orb_levels to NOT return None (or at least find the candle)
    # Note: calculate_orb_levels might return None for stats if not enough candles for consolidation,
    # but we are checking if it *finds* the open candle.
    
    # However, calculate_orb_levels is a bit complex. Let's inspect the internal logic or result.
    # If slicing killed it, open_candle would be empty.
    
    orb.calculate_orb_levels(df_single)
    
    # Check if warning was logged (we can't easily check logger output programmatically without capturing, 
    # but we can check internal state or if it crashed).
    # If the fix works, 'completed_df' inside should have 1 row.
    # We can check orb.last_warning_date. If it found the candle, it shouldn't log "Open Candle not found".
    # Wait, if we only have the open candle, subsequent_candles will be empty, so is_range_final will be False.
    # But it should NOT log "ORB Open Candle not found".
    
    if orb.last_warning_date == pd.to_datetime("2026-02-13").date():
        print("❌ Test Case 1 Failed: It warned 'Open Candle not found' (Slicing likely killed the row)")
    else:
        print("✅ Test Case 1 Passed: No 'Open Candle not found' warning for single row data.")

    # --- Test Case 2: Logging Logic (Warning -> Success) ---
    logger.info("\n[Test Case 2] Verifying Logging Logic (Warning -> Success)")
    
    # 2.1 Trigger Warning first
    # Send data BEFORE open hour (e.g. 00:00 only)
    df_early = pd.DataFrame({
        'time': [pd.to_datetime("2026-02-13 00:00:00")],
        'open': [2000.0], 'high': [2005.0], 'low': [1995.0], 'close': [2000.0], 'tick_volume': [100]
    })
    
    orb.calculate_orb_levels(df_early)
    
    # Should have triggered warning
    today = pd.to_datetime("2026-02-13").date()
    if orb.last_warning_date == today:
        print("   Step 2.1: Warning correctly triggered for missing data.")
    else:
        print(f"   Step 2.1 Failed: Warning not triggered. Last warning: {orb.last_warning_date}")

    # 2.2 Now send Full Data (Success)
    # We need enough candles for consolidation (default 3) + 1 buffer (slicing)
    # 01:00 (Open)
    # 02:00 (C1)
    # 03:00 (C2)
    # 04:00 (C3) -> Range Finalized here
    # 05:00 (Buffer)
    
    dates = [
        "2026-02-13 00:00:00",
        "2026-02-13 01:00:00", # Open
        "2026-02-13 02:00:00",
        "2026-02-13 03:00:00",
        "2026-02-13 04:00:00",
        "2026-02-13 05:00:00"
    ]
    
    df_full = pd.DataFrame({
        'time': [pd.to_datetime(d) for d in dates],
        'open': [2000] * 6,
        'high': [2010] * 6, # High 2010
        'low':  [1990] * 6, # Low 1990
        'close':[2005] * 6, # Close inside range
        'tick_volume': [100] * 6
    })
    
    orb.calculate_orb_levels(df_full)
    
    # Should now be successful. 
    # OLD BUG: last_processed_time was set by warning, so success log blocked.
    # NEW FIX: last_success_date is separate.
    
    if orb.last_success_date == today:
        print("✅ Test Case 2 Passed: Success state correctly updated after previous warning.")
    else:
        print(f"❌ Test Case 2 Failed: Success state NOT updated. last_success_date: {orb.last_success_date}")

if __name__ == "__main__":
    test_orb_fixes()
