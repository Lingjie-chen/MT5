import pandas as pd
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from trading_bot.analysis.advanced_analysis import AdvancedMarketAnalysis

def verify_structure():
    print("=== Verifying SMC Structure Algorithm ===\n")
    analyzer = AdvancedMarketAnalysis()
    
    # Create a synthetic price path with internal structure noise
    # Pattern: Low -> Internal High -> Internal Low -> Higher High (Swing High) -> Low
    prices = [
        100, 98, 102, 101, 103, 102, 105, 104, 108, 107, 106, 105, 100, 95
    ]
    # Indices:
    # 0: 100
    # 1: 98 (Low)
    # 2: 102
    # 3: 101
    # 4: 103
    # 5: 102
    # 6: 105
    # 7: 104
    # 8: 108 (Peak High)
    # 9: 107
    # 10: 106
    # 11: 105
    # 12: 100
    # 13: 95
    
    # We need to construct a DF that produces fractals at specific points.
    # Fractals need 2 bars left and 2 bars right.
    # Let's create a simpler sequence that guarantees fractals.
    
    # L1 (Low) at idx 2: 10, 9, 8, 9, 10
    # H1 (Internal) at idx 6: 10, 11, 12, 11, 10
    # L2 (Internal) at idx 10: 10, 9, 8.5, 9, 10
    # H2 (Swing) at idx 14: 10, 13, 15, 13, 10
    
    highs = [10, 10, 9, 9, 10, 11, 12, 11, 10, 10, 9, 9, 10, 13, 15, 13, 10, 10]
    lows =  [8,  8,  8, 7, 8,  9,  10, 9,  8,  9,  8, 8, 9,  11, 13, 11, 9,  8]
    # Length: 18
    
    # Expected Fractals:
    # i=3: Low=7 (L1)
    # i=6: High=12 (H1)
    # i=10: Low=8 (L2 - higher than L1)
    # i=14: High=15 (H2 - higher than H1)
    
    # Raw Fractals: L1(7), H1(12), L2(8), H2(15)
    # Filtered: L1 -> H1 -> L2 -> H2 (All valid as they alternate)
    
    # What if we have multiple highs?
    # H1(12), H2(13), H3(15) without lows in between?
    # Sequence: ... L(7) ... H(12) ... H(13) ... H(15) ... L(8)
    # The algorithm should pick H(15) as the single Swing High between L(7) and L(8).
    
    df = pd.DataFrame({
        'high': highs,
        'low': lows,
        'open': highs, # dummy
        'close': lows  # dummy
    })
    
    points = analyzer.detect_structure_points(df)
    print(f"Detected {len(points)} points:")
    for p in points:
        print(f" - {p['type']} at {p['price']} (Index {p['index']})")

if __name__ == "__main__":
    verify_structure()
