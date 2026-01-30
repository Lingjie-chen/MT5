
import MetaTrader5 as mt5
import datetime
import time

def check_sessions():
    if not mt5.initialize():
        print(f"MT5 initialize failed: {mt5.last_error()}")
        return

    print(f"Local Machine Time: {datetime.datetime.now()}")
    print(f"MT5 Server Time: {mt5.symbol_info_tick('EURUSD').time if mt5.symbol_info_tick('EURUSD') else 'N/A'}")
    
    symbols = ["EURUSD", "GOLD"]
    
    for symbol in symbols:
        print(f"\n--- {symbol} Trading Sessions (Server Time) ---")
        # 0=Sunday, 1=Monday, ... 6=Saturday
        for day in range(7):
            sessions = mt5.symbol_info_session_trade(symbol, day)
            if sessions:
                print(f"Day {day}:")
                for i, session in enumerate(sessions):
                    print(f"  Session {i}: {session.start.strftime('%H:%M')} - {session.end.strftime('%H:%M')}")
            else:
                print(f"Day {day}: No trading")

    mt5.shutdown()

if __name__ == "__main__":
    check_sessions()
