
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("TestFallback")

def test_sl_tp_logic(orb_signal, llm_decision):
    """
    Simulates the logic block from main.py for SL/TP calculation
    """
    
    # --- Logic from main.py START ---
    
    # Extract Smart SL (Optimal Stop Loss)
    smart_sl = llm_decision.get('exit_conditions', {}).get('sl_price', 0)
    
    # Extract Smart TP (Optimal Take Profit)
    smart_tp = llm_decision.get('exit_conditions', {}).get('tp_price', 0)
    
    # Fallback Logic if LLM returns invalid SL/TP (Math Model Fallback)
    if smart_sl == 0:
        if orb_signal['signal'] == 'buy':
            smart_sl = orb_signal['price'] - orb_signal['sl_dist']
        else:
            smart_sl = orb_signal['price'] + orb_signal['sl_dist']
            
    if smart_tp == 0:
        if orb_signal['signal'] == 'buy':
            smart_tp = orb_signal['price'] + orb_signal['tp_dist']
        else:
            smart_tp = orb_signal['price'] - orb_signal['tp_dist']
            
    # --- Logic from main.py END ---
    
    return smart_sl, smart_tp

def run_tests():
    print("Running SL/TP Fallback Logic Tests...\n")
    
    # Mock Data
    orb_signal_buy = {
        'signal': 'buy',
        'price': 2000.0,
        'sl_dist': 10.0, # SL should be 1990.0 if fallback
        'tp_dist': 20.0  # TP should be 2020.0 if fallback
    }
    
    orb_signal_sell = {
        'signal': 'sell',
        'price': 2000.0,
        'sl_dist': 10.0, # SL should be 2010.0 if fallback
        'tp_dist': 20.0  # TP should be 1980.0 if fallback
    }

    # Test Case 1: LLM provides valid values (BUY)
    llm_valid = {
        'exit_conditions': {
            'sl_price': 1995.0,
            'tp_price': 2030.0
        }
    }
    sl, tp = test_sl_tp_logic(orb_signal_buy, llm_valid)
    assert sl == 1995.0, f"Case 1 Failed: Expected SL 1995.0, got {sl}"
    assert tp == 2030.0, f"Case 1 Failed: Expected TP 2030.0, got {tp}"
    print("✅ Case 1 Passed: LLM values used correctly (BUY)")

    # Test Case 2: LLM provides valid values (SELL)
    llm_valid_sell = {
        'exit_conditions': {
            'sl_price': 2005.0,
            'tp_price': 1970.0
        }
    }
    sl, tp = test_sl_tp_logic(orb_signal_sell, llm_valid_sell)
    assert sl == 2005.0, f"Case 2 Failed: Expected SL 2005.0, got {sl}"
    assert tp == 1970.0, f"Case 2 Failed: Expected TP 1970.0, got {tp}"
    print("✅ Case 2 Passed: LLM values used correctly (SELL)")

    # Test Case 3: LLM provides 0/Missing values (BUY Fallback)
    llm_empty = {} # No exit_conditions
    sl, tp = test_sl_tp_logic(orb_signal_buy, llm_empty)
    expected_sl = 2000.0 - 10.0
    expected_tp = 2000.0 + 20.0
    assert sl == expected_sl, f"Case 3 Failed: Expected SL {expected_sl}, got {sl}"
    assert tp == expected_tp, f"Case 3 Failed: Expected TP {expected_tp}, got {tp}"
    print(f"✅ Case 3 Passed: Fallback logic used correctly (BUY). SL: {sl}, TP: {tp}")

    # Test Case 4: LLM provides 0/Missing values (SELL Fallback)
    sl, tp = test_sl_tp_logic(orb_signal_sell, llm_empty)
    expected_sl = 2000.0 + 10.0
    expected_tp = 2000.0 - 20.0
    assert sl == expected_sl, f"Case 4 Failed: Expected SL {expected_sl}, got {sl}"
    assert tp == expected_tp, f"Case 4 Failed: Expected TP {expected_tp}, got {tp}"
    print(f"✅ Case 4 Passed: Fallback logic used correctly (SELL). SL: {sl}, TP: {tp}")

    # Test Case 5: Partial Missing (LLM gives SL but not TP)
    llm_partial = {
        'exit_conditions': {
            'sl_price': 1998.0
            # tp_price missing (0)
        }
    }
    sl, tp = test_sl_tp_logic(orb_signal_buy, llm_partial)
    assert sl == 1998.0, f"Case 5 Failed: Expected SL 1998.0, got {sl}"
    assert tp == 2020.0, f"Case 5 Failed: Expected TP 2020.0 (Fallback), got {tp}"
    print("✅ Case 5 Passed: Mixed LLM/Fallback values used correctly")

    print("\nAll Tests Passed Successfully!")

if __name__ == "__main__":
    run_tests()
