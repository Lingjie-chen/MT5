import sys
import os
import logging

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

from trading_bot.risk.dynamic_risk_manager import DynamicRiskManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def show_final_config():
    drm = DynamicRiskManager()
    
    print("\n" + "="*50)
    print("🎯 最终 Basket TP/SL 动态风控配置 (Final Configuration)")
    print("="*50)
    
    print(f"\n1. 多维评分权重 (Analysis Weights):")
    for k, v in drm.weights.items():
        print(f"   - {k.ljust(10)}: {v*100:>3.0f}%")
        
    print(f"\n2. 动态调整系数 (Adjustment Multipliers):")
    print(f"   [策略特性]: 非对称风控 (严防守，宽进攻)")
    print(f"   ------------------------------------------------")
    print(f"   {'Type':<6} | {'Base':<6} | {'Factor':<6} | {'Logic Formula'}")
    print(f"   -------|--------|--------|----------------------")
    print(f"   {'SL':<6} | {drm.sl_multiplier_base:<6} | {drm.sl_multiplier_factor:<6} | Base + (Score * Factor)")
    print(f"   {'TP':<6} | {drm.tp_multiplier_base:<6} | {drm.tp_multiplier_factor:<6} | Base + (Score * Factor)")

    print(f"\n3. 场景模拟 (Simulation):")
    print(f"   假设 AI 建议基础值: Base SL = $100, Base TP = $100")
    
    # Simulation Scenarios
    scenarios = [
        ("极差 (Terrible)", 0.1),
        ("中性 (Neutral)", 0.5),
        ("极好 (Perfect)", 0.9)
    ]
    
    print(f"\n   {'Scenario':<15} | {'Score':<5} | {'Final SL ($)':<12} | {'Final TP ($)':<12} | {'Effect'}")
    print(f"   {'-'*15}|{'-'*7}|{'-'*14}|{'-'*14}|{'-'*20}")
    
    for name, score in scenarios:
        # SL Calc
        sl_mult = drm.sl_multiplier_base + (score * drm.sl_multiplier_factor)
        final_sl = 100 * sl_mult
        
        # TP Calc
        tp_mult = drm.tp_multiplier_base + (score * drm.tp_multiplier_factor)
        final_tp = 100 * tp_mult
        
        effect = []
        if final_sl < 100: effect.append("收紧止损")
        else: effect.append("放宽止损")
        
        if final_tp > 100: effect.append("放大止盈")
        else: effect.append("快速落袋")
        
        print(f"   {name:<15} | {score:<5.1f} | ${final_sl:<11.1f} | ${final_tp:<11.1f} | {', '.join(effect)}")

    print("\n" + "="*50)

if __name__ == "__main__":
    show_final_config()
