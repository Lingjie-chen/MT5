import sys
import os
import logging

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Mock MT5 and other dependencies to avoid runtime errors
from unittest.mock import MagicMock
sys.modules['MetaTrader5'] = MagicMock()

# Import the strategy
from trading_bot.strategies.grid_strategy import KalmanGridStrategy

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("VerifyUpdate")

def verify_basket_update():
    print("=== 开始验证 Basket TP/SL 参数覆盖逻辑 ===\n")

    # 1. 初始化策略实例
    strategy = KalmanGridStrategy("XAUUSD", 123456)
    
    # 2. 模拟“上一轮”/“原有”交易设置
    # 假设旧的设置是: TP = $10.0, SL = -$50.0
    strategy.dynamic_global_tp = 10.0
    strategy.dynamic_tp_long = 10.0
    strategy.dynamic_tp_short = 10.0
    strategy.dynamic_sl_long = -50.0
    strategy.dynamic_sl_short = -50.0
    
    print(f"1. [初始状态] 原有参数:")
    print(f"   - Basket TP (Long):  ${strategy.dynamic_tp_long}")
    print(f"   - Basket TP (Short): ${strategy.dynamic_tp_short}")
    print(f"   - Basket SL (Long):  ${strategy.dynamic_sl_long}")
    print(f"   - Basket SL (Short): ${strategy.dynamic_sl_short}")
    print("-" * 40)

    # 3. 模拟新一轮 AI 分析输出
    # 假设 AI 给出的新建议是: TP = $25.0, SL = $100.0 (输入通常为正数，代表亏损金额)
    ai_output = {
        "dynamic_basket_tp": 25.0,
        "dynamic_basket_sl": 100.0
    }
    print(f"2. [新一轮分析] AI 输出新参数:")
    print(f"   - Dynamic Basket TP: ${ai_output['dynamic_basket_tp']}")
    print(f"   - Dynamic Basket SL: ${ai_output['dynamic_basket_sl']}")
    print("-" * 40)

    # 4. 模拟 main.py 中的更新逻辑
    # 逻辑参考 main.py L3321-L3326
    basket_tp = ai_output.get('dynamic_basket_tp')
    basket_sl = ai_output.get('dynamic_basket_sl')
    
    print(f"3. [执行更新] 调用 update_dynamic_params...")
    strategy.update_dynamic_params(
        basket_tp=basket_tp,
        basket_sl_long=basket_sl,  # main.py 将同一个 SL 值传给 Long
        basket_sl_short=basket_sl, # main.py 将同一个 SL 值传给 Short
        lock_trigger=None
    )
    print("-" * 40)

    # 5. 验证结果
    print(f"4. [最终状态] 更新后参数:")
    print(f"   - Basket TP (Long):  ${strategy.dynamic_tp_long}")
    print(f"   - Basket TP (Short): ${strategy.dynamic_tp_short}")
    print(f"   - Basket SL (Long):  ${strategy.dynamic_sl_long}")
    print(f"   - Basket SL (Short): ${strategy.dynamic_sl_short}")
    
    # 断言检查
    success = True
    # TP 检查
    if strategy.dynamic_tp_long != 25.0 or strategy.dynamic_tp_short != 25.0:
        print("❌ 错误: TP 未正确更新!")
        success = False
    
    # SL 检查 (注意符号，应为负数)
    if strategy.dynamic_sl_long != -100.0 or strategy.dynamic_sl_short != -100.0:
        print("❌ 错误: SL 未正确更新! (期望为 -100.0)")
        success = False
        
    print("\n" + "=" * 40)
    if success:
        print("✅ 验证通过: 新参数已成功完全覆盖原有设置。")
        print("   注意: SL 输入的正数已正确转换为负数存储。")
    else:
        print("❌ 验证失败: 参数覆盖逻辑存在问题。")
    print("=" * 40)

if __name__ == "__main__":
    verify_basket_update()
