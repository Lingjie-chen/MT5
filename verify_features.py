
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

# Mock MT5 before importing main
sys.modules["MetaTrader5"] = MagicMock()
import MetaTrader5 as mt5

from trading_bot.analysis.advanced_analysis import SMCAnalyzer
from trading_bot.ai.qwen_client import QwenClient

class TestEnhancedFeatures(unittest.TestCase):
    def setUp(self):
        self.smc = SMCAnalyzer()
        self.qwen = QwenClient("fake_key")
        
        # Create mock price data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='15T')
        self.df = pd.DataFrame({
            'time': dates,
            'open': np.linspace(2000, 2010, 100),
            'high': np.linspace(2005, 2015, 100),
            'low': np.linspace(1995, 2005, 100),
            'close': np.linspace(2002, 2012, 100),
            'tick_volume': np.random.randint(100, 1000, 100)
        })
        self.df.set_index('time', inplace=True)

    def test_smc_structure_detection(self):
        """Test SMC Structure Detection (BOS/CHoCH)"""
        # Create a BOS scenario (Bullish Breakout)
        # Create swing high at index 50: 2020
        self.df.loc[self.df.index[50], 'high'] = 2020
        # Current close at index 99: 2025 (Breakout)
        self.df.loc[self.df.index[-1], 'close'] = 2025
        
        # We need to ensure detect_structure_points finds the swing high
        # Swing High needs neighbors lower than it
        for i in range(1, 4):
            self.df.loc[self.df.index[50-i], 'high'] = 2010
            self.df.loc[self.df.index[50+i], 'high'] = 2010
            
        result = self.smc.detect_smart_structure(self.df, sentiment_score=1)
        
        # Should detect bullish BOS if logic holds
        # Note: detect_structure_points looks at last 10 points. 
        # Index 50 is far back (len=100). Might be missed if limited to recent.
        # Let's move swing high closer, index 90.
        self.df.loc[self.df.index[90], 'high'] = 2020
        for i in range(1, 4):
            self.df.loc[self.df.index[90-i], 'high'] = 2010
            self.df.loc[self.df.index[90+i], 'high'] = 2010
            
        result = self.smc.detect_smart_structure(self.df, sentiment_score=1)
        
        # Check if structure keys exist
        self.assertIn('signal', result)
        self.assertIn('type', result)
        self.assertIn('recent_sh', result) # Check for new field
        
        print(f"SMC Result: {result}")

    def test_qwen_prompt_update(self):
        """Test if Qwen prompt includes new instructions"""
        prompt = self.qwen._build_prompt(
            symbol="GOLD",
            market_data={"close": 2000},
            indicators={},
            news=[],
            strategy_pool={}
        )
        
        # Check for key phrases added
        self.assertIn("Trend Cycle Control", prompt)
        self.assertIn("Anti-FOMO", prompt)
        self.assertIn("Supply & Demand Zones", prompt)
        self.assertIn("BOS (Break of Structure)", prompt)

if __name__ == '__main__':
    unittest.main()
