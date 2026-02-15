
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
logger = logging.getLogger("TestETH_ORB")

class TestTrader(SymbolTrader):
    def __init__(self, symbol):
        self.symbol = symbol
        self.magic_number = 999999
        self.telegram = MagicMock()
        self.telegram.notify_trade = lambda *args, **kwargs: logger.info(f"[TG] Trade: {args} {kwargs}")
        self.telegram.notify_error = lambda *args, **kwargs: logger.error(f"[TG] Error: {args} {kwargs}")
        self.telegram.notify_basket_close = lambda *args, **kwargs: logger.info(f"[TG] Close: {args} {kwargs}")

def run_test():
    if not mt5.initialize():
        logger.error("MT5 Init Failed")
        return

    # 1. Find ETH Symbol
    symbol = "ETHUSD"
    if not mt5.symbol_info(symbol):
        for s in ["ETHUSD.m", "ETHUSD.pro", "Ethereum", "ETHUSDT"]:
            if mt5.symbol_info(s):
                symbol = s
                break
    
    info = mt5.symbol_info(symbol)
    if not info:
        logger.error("ETHUSD symbol not found.")
        return

    logger.info(f"Testing ORB Execution on Symbol: {info.name}")
    logger.info(f"  Min Volume: {info.volume_min}")
    logger.info(f"  Step: {info.volume_step}")
    
    trader = TestTrader(symbol)
    
    # 2. Execute Market Order (Simulate ORB Trigger)
    logger.info("\n--- Executing Market Buy (0.001 lots) ---")
    
    # Ensure no existing test positions
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        test_pos = [p for p in positions if p.magic == 999999]
        if test_pos:
            logger.info("Closing existing test positions...")
            trader.close_positions(test_pos, mt5.POSITION_TYPE_BUY, "Cleanup")
            time.sleep(1)

    # Execute
    trader.execute_trade('buy', 0.001, 0, 0, "Test ORB ETH")
    
    time.sleep(2)
    
    # Verify
    positions = mt5.positions_get(symbol=symbol)
    test_pos = [p for p in positions if p.magic == 999999]
    
    if test_pos:
        pos = test_pos[0]
        logger.info(f"SUCCESS: Position Opened. Ticket: {pos.ticket}")
        logger.info(f"  Volume: {pos.volume}")
        
        if abs(pos.volume - 0.001) < 0.00001:
            logger.info("  Volume Correct: 0.001")
        else:
            logger.error(f"  Volume Incorrect: {pos.volume} (Expected 0.001)")
            
        # 3. Close Position
        logger.info("\n--- Closing Position ---")
        trader.close_positions([pos], mt5.POSITION_TYPE_BUY, "Test End")
        
        time.sleep(2)
        positions_after = mt5.positions_get(symbol=symbol)
        test_pos_after = [p for p in positions_after if p.magic == 999999]
        
        if not test_pos_after:
            logger.info("SUCCESS: Position Closed.")
        else:
            logger.error("FAILURE: Position NOT Closed.")
            
    else:
        logger.error("FAILURE: Trade NOT Opened.")

    mt5.shutdown()

if __name__ == "__main__":
    run_test()
