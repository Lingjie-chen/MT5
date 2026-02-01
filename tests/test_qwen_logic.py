import unittest
from unittest.mock import MagicMock, patch
import json
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from trading_bot.ai.qwen_client import QwenClient

class TestQwenLogic(unittest.TestCase):
    def setUp(self):
        # Initialize with dummy key
        self.client = QwenClient(api_key="dummy_key")
        
        # Mock the _call_api method to return controlled responses
        self.client._call_api = MagicMock()

    def mock_api_response(self, content_dict):
        """Helper to mock API response with a JSON content"""
        self.client._call_api.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps(content_dict)
                }
            }]
        }

    def test_hold_without_positions_converts_to_wait(self):
        """Test: Action 'hold' with NO positions -> 'wait'"""
        print("\nTesting: HOLD without positions -> WAIT")
        
        # 1. Mock API to return 'hold'
        mock_response = {
            "action": "hold",
            "position_size": 0.5,
            "exit_conditions": {"sl_price": 2000, "tp_price": 2020},
            "telegram_report": "💎 持仓中 (Holding): Trend is good."
        }
        self.mock_api_response(mock_response)
        
        # 2. Call optimize_strategy_logic with EMPTY positions
        result = self.client.optimize_strategy_logic(
            market_structure_analysis={},
            current_market_data={"symbol": "XAUUSD"},
            current_positions=[] # Empty
        )
        
        # 3. Verify conversion
        self.assertEqual(result['action'], 'wait')
        self.assertIn("观望", result['telegram_report'])
        self.assertIn("Waiting", result['telegram_report'])
        print(f"Result Action: {result['action']}")
        print(f"Result Report: {result['telegram_report']}")

    def test_wait_with_positions_converts_to_hold(self):
        """Test: Action 'wait' WITH positions -> 'hold'"""
        print("\nTesting: WAIT with positions -> HOLD")
        
        # 1. Mock API to return 'wait'
        mock_response = {
            "action": "wait",
            "position_size": 0.5,
            "exit_conditions": {"sl_price": 2000, "tp_price": 2020},
            "telegram_report": "⏳ 观望中 (Waiting): No signal."
        }
        self.mock_api_response(mock_response)
        
        # 2. Call optimize_strategy_logic WITH positions
        dummy_positions = [{"ticket": 123, "type": "buy", "volume": 0.1, "profit": 10}]
        result = self.client.optimize_strategy_logic(
            market_structure_analysis={},
            current_market_data={"symbol": "XAUUSD"},
            current_positions=dummy_positions
        )
        
        # 3. Verify conversion
        self.assertEqual(result['action'], 'hold')
        self.assertIn("持仓", result['telegram_report'])
        self.assertIn("Holding", result['telegram_report'])
        print(f"Result Action: {result['action']}")
        print(f"Result Report: {result['telegram_report']}")

    def test_sl_tp_logic_enforcement(self):
        """Test: Ensure SL/TP are preserved and position_size is checked"""
        print("\nTesting: SL/TP Presence")
        
        mock_response = {
            "action": "buy",
            # position_size missing, should be defaulted to 0.01
            "exit_conditions": {"sl_price": 1990.0, "tp_price": 2010.0},
            "telegram_report": "Buy Signal"
        }
        self.mock_api_response(mock_response)
        
        result = self.client.optimize_strategy_logic(
            market_structure_analysis={},
            current_market_data={"symbol": "XAUUSD"},
            current_positions=[]
        )
        
        self.assertEqual(result['position_size'], 0.01) # Default applied
        self.assertEqual(result['exit_conditions']['sl_price'], 1990.0)

    def test_main_filter_logic_simulation(self):
        """Test: Simulate main.py filtering logic (Strength < 70)"""
        print("\nTesting: Main.py Filter Logic (Simulation)")
        
        # Inputs
        strength = 65.0 # Low strength
        final_signal = 'buy'
        current_positions_list = [] # No positions
        
        # Logic from main.py
        if strength < 70:
            final_signal = 'hold' if current_positions_list else 'wait'
            reason = f"[Filter] Low Strength ({strength:.1f} < 70)"
            
        self.assertEqual(final_signal, 'wait')
        print(f"Filter Result: {final_signal} (Reason: {reason})")
        
        # Test with positions
        current_positions_list = [1]
        if strength < 70:
            final_signal = 'hold' if current_positions_list else 'wait'
        
        self.assertEqual(final_signal, 'hold')
        print(f"Filter Result with Positions: {final_signal}")

if __name__ == '__main__':
    unittest.main()
