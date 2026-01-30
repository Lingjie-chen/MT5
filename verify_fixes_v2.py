
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

class TestFixesV2(unittest.TestCase):
    def setUp(self):
        self.bot = SymbolTrader("GOLD")
        self.bot.latest_strategy = {}
        self.bot.db_manager = MagicMock()
        self.bot.lot_size = 0.01
        
        # Mock _send_order to capture arguments
        self.bot._send_order = MagicMock(return_value=MagicMock(retcode=mt5.TRADE_RETCODE_DONE))
        self.bot.calculate_dynamic_lot = MagicMock(return_value=0.01)
        
        # Mock MT5 functions
        mt5.symbol_info_tick = MagicMock()
        mt5.symbol_info_tick.return_value.ask = 2000.0
        mt5.symbol_info_tick.return_value.bid = 1999.0
        
        mt5.symbol_info = MagicMock()
        mt5.symbol_info.return_value.point = 0.01
        mt5.symbol_info.return_value.trade_tick_size = 0.01
        mt5.symbol_info.return_value.digits = 2
        
        # Mock copy_rates_from_pos for ATR calculation
        # Return enough data for rolling(14)
        data = {'high': [2005.0]*20, 'low': [1995.0]*20, 'close': [2000.0]*20, 'time': range(20)}
        self.bot.get_market_data = MagicMock(return_value=pd.DataFrame(data))
        
        # Mock mt5.copy_rates_from_pos explicitly for the internal call in execute_trade
        # It returns a numpy array of records
        import numpy as np
        dtype = [('time', 'i8'), ('open', 'f8'), ('high', 'f8'), ('low', 'f8'), ('close', 'f8'), ('tick_volume', 'i8'), ('spread', 'i4'), ('real_volume', 'i8')]
        records = []
        for i in range(20):
            records.append((1000+i, 2000.0, 2005.0, 1995.0, 2000.0, 100, 1, 0))
        mt5.copy_rates_from_pos.return_value = np.array(records, dtype=dtype)
        
        # Mock account_info
        mock_account = MagicMock()
        mock_account.margin_level = 500.0
        mock_account.margin_free = 10000.0
        mock_account.balance = 10000.0
        mt5.account_info = MagicMock(return_value=mock_account)
        
        # Mock positions_get (return empty list by default)
        mt5.positions_get = MagicMock(return_value=[])

    def test_inverted_sl_tp_sell(self):
        """Test if Sell Entry 2000, SL 1960, TP 2010 gets swapped to SL 2010, TP 1960"""
        # "sell" action
        # Entry 1999.0 (Market Sell at Bid)
        # We provide SL=1960 (Profit side), TP=2010 (Loss side) -> Inverted
        entry_params = {
            'action': 'sell',
            'price': 2000.0,
            'sl': 1960.0, # Wrong for Sell (Profit side)
            'tp': 2010.0, # Wrong for Sell (Loss side)
            'lots': 0.15
        }
        
        self.bot.execute_trade('sell', 0.8, {}, entry_params=entry_params)
        
        # Check _send_order arguments
        args, kwargs = self.bot._send_order.call_args
        
        call_sl = args[2]
        call_tp = args[3]
        
        print(f"Test Inverted Sell: SL={call_sl}, TP={call_tp}")
        
        # Expect Swap: SL=2010, TP=1960
        # Risk = |2010-1999| = 11. Reward = |1960-1999| = 39. Ratio > 1.2.
        
        self.assertGreater(call_sl, call_tp) # For Sell, SL > TP
        self.assertAlmostEqual(call_sl, 2010.0)
        self.assertAlmostEqual(call_tp, 1960.0)
        
        self.assertEqual(self.bot.lot_size, 0.15)

    def test_missing_sl_tp_defaults(self):
        """Test if SL/TP are generated when missing"""
        entry_params = {
            'action': 'buy',
            'lots': 0.1
        }
        
        # ATR is (2005-1995) = 10.0
        # Buy @ Ask 2000.0
        # Default SL = Price - 1.5*ATR = 2000 - 15 = 1985
        # Default TP = Price + 2.0*ATR = 2000 + 20 = 2020
        
        self.bot.execute_trade('buy', 0.8, {}, entry_params=entry_params)
        
        args, kwargs = self.bot._send_order.call_args
        call_sl = args[2]
        call_tp = args[3]
        
        print(f"Test Defaults Buy: SL={call_sl}, TP={call_tp}")
        
        self.assertAlmostEqual(call_sl, 1985.0)
        self.assertAlmostEqual(call_tp, 2020.0)
        self.assertEqual(self.bot.lot_size, 0.1)

if __name__ == '__main__':
    unittest.main()
