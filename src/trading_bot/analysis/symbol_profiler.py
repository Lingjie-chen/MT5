import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SymbolProfiler:
    """
    品种画像分析器
    分析MT5平台上的交易品种特征，为智能配置引擎提供基础数据
    """

    def __init__(self):
        self.timeframes = [
            mt5.TIMEFRAME_M1,
            mt5.TIMEFRAME_M5,
            mt5.TIMEFRAME_M15,
            mt5.TIMEFRAME_H1,
            mt5.TIMEFRAME_H4,
            mt5.TIMEFRAME_D1
        ]
        self.tf_names = {
            mt5.TIMEFRAME_M1: 'M1',
            mt5.TIMEFRAME_M5: 'M5',
            mt5.TIMEFRAME_M15: 'M15',
            mt5.TIMEFRAME_H1: 'H1',
            mt5.TIMEFRAME_H4: 'H4',
            mt5.TIMEFRAME_D1: 'D1'
        }

    def analyze_symbol(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        分析单个品种的完整画像
        
        Args:
            symbol: 交易品种名称
            days: 历史数据天数
            
        Returns:
            品种画像字典，包含各种市场特征
        """
        logger.info(f"Analyzing symbol profile for {symbol}...")
        
        profile = {
            'symbol': symbol,
            'analyzed_at': datetime.now().isoformat(),
            'days_analyzed': days,
            'symbol_info': self._get_symbol_info(symbol),
            'volatility_metrics': self._analyze_volatility(symbol, days),
            'volume_metrics': self._analyze_volume(symbol, days),
            'price_metrics': self._analyze_price_behavior(symbol, days),
            'spread_metrics': self._analyze_spread(symbol),
            'session_metrics': self._analyze_session_behavior(symbol, days),
            'correlation_metrics': self._calculate_correlations(symbol, days),
            'regime_metrics': self._detect_market_regime(symbol, days)
        }
        
        self._calculate_risk_profile(profile)
        self._calculate_optimal_timeframes(profile)
        
        logger.info(f"Symbol profile analysis completed for {symbol}")
        return profile

    def _get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """获取品种基本信息"""
        info = mt5.symbol_info(symbol)
        if info is None:
            return {}
        
        return {
            'name': info.name,
            'description': info.description,
            'trade_mode': info.trade_mode,
            'digits': info.digits,
            'point': info.point,
            'trade_tick_size': info.trade_tick_size,
            'trade_contract_size': info.trade_contract_size,
            'volume_min': info.volume_min,
            'volume_max': info.volume_max,
            'volume_step': info.volume_step,
            'spread': info.spread,
            'trade_stops_level': info.trade_stops_level,
            'margin_currency': info.currency_margin,
            'profit_currency': info.currency_profit,
            'swap_long': info.swap_long,
            'swap_short': info.swap_short,
            'starting': info.starting,
            'last': info.last,
            'visible': info.visible,
            'session_deals': info.session_deals,
            'session_buy_orders': info.session_buy_orders,
            'session_sell_orders': info.session_sell_orders,
            'session_volume': info.session_volume,
            'session_turnover': info.session_turnover,
            'session_interest': info.session_interest,
            'session_buy_orders_volume': info.session_buy_orders_volume,
            'session_sell_orders_volume': info.session_sell_orders_volume,
            'session_open': info.session_open,
            'session_high': info.session_high,
            'session_low': info.session_low,
            'session_close': info.session_close,
            'bid': info.bid,
            'ask': info.ask,
            'last_volume': info.volume_last,
            'time': info.time,
        }

    def _analyze_volatility(self, symbol: str, days: int) -> Dict[str, Any]:
        """分析波动性特征"""
        volatility_data = {}
        
        for tf in self.timeframes:
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, int(days * 24 * 60 // self._get_minutes(tf)))
            if rates is None or len(rates) < 50:
                continue
                
            df = pd.DataFrame(rates)
            df['returns'] = df['close'].pct_change()
            
            volatility_data[self.tf_names[tf]] = {
                'std_returns': float(df['returns'].std()),
                'avg_true_range': float(self._calculate_atr(df)),
                'high_low_range': float((df['high'] - df['low']).mean()),
                'open_close_range': float((df['close'] - df['open']).abs().mean()),
                'volatility_percent': float((df['high'] - df['low']).mean() / df['close'].mean() * 100)
            }
        
        return volatility_data

    def _analyze_volume(self, symbol: str, days: int) -> Dict[str, Any]:
        """分析交易量特征"""
        volume_data = {}
        
        for tf in self.timeframes:
            rates = mt5.copy_rates_from_pos(symbol, tf, 0, int(days * 24 * 60 // self._get_minutes(tf)))
            if rates is None or len(rates) < 50:
                continue
                
            df = pd.DataFrame(rates)
            vol_col = 'tick_volume' if 'tick_volume' in df.columns else 'volume'
            
            volume_data[self.tf_names[tf]] = {
                'avg_volume': float(df[vol_col].mean()),
                'volume_std': float(df[vol_col].std()),
                'volume_trend': self._calculate_trend(df[vol_col]),
                'volume_volatility': float(df[vol_col].std() / df[vol_col].mean() * 100)
            }
        
        return volume_data

    def _analyze_price_behavior(self, symbol: str, days: int) -> Dict[str, Any]:
        """分析价格行为特征"""
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, days * 24)
        if rates is None or len(rates) < 100:
            return {}
        
        df = pd.DataFrame(rates)
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
        
        return {
            'price_trend': self._calculate_trend(df['close']),
            'avg_hourly_change': float(df['close'].diff().mean()),
            'max_hourly_gain': float(df['close'].diff().max()),
            'max_hourly_loss': float(df['close'].diff().min()),
            'skewness': float(df['returns'].skew()),
            'kurtosis': float(df['returns'].kurtosis()),
            'autocorrelation': float(df['returns'].autocorr(lag=1)),
            'momentum_factor': self._calculate_momentum(df),
            'mean_reversion_factor': self._calculate_mean_reversion(df)
        }

    def _analyze_spread(self, symbol: str) -> Dict[str, Any]:
        """分析点差特征"""
        info = mt5.symbol_info(symbol)
        if info is None:
            return {}
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return {}
        
        spread_pips = (tick.ask - tick.bid) / info.point / 10
        
        return {
            'current_spread': info.spread,
            'spread_pips': float(spread_pips),
            'spread_currency': float(tick.ask - tick.bid),
            'spread_percent': float((tick.ask - tick.bid) / tick.bid * 100),
            'spread_to_atr_ratio': self._get_spread_to_atr_ratio(symbol, info, tick)
        }

    def _analyze_session_behavior(self, symbol: str, days: int) -> Dict[str, Any]:
        """分析交易时段行为"""
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, days * 24)
        if rates is None or len(rates) < 100:
            return {}
        
        df = pd.DataFrame(rates)
        df['hour'] = pd.to_datetime(df['time'], unit='s').dt.hour
        df['returns'] = df['close'].pct_change()
        
        session_stats = {}
        for hour in range(24):
            hour_data = df[df['hour'] == hour]
            if len(hour_data) < 5:
                continue
            
            session_stats[f'hour_{hour:02d}'] = {
                'avg_return': float(hour_data['returns'].mean()),
                'std_return': float(hour_data['returns'].std()),
                'volume': float(hour_data['tick_volume'].mean() if 'tick_volume' in hour_data.columns else hour_data['volume'].mean()),
                'volatility': float(hour_data['high'].sub(hour_data['low']).mean())
            }
        
        return session_stats

    def _calculate_correlations(self, symbol: str, days: int) -> Dict[str, float]:
        """计算与其他品种的相关性"""
        major_symbols = ['GOLD', 'EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD']
        correlations = {}
        
        try:
            base_rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 0, days)
            if base_rates is None or len(base_rates) < 20:
                return correlations
                
            base_df = pd.DataFrame(base_rates)
            base_df['returns'] = base_df['close'].pct_change()
            
            for other_symbol in major_symbols:
                if other_symbol == symbol:
                    continue
                    
                try:
                    other_rates = mt5.copy_rates_from_pos(other_symbol, mt5.TIMEFRAME_D1, 0, days)
                    if other_rates is None or len(other_rates) < 20:
                        continue
                        
                    other_df = pd.DataFrame(other_rates)
                    other_df['returns'] = other_df['close'].pct_change()
                    
                    min_len = min(len(base_df), len(other_df))
                    corr = base_df['returns'].iloc[-min_len:].corr(other_df['returns'].iloc[-min_len:])
                    correlations[other_symbol] = float(corr) if not np.isnan(corr) else 0.0
                except Exception:
                    continue
        except Exception:
            pass
            
        return correlations

    def _detect_market_regime(self, symbol: str, days: int) -> Dict[str, Any]:
        """检测市场状态（趋势/震荡）"""
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, days * 6)
        if rates is None or len(rates) < 100:
            return {}
        
        df = pd.DataFrame(rates)
        df['returns'] = df['close'].pct_change()
        df['sma_short'] = df['close'].rolling(window=20).mean()
        df['sma_long'] = df['close'].rolling(window=50).mean()
        
        regime_signals = []
        for i in range(50, len(df)):
            if df['sma_short'].iloc[i] > df['sma_long'].iloc[i] and df['returns'].iloc[i] > 0:
                regime_signals.append('trending_up')
            elif df['sma_short'].iloc[i] < df['sma_long'].iloc[i] and df['returns'].iloc[i] < 0:
                regime_signals.append('trending_down')
            else:
                regime_signals.append('ranging')
        
        regime_counts = pd.Series(regime_signals).value_counts()
        total = len(regime_signals)
        
        return {
            'trending_up_ratio': float(regime_counts.get('trending_up', 0) / total) if total > 0 else 0.0,
            'trending_down_ratio': float(regime_counts.get('trending_down', 0) / total) if total > 0 else 0.0,
            'ranging_ratio': float(regime_counts.get('ranging', 0) / total) if total > 0 else 0.0,
            'current_regime': regime_signals[-1] if regime_signals else 'unknown'
        }

    def _calculate_risk_profile(self, profile: Dict[str, Any]):
        """计算风险画像"""
        volatility_data = profile.get('volatility_metrics', {}).get('H1', {})
        spread_data = profile.get('spread_metrics', {})
        regime_data = profile.get('regime_metrics', {})
        
        volatility_score = volatility_data.get('volatility_percent', 0)
        spread_ratio = spread_data.get('spread_to_atr_ratio', 0)
        trending_ratio = regime_data.get('trending_up_ratio', 0) + regime_data.get('trending_down_ratio', 0)
        
        risk_level = 'medium'
        if volatility_score > 2.0 or spread_ratio > 0.1:
            risk_level = 'high'
        elif volatility_score < 0.5 and spread_ratio < 0.02:
            risk_level = 'low'
        
        profile['risk_profile'] = {
            'risk_level': risk_level,
            'volatility_score': volatility_score,
            'spread_efficiency': spread_ratio,
            'trend_suitability': trending_ratio,
            'overall_score': self._calculate_overall_risk_score(volatility_score, spread_ratio, trending_ratio)
        }

    def _calculate_optimal_timeframes(self, profile: Dict[str, Any]):
        """计算最优交易周期"""
        volatility_data = profile.get('volatility_metrics', {})
        regime_data = profile.get('regime_metrics', {})
        
        optimal_timeframes = []
        for tf_name, tf_data in volatility_data.items():
            if tf_data.get('volatility_percent', 0) > 0.1 and tf_data.get('volatility_percent', 0) < 1.5:
                optimal_timeframes.append(tf_name)
        
        if regime_data.get('ranging_ratio', 0) > 0.6:
            optimal_timeframes = [tf for tf in optimal_timeframes if tf in ['M5', 'M15']]
        elif regime_data.get('trending_up_ratio', 0) + regime_data.get('trending_down_ratio', 0) > 0.6:
            optimal_timeframes = [tf for tf in optimal_timeframes if tf in ['H1', 'H4', 'D1']]
        
        profile['optimal_timeframes'] = optimal_timeframes if optimal_timeframes else ['H1']

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算平均真实波幅"""
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)
        
        tr1 = high - low
        tr2 = (high - close).abs()
        tr3 = (low - close).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return float(atr.iloc[-1]) if len(atr) > 0 else 0.0

    def _calculate_trend(self, series: pd.Series) -> float:
        """计算趋势强度"""
        if len(series) < 10:
            return 0.0
        x = np.arange(len(series))
        z = np.polyfit(x, series, 1)
        slope = z[0]
        return float(slope / series.mean() * 100) if series.mean() != 0 else 0.0

    def _calculate_momentum(self, df: pd.DataFrame) -> float:
        """计算动量因子"""
        if len(df) < 20:
            return 0.0
        return float((df['close'].iloc[-1] / df['close'].iloc[-20] - 1) * 100)

    def _calculate_mean_reversion(self, df: pd.DataFrame) -> float:
        """计算均值回归因子"""
        if len(df) < 50:
            return 0.0
        returns = df['returns'].dropna()
        return float(returns.mean() / returns.std() * -100) if returns.std() != 0 else 0.0

    def _get_spread_to_atr_ratio(self, symbol: str, info, tick) -> float:
        """计算点差与ATR的比值"""
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 24)
            if rates is None or len(rates) < 14:
                return 0.0
                
            df = pd.DataFrame(rates)
            atr = self._calculate_atr(df)
            spread = tick.ask - tick.bid
            
            return float(spread / atr) if atr != 0 else 0.0
        except Exception:
            return 0.0

    def _calculate_overall_risk_score(self, volatility: float, spread_ratio: float, trending: float) -> float:
        """计算综合风险分数"""
        return float((volatility * 0.5 + spread_ratio * 100 * 0.3 + trending * 100 * 0.2) / 100)

    def _get_minutes(self, timeframe: int) -> int:
        """获取周期对应的分钟数"""
        mapping = {
            mt5.TIMEFRAME_M1: 1,
            mt5.TIMEFRAME_M5: 5,
            mt5.TIMEFRAME_M15: 15,
            mt5.TIMEFRAME_H1: 60,
            mt5.TIMEFRAME_H4: 240,
            mt5.TIMEFRAME_D1: 1440
        }
        return mapping.get(timeframe, 60)

    def get_all_available_symbols(self) -> List[str]:
        """获取所有可用交易品种"""
        symbols = mt5.symbols_get()
        if symbols is None:
            return []
        
        return [s.name for s in symbols if s.visible and s.trade_mode != mt5.SYMBOL_TRADE_MODE_DISABLED]
