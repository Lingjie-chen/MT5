
import MetaTrader5 as mt5
import time
import logging

# Configure minimal logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("TestBot")

def test_symbol_selection_robustness():
    logger.info("Starting Symbol Selection Robustness Test...")
    
    if not mt5.initialize():
        logger.error(f"MT5 Init Failed: {mt5.last_error()}")
        return

    symbol = "GOLD"
    
    # 1. Simulate "Symbol Not Selected" scenario
    # Try to hide the symbol first (if possible and no charts open)
    # Note: Cannot hide if chart is open. We assume it might fail to hide, but we proceed.
    logger.info(f"Attempting to hide {symbol} to simulate missing symbol...")
    mt5.symbol_select(symbol, False) 
    
    # Check status immediately
    s_info = mt5.symbol_info(symbol)
    if s_info is None:
        logger.info(f"Confirmed: {symbol} info is None (Not in Market Watch).")
    elif not s_info.visible:
        logger.info(f"Confirmed: {symbol} is not visible.")
    else:
        logger.info(f"Note: {symbol} is still visible (probably open chart). Continuing test anyway.")

    # 2. Run the logic from main.py
    logger.info("Running Main.py Logic...")
    
    # --- Logic Start ---
    # Ensure symbol is selected and available
    # Optimization: Check visibility first to avoid unnecessary select calls
    s_info = mt5.symbol_info(symbol)
    
    # If symbol info is missing, force selection immediately
    if s_info is None:
        logger.info("Detected None symbol_info. Forcing selection...")
        if not mt5.symbol_select(symbol, True):
            err = mt5.last_error()
            logger.warning(f"Failed to force select symbol {symbol} (Error={err})")
        else:
            logger.info("Force selection returned True.")
        
        # Check again after selection
        s_info = mt5.symbol_info(symbol)
        if s_info is None:
            logger.warning(f"Symbol info still not found for {symbol} after selection")
        else:
             logger.info(f"Symbol info successfully recovered: {s_info.name}, Visible={s_info.visible}")

    elif not s_info.visible:
        logger.info("Symbol info exists but not visible. Selecting...")
        if not mt5.symbol_select(symbol, True):
            err = mt5.last_error()
            logger.warning(f"Failed to select symbol {symbol} (Error={err})")
        else:
            logger.info("Selection returned True.")
    else:
        logger.info("Symbol was already visible. No action needed.")
        
    # --- Logic End ---
    
    # 3. Final Verification
    final_info = mt5.symbol_info(symbol)
    if final_info and final_info.visible:
        logger.info(f"[PASS] {symbol} is now selected and visible.")
    else:
        logger.error(f"[FAIL] {symbol} is NOT visible or NOT found.")

    mt5.shutdown()

if __name__ == "__main__":
    test_symbol_selection_robustness()
