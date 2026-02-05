import unittest
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from trading_bot.strategies.grid_strategy import KalmanGridStrategy
import MetaTrader5 as mt5

class TestGridStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = KalmanGridStrategy("XAUUSD", mt5.TIMEFRAME_M15, 123456)
        # Configure Dynamic Params
        self.strategy.update_dynamic_params(
            basket_tp=100.0,
            basket_sl_long=-50.0,
            basket_sl_short=-50.0,
            lock_trigger=10.0
        )

    def create_mock_position(self, profit, type_):
        pos = MagicMock()
        pos.profit = profit
        pos.swap = 0.0
        pos.magic = 123456
        pos.type = type_
        # Mock time for state update
        pos.time_msc = 1000
        pos.price_open = 2000.0
        return pos

    def test_basket_tp_long(self):
        print("\n--- Test Basket TP (Long) ---")
        # Profit 100 >= 100
        positions = [self.create_mock_position(100.0, mt5.POSITION_TYPE_BUY)]
        close_long, close_short = self.strategy.check_grid_exit(positions, 2000.0)
        self.assertTrue(close_long)
        print("TP Hit Verified")

    def test_basket_sl_long(self):
        print("\n--- Test Basket SL (Long) ---")
        # Profit -51 <= -50
        positions = [self.create_mock_position(-51.0, mt5.POSITION_TYPE_BUY)]
        close_long, close_short = self.strategy.check_grid_exit(positions, 2000.0)
        self.assertTrue(close_long)
        print("SL Hit Verified")

    def test_profit_locking_long(self):
        print("\n--- Test Profit Locking (Long) ---")
        # 1. Below Trigger (Profit 9)
        positions = [self.create_mock_position(9.0, mt5.POSITION_TYPE_BUY)]
        close_long, _ = self.strategy.check_grid_exit(positions, 2000.0)
        self.assertFalse(close_long)
        self.assertIsNone(self.strategy.basket_lock_level_long)
        print("Step 1: Below Trigger - OK")

        # 2. Hit Trigger (Profit 10) -> Lock should be max(10, 5) = 10
        positions = [self.create_mock_position(10.0, mt5.POSITION_TYPE_BUY)]
        close_long, _ = self.strategy.check_grid_exit(positions, 2000.0)
        self.assertFalse(close_long) # Profit is 10, Lock is 10. 10 < 10 is False. Safe.
        self.assertEqual(self.strategy.basket_lock_level_long, 10.0)
        print("Step 2: Trigger Hit - Lock set to 10.0 - OK")

        # 3. Small Retrace (Profit 9.9) -> Should Close
        positions = [self.create_mock_position(9.9, mt5.POSITION_TYPE_BUY)]
        close_long, _ = self.strategy.check_grid_exit(positions, 2000.0)
        self.assertTrue(close_long)
        print("Step 3: Retrace to 9.9 - Close Triggered - OK")

    def test_trailing_long(self):
        print("\n--- Test Trailing (Long) ---")
        # Reset
        self.strategy = KalmanGridStrategy("XAUUSD", mt5.TIMEFRAME_M15, 123456)
        self.strategy.update_dynamic_params(lock_trigger=10.0)

        # 1. Profit jumps to 40
        # Lock = max(10, 40 * 0.5) = 20
        positions = [self.create_mock_position(40.0, mt5.POSITION_TYPE_BUY)]
        self.strategy.check_grid_exit(positions, 2000.0)
        self.assertEqual(self.strategy.basket_lock_level_long, 20.0)
        print("Step 1: Profit 40 -> Lock 20 - OK")

        # 2. Profit drops to 21 (Safe)
        positions = [self.create_mock_position(21.0, mt5.POSITION_TYPE_BUY)]
        close_long, _ = self.strategy.check_grid_exit(positions, 2000.0)
        self.assertFalse(close_long)
        print("Step 2: Drop to 21 - Safe - OK")

        # 3. Profit drops to 19 (Hit)
        positions = [self.create_mock_position(19.0, mt5.POSITION_TYPE_BUY)]
        close_long, _ = self.strategy.check_grid_exit(positions, 2000.0)
        self.assertTrue(close_long)
        print("Step 3: Drop to 19 - Close Triggered - OK")

    def test_short_consistency(self):
        print("\n--- Test Short Consistency ---")
        # Verify Short logic mirrors Long logic (Lock 10)
        positions = [self.create_mock_position(10.0, mt5.POSITION_TYPE_SELL)]
        close_long, close_short = self.strategy.check_grid_exit(positions, 2000.0)
        self.assertFalse(close_short)
        self.assertEqual(self.strategy.basket_lock_level_short, 10.0) # Should be 10, not 1.0
        print("Short Side Trigger Hit - Lock set to 10.0 - OK")

if __name__ == '__main__':
    unittest.main()