#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os

# 创建测试数据
np.random.seed(42)
dates = pd.date_range(start='2023-01-01', periods=1000)
close_prices = np.cumsum(np.random.normal(0, 0.0005, 1000) + 100
high_prices = close_prices + np.random.normal(0, 0.002, 1000)
low_prices = close_prices - np.random.normal(0, 0.001, 1000)
volumes = np.random.randint(100, 1000, 1000)
opens = close_prices * (1 + np.random.uniform(-0.003, 0.003, 1000))
close_prices = close_prices * (1 + np.random.uniform(-0.002, 0.002, 1000))

df = pd.DataFrame({
    'open': opens,
    'high': high_prices,
    'low': low_prices,
    'close': close_prices,
    'volume': volumes,
    'time': dates
})

# 测试因子发现
print("="*60)
print("测试大模型因子发现系统")
print("="*60)
print()

system = FactorDiscovery(n_features=20, feature_type='all', selection_method='hybrid', use_llm=False)

# 分析市场
print("分析市场...")
factors = system.discover_factors(df, df['close'])

print(f"\n发现 {len(factors.get('selected_features', [])) 个因子")

# 获取排名前10的因子
top_10_factors = system.get_factors(top_n=10)
print(f"\n排名前10的因子:")
for factor_name, factor_data in top_10_factors.items():
    print(f"  {factor_name}:")
    print(f"    排名: {factor_data['rank']}")
    print(f"    评分: {factor_data['scores']}")
    print(f"    平均得分: {factor_data['average_score']:.4f}")
    print(f"    LLM增强: {factor_data.get('llm_enhanced', '否')}")
    print()

# 导出因子
system.export_factors('factor_discovery_results.json')

print("\n" + "="*60)
print("测试完成!")
print("="*60)