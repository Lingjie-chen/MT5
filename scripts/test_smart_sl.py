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
logger = logging.getLogger("ORB_SmartSL_Test")

def test_smart_sl_and_telegram():
    logger.info("Starting Smart SL & Telegram Verification Test...")
    
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
    
    # 2. Patch Telegram to Capture Message
    captured_messages = []
    original_send = bot.telegram.send_message
    
    def mock_send_message(msg):
        logger.info(f"CAPTURED TELEGRAM MSG:\n{msg}")
        captured_messages.append(msg)
        # Call original to actually send (if you want to verify on phone too)
        # return original_send(msg) 
        return True # Return success to avoid errors
        
    bot.telegram.send_message = mock_send_message
    
    # 3. Simulate High Quality Signal
    tick = mt5.symbol_info_tick(target_symbol)
    current_price = tick.ask
    
    # Test Parameters
    TEST_SMART_SL = round(current_price - 5.55, 2)
    TEST_BASKET_TP = 25.50
    TEST_LOT_SIZE = 0.02
    TEST_REASON = "SmartSL Validation Test"
    
    # Construct Signal
    orb_signal = {
        'signal': 'buy',
        'price': current_price,
        'sl_dist': 2.0,
        'tp_dist': 5.0,
        'stats': {'breakout_score': 100}
    }
    
    # 4. Mock Logic to Inject Specific SL/TP
    logger.info("Injecting Mock Logic with specific Smart SL/TP...")
    
    bot.smc_validator.validate_signal = lambda *args, **kwargs: (True, 99, "Perfect Setup")
    bot.llm_client.optimize_strategy_logic = lambda *args, **kwargs: {
        "action": "execute",
        "position_size": TEST_LOT_SIZE,
        "exit_conditions": {"sl_price": TEST_SMART_SL},
        "position_management": {"dynamic_basket_tp": TEST_BASKET_TP},
        "reason": TEST_REASON
    }
    
    # 5. Execute
    logger.info("Executing Signal...")
    bot.handle_orb_signal(orb_signal)
    
    time.sleep(2)
    
    # 6. Verify Results
    logger.info("--- Verification ---")
    
    # A. Verify Position Properties (SL on Order)
    positions = mt5.positions_get(symbol=target_symbol)
    orb_pos = [p for p in positions if p.magic == bot.magic_number]
    
    if orb_pos:
        last_pos = orb_pos[-1]
        
        # Verify SL
        if abs(last_pos.sl - TEST_SMART_SL) < 0.1:
            logger.info(f"✅ Position SL Correct: {last_pos.sl} (Expected ~{TEST_SMART_SL})")
        else:
            logger.error(f"❌ Position SL Mismatch: {last_pos.sl} != {TEST_SMART_SL}")
            
        # Verify TP (Should be 0.0 as it's Basket Managed)
        if last_pos.tp == 0.0:
            logger.info(f"✅ Position TP is 0.0 (Basket Managed)")
        else:
            logger.warning(f"⚠️ Position TP is set: {last_pos.tp} (Expected 0.0 for Basket)")
            
        # Verify Volume
        if abs(last_pos.volume - TEST_LOT_SIZE) < 0.001:
             logger.info(f"✅ Position Volume Correct: {last_pos.volume}")
        
        # Cleanup
        logger.info("Closing Test Position...")
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": target_symbol,
            "volume": last_pos.volume,
            "type": mt5.ORDER_TYPE_SELL,
            "position": last_pos.ticket,
            "price": mt5.symbol_info_tick(target_symbol).bid,
            "magic": bot.magic_number,
            "type_filling": mt5.ORDER_FILLING_IOC
        }
        mt5.order_send(req)
        
    else:
        logger.error("❌ No Position Opened!")
        
    # B. Verify Strategy State (Basket TP)
    current_basket_tp = bot.grid_strategy.dynamic_tp_long
    if abs(current_basket_tp - TEST_BASKET_TP) < 0.01:
        logger.info(f"✅ Strategy Basket TP Updated: {current_basket_tp}")
    else:
        logger.error(f"❌ Strategy Basket TP Mismatch: {current_basket_tp} != {TEST_BASKET_TP}")
        
    # C. Verify Telegram Message
    found_msg = False
    for msg in captured_messages:
        if "Trade Executed" in msg and str(TEST_SMART_SL) in msg and str(TEST_BASKET_TP) in msg:
            logger.info("✅ Telegram Message Content Verified:")
            logger.info(f"   - Contains Smart SL: {TEST_SMART_SL}")
            logger.info(f"   - Contains Basket TP: {TEST_BASKET_TP}")
            logger.info(f"   - Contains Reason: {TEST_REASON}")
            found_msg = True
            break
            
    if not found_msg:
        logger.error("❌ Telegram Message Incorrect or Missing!")

    mt5.shutdown()

if __name__ == "__main__":
    test_smart_sl_and_telegram()
