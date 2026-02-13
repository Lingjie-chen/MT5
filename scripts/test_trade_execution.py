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
    symbol = "XAUUSD"
    
    # 1. Initialize Bot
    logger.info("Initializing Bot for Test...")
    bot = SymbolTrader(symbol)
    if not bot.initialize():
        logger.error("Bot initialization failed!")
        return

    # 2. Get Current Price
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        logger.error(f"Failed to get tick for {symbol}")
        return
        
    current_price = tick.ask
    logger.info(f"Current Price: {current_price}")
    
    # 3. Simulate ORB Signal (Mock)
    # We will force a 'buy' signal logic manually to test execution flow
    # Instead of waiting for market, we call execute_trade directly with a Limit Order far away
    
    test_price = current_price - 50.0 # Buy Limit far below current price
    test_sl = test_price - 10.0
    test_tp = test_price + 20.0
    test_lot = 0.01
    
    logger.info(f"Attempting to place TEST Buy Limit at {test_price}...")
    
    # Custom Limit Order Execution (Since main.py executes Market Orders mostly)
    # We'll use the bot's execute_trade method but modify it slightly or call order_send directly
    # To test the EXACT path in main.py, we need to mock the signal handling.
    
    # Let's inject a fake signal into handle_orb_signal? 
    # No, handle_orb_signal does validation which might fail if data isn't there.
    
    # Best way: Direct call to bot.execute_trade with a safe LIMIT order type
    
    request = {
        "action": mt5.TRADE_ACTION_PENDING, # Pending Order for safety
        "symbol": symbol,
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
