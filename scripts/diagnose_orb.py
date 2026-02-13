import sys
import os
import pandas as pd
import MetaTrader5 as mt5
import logging

# Adjust path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
src_dir = os.path.join(project_root, 'src', 'trading_bot')
sys.path.append(src_dir)

from src.trading_bot.strategies.orb_strategy import GoldORBStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DiagnoseORB")

def diagnose_orb():
    if not mt5.initialize():
        logger.error("MT5 Init Failed")
        return

    symbol = "XAUUSD"
    # Find symbol
    if not mt5.symbol_info(symbol):
        for s in mt5.symbols_get():
            if "XAU" in s.name.upper() or "GOLD" in s.name.upper():
                symbol = s.name
                break
    
    logger.info(f"Diagnosing ORB for {symbol} (M15)")
    
    # Fetch M15 Data
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 200) # Fetch 200 M15 candles
    if rates is None:
        logger.error("Failed to fetch rates")
        return
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Initialize Strategy
    # Default params: open_hour=1, consolidation=3 (Now means 3 M15 candles = 45 mins)
    orb = GoldORBStrategy(symbol, open_hour=1, consolidation_candles=3)
    
    # Run Calculation
    high, low, is_final = orb.calculate_orb_levels(df)
    
    print("\n--- ORB Diagnosis ---")
    print(f"Symbol: {symbol}")
    print(f"Server Time: {mt5.symbol_info_tick(symbol).time}")
    print(f"Current Price: {mt5.symbol_info_tick(symbol).ask}")
    print(f"Config: OpenHour={orb.open_hour}, Consolidation={orb.consolidation_candles} (M15 Bars)")
    print(f"---------------------")
    print(f"Is Range Finalized? {is_final}")
    print(f"Range High: {high}")
    print(f"Range Low: {low}")
    print(f"Consolidation Count: {orb.current_consolidation_count}")
    print(f"---------------------")
    
    # Check Open Candle
    if orb.last_h1_df is not None:
        df = orb.last_h1_df
        # Ensure time index
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
        elif not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, unit='s')
            
        today = df.index[-1].date()
        today_data = df[df.index.date == today]
        
        # Check specific open candle
        from datetime import time as dtime
        target_time = dtime(orb.open_hour, 0)
        open_candle = today_data[today_data.index.time == target_time]
        
        print(f"Today: {today}")
        if open_candle.empty:
            print(f"❌ Open Candle (Time {target_time}) NOT FOUND in data!")
        else:
            print(f"✅ Open Candle Found: {open_candle.index[0]}")
            print(f"   Open: {open_candle.iloc[0]['open']}, Close: {open_candle.iloc[0]['close']}")
            print(f"   High: {open_candle.iloc[0]['high']}, Low: {open_candle.iloc[0]['low']}")
            
            # Show subsequent candles
            subsequent = today_data[today_data.index >= open_candle.index[0]].head(orb.consolidation_candles + 3)
            print("\nSubsequent Candles Check:")
            for t, row in subsequent.iterrows():
                h_mark = "H_MAX" if high and row['high'] == high else ""
                l_mark = "L_MIN" if low and row['low'] == low else ""
                print(f"   {t.time()} | H:{row['high']} L:{row['low']} | {h_mark} {l_mark}")

    mt5.shutdown()

if __name__ == "__main__":
    diagnose_orb()
