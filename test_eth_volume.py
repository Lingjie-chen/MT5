
import sys
import os
import time
import logging
import MetaTrader5 as mt5
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'trading_bot'))

# Mock dependencies
sys.modules['ai.ai_client_factory'] = MagicMock()
sys.modules['data.mt5_data_processor'] = MagicMock()
sys.modules['data.database_manager'] = MagicMock()
sys.modules['strategies.grid_strategy'] = MagicMock()
sys.modules['strategies.orb_strategy'] = MagicMock()
sys.modules['analysis.smc_validator'] = MagicMock()
sys.modules['position_engine.mt5_adapter'] = MagicMock()
sys.modules['analysis.advanced_analysis'] = MagicMock()
sys.modules['utils.file_watcher'] = MagicMock()
sys.modules['utils.telegram_notifier'] = MagicMock()

from src.trading_bot.main import SymbolTrader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestETH")

class TestTrader(SymbolTrader):
    def __init__(self, symbol):
        self.symbol = symbol
        self.magic_number = 999999
        self.telegram = MagicMock()
        self.telegram.notify_trade = lambda *args, **kwargs: logger.info(f"[TG] Trade: {args} {kwargs}")
        self.telegram.notify_error = lambda *args, **kwargs: logger.error(f"[TG] Error: {args} {kwargs}")

def run_test():
    if not mt5.initialize():
        logger.error("MT5 Init Failed")
        return

    # 1. Find ETH Symbol
    symbol = "ETHUSD"
    if not mt5.symbol_info(symbol):
        # Try variants
        for s in ["ETHUSD.m", "ETHUSD.pro", "Ethereum", "ETHUSDT"]:
            if mt5.symbol_info(s):
                symbol = s
                break
    
    info = mt5.symbol_info(symbol)
    if not info:
        logger.error(f"ETHUSD symbol not found. Available symbols example: {[s.name for s in mt5.symbols_get()[:5]]}")
        return

    if not mt5.symbol_select(symbol, True):
        logger.error(f"Failed to select {symbol}")
        return

    logger.info(f"Testing on Symbol: {info.name}")
    logger.info(f"  Min Volume: {info.volume_min}")
    logger.info(f"  Max Volume: {info.volume_max}")
    logger.info(f"  Volume Step: {info.volume_step}")
    
    trader = TestTrader(symbol)
    
    # 2. Test Normalization Logic for 0.001
    logger.info("\n--- 1. Testing Normalization Logic (0.001) ---")
    
    # Case A: Input 0.001
    vol_001 = trader.normalize_volume(0.001)
    logger.info(f"Input 0.001 -> Normalized: {vol_001}")
    
    if vol_001 == 0.001:
        logger.info("SUCCESS: 0.001 preserved correctly.")
    elif vol_001 == info.volume_min:
         logger.info(f"SUCCESS: 0.001 adjusted to symbol min {info.volume_min}")
    else:
        logger.error(f"FAILURE: 0.001 became {vol_001} (Expected 0.001 or {info.volume_min})")

    # Case B: Input 0.0001 (Too small)
    vol_small = trader.normalize_volume(0.0001)
    logger.info(f"Input 0.0001 -> Normalized: {vol_small}")
    if vol_small == info.volume_min:
        logger.info(f"SUCCESS: 0.0001 clamped to min {info.volume_min}")
    else:
        logger.error(f"FAILURE: 0.0001 became {vol_small}")

    # 3. Execution Test (If market open)
    logger.info("\n--- 2. Testing Execution (Pending Buy Limit) ---")
    # We use a pending order far away to avoid filling, just to test placement
    price = info.ask - 500 * info.point 
    
    order = {
        'type': 'buy_limit',
        'price': price,
        'volume': 0.001,
        'comment': 'Test ETH 0.001'
    }
    
    logger.info(f"Placing Buy Limit @ {price} for 0.001 lots...")
    trader.place_limit_order(order)
    
    time.sleep(1)
    
    # Check if order exists
    orders = mt5.orders_get(symbol=symbol)
    test_order = None
    if orders:
        for o in orders:
            if o.magic == 999999 and abs(o.volume_current - 0.001) < 0.00001:
                test_order = o
                break
    
    if test_order:
        logger.info(f"SUCCESS: Order Placed. Ticket: {test_order.ticket}, Volume: {test_order.volume_current}")
        # Cleanup
        req = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": test_order.ticket,
            "magic": 999999
        }
        mt5.order_send(req)
        logger.info("Test Order Cancelled.")
    else:
        logger.warning("Order not found. (Market might be closed or min volume issue if not 0.001)")
        # Check logs for "Grid Order Failed"

    mt5.shutdown()

if __name__ == "__main__":
    run_test()
