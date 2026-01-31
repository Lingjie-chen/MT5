import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from trading_bot.main import SymbolTrader, mt5

class TestTimeframeAndRR(unittest.TestCase):
    def setUp(self):
        self.bot = SymbolTrader(symbol="GOLD")
        self.bot.point = 0.01
        
    def test_default_timeframe(self):
        """Verify default timeframe is M15"""
        self.assertEqual(self.bot.timeframe, mt5.TIMEFRAME_M15, "Default timeframe should be M15")
        
    def test_rr_check(self):
        """Verify Risk/Reward ratio check"""
        # Mock MT5 functions used in execute_trade
        with patch('trading_bot.main.mt5') as mock_mt5:
            # Setup symbol info
            mock_info = MagicMock()
            mock_info.point = 0.01
            mock_info.trade_stops_level = 0
            mock_info.ask = 2000.0
            mock_info.bid = 2000.0
            mock_mt5.symbol_info.return_value = mock_info
            mock_mt5.symbol_info_tick.return_value = mock_info
            # Define success retcode constant
            mock_mt5.TRADE_RETCODE_DONE = 0
            
            # Setup bot internal state
            self.bot.lot_size = 0.01
            self.bot.magic_number = 123
            self.bot._get_filling_mode = MagicMock(return_value=mt5.ORDER_FILLING_FOK)
            self.bot._normalize_price = lambda p: round(p, 2)
            
            # Case 1: Good RR (2.0) -> Should proceed
            # Market Buy at 2000, SL 1990 (Risk 10), TP 2020 (Reward 20) -> RR 2.0
            class Result:
                retcode = 0
                comment = "OK"
                order = 12345678
            mock_mt5.order_send.return_value = Result()
            # Call
            result = self.bot._send_order(
                type_str="buy",
                price=2000.0,
                sl=1990.0,
                tp=2020.0,
                comment="Test Good RR"
            )
            # _send_order does not return result; verify that order_send was called
            self.assertTrue(mock_mt5.order_send.called, "Order should be sent when RR >= 1.5")
            
            # Case 2: Bad RR (1.0) -> Should be rejected
            # Buy at 2000, SL 1990 (Risk 10), TP 2010 (Reward 10) -> RR 1.0
            mock_mt5.order_send.reset_mock()
            result = self.bot._send_order(
                type_str="buy",
                price=2000.0,
                sl=1990.0,
                tp=2010.0,
                comment="Test Bad RR"
            )
            self.assertIsNone(result, "Trade with RR 1.0 should be rejected")
            self.assertFalse(mock_mt5.order_send.called, "Order should NOT be sent when RR < 1.5")
            
            # Case 3: Bad RR (1.4) -> Should be rejected
            # Buy at 2000, SL 1990 (Risk 10), TP 2014 (Reward 14) -> RR 1.4
            mock_mt5.order_send.reset_mock()
            result = self.bot._send_order(
                type_str="buy",
                price=2000.0,
                sl=1990.0,
                tp=2014.0,
                comment="Test Bad RR 1.4"
            )
            self.assertIsNone(result, "Trade with RR 1.4 should be rejected")
            self.assertFalse(mock_mt5.order_send.called, "Order should NOT be sent when RR < 1.5")

if __name__ == '__main__':
    unittest.main()
