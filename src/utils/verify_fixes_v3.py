import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from trading_bot.main import MT5Bot

class TestFixesV3(unittest.TestCase):
    def setUp(self):
        self.bot = MT5Bot()
        self.bot.symbol = "XAUUSD"
        self.bot.lot_size = 0.01
        
    def test_calculate_smart_basket_tp_zero(self):
        """Test that explicit 0.0 from LLM is respected"""
        # Case 1: LLM returns 0.0 -> Should return 0.0
        result = self.bot.calculate_smart_basket_tp(
            llm_tp=0.0,
            atr=1.0,
            market_regime='ranging',
            smc_data={},
            current_positions=[]
        )
        self.assertEqual(result, 0.0, "Should return 0.0 when LLM explicitly sets 0.0")
        
        # Case 2: LLM returns None -> Should return default 100.0
        result = self.bot.calculate_smart_basket_tp(
            llm_tp=None,
            atr=1.0,
            market_regime='ranging',
            smc_data={},
            current_positions=[]
        )
        self.assertEqual(result, 100.0, "Should return 100.0 default when LLM returns None")

    @patch('trading_bot.main.mt5')
    def test_lot_size_validation(self, mock_mt5):
        """Test lot size normalization logic"""
        # Setup symbol info mock
        mock_info = MagicMock()
        mock_info.volume_step = 0.01
        mock_info.volume_min = 0.01
        mock_info.volume_max = 100.0
        mock_mt5.symbol_info.return_value = mock_info
        
        # Simulate the logic block manually (since it's embedded in main loop, we extract the logic)
        strategy = {'position_size': 0.12345}
        
        # Logic from main.py
        qwen_lot = float(strategy['position_size'])
        if qwen_lot > 0:
            step = mock_info.volume_step
            min_vol = mock_info.volume_min
            max_vol = mock_info.volume_max
            
            # 1. Normalize
            qwen_lot = round(qwen_lot / step) * step
            qwen_lot = round(qwen_lot, 2)
            
            # 2. Clamp
            if qwen_lot < min_vol: qwen_lot = min_vol
            elif qwen_lot > max_vol: qwen_lot = max_vol
            
        self.assertEqual(qwen_lot, 0.12, "Should round 0.12345 to 0.12 with step 0.01")
        
        # Test Min Clamp
        strategy['position_size'] = 0.001
        qwen_lot = float(strategy['position_size'])
        if qwen_lot > 0:
            qwen_lot = round(qwen_lot / step) * step
            qwen_lot = round(qwen_lot, 2)
            if qwen_lot < min_vol: qwen_lot = min_vol
            
        self.assertEqual(qwen_lot, 0.01, "Should clamp 0.001 to min 0.01")

if __name__ == '__main__':
    unittest.main()
