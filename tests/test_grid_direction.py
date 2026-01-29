
import sys
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import pandas as pd

# Mock mt5 before importing main
sys.modules['MetaTrader5'] = MagicMock()
import MetaTrader5 as mt5

# Adjust path to import TradingBot
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from trading_bot.main import TradingBot

class TestGridDirection(unittest.TestCase):
    def setUp(self):
        self.bot = TradingBot()
        self.bot.symbol = "XAUUSD"
        self.bot.grid_strategy = MagicMock()
        self.bot.magic_number = 123456
        
        # Mock mt5 functions used in execute_trade
        mt5.symbol_info_tick.return_value = MagicMock(ask=2000.0, bid=1999.0)
        mt5.account_info.return_value = MagicMock(margin_free=10000.0)
        mt5.symbol_info.return_value = MagicMock(point=0.01, trade_stops_level=0)
        mt5.positions_get.return_value = [] # No positions
        mt5.orders_get.return_value = [] # No pending orders
        
        # Mock copy_rates for ATR calculation
        dtype = [('high', 'f8'), ('low', 'f8'), ('close', 'f8'), ('open', 'f8')]
        rates = np.zeros(20, dtype=dtype)
        rates['high'] = 2005.0
        rates['low'] = 1995.0
        mt5.copy_rates_from_pos.return_value = rates
        
        # Mock _send_order to avoid actual MT5 calls and just log
        self.bot._send_order = MagicMock()
        self.bot.cancel_all_pending_orders = MagicMock()

    def test_grid_start_bearish_inference(self):
        print("\nTesting Grid Start Bearish Inference...")
        # Mock strategy response from LLM (Qwen style)
        strategy = {
            'action': 'grid_start',
            'market_analysis': {
                'sentiment_analysis': {
                    'sentiment': 'bearish' # Key indicator
                },
                'market_structure': {
                    'trend': 'bearish'
                }
            },
            'grid_config': {
                'initial_lot': 0.01,
                'grid_step_pips': 20.0
            }
        }
        self.bot.latest_strategy = strategy
        
        # Execute trade
        # Signal passed as 'grid_start' (neutral string), so it relies on strategy content
        self.bot.execute_trade('grid_start', 80, {}, entry_params=None)
        
        # Check if generate_grid_plan was called with direction='bearish'
        self.bot.grid_strategy.generate_grid_plan.assert_called()
        args, kwargs = self.bot.grid_strategy.generate_grid_plan.call_args
        # generate_grid_plan(current_price, direction, atr, ...)
        direction_arg = args[1]
        print(f"Inferred Direction: {direction_arg}")
        
        self.assertEqual(direction_arg, 'bearish', "Grid direction should be inferred as bearish based on market_analysis")

    def test_grid_start_bullish_inference(self):
        print("\nTesting Grid Start Bullish Inference...")
        strategy = {
            'action': 'grid_start',
            'market_analysis': {
                'sentiment_analysis': {
                    'sentiment': 'bullish'
                }
            }
        }
        self.bot.latest_strategy = strategy
        
        self.bot.execute_trade('grid_start', 80, {}, entry_params=None)
        
        args, kwargs = self.bot.grid_strategy.generate_grid_plan.call_args
        direction_arg = args[1]
        print(f"Inferred Direction: {direction_arg}")
        self.assertEqual(direction_arg, 'bullish')

    def test_grid_start_explicit_short(self):
        print("\nTesting Grid Start Explicit Short...")
        # Even if sentiment is bullish, explicit action should override
        strategy = {
            'action': 'grid_start_short',
            'market_analysis': {
                'sentiment_analysis': {
                    'sentiment': 'bullish' 
                }
            }
        }
        self.bot.latest_strategy = strategy
        
        self.bot.execute_trade('grid_start_short', 80, {}, entry_params=None)
        
        args, kwargs = self.bot.grid_strategy.generate_grid_plan.call_args
        direction_arg = args[1]
        print(f"Inferred Direction: {direction_arg}")
        self.assertEqual(direction_arg, 'bearish')

if __name__ == '__main__':
    unittest.main()
