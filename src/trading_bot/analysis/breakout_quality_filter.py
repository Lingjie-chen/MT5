import pandas as pd
import numpy as np
import logging
from datetime import datetime, time as dtime
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List

logger = logging.getLogger("BreakoutQuality")

@dataclass
class QualityResult:
    is_valid: bool
    score: float # 0-100 score contribution
    details: List[str]
    metrics: Dict[str, float]

class BreakoutQualityFilter:
    """
    SMC Breakout Quality Filter Module
    Implements 5-layer validation pipeline for ORB strategies:
    1. Kill Zone (Time)
    2. RVOL (Volume)
    3. Displacement (Price Action)
    4. FVG Formation (Structure)
    5. ATR Checks (Volatility)
    """
    
    def __init__(self):
        # Kill Zones (UTC) - London & NY Open
        self.kill_zones = [
            (dtime(7, 0), dtime(10, 0)),  # London: 07:00 - 10:00
            (dtime(13, 0), dtime(16, 0))  # NY: 13:00 - 16:00
        ]
        
        # Thresholds
        self.rvol_threshold = 1.5
        self.displacement_threshold = 0.60
        self.atr_period = 14
        
    def check_kill_zone(self, current_time: datetime) -> Tuple[bool, str]:
        """Gate 1: Check if current time is within high-probability trading windows."""
        t = current_time.time()
        for start, end in self.kill_zones:
            if start <= t <= end:
                return True, f"In Kill Zone ({start.strftime('%H:%M')}-{end.strftime('%H:%M')})"
        return False, "Outside Kill Zones (Low Probability)"

    def calculate_rvol(self, df: pd.DataFrame, period=20) -> float:
        """Gate 2: Relative Volume Calculation."""
        if len(df) < period + 1:
            return 1.0
            
        # Current volume (breakout candle)
        curr_vol = df['tick_volume'].iloc[-1]
        
        # Average of previous N candles (excluding current)
        avg_vol = df['tick_volume'].iloc[-(period+1):-1].mean()
        
        if avg_vol == 0: return 0.0
        
        return curr_vol / avg_vol

    def calculate_displacement_ratio(self, candle: pd.Series) -> float:
        """Gate 3: Calculate Body-to-Range Ratio."""
        high = candle['high']
        low = candle['low']
        open_px = candle['open']
        close_px = candle['close']
        
        total_range = high - low
        body_size = abs(close_px - open_px)
        
        if total_range == 0: return 0.0
        
        return body_size / total_range

    def detect_breakout_fvg(self, df: pd.DataFrame, signal_type: str) -> bool:
        """
        Gate 4: Check if the breakout leg CREATED an FVG.
        
        Optimized Logic:
        - For BUY Breakout: Check if Low[i] > High[i-2] (Bullish FVG)
        - For SELL Breakout: Check if High[i] < Low[i-2] (Bearish FVG)
        
        We check the last complete candle (breakout candle).
        """
        if len(df) < 3: return False
        
        i = -1 # Last candle index
        
        # Extract OHLC
        curr_low = df['low'].iloc[i]
        curr_high = df['high'].iloc[i]
        prev_2_high = df['high'].iloc[i-2]
        prev_2_low = df['low'].iloc[i-2]
        point = 0.00001 # Tolerance
        
        if signal_type == 'buy':
            # Bullish FVG: Current Low > Prev-2 High
            if curr_low > prev_2_high + (3 * point):
                return True
        elif signal_type == 'sell':
            # Bearish FVG: Current High < Prev-2 Low
            if curr_high < prev_2_low - (3 * point):
                return True
                
        return False

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Helper: Calculate latest ATR."""
        if len(df) < period + 1: return 0.0
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        # TR calculation
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        return atr

    def detect_breaker_block(self, df: pd.DataFrame, breakout_idx: int, signal_type: str) -> float:
        """
        Identify the invalidation level (Breaker Block) for a breakout.
        
        Logic:
        - BUY Breakout: The LOW of the breakout impulse (the candle that started the move or the breakout candle itself).
        - SELL Breakout: The HIGH of the breakout impulse.
        
        Returns the price level to exit if breached.
        """
        if breakout_idx >= len(df) or breakout_idx < 0:
            return 0.0
            
        # For simplicity, we use the Low/High of the breakout candle itself 
        # as the tightest validation point for an Impulse.
        candle = df.iloc[breakout_idx]
        
        if signal_type == 'buy':
            return candle['low']
        else:
            return candle['high']

    def validate_breakout_quality(self, df: pd.DataFrame, signal_type: str, current_time: datetime) -> QualityResult:
        """
        Master Pipeline: Validates a breakout signal through all gates.
        Returns detailed score and metrics.
        """
        details = []
        metrics = {}
        score = 0.0
        
        # 1. Kill Zone Check (Pass/Fail)
        in_zone, zone_msg = self.check_kill_zone(current_time)
        metrics['kill_zone'] = 1.0 if in_zone else 0.0
        if not in_zone:
            details.append(f"❌ {zone_msg}")
            # We don't return immediately, allowing other metrics to be calculated for analysis,
            # but score will be heavily impacted.
        else:
            details.append(f"✅ {zone_msg}")
            score += 10

        # 2. RVOL Check (0-10 pts)
        rvol = self.calculate_rvol(df)
        metrics['rvol'] = rvol
        if rvol >= self.rvol_threshold:
            score += 10
            details.append(f"✅ High Volume (RVOL {rvol:.2f} >= {self.rvol_threshold})")
        else:
            # Partial credit for > 1.0
            if rvol > 1.0:
                score += 5
                details.append(f"⚠️ Moderate Volume (RVOL {rvol:.2f})")
            else:
                details.append(f"❌ Low Volume (RVOL {rvol:.2f})")

        # 3. Displacement Check (0-10 pts)
        disp = self.calculate_displacement_ratio(df.iloc[-1])
        metrics['displacement'] = disp
        if disp >= self.displacement_threshold:
            score += 10
            details.append(f"✅ Strong Displacement ({disp*100:.1f}%)")
        else:
            details.append(f"❌ Weak Candle ({disp*100:.1f}%)")

        # 4. FVG Formation (0-10 pts)
        has_fvg = self.detect_breakout_fvg(df, signal_type)
        metrics['has_fvg'] = 1.0 if has_fvg else 0.0
        if has_fvg:
            score += 10
            details.append("✅ FVG Formed")
        else:
            details.append("❌ No FVG Formed (Efficient Move)")
            
        # Final Validity Check
        # Strict Mode: Must be in Kill Zone AND (RVOL OK OR FVG OK)
        is_valid = in_zone and (rvol >= 1.0 or has_fvg)
        
        return QualityResult(
            is_valid=is_valid,
            score=score,
            details=details,
            metrics=metrics
        )
