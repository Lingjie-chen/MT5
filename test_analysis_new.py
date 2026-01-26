
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from trading_bot.analysis.advanced_analysis import AdvancedMarketAnalysisAdapter

def test_analysis():
    # Create dummy data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='15min')
    data = {
        'time': dates,
        'open': np.random.randn(100) + 100,
        'high': np.random.randn(100) + 102,
        'low': np.random.randn(100) + 98,
        'close': np.random.randn(100) + 100,
        'tick_volume': np.random.randint(100, 1000, 100),
        'volume': np.random.randint(100, 1000, 100)
    }
    df = pd.DataFrame(data)
    
    # Ensure high > low
    df['high'] = df[['open', 'close']].max(axis=1) + 1
    df['low'] = df[['open', 'close']].min(axis=1) - 1
    
    analyzer = AdvancedMarketAnalysisAdapter()
    result = analyzer.analyze_full(df)
    
    if result:
        print("Analysis Successful!")
        print(f"Keys: {result.keys()}")
        
        if 'donchian' in result:
            print(f"Donchian: {result['donchian']}")
        else:
            print("ERROR: Donchian missing")
            
        if 'strict_supply_demand' in result:
            print(f"Strict S/D: {result['strict_supply_demand']}")
        else:
            print("ERROR: Strict S/D missing")
            
    else:
        print("Analysis Failed!")

if __name__ == "__main__":
    test_analysis()
