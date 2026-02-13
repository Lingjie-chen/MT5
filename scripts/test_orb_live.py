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
logger = logging.getLogger("LiveORBTest")

def test_orb_live_execution():
    logger.info("Starting Live ORB Execution Test...")
    
    # 1. Initialize Bot
    if not mt5.initialize():
        logger.error("MT5 Initialize Failed")
        return

    target_symbol = "GOLD"
    # Find symbol
    if not mt5.symbol_info(target_symbol):
        for s in mt5.symbols_get():
            if "XAU" in s.name.upper() or "GOLD" in s.name.upper():
                target_symbol = s.name
                break
    
    logger.info(f"Target Symbol: {target_symbol}")
    if not mt5.symbol_select(target_symbol, True):
        logger.error(f"Failed to select {target_symbol}")
        return

    bot = SymbolTrader(target_symbol)
    bot.symbol = target_symbol
    bot.magic_number = 888888
    
    # 2. Setup Pre-condition: Active Grid (Place a dummy Limit Order)
    logger.info("Setting up GRID environment...")
    bot.current_strategy_mode = "GRID_RANGING"
    bot.grid_strategy.is_ranging = True
    
    tick = mt5.symbol_info_tick(target_symbol)
    if not tick:
        logger.error("No tick data")
        return
        
    # Place a pending order far away to simulate Grid
    limit_price = tick.ask - 50.0 # Way below market
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": target_symbol,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": limit_price,
        "magic": bot.magic_number,
        "comment": "Grid Dummy",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    res = mt5.order_send(request)
    if res.retcode == mt5.TRADE_RETCODE_DONE:
        logger.info(f"Dummy Grid Order Placed: #{res.order}")
    else:
        logger.error(f"Failed to place dummy order: {res.comment}")
        return
        
    time.sleep(1)
    
    # 3. Simulate ORB Signal & Trigger Execution
    logger.info("Simulating ORB Breakout Signal...")
    
    # Construct a fake high-quality signal
    orb_signal = {
        'signal': 'buy',
        'price': tick.ask,
        'sl_dist': 2.0,
        'tp_dist': 5.0,
        'stats': {'breakout_score': 100}
    }
    
    # Mock SMC & LLM to ensure it passes validation
    # We patch the validator methods on the live bot instance
    bot.smc_validator.validate_signal = lambda *args, **kwargs: (True, 95, "Test Pass")
    bot.llm_client.optimize_strategy_logic = lambda *args, **kwargs: {
        "action": "execute",
        "position_size": 0.02, # TEST REQUIREMENT: 0.02 Lots
        "exit_conditions": {"sl_price": tick.ask - 2.0},
        "position_management": {"dynamic_basket_tp": 10.0},
        "reason": "Live Test Execution"
    }
    bot.telegram.notify_trade = lambda *args, **kwargs: logger.info("Telegram Notified (Mock)")
    
    # Execute!
    bot.handle_orb_signal(orb_signal)
    
    time.sleep(2)
    
    # 4. Verify Results
    logger.info("--- Verification ---")
    
    # A. Check Grid State
    if bot.current_strategy_mode == "ORB_BREAKOUT":
        logger.info("✅ Strategy Mode switched to ORB_BREAKOUT")
    else:
        logger.error(f"❌ Strategy Mode: {bot.current_strategy_mode}")
        
    if not bot.grid_strategy.is_ranging:
        logger.info("✅ Grid Ranging Flag Disabled")
    else:
        logger.error("❌ Grid Flag Still Active")
        
    # B. Check Pending Orders (Should be cancelled)
    orders = mt5.orders_get(symbol=target_symbol)
    grid_orders = [o for o in orders if o.magic == bot.magic_number] if orders else []
    if not grid_orders:
        logger.info("✅ All Grid Orders Cancelled")
    else:
        logger.error(f"❌ Grid Orders Remain: {len(grid_orders)}")
        
    # C. Check Position (Should be opened 0.02)
    positions = mt5.positions_get(symbol=target_symbol)
    orb_pos = [p for p in positions if p.magic == bot.magic_number and p.comment.startswith("ORB_SMC")]
    
    # Since comment might be truncated or specific, check generic properties
    # Or just check last position opened
    if positions:
        last_pos = positions[-1] # Assuming it's the one we just opened
        if abs(last_pos.volume - 0.02) < 0.001:
            logger.info(f"✅ ORB Position Opened: #{last_pos.ticket} Vol: {last_pos.volume}")
            
            # 5. Clean Up (Close Position)
            logger.info("Cleaning up (Closing Position)...")
            req_close = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": target_symbol,
                "volume": last_pos.volume,
                "type": mt5.ORDER_TYPE_SELL if last_pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": last_pos.ticket,
                "price": mt5.symbol_info_tick(target_symbol).bid if last_pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(target_symbol).ask,
                "magic": bot.magic_number,
                "comment": "Test Cleanup",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            mt5.order_send(req_close)
            logger.info("Position Closed.")
        else:
            logger.error(f"❌ Wrong Volume: {last_pos.volume} (Expected 0.02)")
    else:
        logger.error("❌ No Position Found")

    mt5.shutdown()

if __name__ == "__main__":
    test_orb_live_execution()
