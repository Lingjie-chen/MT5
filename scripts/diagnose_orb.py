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
    
    logger.info(f"Diagnosing ORB for {symbol}")
    
    # Fetch H1 Data
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 100)
    if rates is None:
        logger.error("Failed to fetch rates")
        return
        
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    
    # Initialize Strategy
    # Default params: open_hour=1, consolidation=3
    orb = GoldORBStrategy(symbol, open_hour=1, consolidation_candles=3)
    
    # Run Calculation
    high, low, is_final = orb.calculate_orb_levels(df)
    
    print("\n--- ORB Diagnosis ---")
    print(f"Symbol: {symbol}")
    print(f"Server Time: {mt5.symbol_info_tick(symbol).time}")
    print(f"Current Price: {mt5.symbol_info_tick(symbol).ask}")
    print(f"Config: OpenHour={orb.open_hour}, Consolidation={orb.consolidation_candles}")
    print(f"---------------------")
    print(f"Is Range Finalized? {is_final}")
    print(f"Range High: {high}")
    print(f"Range Low: {low}")
    print(f"Consolidation Count: {orb.current_consolidation_count}")
    print(f"---------------------")
    
    # Check Open Candle
    if orb.last_h1_df is not None:
        df = orb.last_h1_df
        today = df.index[-1].date()
        today_data = df[df.index.date == today]
        open_candle = today_data[today_data.index.hour == orb.open_hour]
        
        print(f"Today: {today}")
        if open_candle.empty:
            print(f"❌ Open Candle (Hour {orb.open_hour}) NOT FOUND in data!")
            print("Available Hours today:", today_data.index.hour.tolist())
        else:
            print(f"✅ Open Candle Found: {open_candle.index[0]}")
            print(f"   Open: {open_candle.iloc[0]['open']}, Close: {open_candle.iloc[0]['close']}")
            print(f"   High: {open_candle.iloc[0]['high']}, Low: {open_candle.iloc[0]['low']}")
            
            # Show subsequent candles
            subsequent = today_data[today_data.index > open_candle.index[0]]
            print("\nSubsequent Candles Check:")
            for t, row in subsequent.iterrows():
                print(f"   {t.hour}:00 | H:{row['high']} L:{row['low']} | vs Range H:{orb.final_range_high} L:{orb.final_range_low}")

    mt5.shutdown()

if __name__ == "__main__":
    diagnose_orb()
