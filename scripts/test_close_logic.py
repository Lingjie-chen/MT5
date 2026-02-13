import MetaTrader5 as mt5
import time
import sys
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("TestClose")

def test_close_position():
    if not mt5.initialize():
        print("MT5 Init Failed")
        return

    # 1. Get Open Positions
    positions = mt5.positions_get()
    if not positions:
        print("No open positions found to test closing.")
        mt5.shutdown()
        return

    # 2. Pick the first position
    pos = positions[0]
    symbol = pos.symbol
    ticket = pos.ticket
    vol = pos.volume
    type_str = "BUY" if pos.type == mt5.POSITION_TYPE_BUY else "SELL"
    
    print(f"Attempting to close Position #{ticket} ({type_str} {vol} {symbol})...")
    
    # 3. Determine Price
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        print("Failed to get tick")
        return
        
    price = tick.bid if pos.type == mt5.POSITION_TYPE_BUY else tick.ask
    
    # 4. Try Closing with Robust Logic (Simulating main.py)
    filling_modes = [mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN]
    
    success = False
    for mode in filling_modes:
        print(f"Trying Filling Mode: {mode}...")
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(vol),
            "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": int(ticket),
            "price": float(price),
            "deviation": 50,
            "magic": pos.magic,
            "comment": "Test Close Script",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mode,
        }
        
        result = mt5.order_send(request)
        
        if result is None:
            print(f"Result is None. Error: {mt5.last_error()}")
            continue
            
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"SUCCESS! Position Closed. Price: {result.price}")
            success = True
            break
        else:
            print(f"Failed with mode {mode}: {result.comment} ({result.retcode})")
            
    if not success:
        print("All attempts failed.")
    
    mt5.shutdown()

if __name__ == "__main__":
    test_close_position()
