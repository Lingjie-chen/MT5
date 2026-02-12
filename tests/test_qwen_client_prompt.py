
import sys
import os
import pytest
import json
import logging
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from trading_bot.ai.qwen_client import QwenClient

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

class TestQwenClient:
    def setup_method(self):
        """Setup before each test"""
        self.api_key = "test_key"
        self.client = QwenClient(api_key=self.api_key)
        
        # Mock Market Data
        self.market_data = {
            "symbol": "XAUUSD",
            "bid": 2000.0,
            "ask": 2000.5,
            "account_info": {"available_balance": 10000},
            "contract_size": 100,
            "server_time": "2023-10-27 10:00:00"
        }

    @patch('requests.Session.post')
    def test_optimize_strategy_logic_prompt_generation(self, mock_post):
        """Test if the prompt generated for optimize_strategy_logic contains new requirements"""
        
        # 1. Setup Mock Response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "action": "hold",
                        "strategy_mode": "grid_consolidation", # Expect new field
                        "telegram_report": "Report content",
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

        # 2. Prepare Context Data
        market_structure_analysis = {
            "market_structure": {"trend": "bullish"},
            "smc_signals": {"ob": "none"},
            "sentiment_analysis": {"score": 0.5},
            "symbol_specific_analysis": {},
            "key_observations": "Waiting for breakout"
        }
        
        grid_config_context = {
            "orb_stats": {"z_score": 0.5, "breakout_score": 45.0, "range_high": 2010}
        }

        # 3. Execute
        self.client.optimize_strategy_logic(
            market_structure_analysis=market_structure_analysis,
            current_market_data=self.market_data,
            # existing_positions=[], # Not used in signature if not updated
            grid_config_context=grid_config_context
        )

        # 4. Verify Prompt Content
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        system_prompt = payload['messages'][0]['content']
        user_prompt = payload['messages'][1]['content']

        print("\n--- Checking System Prompt Content ---")
        
        # Check Strategy Mode definition
        assert '"trend" / "orb_breakout" / "grid_consolidation"' in system_prompt, \
            "System Prompt missing new strategy_mode options"
            
        # Check Telegram Report requirements
        assert "🚀策略模式(ORB/Grid)" in system_prompt, \
            "System Prompt missing 'Strategy Mode' in telegram_report requirements"
            
        # Check Entry Execution Logic (SMC Removal)
        assert "SMC/结构分析仅作参考 (SMC as Reference Only)" in user_prompt, \
            "User Prompt missing SMC reference-only instruction"
            
        assert "ORB 突破信号 (Primary Signal - Mode A)" in user_prompt, \
            "User Prompt missing ORB Mode A instruction"
            
        assert "网格震荡信号 (Secondary Signal - Mode B)" in user_prompt, \
            "User Prompt missing Grid Mode B instruction"

        print("✅ All Prompt checks passed!")

if __name__ == "__main__":
    # Manually run if executed as script
    t = TestQwenClient()
    t.setup_method()
    # Remove the decorator for manual execution to avoid double injection issues in this simple script
    # or just unwrap it.
    pass

    # Actually, simpler to just run with pytest

