
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
logger = logging.getLogger("VerifyFinal")

def verify_final_logic():
    logger.info("Starting Final Logic Verification...")
    
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
        
        # Check 1: ORB Breakout Strict Condition
        if "ORB Breakout Score > 60" in full_prompt and "Z-Score" in full_prompt and "绝对值 > 1.0" in full_prompt:
             checks.append(("✅ ORB Breakout strict condition (Score > 60 & Z > 1.0) found", True))
        else:
             checks.append(("❌ ORB Breakout strict condition MISSING", False))

        # Check 2: Grid Consolidation Logic (No Boundary Constraint)
        # We removed "触及边界" from one part, but we want to make sure the NEW logic is there
        if "只要确认是震荡，即可启动" in full_prompt or "不要等待触及边界" in full_prompt:
            checks.append(("✅ Grid Consolidation 'Immediate Start' logic found", True))
        else:
            checks.append(("❌ Grid Consolidation 'Immediate Start' logic MISSING", False))

        # Check 3: Q8 Execution Priority
        if "优先级" in full_prompt and "1. **ORB 强突破**" in full_prompt and "2. **Grid 触发**" in full_prompt:
            checks.append(("✅ Q8 Execution Priority Logic found", True))
        else:
            checks.append(("❌ Q8 Execution Priority Logic MISSING", False))
            
        # Check 4: No "Perfect Trend" loophole
        if "1. **完美趋势**" not in full_prompt:
             checks.append(("✅ 'Perfect Trend' loophole successfully removed", True))
        else:
             checks.append(("❌ 'Perfect Trend' loophole STILL PRESENT", False))

        # Check 5: Trend Surfing Constraint
        if "Trend Surfing" in full_prompt and "必须" in full_prompt and "ORB Breakout 条件" in full_prompt:
             checks.append(("✅ Trend Surfing constraint found", True))
        else:
             checks.append(("❌ Trend Surfing constraint MISSING", False))

        # Output Results
        print("\n" + "="*50)
        print("FINAL LOGIC VERIFICATION RESULTS")
        print("="*50)
        all_passed = True
        for msg, passed in checks:
            print(msg)
            if not passed:
                all_passed = False
        print("="*50)
        
        if all_passed:
            print("🎉 ALL CHECKS PASSED! Logic is fully updated.")
        else:
            print("⚠️ SOME CHECKS FAILED. Please review.")

if __name__ == "__main__":
    verify_final_logic()
