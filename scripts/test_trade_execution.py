import sys
import os
import time
import logging
from datetime import datetime

# Adjust path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
src_dir = os.path.join(project_root, 'src', 'trading_bot')
sys.path.append(src_dir)

import MetaTrader5 as mt5
from src.trading_bot.main import SymbolTrader

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TestTrade")

def test_trade_execution():
    """
    Simulate a trading signal to verify execution logic.
    WARNING: This will attempt to place a pending order (Limit) to avoid market loss.
    """
    # 1. Initialize Bot (without symbol first to check connection)
    if not mt5.initialize():
        logger.error("MT5 Initialize Failed")
        return

    logger.info("MT5 Initialized Successfully")
    
    # 2. Check Available Symbols
    symbols = mt5.symbols_get()
    found_symbols = []
    target_symbol = "XAUUSD"
    
    if symbols:
        count = 0
        for s in symbols:
            if "XAU" in s.name.upper() or "GOLD" in s.name.upper():
                found_symbols.append(s.name)
                logger.info(f"Found Potential Symbol: {s.name} (Path: {s.path})")
            
    if not found_symbols:
        logger.error("No Gold/XAU symbols found in Market Watch! Please add XAUUSD or GOLD to Market Watch in MT5.")
        mt5.shutdown()
        return
        
    # Prefer XAUUSD if available, otherwise take the first one
    if "XAUUSD" in found_symbols:
        target_symbol = "XAUUSD"
    else:
        target_symbol = found_symbols[0]
        logger.warning(f"XAUUSD not found, using {target_symbol} instead.")

    logger.info(f"Using Target Symbol: {target_symbol}")
    
    # 3. Initialize Bot with Correct Symbol
    bot = SymbolTrader(target_symbol)
    # Re-init bot logic (it calls mt5.initialize inside but that's fine)
    # We manually set the symbol
    bot.symbol = target_symbol

    # 4. Get Current Price
    # Ensure symbol is selected in Market Watch
    if not mt5.symbol_select(target_symbol, True):
        logger.error(f"Failed to select {target_symbol}")
        mt5.shutdown()
        return

    tick = mt5.symbol_info_tick(target_symbol)
    if tick is None:
        logger.error(f"Failed to get tick for {target_symbol} - Check Internet Connection or Market Hours")
        last_error = mt5.last_error()
        logger.error(f"MT5 Error Code: {last_error}")
        mt5.shutdown()
        return
        
    current_price = tick.ask
    logger.info(f"Current Price for {target_symbol}: {current_price}")
    
    # 5. Simulate ORB Signal (Mock)
    test_price = current_price - 50.0 # Buy Limit far below current price
    test_sl = test_price - 10.0
    test_tp = test_price + 20.0
    test_lot = 0.01
    
    logger.info(f"Attempting to place TEST Buy Limit at {test_price}...")
    
    request = {
        "action": mt5.TRADE_ACTION_PENDING, # Pending Order for safety
        "symbol": target_symbol,
        "volume": test_lot,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": test_price,
        "sl": test_sl,
        "tp": test_tp,
        "deviation": 20,
        "magic": bot.magic_number,
        "comment": "Test Execution",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    
    logger.info(f"Sending Order Request: {request}")
    result = mt5.order_send(request)
    
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Order Send Failed: {result.comment} ({result.retcode})")
        logger.error("Possible reasons: Algo Trading disabled, Invalid Volume, or Market Closed.")
    else:
        logger.info(f"Order Placed Successfully! Ticket: {result.order}")
        logger.info("Waiting 5 seconds before cleaning up...")
        time.sleep(5)
        
        # Cleanup - Delete the test order
        delete_request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": result.order,
            "magic": bot.magic_number,
        }
        del_res = mt5.order_send(delete_request)
        if del_res.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Test Order {result.order} Deleted Successfully.")
        else:
            logger.warning(f"Failed to delete test order: {del_res.comment}")

    mt5.shutdown()

if __name__ == "__main__":
    test_trade_execution()
