
import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Mock MetaTrader5 before importing main
mock_mt5 = MagicMock()
# Set constants
mock_mt5.TIMEFRAME_M15 = 15
mock_mt5.ORDER_TIME_GTC = 0
mock_mt5.ORDER_FILLING_IOC = 1
mock_mt5.TRADE_ACTION_DEAL = 1
mock_mt5.ORDER_TYPE_BUY = 0
mock_mt5.ORDER_TYPE_SELL = 1
sys.modules["MetaTrader5"] = mock_mt5

# Now import the bot class
# Assuming the script is run from project root
import os
sys.path.append(os.getcwd())
from src.trading_bot.main import SymbolTrader

class TestBotLogic(unittest.TestCase):
    def setUp(self):
        self.bot = SymbolTrader("ETHUSD", timeframe=mock_mt5.TIMEFRAME_M15)
        self.bot.lot_size = 1.0
        self.bot.magic_number = 123456
        # Mock logger to avoid spam
        self.bot.logger = MagicMock()

    def test_ethusd_trading_hours(self):
        """Verify ETHUSD is only allowed on Weekends (Sat 06:00 - Mon 05:59)"""
        print("\nTesting ETHUSD Trading Hours...")
        
        # Case 1: Saturday 07:00 (Allowed)
        with patch('src.trading_bot.main.datetime') as mock_date:
            mock_date.now.return_value = datetime(2023, 10, 7, 7, 0) # Oct 7 2023 is Saturday
            self.assertTrue(self.bot.is_trading_time(), "Sat 07:00 should be allowed for ETHUSD")
            print("  [Pass] Sat 07:00 is allowed")

        # Case 2: Monday 05:00 (Allowed)
        with patch('src.trading_bot.main.datetime') as mock_date:
            mock_date.now.return_value = datetime(2023, 10, 9, 5, 0) # Oct 9 2023 is Monday
            self.assertTrue(self.bot.is_trading_time(), "Mon 05:00 should be allowed for ETHUSD")
            print("  [Pass] Mon 05:00 is allowed")

        # Case 3: Monday 07:00 (Not Allowed)
        with patch('src.trading_bot.main.datetime') as mock_date:
            mock_date.now.return_value = datetime(2023, 10, 9, 7, 0) 
            self.assertFalse(self.bot.is_trading_time(), "Mon 07:00 should NOT be allowed for ETHUSD")
            print("  [Pass] Mon 07:00 is blocked")
            
        # Case 4: Wednesday 12:00 (Not Allowed)
        with patch('src.trading_bot.main.datetime') as mock_date:
            mock_date.now.return_value = datetime(2023, 10, 11, 12, 0) 
            self.assertFalse(self.bot.is_trading_time(), "Wed 12:00 should NOT be allowed for ETHUSD")
            print("  [Pass] Wed 12:00 is blocked")

    def test_send_order_sl_tp_forcing(self):
        """Verify SL and TP are forced to 0.0"""
        print("\nTesting SL/TP Forcing to 0.0...")
        
        # Mock account info for margin check (plenty of money)
        mock_acc = MagicMock()
        mock_acc.margin_free = 10000.0
        mock_mt5.account_info.return_value = mock_acc
        
        # Mock symbol info
        mock_sym = MagicMock()
        mock_sym.point = 0.01
        mock_sym.trade_stops_level = 10
        mock_sym.volume_step = 0.01
        mock_sym.volume_min = 0.01
        mock_mt5.symbol_info.return_value = mock_sym
        
        mock_mt5.order_calc_margin.return_value = 100.0 # Low margin req
        mock_mt5.order_send.return_value = MagicMock(retcode=10009) # Done

        # Execute trade with SL=1950, TP=2050
        # Signature: _send_order(self, type_str, price, sl, tp, comment="")
        self.bot._send_order("buy", 2000.0, 1950.0, 2050.0)
        
        # Check arguments passed to order_send
        args, _ = mock_mt5.order_send.call_args
        request = args[0]
        
        self.assertEqual(request['sl'], 0.0, "SL should be forced to 0.0")
        self.assertEqual(request['tp'], 0.0, "TP should be forced to 0.0")
        print(f"  [Pass] SL sent as {request['sl']}, TP sent as {request['tp']}")

    def test_margin_auto_resize(self):
        """Verify Volume Auto-Resize when margin is insufficient"""
        print("\nTesting Margin Auto-Resize...")
        
        # Scenario: Balance 500, Margin Required 1000 for 1.0 lot
        # Should resize to approx 0.5 lot
        mock_acc = MagicMock()
        mock_acc.margin_free = 500.0
        mock_mt5.account_info.return_value = mock_acc
        mock_mt5.order_calc_margin.return_value = 1000.0 
        
        # Mock symbol info for step
        mock_sym = MagicMock()
        mock_sym.point = 0.01
        mock_sym.trade_stops_level = 10
        mock_sym.volume_step = 0.01
        mock_sym.volume_min = 0.01
        mock_mt5.symbol_info.return_value = mock_sym
        
        self.bot.lot_size = 1.0 # Requesting 1.0
        
        self.bot._send_order("buy", 2000.0, 0, 0)
        
        args, _ = mock_mt5.order_send.call_args
        request = args[0]
        
        # Expected: 1.0 * (500/1000) * 0.95 = 0.475 -> floor to 0.01 -> 0.47
        expected_vol = 0.47
        self.assertAlmostEqual(request['volume'], expected_vol, places=2)
        print(f"  [Pass] Volume resized from 1.0 to {request['volume']} (Expected ~0.47)")

if __name__ == '__main__':
    unittest.main()
