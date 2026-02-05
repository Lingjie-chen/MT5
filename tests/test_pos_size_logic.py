
import unittest
import json
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path to import QwenClient
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mock logging to avoid clutter
logging_mock = MagicMock()
sys.modules['logging'] = logging_mock

from trading_bot.ai.qwen_client import QwenClient

class TestQwenPositionSize(unittest.TestCase):
    def setUp(self):
        self.client = QwenClient()
        # Mock the _call_api method to avoid actual network calls
        self.client._call_api = MagicMock()
        
        # Base dummy data for optimize_strategy_logic
        self.dummy_market_structure = {"sentiment": "neutral"}
        self.dummy_market_data = {"symbol": "XAUUSD", "account_info": {"available_balance": 10000}}
    
    def mock_api_response(self, content_dict):
        """Helper to mock the API response with specific JSON content"""
        self.client._call_api.return_value = {
            "choices": [{
                "message": {
                    "content": json.dumps(content_dict)
                }
            }]
        }

    def test_risk_control_zero_lot(self):
        """Test Case 1: AI returns 0.0 for Risk Control"""
        response_data = {
            "action": "sell",
            "position_size": 0.0,
            "entry_conditions": {"price": 2000, "action": "sell"},
            "exit_conditions": {"sl_price": 2010, "tp_price": 1980},
            "strategy_rationale": "High Risk",
            "confidence": 80,
            "market_state": "Bearish",
            "analysis_breakdown": {"position_calculation_logic": "Risk Control"}
        }
        self.mock_api_response(response_data)
        
        result = self.client.optimize_strategy_logic(
            self.dummy_market_structure, self.dummy_market_data
        )
        
        print(f"\n[Test Case 1] Input: 0.0 -> Output: {result.get('position_size')}")
        self.assertEqual(result['position_size'], 0.0)
        
        # Simulate Main.py Execution Logic
        execution_decision = "EXECUTED"
        if result['position_size'] == 0.0:
            execution_decision = "SKIPPED (Risk Control)"
        
        print(f"Main.py Logic Simulation: {execution_decision}")
        self.assertEqual(execution_decision, "SKIPPED (Risk Control)")

    def test_normal_trade(self):
        """Test Case 2: AI returns 0.15 for Normal Trade"""
        response_data = {
            "action": "sell",
            "position_size": 0.15,
            "entry_conditions": {"price": 2000, "action": "sell"},
            "exit_conditions": {"sl_price": 2010, "tp_price": 1980},
            "strategy_rationale": "Good Setup",
            "confidence": 85,
            "market_state": "Bearish",
            "analysis_breakdown": {"position_calculation_logic": "Calc"}
        }
        self.mock_api_response(response_data)
        
        result = self.client.optimize_strategy_logic(
            self.dummy_market_structure, self.dummy_market_data
        )
        
        print(f"\n[Test Case 2] Input: 0.15 -> Output: {result.get('position_size')}")
        self.assertEqual(result['position_size'], 0.15)
        
        # Simulate Main.py Execution Logic
        execution_decision = "EXECUTED"
        if result['position_size'] == 0.0:
            execution_decision = "SKIPPED (Risk Control)"
        
        print(f"Main.py Logic Simulation: {execution_decision}")
        self.assertEqual(execution_decision, "EXECUTED")

    def test_fallback_min_lot(self):
        """Test Case 3: AI returns 0.01 (Fallback)"""
        response_data = {
            "action": "sell",
            "position_size": 0.01,
            "entry_conditions": {"price": 2000, "action": "sell"},
            "exit_conditions": {"sl_price": 2010, "tp_price": 1980},
            "strategy_rationale": "Low Risk",
            "confidence": 60,
            "market_state": "Bearish",
            "analysis_breakdown": {"position_calculation_logic": "Fallback"}
        }
        self.mock_api_response(response_data)
        
        result = self.client.optimize_strategy_logic(
            self.dummy_market_structure, self.dummy_market_data
        )
        
        print(f"\n[Test Case 3] Input: 0.01 -> Output: {result.get('position_size')}")
        self.assertEqual(result['position_size'], 0.01)
        
        # Simulate Main.py Execution Logic
        execution_decision = "EXECUTED"
        if result['position_size'] == 0.0:
            execution_decision = "SKIPPED (Risk Control)"
        
        print(f"Main.py Logic Simulation: {execution_decision}")
        self.assertEqual(execution_decision, "EXECUTED")

if __name__ == '__main__':
    unittest.main()
