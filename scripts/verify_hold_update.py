import sys
import os
import logging
from unittest.mock import MagicMock

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

# Mock MT5
sys.modules['MetaTrader5'] = MagicMock()

from trading_bot.strategies.grid_strategy import KalmanGridStrategy

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("VerifyHoldUpdate")

def verify_hold_update():
    print("=== 验证 HOLD 状态下 Basket 参数更新逻辑 ===\n")

    # 1. 初始化策略
    strategy = KalmanGridStrategy("XAUUSD", 123456)
    
    # 初始状态
    strategy.dynamic_global_tp = 10.0
    strategy.dynamic_sl_long = -50.0
    
    print(f"1. [初始状态] Basket TP: ${strategy.dynamic_global_tp}, SL: ${strategy.dynamic_sl_long}")

    # 2. 模拟 AI 返回 (Action: HOLD, 但有新的 Basket 参数)
    ai_response = {
        "action": "hold",
        "position_management": {
            "dynamic_basket_tp": 88.0,
            "dynamic_basket_sl": 200.0
        },
        "grid_config": {},
        "strategy_rationale": "Hold current positions but tighten risk parameters."
    }
    
    print(f"2. [AI 响应] Action: {ai_response['action']}")
    print(f"   - New Basket TP: {ai_response['position_management']['dynamic_basket_tp']}")
    print(f"   - New Basket SL: {ai_response['position_management']['dynamic_basket_sl']}")

    # 3. 模拟 main.py 中的提取与更新逻辑
    pos_mgmt = ai_response.get('position_management', {})
    if pos_mgmt:
        basket_tp = pos_mgmt.get('dynamic_basket_tp')
        basket_sl = pos_mgmt.get('dynamic_basket_sl')
        
        print(f"3. [执行更新] 调用 update_dynamic_params...")
        strategy.update_dynamic_params(
            basket_tp=basket_tp,
            basket_sl_long=basket_sl,
            basket_sl_short=basket_sl,
            lock_trigger=None
        )

    # 4. 验证结果
    print(f"4. [最终状态] Basket TP: ${strategy.dynamic_global_tp}, SL: ${strategy.dynamic_sl_long}")
    
    if strategy.dynamic_global_tp == 88.0 and strategy.dynamic_sl_long == -200.0:
        print("\n✅ 验证成功: 即使在 HOLD 状态下，参数也已更新。")
    else:
        print("\n❌ 验证失败: 参数未更新。")

if __name__ == "__main__":
    verify_hold_update()
