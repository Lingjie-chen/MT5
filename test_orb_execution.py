
import sys
import os
import time
import logging
import MetaTrader5 as mt5
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src', 'trading_bot'))

# Mock dependencies to allow importing SymbolTrader without side effects
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

# Now import main
from src.trading_bot.main import SymbolTrader

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestExecution")

class TestTrader(SymbolTrader):
    def __init__(self, symbol):
        self.symbol = symbol
        self.magic_number = 999999 # Test Magic
        
        # Mock Telegram
        self.telegram = MagicMock()
        self.telegram.notify_trade = lambda *args, **kwargs: logger.info(f"[TG] Trade: {args} {kwargs}")
        self.telegram.notify_error = lambda *args, **kwargs: logger.error(f"[TG] Error: {args} {kwargs}")
        self.telegram.notify_basket_close = lambda *args, **kwargs: logger.info(f"[TG] Close: {args} {kwargs}")
        
    # We inherit normalize_volume, execute_trade, close_positions from SymbolTrader

def run_test():
    if not mt5.initialize():
        logger.error("MT5 Init Failed")
        return

    symbol = "GOLD"
    
    # Check if symbol exists
    if not mt5.symbol_info(symbol):
        logger.error(f"Symbol {symbol} not found")
        return
        
    trader = TestTrader(symbol)
    
    # 1. Test Normalization Logic directly
    logger.info("--- 1. Testing Normalization Logic ---")
    vol_001 = trader.normalize_volume(0.001)
    logger.info(f"Input 0.001 -> Normalized: {vol_001}")
    
    if vol_001 == 0.01:
        logger.info("SUCCESS: 0.001 normalized to min volume 0.01")
    else:
        logger.warning(f"WARNING: 0.001 normalized to {vol_001} (Expected 0.01)")

    # 2. Test Execution
    logger.info("\n--- 2. Testing Execution (Buy 0.001 -> 0.01) ---")
    
    # Check for existing test positions and close them
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        test_pos = [p for p in positions if p.magic == 999999]
        if test_pos:
            logger.info(f"Closing {len(test_pos)} existing test positions...")
            trader.close_positions(test_pos, mt5.POSITION_TYPE_BUY, "Cleanup")
            trader.close_positions(test_pos, mt5.POSITION_TYPE_SELL, "Cleanup")
            time.sleep(1)

    # Execute Trade
    trader.execute_trade('buy', 0.001, 0, 0, "Test 0.001")
    
    # Verify
    time.sleep(1)
    positions = mt5.positions_get(symbol=symbol)
    test_pos = [p for p in positions if p.magic == 999999]
    
    if test_pos:
        logger.info(f"SUCCESS: Trade Placed. Ticket: {test_pos[0].ticket}, Volume: {test_pos[0].volume}")
        
        # 3. Test Closing
        logger.info("\n--- 3. Testing Closing ---")
        trader.close_positions(test_pos, mt5.POSITION_TYPE_BUY, "Test End")
        
        time.sleep(1)
        positions_after = mt5.positions_get(symbol=symbol)
        test_pos_after = [p for p in positions_after if p.magic == 999999]
        
        if not test_pos_after:
            logger.info("SUCCESS: Position Closed.")
        else:
            logger.error("FAILURE: Position NOT Closed.")
            
    else:
        logger.error("FAILURE: Trade NOT Placed.")

    mt5.shutdown()

if __name__ == "__main__":
    run_test()
