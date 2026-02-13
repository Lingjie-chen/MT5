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
logger = logging.getLogger("TestBasketClose")

MAGIC_NUMBER = 888888

def initialize_mt5():
    if not mt5.initialize():
        logger.error("MT5 Initialize Failed")
        return False
    return True

def get_target_symbol():
    target_symbol = "XAUUSD"
    if not mt5.symbol_info(target_symbol):
        symbols = mt5.symbols_get()
        for s in symbols:
            if "XAU" in s.name.upper() or "GOLD" in s.name.upper():
                target_symbol = s.name
                break
    return target_symbol

def open_grid_positions(symbol, count=2):
    logger.info(f"Opening {count} positions for {symbol} (Magic: {MAGIC_NUMBER})...")
    
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        logger.error(f"Symbol {symbol} not found")
        return []

    if not mt5.symbol_select(symbol, True):
        logger.error(f"Failed to select {symbol}")
        return []
        
    filling_mode = mt5.ORDER_FILLING_FOK
    if symbol_info.filling_mode & 2:
        filling_mode = mt5.ORDER_FILLING_IOC
    elif symbol_info.filling_mode & 1:
        filling_mode = mt5.ORDER_FILLING_FOK

    tickets = []
    for i in range(count):
        tick = mt5.symbol_info_tick(symbol)
        if not tick:
            continue
            
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": 0.01,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick.ask,
            "sl": 0.0,
            "tp": 0.0,
            "deviation": 20,
            "magic": MAGIC_NUMBER,
            "comment": f"Grid Test {i+1}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        result = mt5.order_send(request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Opened Position #{result.order}")
            tickets.append(result.order)
        else:
            logger.error(f"Failed to open position: {result.comment}")
            
        time.sleep(1) # Spacing
        
    return tickets

def test_basket_trigger(symbol):
    logger.info("Starting Basket Trigger Test...")
    
    # Initialize Bot
    bot = SymbolTrader(symbol)
    bot.magic_number = MAGIC_NUMBER
    # Ensure strategy has same magic
    bot.grid_strategy.magic_number = MAGIC_NUMBER
    
    # FORCE TRIGGER: Set global_tp to a large negative number
    # This ensures (current_profit >= global_tp) is TRUE even if we are losing money (spread)
    logger.info("Forcing Global TP to -10000.0 to trigger immediate Basket Close...")
    bot.grid_strategy.global_tp = -10000.0
    
    # Get current price for evaluation
    tick = mt5.symbol_info_tick(symbol)
    if not tick:
        logger.error("Failed to get tick for evaluation")
        return
        
    # Execute Logic
    logger.info("Calling manage_positions()...")
    bot.manage_positions(tick.ask)
    
    # Verify
    time.sleep(2)
    positions = mt5.positions_get(symbol=symbol)
    active_grid_positions = [p for p in positions if p.magic == MAGIC_NUMBER] if positions else []
    
    if not active_grid_positions:
        logger.info("SUCCESS: All grid positions closed via Basket Logic!")
    else:
        logger.error(f"FAILURE: {len(active_grid_positions)} positions still remain!")
        for p in active_grid_positions:
            logger.info(f" - Remaining: #{p.ticket} Profit: {p.profit}")

def main():
    if not initialize_mt5():
        return
        
    symbol = get_target_symbol()
    logger.info(f"Target Symbol: {symbol}")
    
    # 1. Open Positions
    tickets = open_grid_positions(symbol, count=3)
    if not tickets:
        logger.error("No positions opened, aborting test.")
        mt5.shutdown()
        return
        
    time.sleep(2)
    
    # 2. Trigger Close
    test_basket_trigger(symbol)
    
    mt5.shutdown()

if __name__ == "__main__":
    main()
