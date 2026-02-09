import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging

logger = logging.getLogger("TradePerfAnalyzer")

class TradePerformanceAnalyzer:
    """
    Advanced Trading Record Analysis Module.
    Analyzes historical trades to identify patterns, common failure modes,
    and dynamic optimization thresholds.
    """
    
    def __init__(self, lookback_window: int = 50):
        self.lookback_window = lookback_window
        
    def analyze_trades(self, trades: List[Dict]) -> Dict:
        """
        Analyze a list of trade dictionaries to generate comprehensive performance metrics.
        
        Args:
            trades: List of trade dicts (from DB).
                    Expected keys: 'profit', 'type', 'entry_price', 'close_price', 
                    'open_time', 'close_time', 'reason', 'strategy_data' (optional)
        
        Returns:
            Dict containing classified stats and actionable insights.
        """
        if not trades:
            return self._get_empty_stats()
            
        df = pd.DataFrame(trades)
        
        # Basic Classification
        winning_trades = df[df['profit'] > 0].copy()
        losing_trades = df[df['profit'] <= 0].copy()
        
        # 1. Performance Metrics
        metrics = self._calculate_metrics(df, winning_trades, losing_trades)
        
        # 2. Pattern Recognition (Why did we lose?)
        loss_patterns = self._analyze_loss_patterns(losing_trades)
        
        # 3. Dynamic Thresholds (Optimization)
        dynamic_thresholds = self._calculate_dynamic_thresholds(df)
        
        return {
            "metrics": metrics,
            "loss_analysis": loss_patterns,
            "dynamic_thresholds": dynamic_thresholds,
            "recent_trend": self._analyze_recent_trend(df)
        }
        
    def _calculate_metrics(self, df, winners, losers) -> Dict:
        total_trades = len(df)
        if total_trades == 0: return {}
        
        win_rate = len(winners) / total_trades
        avg_win = winners['profit'].mean() if not winners.empty else 0
        avg_loss = losers['profit'].mean() if not losers.empty else 0
        
        profit_factor = abs(winners['profit'].sum() / losers['profit'].sum()) if losers['profit'].sum() != 0 else 999.0
        
        return {
            "total_trades": total_trades,
            "win_rate": round(win_rate * 100, 2),
            "profit_factor": round(profit_factor, 2),
            "avg_win_usd": round(avg_win, 2),
            "avg_loss_usd": round(avg_loss, 2),
            "risk_reward_ratio": round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0
        }
        
    def _analyze_loss_patterns(self, losers: pd.DataFrame) -> Dict:
        """Identify common characteristics of losing trades"""
        if losers.empty:
            return {"dominant_cause": "None", "risky_hours": []}
            
        patterns = {
            "by_hour": {},
            "by_type": {},
            "common_tags": []
        }
        
        # Time Analysis (Hour of Day)
        if 'open_time' in losers.columns:
            # Handle potential string timestamps or datetime objects
            try:
                losers['hour'] = pd.to_datetime(losers['open_time']).dt.hour
                hourly_losses = losers['hour'].value_counts().head(3).to_dict()
                patterns['risky_hours'] = list(hourly_losses.keys())
            except Exception as e:
                logger.warning(f"Failed to parse time for loss analysis: {e}")
                
        # Type Analysis
        if 'type' in losers.columns:
            patterns['by_type'] = losers['type'].value_counts().to_dict()
            
        return patterns
        
    def _calculate_dynamic_thresholds(self, df: pd.DataFrame) -> Dict:
        """
        Calculate dynamic optimization thresholds based on recent 50 trades.
        Used to adjust opening conditions (e.g., higher RSI threshold if longs are failing).
        """
        # Default thresholds
        thresholds = {
            "min_confidence": 0.75,
            "rsi_buy_max": 70,
            "rsi_sell_min": 30,
            "price_buffer_mult": 1.0 # Multiplier for entry price buffer
        }
        
        if len(df) < 10:
            return thresholds
            
        recent = df.tail(self.lookback_window)
        win_rate = len(recent[recent['profit'] > 0]) / len(recent)
        
        # Adaptive Logic
        
        # 1. If Win Rate is Low (< 40%), Increase Confidence Requirement
        if win_rate < 0.40:
            thresholds["min_confidence"] = 0.85
            thresholds["price_buffer_mult"] = 1.2 # Require 20% more pullback for entry
        elif win_rate > 0.60:
            thresholds["min_confidence"] = 0.65 # Relax slightly to catch more trades
            
        # 2. RSI Optimization (Simplified Simulation)
        # In a real scenario, we would parse the 'technical_signals' stored in trade history
        # Here we apply a heuristic based on overall trend performance if available
        
        return thresholds

    def _analyze_recent_trend(self, df: pd.DataFrame) -> str:
        if len(df) < 5: return "Stable"
        
        recent_pnl = df['profit'].tail(5).sum()
        if recent_pnl < -50: return "Drawdown_Mode" # Optimization: Stop or Reduce Size
        if recent_pnl > 100: return "Winning_Streak"
        return "Normal"

    def _get_empty_stats(self):
        return {
            "metrics": {"total_trades": 0, "win_rate": 0.0},
            "loss_analysis": {},
            "dynamic_thresholds": {"min_confidence": 0.75},
            "recent_trend": "Normal"
        }
