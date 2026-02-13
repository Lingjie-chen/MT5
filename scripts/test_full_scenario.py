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
logger = logging.getLogger("FullScenarioTest")

def test_full_scenario():
    logger.info("Starting Full ORB Conflict Scenario Test...")
    
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
    
    # 2. SETUP PRECONDITION: Active Grid with Opposite Position
    # We will simulate an ORB BUY signal. So we need a GRID SELL Position (Counter-trend).
    
    logger.info("Step 1: Setting up Counter-Trend Grid Position (SELL 0.02)...")
    bot.current_strategy_mode = "GRID_RANGING"
    bot.grid_strategy.is_ranging = True
    
    tick = mt5.symbol_info_tick(target_symbol)
    
    # Open Grid Sell Position
    req_grid = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": target_symbol,
        "volume": 0.02,
        "type": mt5.ORDER_TYPE_SELL,
        "price": tick.bid,
        "magic": bot.magic_number,
        "comment": "Grid Counter",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    res_grid = mt5.order_send(req_grid)
    if res_grid.retcode != mt5.TRADE_RETCODE_DONE:
        logger.error(f"Failed to open grid position: {res_grid.comment}")
        return
    grid_ticket = res_grid.order
    logger.info(f"Grid SELL Position Opened: #{grid_ticket}")
    
    # Place a Grid Pending Order too (to check cancellation)
    req_pending = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": target_symbol,
        "volume": 0.01,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": tick.bid + 10.0,
        "magic": bot.magic_number,
        "comment": "Grid Pending",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    mt5.order_send(req_pending)
    logger.info("Grid Pending Order Placed.")
    
    time.sleep(1)
    
    # 3. SIMULATE ORB BREAKOUT (BUY)
    logger.info("Step 2: Simulating ORB BUY Breakout...")
    
    # Test Params
    SMART_SL = round(tick.ask - 3.0, 2)
    BASKET_TP = 15.0
    
    orb_signal = {
        'signal': 'buy',
        'price': tick.ask,
        'sl_dist': 2.0,
        'tp_dist': 5.0,
        'stats': {'breakout_score': 100}
    }
    
    # Mock AI/SMC
    bot.smc_validator.validate_signal = lambda *args, **kwargs: (True, 95, "Pass")
    bot.llm_client.optimize_strategy_logic = lambda *args, **kwargs: {
        "action": "execute",
        "position_size": 0.02,
        "exit_conditions": {"sl_price": SMART_SL},
        "position_management": {"dynamic_basket_tp": BASKET_TP},
        "reason": "Full Scenario Test"
    }
    
    # Execute
    bot.handle_orb_signal(orb_signal)
    
    time.sleep(3)
    
    # 4. VERIFICATION
    logger.info("Step 3: Verifying State...")
    
    # A. Check Grid Strategy State
    if bot.current_strategy_mode == "ORB_BREAKOUT":
        logger.info("✅ Mode switched to ORB_BREAKOUT")
    else:
        logger.error(f"❌ Mode Failed: {bot.current_strategy_mode}")
        
    if not bot.grid_strategy.is_ranging:
        logger.info("✅ Grid Ranging Disabled")
    else:
        logger.error("❌ Grid Ranging Still Active")
        
    # B. Check Pending Orders (Should be 0)
    orders = mt5.orders_get(symbol=target_symbol)
    my_orders = [o for o in orders if o.magic == bot.magic_number] if orders else []
    if not my_orders:
        logger.info("✅ All Pending Orders Cancelled")
    else:
        logger.error(f"❌ Pending Orders Remain: {len(my_orders)}")
        
    # C. Check Positions
    positions = mt5.positions_get(symbol=target_symbol)
    my_positions = [p for p in positions if p.magic == bot.magic_number]
    
    # Should have: 
    # 1. Old Grid SELL (Bot doesn't auto-close existing positions yet, only cancels pending and stops new ones)
    #    Wait, user requirement: "是否可以停止所有网格反向单" -> Stop all grid reverse orders.
    #    Currently logic only cancels PENDING orders. Existing positions are usually managed by basket or SL.
    #    Let's check if the ORB BUY was opened correctly.
    
    orb_pos = None
    for p in my_positions:
        if abs(p.volume - 0.02) < 0.001 and p.type == mt5.POSITION_TYPE_BUY:
            orb_pos = p
            break
            
    if orb_pos:
        logger.info(f"✅ ORB BUY Position Opened: #{orb_pos.ticket}")
        if abs(orb_pos.sl - SMART_SL) < 0.1:
            logger.info(f"✅ Smart SL Correct: {orb_pos.sl}")
        else:
            logger.error(f"❌ Smart SL Mismatch: {orb_pos.sl}")
    else:
        logger.error("❌ ORB BUY Position NOT Found")

    # D. Cleanup
    logger.info("Step 4: Cleanup...")
    for p in my_positions:
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": target_symbol,
            "volume": p.volume,
            "type": mt5.ORDER_TYPE_SELL if p.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": p.ticket,
            "price": mt5.symbol_info_tick(target_symbol).bid if p.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(target_symbol).ask,
            "magic": bot.magic_number,
            "type_filling": mt5.ORDER_FILLING_IOC
        }
        mt5.order_send(req)
        
    mt5.shutdown()

if __name__ == "__main__":
    test_full_scenario()
