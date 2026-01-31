import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from trading_bot.analysis.advanced_analysis import AdvancedMarketAnalysis
from trading_bot.main import mt5

class TestAnalysisTimeframes(unittest.TestCase):
    def test_only_h1_m15(self):
        ama = AdvancedMarketAnalysis()
        tfs = ama.timeframes
        self.assertIn("M15", tfs, "M15 should be present")
        self.assertIn("H1", tfs, "H1 should be present")
        self.assertNotIn("M6", tfs, "M6 should be removed")
        self.assertEqual(tfs["M15"], mt5.TIMEFRAME_M15)
        self.assertEqual(tfs["H1"], mt5.TIMEFRAME_H1)

if __name__ == '__main__':
    unittest.main()
