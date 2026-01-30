
import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

# Mock MT5
sys.modules["MetaTrader5"] = MagicMock()
import MetaTrader5 as mt5

# Create a dummy bot instance for testing execute_trade logic
class DummyBot:
    def __init__(self):
        self.latest_strategy = {}
        self.symbol = "XAUUSD"
        self.lot_size = 0.01
        self.logger = MagicMock()
        self.magic_number = 123456
    
    # Copy the relevant logic snippet to test it isolated
    # Or better, we import SymbolTrader and patch everything around it.
    pass

from trading_bot.main import SymbolTrader

class TestSLTPLogic(unittest.TestCase):
    def setUp(self):
        self.bot = SymbolTrader("XAUUSD")
        self.bot.logger = MagicMock()
        
        # Mock MT5
        mt5.symbol_info_tick = MagicMock()
        mt5.positions_get = MagicMock(return_value=[])
        
        # Mock check_account_safety to bypass risk check
        self.bot.check_account_safety = MagicMock(return_value=(True, "Safe"))
        
    def test_buy_sl_tp_validation(self):
        """Test SL/TP validation for BUY orders"""
        # Current Price: 2000
        tick = MagicMock()
        tick.ask = 2000.0
        tick.bid = 1999.0
        mt5.symbol_info_tick.return_value = tick
        
        # Case 1: Valid SL/TP
        # SL: 1990 (Below), TP: 2010 (Above) -> OK
        self.bot.latest_strategy = {'sl': 1990.0, 'tp': 2010.0, 'action': 'buy'}
        self.bot.execute_trade('buy', 0.9, {})
        
        # Verify log message or internal state (hard to verify local var, check logger calls)
        # We look for "执行逻辑: Action=buy, Signal=buy, Explicit SL=1990.0, TP=2010.0"
        args, _ = self.bot.logger.info.call_args
        self.assertIn("Explicit SL=1990.0", args[0])
        self.assertIn("TP=2010.0", args[0])
        
        # Case 2: Invalid SL (Above Price)
        # SL: 2010 (Above 2000) -> Invalid
        self.bot.latest_strategy = {'sl': 2010.0, 'tp': 2020.0, 'action': 'buy'}
        self.bot.execute_trade('buy', 0.9, {})
        
        # Check for warning
        warn_args_list = self.bot.logger.warning.call_args_list
        found_warning = False
        for call in warn_args_list:
            if "Invalid Buy SL" in call[0][0]:
                found_warning = True
                break
        self.assertTrue(found_warning)

    def test_sell_sl_tp_validation(self):
        """Test SL/TP validation for SELL orders"""
        # Current Price: 2000
        tick = MagicMock()
        tick.ask = 2001.0
        tick.bid = 2000.0
        mt5.symbol_info_tick.return_value = tick
        
        # Case 1: Valid SL/TP
        # SL: 2010 (Above), TP: 1990 (Below) -> OK
        self.bot.latest_strategy = {'sl': 2010.0, 'tp': 1990.0, 'action': 'sell'}
        self.bot.execute_trade('sell', 0.9, {})
        
        # Verify
        # We need to find the specific log call among many
        found_info = False
        for call in self.bot.logger.info.call_args_list:
            if "Explicit SL=2010.0" in call[0][0] and "TP=1990.0" in call[0][0]:
                found_info = True
                break
        self.assertTrue(found_info)
        
        # Case 2: Invalid TP (Above Price)
        # TP: 2010 (Above 2000) -> Invalid
        self.bot.latest_strategy = {'sl': 2020.0, 'tp': 2010.0, 'action': 'sell'}
        self.bot.execute_trade('sell', 0.9, {})
        
        # Check for warning
        found_warning = False
        for call in self.bot.logger.warning.call_args_list:
            if "Invalid Sell TP" in call[0][0]:
                found_warning = True
                break
        self.assertTrue(found_warning)

if __name__ == '__main__':
    unittest.main()
