
import sys
import unittest
from unittest.mock import MagicMock
import os
import types

# Adjust path to import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Mock MetaTrader5 before importing strategy to provide required constants
mt5_stub = types.SimpleNamespace(ORDER_TYPE_BUY=0, ORDER_TYPE_SELL=1, POSITION_TYPE_BUY=0, POSITION_TYPE_SELL=1)
sys.modules['MetaTrader5'] = mt5_stub

from trading_bot.strategies.grid_strategy import KalmanGridStrategy
import MetaTrader5 as mt5

class TestBasketTP(unittest.TestCase):
    def setUp(self):
        self.strategy = KalmanGridStrategy("XAUUSD", 123456)
        # Mock global_tp
        self.strategy.global_tp = 10.0
        self.strategy.dynamic_global_tp = None
        self.strategy.tp_steps = {1: 5.0, 2: 10.0}

    def test_basket_tp_loss_prevention(self):
        print("\nTesting Basket TP Loss Prevention...")
        
        # Scenario: Profit is negative (Loss)
        # Target TP is 5.0
        # Should NOT close
        
        pos1 = MagicMock()
        pos1.magic = 123456
        pos1.symbol = "XAUUSD"
        pos1.type = mt5.ORDER_TYPE_BUY
        pos1.volume = 0.01
        pos1.profit = -50.0 # Loss
        pos1.swap = 0.0
        pos1.commission = 0.0
        
        positions = [pos1]
        
        should_close_long, _ = self.strategy.check_basket_tp(positions)
        print(f"Profit: -50.0, Target: 5.0 -> Close: {should_close_long}")
        
        self.assertFalse(should_close_long, "Should NOT close when in loss, even if logic was flawed before")

    def test_basket_tp_zero_profit(self):
        print("\nTesting Basket TP Zero Profit...")
        pos1 = MagicMock()
        pos1.magic = 123456
        pos1.type = mt5.ORDER_TYPE_BUY
        pos1.profit = 0.0
        pos1.swap = 0.0
        pos1.commission = 0.0
        
        should_close_long, _ = self.strategy.check_basket_tp([pos1])
        print(f"Profit: 0.0, Target: 5.0 -> Close: {should_close_long}")
        self.assertFalse(should_close_long)

    def test_basket_tp_profit_reached(self):
        print("\nTesting Basket TP Profit Reached...")
        pos1 = MagicMock()
        pos1.magic = 123456
        pos1.type = mt5.ORDER_TYPE_BUY
        pos1.profit = 6.0 # > 5.0
        pos1.swap = 0.0
        pos1.commission = 0.0
        
        should_close_long, _ = self.strategy.check_basket_tp([pos1])
        print(f"Profit: 6.0, Target: 5.0 -> Close: {should_close_long}")
        self.assertTrue(should_close_long)

    def test_separate_directions(self):
        print("\nTesting Separate Directions...")
        # Long in Profit, Short in Loss
        pos_long = MagicMock()
        pos_long.magic = 123456
        pos_long.type = mt5.ORDER_TYPE_BUY
        pos_long.profit = 100.0
        pos_long.swap = 0.0
        pos_long.commission = 0.0
        
        pos_short = MagicMock()
        pos_short.magic = 123456
        pos_short.type = mt5.ORDER_TYPE_SELL
        pos_short.profit = -50.0
        pos_short.swap = 0.0
        pos_short.commission = 0.0
        
        should_close_long, should_close_short = self.strategy.check_basket_tp([pos_long, pos_short])
        
        print(f"Long Profit: 100.0 -> Close: {should_close_long}")
        print(f"Short Profit: -50.0 -> Close: {should_close_short}")
        
        self.assertTrue(should_close_long, "Long should close")
        self.assertFalse(should_close_short, "Short should NOT close")

if __name__ == '__main__':
    unittest.main()
