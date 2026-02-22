"""
MT5品种智能配置框架 - 使用示例

本示例展示如何使用智能交易优化器来自动配置交易参数
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analysis.smart_trading_optimizer import SmartTradingOptimizer
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_1_single_symbol_optimization():
    """示例1: 单品种优化"""
    print("=" * 60)
    print("示例1: 单品种优化")
    print("=" * 60)
    
    optimizer = SmartTradingOptimizer(mt5_initialized=True)
    
    try:
        result = optimizer.optimize_symbol("XAUUSD", force_refresh=False)
        
        if 'error' not in result:
            profile = result['profile']
            params = result['optimized_params']['optimized_parameters']
            
            print(f"\n✅ XAUUSD优化成功!")
            print(f"\n品种特征:")
            print(f"  - 风险等级: {profile['risk_profile']['risk_level']}")
            print(f"  - 波动性分数: {profile['risk_profile']['volatility_score']:.2f}")
            print(f"  - 最优周期: {', '.join(profile['optimal_timeframes'])}")
            
            print(f"\n优化参数:")
            print(f"  - 仓位大小: {params['position_size']:.2f} 手")
            print(f"  - 止损ATR倍数: {params['stop_loss_atr_multiplier']:.2f}")
            print(f"  - 止盈ATR倍数: {params['take_profit_atr_multiplier']:.2f}")
            print(f"  - 风险百分比: {params['risk_per_trade']:.2f}%")
            print(f"  - 最小止盈: {params['min_profit_target']:.2f} ATR")
            
            print(f"\nAI分析:")
            print(f"  - 原因: {result['optimized_params']['reasoning']}")
            print(f"  - 风险评估: {result['optimized_params']['risk_assessment']}")
            print(f"  - 置信度: {result['optimized_params']['confidence_score']:.2f}")
        else:
            print(f"❌ 优化失败: {result['error']}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    optimizer.shutdown()


def example_2_trading_recommendation():
    """示例2: 获取交易建议"""
    print("\n" + "=" * 60)
    print("示例2: 获取交易建议")
    print("=" * 60)
    
    optimizer = SmartTradingOptimizer(mt5_initialized=True)
    
    try:
        recommendation = optimizer.get_trading_recommendation(
            symbol="XAUUSD",
            account_balance=10000.0,
            current_price=2350.50,
            trade_type='buy'
        )
        
        if 'error' not in recommendation:
            print(f"\n✅ XAUUSD交易建议:")
            print(f"\n基本信息:")
            print(f"  - 当前价格: ${recommendation['current_price']:.2f}")
            print(f"  - 交易方向: {recommendation['trade_type'].upper()}")
            
            print(f"\n推荐参数:")
            print(f"  - 仓位大小: {recommendation['recommended_position_size']:.2f} 手")
            print(f"  - 止损价格: ${recommendation['recommended_sl']:.2f}")
            print(f"  - 止盈价格: ${recommendation['recommended_tp']:.2f}")
            print(f"  - 风险百分比: {recommendation['risk_percent']:.2f}%")
            
            print(f"\n距离信息:")
            print(f"  - 止损距离: {recommendation['sl_distance']:.2f} 点")
            print(f"  - 止盈距离: {recommendation['tp_distance']:.2f} 点")
            print(f"  - 风险回报比: {recommendation['rr_ratio']:.2f}")
            
            print(f"\n品种特征:")
            print(f"  - 风险等级: {recommendation['symbol_profile']['risk_level']}")
            print(f"  - 波动性分数: {recommendation['symbol_profile']['volatility_score']:.2f}")
            print(f"  - 最优周期: {', '.join(recommendation['symbol_profile']['optimal_timeframes'])}")
            
            print(f"\n验证结果:")
            validation = recommendation['validation']
            if validation['valid']:
                print(f"  - 状态: ✅ 通过")
            else:
                print(f"  - 状态: ❌ 未通过")
                print(f"  - 原因: {validation['reason']}")
            
            if validation['warnings']:
                print(f"  - 警告:")
                for warning in validation['warnings']:
                    print(f"    • {warning}")
            
            print(f"\n置信度: {recommendation['confidence_score']:.2f}")
        else:
            print(f"❌ 获取建议失败: {recommendation['error']}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    optimizer.shutdown()


def example_3_batch_optimization():
    """示例3: 批量优化多个品种"""
    print("\n" + "=" * 60)
    print("示例3: 批量优化多个品种")
    print("=" * 60)
    
    optimizer = SmartTradingOptimizer(mt5_initialized=True)
    
    symbols = ["XAUUSD", "EURUSD"]
    
    try:
        print(f"\n开始批量优化 {len(symbols)} 个品种...")
        results = optimizer.batch_optimize(symbols=symbols, force_refresh=False)
        
        print(f"\n✅ 批量优化完成!")
        print(f"  - 总品种数: {results['total_symbols']}")
        print(f"  - 成功: {results['successful']}")
        print(f"  - 失败: {results['failed']}")
        print(f"  - 耗时: {results['duration_seconds']:.1f} 秒")
        
        print(f"\n详细结果:")
        for symbol, result in results['results'].items():
            if 'error' not in result:
                params = result['optimized_params']['optimized_parameters']
                print(f"\n  {symbol}:")
                print(f"    仓位: {params['position_size']:.2f} 手")
                print(f"    风险: {params['risk_per_trade']:.2f}%")
                print(f"    置信度: {result['optimized_params']['confidence_score']:.2f}")
            else:
                print(f"\n  {symbol}: ❌ {result['error']}")
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    optimizer.shutdown()


def example_4_cache_management():
    """示例4: 缓存管理"""
    print("\n" + "=" * 60)
    print("示例4: 缓存管理")
    print("=" * 60)
    
    optimizer = SmartTradingOptimizer(mt5_initialized=True)
    
    try:
        cache_info = optimizer.get_cache_status()
        
        print(f"\n缓存信息:")
        print(f"  - 缓存目录: {cache_info['cache_dir']}")
        print(f"  - 过期时间: {cache_info['cache_expiry_hours']} 小时")
        print(f"  - 已缓存品种数: {len(cache_info['symbols'])}")
        
        if cache_info['symbols']:
            print(f"\n已缓存的品种:")
            for symbol_info in cache_info['symbols']:
                symbol = symbol_info['symbol']
                print(f"\n  {symbol}:")
                
                for cache_type in ['profile', 'optimized_params', 'performance']:
                    data = symbol_info.get(cache_type)
                    if data and data['exists']:
                        status = "✅" if data['valid'] else "⚠️"
                        print(f"    {status} {cache_type}: {data['age_hours']:.1f} 小时前")
        
        print(f"\n导出配置...")
        export_file = "export/symbol_configs_export.json"
        os.makedirs("export", exist_ok=True)
        if optimizer.export_configs(export_file):
            print(f"  ✅ 已导出到: {export_file}")
        else:
            print(f"  ❌ 导出失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    optimizer.shutdown()


def example_5_performance_tracking():
    """示例5: 表现跟踪"""
    print("\n" + "=" * 60)
    print("示例5: 表现跟踪")
    print("=" * 60)
    
    optimizer = SmartTradingOptimizer(mt5_initialized=True)
    
    try:
        from datetime import datetime
        
        trade_data = {
            'ticket': 12345,
            'symbol': 'XAUUSD',
            'profit': 50.0,
            'mfe': 100.0,
            'mae': 20.0,
            'opened_at': datetime.now().isoformat()
        }
        
        print(f"\n添加交易记录...")
        print(f"  - 品种: {trade_data['symbol']}")
        print(f"  - 利润: ${trade_data['profit']:.2f}")
        print(f"  - 最大有利偏移: ${trade_data['mfe']:.2f}")
        print(f"  - 最大不利偏移: ${trade_data['mae']:.2f}")
        
        if optimizer.update_performance("XAUUSD", trade_data):
            print(f"  ✅ 表现数据已更新")
            
            perf_stats = optimizer.cache.load_performance_stats("XAUUSD")
            if perf_stats:
                print(f"\n当前表现统计:")
                print(f"  - 总交易数: {perf_stats['total_trades']}")
                print(f"  - 胜率: {perf_stats['win_rate']:.2%}")
                print(f"  - 总利润: ${perf_stats['total_profit']:.2f}")
                print(f"  - 平均MFE: ${perf_stats['avg_mfe']:.2f}")
                print(f"  - 平均MAE: ${perf_stats['avg_mae']:.2f}")
        else:
            print(f"  ❌ 更新失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    optimizer.shutdown()


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("MT5品种智能配置框架 - 使用示例")
    print("=" * 60)
    
    examples = [
        ("单品种优化", example_1_single_symbol_optimization),
        ("获取交易建议", example_2_trading_recommendation),
        ("批量优化", example_3_batch_optimization),
        ("缓存管理", example_4_cache_management),
        ("表现跟踪", example_5_performance_tracking)
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print(f"\n{len(examples)+1}. 运行所有示例")
    print(f"  0. 退出")
    
    choice = input("\n请选择示例 (0-{}): ".format(len(examples)+1))
    
    try:
        choice_int = int(choice)
        
        if choice_int == 0:
            print("退出...")
        elif choice_int <= len(examples):
            examples[choice_int - 1][1]()
        elif choice_int == len(examples) + 1:
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n示例 '{name}' 出错: {e}")
                    continue
        else:
            print("无效选择")
            
    except ValueError:
        print("无效输入")
    
    print("\n" + "=" * 60)
    print("示例运行完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
