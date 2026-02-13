import sys
import os
import time
import logging
from unittest.mock import MagicMock
import pandas as pd

# Adjust path to import bot modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
src_dir = os.path.join(project_root, 'src', 'trading_bot')
sys.path.append(src_dir)

# Mock MT5 before importing main
sys.modules['MetaTrader5'] = MagicMock()
import MetaTrader5 as mt5

# Set up MT5 Mock Constants
mt5.TIMEFRAME_M15 = 15
mt5.ORDER_TYPE_BUY = 0
mt5.ORDER_TYPE_SELL = 1
mt5.TRADE_ACTION_DEAL = 1
mt5.TRADE_RETCODE_DONE = 10009
mt5.symbol_info_tick = MagicMock()
mt5.symbol_info = MagicMock()
mt5.order_send = MagicMock()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestExecution")

# Import Bot
from src.trading_bot.main import SymbolTrader

def test_orb_execution_trigger():
    logger.info("Starting ORB Execution Trigger Test...")
    
    # 1. Initialize Bot (Mocked)
    bot = SymbolTrader("XAUUSD")
    bot.symbol = "XAUUSD"
    bot.magic_number = 888888
    
    # Mock Components
    bot.telegram = MagicMock()
    bot.llm_client = MagicMock()
    bot.smc_validator = MagicMock()
    bot.advanced_analysis = MagicMock()
    
    # Mock Dataframe Helper
    bot.get_dataframe = MagicMock(return_value=pd.DataFrame({
        'time': pd.date_range(start='2024-01-01', periods=100, freq='15min'),
        'close': [2000] * 100,
        'high': [2005] * 100,
        'low': [1995] * 100,
        'volume': [1000] * 100
    }))
    
    # Mock Advanced Analysis (Force "Trending" to pass filter)
    bot.advanced_analysis.analyze_full.return_value = {
        'regime': {'regime': 'trending', 'confidence': 0.9}
    }
    
    # Mock SMC Validator (Force High Score)
    bot.smc_validator.validate_signal.return_value = (True, 90, "Perfect Setup")
    
    # Mock LLM Response
    bot.llm_client.optimize_strategy_logic.return_value = {
        "action": "execute",
        "position_size": 0.05,
        "exit_conditions": {"sl_price": 1990.0},
        "position_management": {"dynamic_basket_tp": 50.0},
        "reason": "Test Breakout"
    }
    
    # Mock MT5 Tick
    tick = MagicMock()
    tick.ask = 2010.0
    tick.bid = 2009.0
    mt5.symbol_info_tick.return_value = tick
    
    # Mock Order Send Result
    order_result = MagicMock()
    order_result.retcode = mt5.TRADE_RETCODE_DONE
    order_result.order = 123456
    mt5.order_send.return_value = order_result
    
    # Mock Strategy State (Simulate Breakout)
    orb_signal = {
        'signal': 'buy',
        'price': 2010.0,
        'sl_dist': 5.0,
        'tp_dist': 10.0,
        'stats': {}
    }
    
    # Mock Grid State (Active)
    bot.current_strategy_mode = "GRID_RANGING"
    bot.grid_strategy.is_ranging = True
    bot.cancel_all_pending = MagicMock()
    
    logger.info("Test Scenario: Grid is Active, ORB Signal Arrives.")
    
    # 2. Execute Handler
    bot.handle_orb_signal(orb_signal)
    
    # 3. Verify Execution
    logger.info("--- Verification Results ---")
    
    # Check 1: Did it call LLM?
    if bot.llm_client.optimize_strategy_logic.called:
        logger.info("✅ LLM Analysis Requested")
    else:
        logger.error("❌ LLM Analysis NOT Requested")
        
    # Check 2: Did it execute trade?
    # execute_trade calls mt5.order_send
    if mt5.order_send.called:
        args = mt5.order_send.call_args[0][0]
        if args['action'] == mt5.TRADE_ACTION_DEAL and args['volume'] == 0.05:
            logger.info(f"✅ Trade Executed Correctly: Buy 0.05 Lots @ {args['price']}")
        else:
            logger.error(f"❌ Incorrect Trade Params: {args}")
    else:
        logger.error("❌ Trade NOT Executed")
        
    # Check 3: Did it stop Grid?
    if bot.current_strategy_mode == "ORB_BREAKOUT":
        logger.info("✅ Strategy Mode Switched to ORB_BREAKOUT")
    else:
        logger.error(f"❌ Strategy Mode Failed Switch: {bot.current_strategy_mode}")
        
    if bot.grid_strategy.is_ranging is False:
        logger.info("✅ Grid Ranging Flag Disabled")
    else:
        logger.error("❌ Grid Ranging Flag NOT Disabled")
        
    if bot.cancel_all_pending.called:
        logger.info("✅ Pending Orders Cancelled")
    else:
        logger.error("❌ Pending Orders NOT Cancelled")

if __name__ == "__main__":
    test_orb_execution_trigger()
