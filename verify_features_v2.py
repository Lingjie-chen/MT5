
import unittest
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

# Mock MT5
sys.modules["MetaTrader5"] = MagicMock()

from trading_bot.analysis.advanced_analysis import SMCAnalyzer
from trading_bot.ai.qwen_client import QwenClient

class TestEnhancedFeaturesV2(unittest.TestCase):
    def setUp(self):
        self.smc = SMCAnalyzer()
        self.qwen = QwenClient("fake_key")
        
        # Create mock price data
        dates = pd.date_range(start='2024-01-01', periods=200, freq='15min')
        self.df = pd.DataFrame({
            'time': dates,
            'open': np.full(200, 2000.0),
            'high': np.full(200, 2005.0),
            'low': np.full(200, 1995.0),
            'close': np.full(200, 2000.0),
            'tick_volume': np.random.randint(100, 1000, 200)
        })
        self.df.set_index('time', inplace=True)

    def test_smc_structure_detection(self):
        """Test SMC Structure Detection (BOS/CHoCH) with valid Fractal Data"""
        
        # Helper to set a candle
        def set_candle(idx, high, low, close):
            if idx < 0: idx += len(self.df)
            self.df.iloc[idx, self.df.columns.get_loc('high')] = high
            self.df.iloc[idx, self.df.columns.get_loc('low')] = low
            self.df.iloc[idx, self.df.columns.get_loc('close')] = close
            
        # Create Structure Points (Fractals)
        # detect_structure_points uses range(n-3, 2, -1) and looks +/- 3 bars
        # High[i] > High[i +/- k] for k in 1..3
        
        # 1. Create a Swing High at index 100
        # High=2020. Surrounding=2010.
        set_candle(100, 2020.0, 1990.0, 2000.0)
        for i in range(1, 4):
            set_candle(100-i, 2010.0, 1990.0, 2000.0)
            set_candle(100+i, 2010.0, 1990.0, 2000.0)
            
        # 2. Create a Swing Low at index 120
        # Low=1980. Surrounding=1990.
        set_candle(120, 2010.0, 1980.0, 2000.0)
        for i in range(1, 4):
            set_candle(120-i, 2010.0, 1990.0, 2000.0)
            set_candle(120+i, 2010.0, 1990.0, 2000.0)
            
        # 3. Create a Higher High (Swing High) at index 140 -> Bullish Structure
        set_candle(140, 2030.0, 1990.0, 2000.0)
        for i in range(1, 4):
            set_candle(140-i, 2010.0, 1990.0, 2000.0)
            set_candle(140+i, 2010.0, 1990.0, 2000.0)
            
        # 4. Create a Higher Low (Swing Low) at index 160 -> Bullish Structure
        set_candle(160, 2010.0, 1985.0, 2000.0)
        for i in range(1, 4):
            set_candle(160-i, 2010.0, 1990.0, 2000.0)
            set_candle(160+i, 2010.0, 1990.0, 2000.0)
            
        # At this point, we have:
        # SH (100): 2020
        # SL (120): 1980
        # SH (140): 2030 (HH)
        # SL (160): 1985 (HL)
        # Micro Trend should be Bullish (HH + HL)
        
        # 5. Trigger BOS: Break above recent SH (2030)
        # Current price at end (199)
        set_candle(-1, 2040.0, 2035.0, 2035.0) # Close 2035 > 2030
        
        result = self.smc.detect_smart_structure(self.df, sentiment_score=1)
        
        print(f"SMC Result: {result}")
        
        # Verify
        self.assertEqual(result['signal'], 'buy')
        self.assertEqual(result['type'], 'BOS')
        self.assertIn('Closed above SH', result['reason'])
        self.assertIn('recent_sh', result)
        self.assertEqual(result['recent_sh'], 2030.0)

    def test_qwen_system_prompt(self):
        """Test if Qwen System Prompt contains new instructions"""
        # We test the internal method _get_system_prompt directly
        prompt = self.qwen._get_system_prompt("GOLD")
        
        # Check for key phrases added
        self.assertIn("Trend Cycle Control", prompt)
        self.assertIn("Anti-FOMO", prompt)
        self.assertIn("Supply & Demand Zones", prompt)
        self.assertIn("BOS (Break of Structure)", prompt)
        self.assertIn("Trend Only", prompt)

if __name__ == '__main__':
    unittest.main()
