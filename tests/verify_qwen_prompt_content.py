
import sys
import os
import json
import logging
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from trading_bot.ai.qwen_client import QwenClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyPrompt")

def verify_qwen_prompt():
    logger.info("Starting Qwen Prompt Verification...")
    
    # 1. Setup Client
    client = QwenClient(api_key="test_key")
    
    # 2. Prepare Dummy Data
    market_data = {
        "symbol": "XAUUSD",
        "bid": 2000.0,
        "ask": 2000.5,
        "account_info": {"available_balance": 10000},
        "contract_size": 100,
        "server_time": "2023-10-27 10:00:00"
    }
    
    market_analysis = {
        "market_structure": {"trend": "bullish"},
        "smc_signals": {},
        "sentiment_analysis": {},
        "symbol_specific_analysis": {},
        "key_observations": "Test"
    }
    
    technical_signals = {
        "grid_strategy": {
            "config": {
                "orb_open_hour": 8,
                "grid_step_points": 200
            },
            "orb_data": {
                "stats": {
                    "z_score": 0.5, 
                    "breakout_score": 45.0,
                    "range_high": 2010,
                    "range_low": 1990
                }
            }
        }
    }

    # 3. Mock API and Call Method
    with patch('requests.Session.post') as mock_post:
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "action": "hold",
                        "strategy_mode": "grid_consolidation",
                        "telegram_report": "Report",
                        "position_size": 0.0,
                        "entry_conditions": None,
                        "exit_conditions": {"sl": 0, "tp": 0},
                        "strategy_rationale": "Rationale",
                        "pre_market_check": {},
                        "sl": 0, "tp": 0,
                        "position_management": {"dynamic_basket_sl": 0}
                    })
                }
            }]
        }
        mock_post.return_value = mock_response

        # Execute
        client.optimize_strategy_logic(
            market_structure_analysis=market_analysis,
            current_market_data=market_data,
            technical_signals=technical_signals,
            current_positions=[]
        )

        # 4. Inspect Prompt
        call_args = mock_post.call_args
        if not call_args:
            logger.error("API was not called!")
            return False
            
        payload = call_args[1]['json']
        system_prompt = payload['messages'][0]['content']
        user_prompt = payload['messages'][1]['content']
        full_prompt = system_prompt + "\n" + user_prompt

        # 5. Verification Checks
        checks = []
        
        # Check 1: No "Trend Only"
        if "Trend Only" not in full_prompt and "单边趋势专用" not in full_prompt:
            checks.append(("✅ No 'Trend Only' constraint found", True))
        else:
            checks.append(("❌ 'Trend Only' constraint STILL PRESENT", False))

        # Check 2: "Adaptive Trading" present
        if "Adaptive Trading" in full_prompt or "自适应交易" in full_prompt:
            checks.append(("✅ 'Adaptive Trading' instruction found", True))
        else:
            checks.append(("❌ 'Adaptive Trading' instruction MISSING", False))

        # Check 3: Strategy Mode Options
        if '"orb_breakout" / "grid_consolidation"' in full_prompt and '"trend"' not in full_prompt.split('strategy_mode**: str (')[1].split(')')[0]:
             checks.append(("✅ strategy_mode options correct (No 'trend')", True))
        else:
             checks.append(("❌ strategy_mode options INCORRECT (Check if 'trend' is removed)", False))

        # Check 4: GRID_START in actions
        if "GRID_START" in full_prompt:
            checks.append(("✅ 'GRID_START' action found", True))
        else:
            checks.append(("❌ 'GRID_START' action MISSING", False))

        # Check 5: Z-Score Constraint
        if "Z-Score < 1.0" in full_prompt and "绝对禁止" in full_prompt:
            checks.append(("✅ Z-Score < 1.0 constraint found", True))
        else:
            checks.append(("❌ Z-Score < 1.0 constraint MISSING", False))

        # Check 6: Fibonacci Mandate
        if "Fibonacci Levels" in full_prompt and "Limit 挂单" in full_prompt:
            checks.append(("✅ Fibonacci Limit Order mandate found", True))
        else:
            checks.append(("❌ Fibonacci Limit Order mandate MISSING", False))
            
        # Check 7: Basket TP Hold Logic
        if "Hold 状态判断" in full_prompt:
            checks.append(("✅ Basket TP Hold logic found", True))
        else:
            checks.append(("❌ Basket TP Hold logic MISSING", False))

        # Output Results
        print("\n" + "="*50)
        print("VERIFICATION RESULTS")
        print("="*50)
        all_passed = True
        for msg, passed in checks:
            print(msg)
            if not passed:
                all_passed = False
        print("="*50)
        
        if all_passed:
            print("🎉 ALL CHECKS PASSED! Code is ready.")
        else:
            print("⚠️ SOME CHECKS FAILED. Review code.")

if __name__ == "__main__":
    verify_qwen_prompt()
