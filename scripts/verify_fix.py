import sys
import os
import pandas as pd
from unittest.mock import MagicMock

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Mock MT5
sys.modules['MetaTrader5'] = MagicMock()

from trading_bot.analysis.advanced_analysis import AdvancedMarketAnalysisAdapter

def verify_fix():
    print("=== 验证 AttributeError 修复 ===\n")
    
    adapter = AdvancedMarketAnalysisAdapter()
    
    # Check if method exists
    if hasattr(adapter, 'detect_structure_points'):
        print("✅ AdvancedMarketAnalysisAdapter 拥有 detect_structure_points 方法")
    else:
        print("❌ AdvancedMarketAnalysisAdapter 仍然缺少 detect_structure_points 方法")
        return

    # Test execution
    try:
        df = pd.DataFrame({
            'high': [10, 12, 11, 13, 12, 14, 13, 15, 14, 16],
            'low':  [8,  10, 9,  11, 10, 12, 11, 13, 12, 14],
            'close': [9, 11, 10, 12, 11, 13, 12, 14, 13, 15],
            'open': [9, 11, 10, 12, 11, 13, 12, 14, 13, 15],
            'volume': [100]*10
        })
        points = adapter.detect_structure_points(df)
        print(f"✅ 方法调用成功，返回 {len(points)} 个结构点")
    except Exception as e:
        print(f"❌ 方法调用失败: {e}")

if __name__ == "__main__":
    verify_fix()
