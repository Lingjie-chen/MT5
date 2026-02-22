import MetaTrader5 as mt5
import logging
from typing import Dict, Any, Optional
from decimal import Decimal, getcontext
from datetime import datetime

logger = logging.getLogger(__name__)

getcontext().prec = 28


class DynamicPositionManager:
    """
    动态仓位和止盈止损优化器
    根据品种画像、历史表现和市场状态，动态调整仓位大小、止盈止损点位
    """

    def __init__(self, mt5_client):
        self.mt5_client = mt5_client

    def calculate_optimal_position_size(self, symbol: str, 
                                     account_balance: float,
                                     sl_price: float,
                                     current_price: float,
                                     risk_percent: float,
                                     symbol_profile: Optional[Dict[str, Any]] = None) -> float:
        """
        计算最优仓位大小 (使用高精度Decimal计算)
        
        Args:
            symbol: 交易品种
            account_balance: 账户余额
            sl_price: 止损价格
            current_price: 当前价格
            risk_percent: 风险百分比
            symbol_profile: 品种画像 (可选，用于额外调整)
            
        Returns:
            计算后的仓位大小 (手数)
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Cannot get symbol info for {symbol}")
                return 0.01
            
            point = symbol_info.point
            trade_tick_size = symbol_info.trade_tick_size
            trade_contract_size = symbol_info.trade_contract_size
            
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Cannot get tick info for {symbol}")
                return 0.01
            
            current_price = tick.bid if sl_price > current_price else tick.ask
            
            sl_distance = abs(sl_price - current_price)
            
            if sl_distance == 0:
                logger.warning(f"SL distance is 0 for {symbol}, using default 0.01")
                return 0.01
            
            risk_amount = Decimal(str(account_balance)) * Decimal(str(risk_percent)) / Decimal('100')
            
            sl_distance_decimal = Decimal(str(sl_distance))
            contract_size_decimal = Decimal(str(trade_contract_size))
            
            if sl_distance_decimal == 0 or contract_size_decimal == 0:
                logger.error(f"Invalid SL distance or contract size for {symbol}")
                return 0.01
            
            position_size_decimal = risk_amount / (sl_distance_decimal * contract_size_decimal)
            
            position_size_float = float(position_size_decimal)
            
            volume_min = float(symbol_info.volume_min)
            volume_max = float(symbol_info.volume_max)
            volume_step = float(symbol_info.volume_step)
            
            position_size_float = max(volume_min, position_size_float)
            
            if volume_step > 0:
                position_size_float = round(position_size_float / volume_step) * volume_step
            
            position_size_float = min(volume_max, position_size_float)
            
            logger.info(f"Calculated position size for {symbol}: {position_size_float:.2f} lots (Risk: {risk_percent}%, SL Distance: {sl_distance:.2f})")
            return position_size_float
            
        except Exception as e:
            logger.error(f"Error calculating position size for {symbol}: {e}")
            return 0.01

    def calculate_dynamic_stop_loss(self, symbol: str,
                                   current_price: float,
                                   trade_type: str,
                                   symbol_profile: Optional[Dict[str, Any]] = None,
                                   atr_value: Optional[float] = None) -> float:
        """
        计算动态止损位
        
        Args:
            symbol: 交易品种
            current_price: 当前价格
            trade_type: 交易类型 ('buy' or 'sell')
            symbol_profile: 品种画像
            atr_value: ATR值 (可选)
            
        Returns:
            止损价格
        """
        try:
            base_atr = atr_value or self._get_atr(symbol)
            
            if base_atr == 0:
                base_atr = current_price * 0.005
            
            volatility_multiplier = 1.5
            if symbol_profile:
                volatility_metrics = symbol_profile.get('volatility_metrics', {}).get('H1', {})
                volatility_percent = volatility_metrics.get('volatility_percent', 1.0)
                
                if volatility_percent > 2.0:
                    volatility_multiplier = 2.5
                elif volatility_percent > 1.5:
                    volatility_multiplier = 2.0
                elif volatility_percent < 0.5:
                    volatility_multiplier = 1.0
            
            sl_distance = base_atr * volatility_multiplier
            
            if trade_type == 'buy':
                sl_price = current_price - sl_distance
            else:
                sl_price = current_price + sl_distance
            
            logger.info(f"Dynamic SL for {symbol} {trade_type}: {sl_price:.2f} (ATR: {base_atr:.2f}, Multiplier: {volatility_multiplier})")
            return sl_price
            
        except Exception as e:
            logger.error(f"Error calculating dynamic SL for {symbol}: {e}")
            return current_price * 0.99 if trade_type == 'buy' else current_price * 1.01

    def calculate_dynamic_take_profit(self, symbol: str,
                                     entry_price: float,
                                     sl_price: float,
                                     trade_type: str,
                                     symbol_profile: Optional[Dict[str, Any]] = None,
                                     min_rr_ratio: float = 1.5) -> float:
        """
        计算动态止盈位
        
        Args:
            symbol: 交易品种
            entry_price: 入场价格
            sl_price: 止损价格
            trade_type: 交易类型
            symbol_profile: 品种画像
            min_rr_ratio: 最小盈亏比
            
        Returns:
            止盈价格
        """
        try:
            sl_distance = abs(entry_price - sl_price)
            
            spread_metrics = symbol_profile.get('spread_metrics', {}) if symbol_profile else {}
            spread_ratio = spread_metrics.get('spread_to_atr_ratio', 0.05)
            
            volatility_metrics = symbol_profile.get('volatility_metrics', {}).get('H1', {}) if symbol_profile else {}
            volatility_percent = volatility_metrics.get('volatility_percent', 1.0)
            
            base_rr = min_rr_ratio
            if spread_ratio > 0.1:
                base_rr = max(2.5, min_rr_ratio)
            
            if volatility_percent > 2.0:
                base_rr *= 1.5
            elif volatility_percent < 0.5:
                base_rr *= 0.8
            
            tp_distance = sl_distance * base_rr
            
            if trade_type == 'buy':
                tp_price = entry_price + tp_distance
            else:
                tp_price = entry_price - tp_distance
            
            logger.info(f"Dynamic TP for {symbol} {trade_type}: {tp_price:.2f} (RR Ratio: {base_rr:.2f})")
            return tp_price
            
        except Exception as e:
            logger.error(f"Error calculating dynamic TP for {symbol}: {e}")
            return entry_price * 1.02 if trade_type == 'buy' else entry_price * 0.98

    def calculate_basket_tp(self, symbol: str,
                          total_lots: float,
                          avg_entry_price: float,
                          current_price: float,
                          symbol_profile: Optional[Dict[str, Any]] = None,
                          historical_mfe: Optional[float] = None) -> float:
        """
        计算组合止盈金额 (基于总持仓量的动态TP)
        
        Args:
            symbol: 交易品种
            total_lots: 总持仓手数
            avg_entry_price: 平均入场价
            current_price: 当前价格
            symbol_profile: 品种画像
            historical_mfe: 历史平均MFE (可选)
            
        Returns:
            组合止盈金额 (USD)
        """
        try:
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Cannot get symbol info for {symbol}")
                return 50.0
            
            contract_size = symbol_info.trade_contract_size
            
            atr_value = self._get_atr(symbol)
            if atr_value == 0:
                atr_value = current_price * 0.01
            
            base_distance = atr_value * 2.0
            
            volatility_metrics = symbol_profile.get('volatility_metrics', {}).get('H1', {}) if symbol_profile else {}
            volatility_percent = volatility_metrics.get('volatility_percent', 1.0)
            
            if volatility_percent > 2.0:
                base_distance *= 2.0
            elif volatility_percent < 0.5:
                base_distance *= 0.8
            
            if historical_mfe and historical_mfe > 0:
                max_mfe_distance = historical_mfe * 0.8
                base_distance = min(base_distance, max_mfe_distance)
            
            estimated_profit_per_lot = base_distance * contract_size
            basket_tp = total_lots * estimated_profit_per_lot
            
            min_basket_tp = 20.0
            max_basket_tp = 500.0
            
            basket_tp = max(min_basket_tp, min(max_basket_tp, basket_tp))
            
            logger.info(f"Basket TP for {symbol}: ${basket_tp:.2f} (Total Lots: {total_lots:.2f}, Distance: {base_distance:.2f})")
            return basket_tp
            
        except Exception as e:
            logger.error(f"Error calculating basket TP for {symbol}: {e}")
            return 50.0

    def optimize_entry_exit_levels(self, 
                                   symbol: str,
                                   market_data: Dict[str, Any],
                                   symbol_profile: Optional[Dict[str, Any]] = None,
                                   historical_performance: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        综合优化入场、止损、止盈点位
        
        Args:
            symbol: 交易品种
            market_data: 市场数据
            symbol_profile: 品种画像
            historical_performance: 历史表现
            
        Returns:
            包含优化后的入场、止损、止盈点位的字典
        """
        current_price = market_data.get('current_price', 0)
        trade_type = market_data.get('trade_type', 'buy')
        
        if current_price == 0:
            logger.error(f"Invalid current price for {symbol}")
            return {}
        
        atr_value = self._get_atr(symbol)
        
        sl_price = self.calculate_dynamic_stop_loss(
            symbol, current_price, trade_type, symbol_profile, atr_value
        )
        
        tp_price = self.calculate_dynamic_take_profit(
            symbol, current_price, sl_price, trade_type, symbol_profile
        )
        
        optimized_levels = {
            'symbol': symbol,
            'current_price': current_price,
            'trade_type': trade_type,
            'optimized_entry': current_price,
            'optimized_sl': sl_price,
            'optimized_tp': tp_price,
            'sl_distance': abs(current_price - sl_price),
            'tp_distance': abs(tp_price - current_price),
            'rr_ratio': abs(tp_price - current_price) / abs(current_price - sl_price) if current_price != sl_price else 0,
            'atr_value': atr_value,
            'optimized_at': datetime.now().isoformat()
        }
        
        return optimized_levels

    def get_risk_adjusted_position_size(self, 
                                       symbol: str,
                                       account_balance: float,
                                       current_price: float,
                                       symbol_profile: Optional[Dict[str, Any]] = None,
                                       trade_confidence: float = 0.7) -> float:
        """
        根据风险画像和交易置信度调整仓位
        
        Args:
            symbol: 交易品种
            account_balance: 账户余额
            current_price: 当前价格
            symbol_profile: 品种画像
            trade_confidence: 交易置信度 (0-1)
            
        Returns:
            调整后的风险百分比
        """
        base_risk = 1.0
        
        if symbol_profile:
            risk_profile = symbol_profile.get('risk_profile', {})
            risk_level = risk_profile.get('risk_level', 'medium')
            
            if risk_level == 'high':
                base_risk = 0.5
            elif risk_level == 'low':
                base_risk = 2.0
        
        confidence_multiplier = 0.5 + trade_confidence
        
        adjusted_risk = base_risk * confidence_multiplier
        
        adjusted_risk = max(0.5, min(3.0, adjusted_risk))
        
        logger.info(f"Risk adjusted for {symbol}: {adjusted_risk:.2f}% (Base: {base_risk:.2f}%, Confidence: {trade_confidence:.2f})")
        return adjusted_risk

    def _get_atr(self, symbol: str, period: int = 14) -> float:
        """
        计算ATR (平均真实波幅)
        
        Args:
            symbol: 交易品种
            period: ATR周期
            
        Returns:
            ATR值
        """
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, period + 10)
            if rates is None or len(rates) < period + 1:
                return 0.0
            
            import pandas as pd
            
            df = pd.DataFrame(rates)
            df['high'] = df['high']
            df['low'] = df['low']
            df['close'] = df['close'].shift(1)
            
            df['tr1'] = df['high'] - df['low']
            df['tr2'] = (df['high'] - df['close']).abs()
            df['tr3'] = (df['low'] - df['close']).abs()
            
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            
            atr = df['tr'].rolling(window=period).mean().iloc[-1]
            
            return float(atr) if not pd.isna(atr) else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating ATR for {symbol}: {e}")
            return 0.0

    def validate_entry_conditions(self, 
                                  symbol: str,
                                  entry_price: float,
                                  sl_price: float,
                                  tp_price: float,
                                  account_balance: float,
                                  min_rr_ratio: float = 1.5) -> Dict[str, Any]:
        """
        验证入场条件是否合理
        
        Args:
            symbol: 交易品种
            entry_price: 入场价格
            sl_price: 止损价格
            tp_price: 止盈价格
            account_balance: 账户余额
            min_rr_ratio: 最小盈亏比
            
        Returns:
            验证结果字典
        """
        validation = {
            'valid': True,
            'reason': '',
            'warnings': []
        }
        
        try:
            sl_distance = abs(entry_price - sl_price)
            tp_distance = abs(tp_price - entry_price)
            
            if sl_distance == 0:
                validation['valid'] = False
                validation['reason'] = 'Stop loss distance is zero'
                return validation
            
            rr_ratio = tp_distance / sl_distance
            
            if rr_ratio < min_rr_ratio:
                validation['valid'] = False
                validation['reason'] = f'Risk/Reward ratio ({rr_ratio:.2f}) is below minimum ({min_rr_ratio})'
                return validation
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info:
                point = symbol_info.point
                
                if sl_distance < point * 10:
                    validation['warnings'].append(f'Stop loss distance ({sl_distance:.2f}) is too tight (minimum: {point * 10:.2f})')
            
            if account_balance < 100:
                validation['warnings'].append('Low account balance, consider reducing position size')
            
            if validation['warnings']:
                logger.warning(f"Entry validation warnings for {symbol}: {validation['warnings']}")
            else:
                logger.info(f"Entry validation passed for {symbol}: RR={rr_ratio:.2f}")
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating entry conditions for {symbol}: {e}")
            validation['valid'] = False
            validation['reason'] = f'Validation error: {str(e)}'
            return validation
