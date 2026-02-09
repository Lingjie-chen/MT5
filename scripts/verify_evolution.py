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

from trading_bot.analysis.stress_tester import StrategyStressTester
from trading_bot.analysis.rl_weight_optimizer import RLWeightOptimizer
from trading_bot.analysis.trade_performance_analyzer import TradePerformanceAnalyzer

def verify_evolution_modules():
    print("=== Verifying Self-Evolution Modules ===\n")
    
    # 1. Stress Tester
    print("1. Testing Monte Carlo Stress Tester...")
    tester = StrategyStressTester(num_simulations=100)
    trades = [{'profit': 10}, {'profit': -5}, {'profit': 12}, {'profit': -8}, {'profit': 15}] * 10
    result = tester.run_stress_test(trades)
    print(f"   Score: {result['score']}")
    print(f"   Avg DD: {result['avg_drawdown']}")
    print(f"   Prob Loss: {result['probability_of_loss']}")
    
    if result['score'] > 0: print("   ✅ Stress Tester Passed")
    else: print("   ❌ Stress Tester Failed")
    
    # 2. RL Optimizer
    print("\n2. Testing RL Weight Optimizer...")
    rl = RLWeightOptimizer()
    initial_weights = rl.get_weights().copy()
    print(f"   Initial Weights: {initial_weights}")
    
    # Simulate a WIN where Qwen said BUY (Correct) and SMC said SELL (Wrong)
    trade_res = {
        'profit': 50,
        'action': 'BUY',
        'signals_snapshot': {'qwen': 'buy', 'smc': 'sell', 'crt': 'neutral'}
    }
    rl.update_weights(trade_res)
    new_weights = rl.get_weights()
    print(f"   New Weights: {new_weights}")
    
    if new_weights['qwen'] > initial_weights['qwen'] and new_weights['smc'] < initial_weights['smc']:
        print("   ✅ RL Logic Passed (Qwen Up, SMC Down)")
    else:
        print("   ❌ RL Logic Failed")

    # 3. Health Check Logic (Analyzer)
    print("\n3. Testing Health Check Logic...")
    analyzer = TradePerformanceAnalyzer()
    # Simulate bad performance
    bad_trades = [{'profit': -10}, {'profit': -5}, {'profit': -2}] * 10
    health = analyzer.calculate_strategy_health_score(bad_trades)
    print(f"   Health Score: {health['score']}")
    print(f"   Status: {health['status']}")
    print(f"   Action: {health['action']}")
    
    if health['status'] in ['Unhealthy', 'Critical']:
        print("   ✅ Health Check Correctly Identified Failure")
    else:
        print("   ❌ Health Check Failed to Detect Failure")

if __name__ == "__main__":
    verify_evolution_modules()
