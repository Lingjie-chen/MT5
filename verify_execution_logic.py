
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

# Mock MT5 before importing main
sys.modules["MetaTrader5"] = MagicMock()
import MetaTrader5 as mt5

# Mock pandas
import pandas as pd

from trading_bot.main import SymbolTrader

class TestExecutionLogic(unittest.TestCase):
    def setUp(self):
        self.bot = SymbolTrader("GOLD")
        self.bot.latest_strategy = {}
        self.bot.db_manager = MagicMock()
        self.bot.lot_size = 0.01
        
        # Mock logging to avoid clutter
        self.bot.logger = MagicMock()
        
        # Mock internal methods to isolate logic
        self.bot._send_order = MagicMock()
        self.bot.calculate_dynamic_lot = MagicMock(return_value=0.01)
        
        # Mock MT5 functions default behavior
        mt5.symbol_info_tick = MagicMock()
        mt5.symbol_info_tick.return_value.ask = 2000.0
        mt5.symbol_info_tick.return_value.bid = 1999.0
        
        mt5.symbol_info = MagicMock()
        mt5.symbol_info.return_value.point = 0.01
        mt5.symbol_info.return_value.digits = 2
        
        # Mock account info
        self.mock_account = MagicMock()
        self.mock_account.margin_free = 1000.0 # $1000 free margin
        self.mock_account.margin_level = 500.0 # Safe margin level
        mt5.account_info.return_value = self.mock_account

    def test_suggested_lot_within_margin(self):
        """Test that suggested lot is used when within margin limits"""
        # Scenario: Suggest 0.1 lot. Margin needed = $100. Free Margin = $1000.
        # 100 < 1000 * 0.9 (900). Safe.
        
        mt5.order_calc_margin.return_value = 100.0
        
        entry_params = {
            'lots': 0.1,
            'action': 'buy',
            'sl': 1990.0,
            'tp': 2010.0
        }
        
        # We assume explicit_sl/tp and suggested_lot extraction works (tested elsewhere)
        # We bypass extraction and call execute_trade logic directly?
        # Or better: mimic call to execute_trade with extracted args
        
        # main.py: execute_trade(self, signal, strength, sl_tp_params, entry_params=None, suggested_lot=None)
        
        self.bot.execute_trade(
            'buy', 0.8, {}, 
            entry_params=entry_params,
            suggested_lot=0.1
        )
        
        # Verify lot_size was updated to 0.1
        self.assertEqual(self.bot.lot_size, 0.1)
        
        # Verify _send_order was called
        self.bot._send_order.assert_called()

    def test_suggested_lot_exceeds_margin(self):
        """Test that suggested lot is reduced when exceeding margin limits"""
        # Scenario: Suggest 1.0 lot. Margin needed = $2000. Free Margin = $1000.
        # Limit = 1000 * 0.9 = 900.
        # Ratio needed: 900 / 2000 = 0.45.
        # Max Lot = 1.0 * 0.45 = 0.45.
        
        mt5.order_calc_margin.return_value = 2000.0
        
        entry_params = {
            'lots': 1.0,
            'action': 'buy',
            'sl': 1990.0,
            'tp': 2010.0
        }
        
        self.bot.execute_trade(
            'buy', 0.8, {}, 
            entry_params=entry_params,
            suggested_lot=1.0
        )
        
        # Verify lot_size was reduced to 0.45
        self.assertAlmostEqual(self.bot.lot_size, 0.45)
        
        # Verify _send_order was called
        self.bot._send_order.assert_called()

    def test_margin_check_exception(self):
        """Test fallback when margin check fails"""
        mt5.order_calc_margin.side_effect = Exception("MT5 Error")
        
        entry_params = {
            'lots': 0.5,
            'action': 'buy',
            'sl': 1990.0,
            'tp': 2010.0
        }
        
        self.bot.execute_trade(
            'buy', 0.8, {}, 
            entry_params=entry_params,
            suggested_lot=0.5
        )
        
        # Should fallback to original suggested lot
        self.assertEqual(self.bot.lot_size, 0.5)

if __name__ == '__main__':
    unittest.main()
