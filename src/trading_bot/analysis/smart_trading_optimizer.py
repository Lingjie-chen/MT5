import MetaTrader5 as mt5
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .symbol_profiler import SymbolProfiler
from .ai_strategy_optimizer import AIStrategyOptimizer
from .dynamic_position_manager import DynamicPositionManager
from .symbol_config_cache import SymbolConfigCache

logger = logging.getLogger(__name__)


class SmartTradingOptimizer:
    """
    MT5品种智能配置系统 - 主集成类
    
    整合所有组件，提供统一的接口来自动化品种分析和参数优化
    """

    def __init__(self, mt5_initialized: bool = True):
        """
        初始化智能交易优化器
        
        Args:
            mt5_initialized: MT5是否已初始化
        """
        if mt5_initialized and not mt5.initialize():
            logger.error("Failed to initialize MT5")
            raise RuntimeError("MT5 initialization failed")
        
        self.profiler = SymbolProfiler()
        self.ai_optimizer = AIStrategyOptimizer(model_name="qwen")
        self.position_manager = DynamicPositionManager(self)
        self.cache = SymbolConfigCache()
        
        logger.info("Smart Trading Optimizer initialized")

    def optimize_symbol(self, 
                        symbol: str,
                        force_refresh: bool = False,
                        analysis_days: int = 30) -> Dict[str, Any]:
        """
        优化单个品种的交易参数
        
        Args:
            symbol: 交易品种名称
            force_refresh: 是否强制重新分析
            analysis_days: 历史数据分析天数
            
        Returns:
            包含品种画像和优化参数的完整结果
        """
        logger.info(f"Starting optimization for {symbol}...")
        
        result = {
            'symbol': symbol,
            'optimized_at': datetime.now().isoformat(),
            'profile': None,
            'optimized_params': None,
            'performance_stats': None
        }
        
        try:
            cached_profile = self.cache.load_symbol_profile(symbol, force_refresh=force_refresh)
            
            if not cached_profile or force_refresh:
                logger.info(f"Analyzing symbol profile for {symbol}...")
                profile = self.profiler.analyze_symbol(symbol, days=analysis_days)
                self.cache.save_symbol_profile(symbol, profile)
                result['profile'] = profile
            else:
                logger.info(f"Using cached profile for {symbol}")
                result['profile'] = cached_profile
            
            cached_params = self.cache.load_optimized_params(symbol, force_refresh=force_refresh)
            
            if not cached_params or force_refresh:
                logger.info(f"Optimizing strategy parameters for {symbol}...")
                performance_stats = self.cache.load_performance_stats(symbol)
                
                optimized_params = self.ai_optimizer.optimize_strategy(
                    result['profile'],
                    performance_stats
                )
                
                if 'optimized_parameters' not in optimized_params:
                    optimized_params = self.ai_optimizer._generate_fallback_params(result['profile'])
                
                self.cache.save_optimized_params(symbol, optimized_params)
                result['optimized_params'] = optimized_params
            else:
                logger.info(f"Using cached optimized params for {symbol}")
                result['optimized_params'] = cached_params
            
            result['performance_stats'] = self.cache.load_performance_stats(symbol)
            
            logger.info(f"Optimization completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing {symbol}: {e}")
            result['error'] = str(e)
            return result

    def batch_optimize(self, 
                       symbols: Optional[List[str]] = None,
                       force_refresh: bool = False) -> Dict[str, Any]:
        """
        批量优化多个品种
        
        Args:
            symbols: 品种列表，None表示自动发现所有可用品种
            force_refresh: 是否强制重新分析
            
        Returns:
            批量优化结果
        """
        if symbols is None:
            symbols = self.profiler.get_all_available_symbols()
            logger.info(f"Auto-discovered {len(symbols)} available symbols")
        
        logger.info(f"Starting batch optimization for {len(symbols)} symbols...")
        
        results = {
            'started_at': datetime.now().isoformat(),
            'total_symbols': len(symbols),
            'successful': 0,
            'failed': 0,
            'results': {}
        }
        
        for symbol in symbols:
            try:
                result = self.optimize_symbol(symbol, force_refresh=force_refresh)
                
                if 'error' in result:
                    results['failed'] += 1
                else:
                    results['successful'] += 1
                
                results['results'][symbol] = result
                
            except Exception as e:
                logger.error(f"Failed to optimize {symbol}: {e}")
                results['failed'] += 1
                results['results'][symbol] = {
                    'symbol': symbol,
                    'error': str(e)
                }
        
        results['completed_at'] = datetime.now().isoformat()
        results['duration_seconds'] = (
            datetime.fromisoformat(results['completed_at']) - 
            datetime.fromisoformat(results['started_at'])
        ).total_seconds()
        
        logger.info(f"Batch optimization completed: {results['successful']} successful, {results['failed']} failed")
        
        return results

    def get_trading_recommendation(self, 
                                  symbol: str,
                                  account_balance: float,
                                  current_price: float,
                                  trade_type: str = 'buy') -> Dict[str, Any]:
        """
        获取交易建议（包含所有参数）
        
        Args:
            symbol: 交易品种
            account_balance: 账户余额
            current_price: 当前价格
            trade_type: 交易类型 ('buy' or 'sell')
            
        Returns:
            交易建议字典
        """
        logger.info(f"Getting trading recommendation for {symbol}...")
        
        result = self.optimize_symbol(symbol, force_refresh=False)
        
        if 'error' in result:
            logger.error(f"Cannot get recommendation for {symbol}: {result['error']}")
            return {'error': result['error']}
        
        profile = result['profile']
        optimized_params = result['optimized_params'].get('optimized_parameters', {})
        
        try:
            atr_value = self.position_manager._get_atr(symbol)
            
            sl_price = self.position_manager.calculate_dynamic_stop_loss(
                symbol, current_price, trade_type, profile, atr_value
            )
            
            tp_price = self.position_manager.calculate_dynamic_take_profit(
                symbol, current_price, sl_price, trade_type, profile
            )
            
            risk_percent = optimized_params.get('risk_per_trade', 1.0)
            position_size = self.position_manager.calculate_optimal_position_size(
                symbol, account_balance, sl_price, current_price, risk_percent, profile
            )
            
            validation = self.position_manager.validate_entry_conditions(
                symbol, current_price, sl_price, tp_price, account_balance
            )
            
            recommendation = {
                'symbol': symbol,
                'generated_at': datetime.now().isoformat(),
                'trade_type': trade_type,
                'current_price': current_price,
                'recommended_position_size': position_size,
                'recommended_sl': sl_price,
                'recommended_tp': tp_price,
                'risk_percent': risk_percent,
                'sl_distance': abs(current_price - sl_price),
                'tp_distance': abs(tp_price - current_price),
                'rr_ratio': abs(tp_price - current_price) / abs(current_price - sl_price),
                'validation': validation,
                'symbol_profile': {
                    'risk_level': profile.get('risk_profile', {}).get('risk_level', 'unknown'),
                    'volatility_score': profile.get('risk_profile', {}).get('volatility_score', 0),
                    'optimal_timeframes': profile.get('optimal_timeframes', [])
                },
                'optimized_params': optimized_params,
                'confidence_score': result['optimized_params'].get('confidence_score', 0.5)
            }
            
            logger.info(f"Trading recommendation generated for {symbol}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation for {symbol}: {e}")
            return {'error': str(e)}

    def update_performance(self, symbol: str, trade_data: Dict[str, Any]) -> bool:
        """
        更新品种的历史表现数据
        
        Args:
            symbol: 交易品种
            trade_data: 交易数据
            
        Returns:
            是否更新成功
        """
        try:
            performance_stats = self.cache.load_performance_stats(symbol) or {}
            
            if 'trades' not in performance_stats:
                performance_stats['trades'] = []
            
            performance_stats['trades'].append(trade_data)
            
            trades = performance_stats['trades']
            
            wins = [t for t in trades if t.get('profit', 0) > 0]
            losses = [t for t in trades if t.get('profit', 0) <= 0]
            
            performance_stats['total_trades'] = len(trades)
            performance_stats['win_rate'] = len(wins) / len(trades) if trades else 0
            performance_stats['total_profit'] = sum(t.get('profit', 0) for t in trades)
            performance_stats['avg_profit'] = sum(t.get('profit', 0) for t in wins) / len(wins) if wins else 0
            performance_stats['avg_loss'] = sum(t.get('profit', 0) for t in losses) / len(losses) if losses else 0
            
            mfe_values = [t.get('mfe', 0) for t in trades if t.get('mfe') is not None]
            mae_values = [t.get('mae', 0) for t in trades if t.get('mae') is not None]
            
            performance_stats['avg_mfe'] = sum(mfe_values) / len(mfe_values) if mfe_values else 0
            performance_stats['avg_mae'] = sum(mae_values) / len(mae_values) if mae_values else 0
            
            performance_stats['last_updated'] = datetime.now().isoformat()
            
            self.cache.save_performance_stats(symbol, performance_stats)
            
            logger.info(f"Updated performance stats for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating performance for {symbol}: {e}")
            return False

    def get_cache_status(self) -> Dict[str, Any]:
        """
        获取缓存状态
        
        Returns:
            缓存状态信息
        """
        return self.cache.get_cache_info()

    def clear_all_cache(self):
        """清除所有缓存"""
        self.cache.clear_cache()
        logger.info("All cache cleared")

    def export_configs(self, output_file: str) -> bool:
        """
        导出所有配置到文件
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            是否导出成功
        """
        return self.cache.export_config(output_file)

    def import_configs(self, input_file: str, overwrite: bool = False) -> bool:
        """
        从文件导入配置
        
        Args:
            input_file: 输入文件路径
            overwrite: 是否覆盖现有配置
            
        Returns:
            是否导入成功
        """
        return self.cache.import_config(input_file, overwrite)

    def shutdown(self):
        """关闭优化器"""
        if mt5.initialize():
            mt5.shutdown()
        logger.info("Smart Trading Optimizer shutdown")


def main():
    """测试示例"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("=== MT5 Smart Trading Optimizer Demo ===\n")
    
    try:
        optimizer = SmartTradingOptimizer(mt5_initialized=True)
        
        print("1. Getting trading recommendation for XAUUSD...")
        recommendation = optimizer.get_trading_recommendation(
            symbol="XAUUSD",
            account_balance=10000.0,
            current_price=2350.50,
            trade_type='buy'
        )
        
        if 'error' not in recommendation:
            print(f"\n✅ Recommendation for XAUUSD:")
            print(f"   - Position Size: {recommendation['recommended_position_size']:.2f} lots")
            print(f"   - Stop Loss: ${recommendation['recommended_sl']:.2f}")
            print(f"   - Take Profit: ${recommendation['recommended_tp']:.2f}")
            print(f"   - Risk/Reward: {recommendation['rr_ratio']:.2f}")
            print(f"   - Risk Level: {recommendation['symbol_profile']['risk_level']}")
            print(f"   - Confidence: {recommendation['confidence_score']:.2f}")
        else:
            print(f"❌ Error: {recommendation['error']}")
        
        print("\n2. Getting cache status...")
        cache_status = optimizer.get_cache_status()
        print(f"   - Cached symbols: {len(cache_status.get('symbols', []))}")
        
        print("\n3. Demo completed!")
        
        optimizer.shutdown()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
