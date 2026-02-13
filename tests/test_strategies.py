import unittest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'trading_bot')))

from strategies.orb_strategy import GoldORBStrategy
from strategies.grid_strategy import KalmanGridStrategy
from analysis.smc_validator import SMCQualityValidator

class TestORBStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = GoldORBStrategy("XAUUSD")
        
    def test_orb_calculation(self):
        # Create dummy H1 data
        dates = pd.date_range(start='2024-01-01', periods=24, freq='H')
        df = pd.DataFrame({
            'time': dates,
            'open': [2000 + i for i in range(24)],
            'high': [2005 + i for i in range(24)],
            'low': [1995 + i for i in range(24)],
            'close': [2002 + i for i in range(24)],
            'tick_volume': [100] * 24
        })
        
        # Test calculation
        high, low, is_final = self.strategy.calculate_orb_levels(df)
        self.assertIsNotNone(high)
        self.assertIsNotNone(low)
        
    def test_realtime_breakout(self):
        # Setup state manually
        self.strategy.final_range_high = 2010
        self.strategy.final_range_low = 2000
        self.strategy.is_range_final = True
        self.strategy.trades_today_count = 0
        
        # Test Buy Breakout
        signal = self.strategy.check_realtime_breakout(2011)
        self.assertIsNotNone(signal)
        self.assertEqual(signal['signal'], 'buy')
        
        # Test Double Trigger Prevention
        signal2 = self.strategy.check_realtime_breakout(2012)
        self.assertIsNone(signal2) # Should be None because signal taken

class TestGridStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = KalmanGridStrategy("XAUUSD", 123456)
        
    def test_fibonacci_grid(self):
        self.strategy.swing_high = 2000
        self.strategy.swing_low = 1900
        self.strategy.is_ranging = True
        
        current_price = 1950
        orders = self.strategy.generate_fibonacci_grid(current_price, "bullish")
        
        self.assertTrue(len(orders) > 0)
        # Check if orders are valid dicts
        self.assertIn('price', orders[0])
        self.assertIn('type', orders[0])

class TestSMCValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SMCQualityValidator()
        
    @patch('analysis.advanced_analysis.SMCAnalyzer.analyze')
    def test_validation_logic(self, mock_analyze):
        # Mock SMC Analyzer return
        mock_analyze.return_value = {
            'signal': 'buy',
            'sentiment_score': 0.5,
            'details': {
                'premium_discount': {'zone': 'discount'},
                'ob': {'active_obs': [{'type': 'bullish', 'bottom': 1990, 'top': 2000}]},
                'fvg': {'active_fvgs': []}
            }
        }
        
        is_valid, score, details = self.validator.validate_signal(
            pd.DataFrame({'close': [1] * 60}), # Dummy DF with enough length
            current_price=2005,
            signal_type='buy',
            volatility_stats={'breakout_score': 60, 'z_score': 1.5}
        )
        
        self.assertTrue(is_valid)
        self.assertTrue(score >= 75)

if __name__ == '__main__':
    unittest.main()
