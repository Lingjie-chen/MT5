import sys
import os
import time
import logging
import MetaTrader5 as mt5

# Adjust path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
src_dir = os.path.join(project_root, 'src', 'trading_bot')
sys.path.append(src_dir)

from src.trading_bot.main import SymbolTrader

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("TestClose")

def test_position_close():
    # 1. Initialize Bot
    if not mt5.initialize():
        logger.error("MT5 Initialize Failed")
        return

    # 2. Setup Symbol
    target_symbol = "XAUUSD"
    # Try to find symbol if not XAUUSD
    if not mt5.symbol_info(target_symbol):
        symbols = mt5.symbols_get()
        for s in symbols:
            if "XAU" in s.name.upper() or "GOLD" in s.name.upper():
                target_symbol = s.name
                break
    
    logger.info(f"Target Symbol: {target_symbol}")
    if not mt5.symbol_select(target_symbol, True):
        logger.error(f"Failed to select {target_symbol}")
        return

    bot = SymbolTrader(target_symbol)
    bot.symbol = target_symbol
    
    # 3. Place Market Order (Buy 0.01)
    logger.info("Placing Market Buy Order (0.01 lots)...")
    
    tick = mt5.symbol_info_tick(target_symbol)
    if not tick:
        logger.error("Failed to get tick")
        return

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": target_symbol,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY,
        "price": tick.ask,
        "sl": 0.0,
        "tp": 0.0,
        "deviation": 20,
        "magic": bot.magic_number,
        "comment": "Test Open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Market Order Failed: {result.comment} ({result.retcode})")
        return
        
    logger.info(f"Market Order Opened: #{result.order}")
    
    # Wait for position to settle
    time.sleep(2)
    
    # 4. Fetch Position
    positions = mt5.positions_get(ticket=result.order)
    if not positions:
        logger.error(f"Position #{result.order} not found!")
        return
        
    logger.info(f"Position Found: {positions[0].ticket}. Attempting to close using SymbolTrader.close_positions...")
    
    # 5. Close Position using Bot Logic
    # We simulate what check_grid_exit passes to close_positions
    # close_positions(self, positions, type_filter, reason)
    
    # Passing all positions, but we filter by our specific type
    # Since we opened a BUY, type is POSITION_TYPE_BUY (0)
    
    try:
        bot.close_positions(
            positions=positions, 
            type_filter=mt5.POSITION_TYPE_BUY, 
            reason="Test Close Logic"
        )
    except Exception as e:
        logger.error(f"Exception during close_positions: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Verify Closure
    time.sleep(1)
    check_pos = mt5.positions_get(ticket=result.order)
    if not check_pos:
        logger.info("SUCCESS: Position closed successfully.")
    else:
        logger.error("FAILURE: Position still exists!")

    mt5.shutdown()

if __name__ == "__main__":
    test_position_close()
