import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from trading_bot.main import SymbolTrader, mt5
from trading_bot.strategies.grid_strategy import KalmanGridStrategy

class TestRunV4(unittest.TestCase):
    def setUp(self):
        self.bot = SymbolTrader(symbol="GOLD")
        self.grid = KalmanGridStrategy(symbol="GOLD", magic_number=123456)
        
    @patch('trading_bot.main.mt5')
    def test_calculate_smart_basket_tp_with_smc(self, mock_mt5):
        """Test Basket TP calculation with SMC targets"""
        # Setup SMC Data
        smc_data = {
            'key_levels': {
                'resistance': [2010.0, 2020.0],
                'support': [1990.0, 1980.0]
            }
        }
        
        # Setup Positions (Net Long)
        positions = [
            {'volume': 1.0, 'type': mt5.POSITION_TYPE_BUY, 'profit': 100.0, 'swap': 0.0}
        ]
        
        # Setup Market Info
        mock_tick = MagicMock()
        mock_tick.bid = 2000.0
        mock_tick.ask = 2000.5
        mock_mt5.symbol_info_tick.return_value = mock_tick
        
        mock_info = MagicMock()
        mock_info.point = 0.01
        mock_info.trade_tick_value = 1.0
        mock_info.trade_tick_size = 0.01
        mock_mt5.symbol_info.return_value = mock_info
        
        # Run Calculation
        # Base TP = 100. SMC Resistance at 2010. Current ~2000.
        # Dist = 10.0. Value = 10.0 * 1.0 lot * $1/point = $1000? 
        # Wait, Point=0.01. 10.0 price diff = 1000 points.
        # Value = 1000 * 1.0 = $1000.
        # Buffer 50 points (0.5 price). Target = 2009.5.
        # Dist = 9.5. Profit = 950.
        # Total = 100 (curr) + 950 = 1050.
        # Result should be mix of 100 and 1050.
        
        tp = self.bot.calculate_smart_basket_tp(
            llm_tp=100.0,
            atr=2.0,
            market_regime='trending',
            smc_data=smc_data,
            current_positions=positions
        )
        
        print(f"Calculated TP: {tp}")
        self.assertGreater(tp, 100.0, "TP should be boosted by SMC target")

    def test_check_grid_exit(self):
        """Test Grid Exit Logic"""
        self.grid.dynamic_tp_long = 500.0
        self.grid.long_pos_count = 1
        self.grid.magic_number = 123
        
        # Mock Position
        mock_pos = MagicMock()
        mock_pos.magic = 123
        mock_pos.type = mt5.POSITION_TYPE_BUY
        mock_pos.profit = 600.0 # > 500
        mock_pos.swap = 0.0
        
        close_long, close_short = self.grid.check_grid_exit([mock_pos], current_price=2000.0)
        
        self.assertTrue(close_long, "Should trigger Long Basket Exit")
        self.assertFalse(close_short, "Should not trigger Short Exit")

if __name__ == '__main__':
    unittest.main()
