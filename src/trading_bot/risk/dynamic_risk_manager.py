import logging
import numpy as np
from typing import Dict, Optional, Tuple

logger = logging.getLogger("DynamicRiskManager")

class DynamicRiskManager:
    """
    Dynamic Risk Manager
    Implements a multi-dimensional dynamic stop-loss and tiered take-profit system.
    Factors:
    1. Trend (30%)
    2. Sentiment (20%)
    3. SMC (25%)
    4. MAE/MFE Stats (10%)
    5. AI Prediction (15%)
    """

    def __init__(self):
        # 1. Weights for Total Score Calculation (Sum must be 1.0)
        self.weights = {
            "trend": 0.3,
            "sentiment": 0.2,
            "smc": 0.25,
            "mae_mfe": 0.1,
            "ai": 0.15
        }
        
        # 2. SL Multiplier Config (Asymmetric - Conservative)
        # Score 0.0 -> 0.5x SL (Very Tight)
        # Score 0.5 -> 0.85x SL (Tight)
        # Score 1.0 -> 1.2x SL (Looser)
        self.sl_multiplier_base = 0.5
        self.sl_multiplier_factor = 0.7 
        
        # 3. TP Multiplier Config (Asymmetric - Optimistic)
        # Score 0.0 -> 0.6x TP (Quick Take Profit)
        # Score 0.5 -> 1.3x TP (Run)
        # Score 1.0 -> 2.0x TP (Let it Fly)
        self.tp_multiplier_base = 0.6
        self.tp_multiplier_factor = 1.4
        
        logger.info("DynamicRiskManager Initialized with weights: %s", self.weights)
        logger.info(f"SL Config: Base={self.sl_multiplier_base}, Factor={self.sl_multiplier_factor}")
        logger.info(f"TP Config: Base={self.tp_multiplier_base}, Factor={self.tp_multiplier_factor}")

    def calculate_dynamic_basket_sl(
        self, 
        base_sl_amount: float, 
        direction: str, 
        market_analysis: Dict,
        ai_confidence: float = 0.8,
        mae_stats: Optional[Dict] = None,
        current_drawdown: float = 0.0
    ) -> Tuple[float, Dict]:
        """
        Calculate the dynamic Basket SL threshold ($ amount).
        
        Args:
            base_sl_amount (float): The base max loss amount (positive float, e.g. 100.0).
            direction (str): 'long' or 'short'.
            market_analysis (Dict): Output from AdvancedMarketAnalysis.analyze_full or equivalent.
            ai_confidence (float): 0.0 to 1.0 (or 0-100).
            mae_stats (Dict): Historical MAE stats (e.g. {'95%': 150.0}).
            current_drawdown (float): Current drawdown amount (positive).

        Returns:
            Tuple[float, Dict]: (New SL Amount (negative), Log Details)
        """
        if base_sl_amount <= 0:
            return -100.0, {"error": "Invalid base_sl_amount"}

        # Normalize direction
        is_long = direction.lower() == 'long'
        
        # 1. Trend Score (0.0 - 1.0)
        trend_score = self._calculate_trend_score(market_analysis, is_long)
        
        # 2. Sentiment Score (0.0 - 1.0)
        sentiment_score = self._calculate_sentiment_score(market_analysis, is_long)
        
        # 3. SMC Score (0.0 - 1.0)
        smc_score = self._calculate_smc_score(market_analysis, is_long)
        
        # 4. MAE/MFE Score (0.0 - 1.0)
        mae_score = self._calculate_mae_score(mae_stats, current_drawdown, base_sl_amount)
        
        # 5. AI Score (0.0 - 1.0)
        ai_score = min(max(ai_confidence if ai_confidence <= 1.0 else ai_confidence / 100.0, 0.0), 1.0)

        # Weighted Sum
        total_score = (
            trend_score * self.weights["trend"] +
            sentiment_score * self.weights["sentiment"] +
            smc_score * self.weights["smc"] +
            mae_score * self.weights["mae_mfe"] +
            ai_score * self.weights["ai"]
        )

        # Calculate Adjustment Multiplier using Configured Parameters
        multiplier = self.sl_multiplier_base + (total_score * self.sl_multiplier_factor)
        
        # Apply Volatility Adjustment (Optional, if volatility is extreme, maybe widen?)
        # For now, we assume Trend Score already accounts for volatility risk.
        
        new_sl_amount = base_sl_amount * multiplier
        
        # Ensure it's not too tight (e.g., minimum 30% of base)
        new_sl_amount = max(new_sl_amount, base_sl_amount * 0.3)

        log_details = {
            "base_sl": base_sl_amount,
            "direction": direction,
            "scores": {
                "trend": round(trend_score, 2),
                "sentiment": round(sentiment_score, 2),
                "smc": round(smc_score, 2),
                "mae_mfe": round(mae_score, 2),
                "ai": round(ai_score, 2)
            },
            "total_score": round(total_score, 3),
            "multiplier": round(multiplier, 3),
            "calculated_sl": round(new_sl_amount, 2),
            "conflict_alert": total_score < 0.4 # Alert if score is very low
        }
        
        # Return as negative number (standard MT5/Codebase convention for loss limit)
        return -new_sl_amount, log_details

    def calculate_dynamic_basket_tp(
        self,
        base_tp_amount: float,
        direction: str,
        market_analysis: Dict,
        ai_confidence: float = 0.8,
        mae_stats: Optional[Dict] = None,
        current_atr: float = 0.0,
        current_profit: float = 0.0
    ) -> Tuple[float, Dict]:
        """
        Calculate the dynamic Basket TP target ($ amount) using 5-Dimensional Analysis.
        
        Args:
            base_tp_amount (float): The base target profit (positive float).
            direction (str): 'long' or 'short'.
            market_analysis (Dict): Full market analysis including Sentiment, SMC, etc.
            ai_confidence (float): 0.0 to 1.0.
            mae_stats (Dict): Contains 'avg_mfe' or 'mfe_target'.
            current_atr (float): Current ATR for volatility scaling.
            current_profit (float): Current floating profit (for context).

        Returns:
            Tuple[float, Dict]: (New TP Amount, Log Details)
        """
        if base_tp_amount <= 0:
            return 50.0, {"error": "Invalid base_tp_amount"}

        is_long = direction.lower() == 'long'
        
        # 1. Trend Score (Trend Following -> Higher TP)
        trend_score = self._calculate_trend_score(market_analysis, is_long)
        
        # 2. Sentiment Score (Greed -> Higher TP, Fear -> Lower TP)
        # We need to map Sentiment Score (-1 to 1) to a scaling factor
        # If Sentiment supports direction strongly -> Score 1.0 -> Expand TP
        sentiment_score = self._calculate_sentiment_score(market_analysis, is_long)
        
        # 3. SMC Score (Structure Support -> Higher TP)
        smc_score = self._calculate_smc_score(market_analysis, is_long)
        
        # 4. MFE Score (Historical Potential)
        # If MFE stats say we usually hit $80, but Base is $50 -> Expand
        mfe_score = self._calculate_mfe_score(mae_stats, base_tp_amount)
        
        # 5. AI Score
        ai_score = min(max(ai_confidence if ai_confidence <= 1.0 else ai_confidence / 100.0, 0.0), 1.0)
        
        # Weighted Sum
        total_score = (
            trend_score * self.weights["trend"] +
            sentiment_score * self.weights["sentiment"] +
            smc_score * self.weights["smc"] +
            mfe_score * self.weights["mae_mfe"] +
            ai_score * self.weights["ai"]
        )
        
        # Calculate Multiplier for TP using Configured Parameters
        multiplier = self.tp_multiplier_base + (total_score * self.tp_multiplier_factor)
        
        new_tp_amount = base_tp_amount * multiplier
        
        # Volatility Scaling (ATR)
        # If high volatility, we can aim higher
        if current_atr > 0:
            # Assuming standard "base" volatility context, if ATR expands, target expands
            # This is a bit subjective, let's just use it as a sanity check minimum
            min_atr_tp = current_atr * 10.0 # Example: 10 pips * volume? No, this is hard to generalize without volume.
            # Let's skip direct ATR math on $ amount unless we know volume.
            pass

        log_details = {
            "base_tp": base_tp_amount,
            "direction": direction,
            "scores": {
                "trend": round(trend_score, 2),
                "sentiment": round(sentiment_score, 2),
                "smc": round(smc_score, 2),
                "mfe": round(mfe_score, 2),
                "ai": round(ai_score, 2)
            },
            "total_score": round(total_score, 3),
            "multiplier": round(multiplier, 3),
            "calculated_tp": round(new_tp_amount, 2)
        }
        
        return new_tp_amount, log_details

    def calculate_tiered_tp(
        self,
        base_tp: float,
        current_atr: float,
        volatility_factor: float = 1.0,
        level_index: int = 1
    ) -> float:
        """
        Calculate Tiered TP based on ATR and Volatility.
        """
        if current_atr <= 0:
            return base_tp
        
        # Logic:
        # Base TP is dynamically extended by ATR * level * volatility
        # Example: TP = Base + (ATR * 0.5 * Level * Volatility)
        
        extension = current_atr * 0.5 * level_index * volatility_factor
        return base_tp + extension

    def _calculate_trend_score(self, analysis: Dict, is_long: bool) -> float:
        if not analysis: return 0.5
        
        score = 0.5
        regime = analysis.get('regime', {}).get('regime', 'unknown')
        signal_info = analysis.get('signal_info', {})
        signal = signal_info.get('signal', 'hold')
        
        # Base alignment
        if is_long:
            if signal == 'buy': score += 0.3
            elif signal == 'sell': score -= 0.3
        else:
            if signal == 'sell': score += 0.3
            elif signal == 'buy': score -= 0.3
            
        # Regime adjustment
        if regime == 'trending':
            score += 0.1 # Trending is generally good if aligned
        elif regime == 'high_volatility':
            score -= 0.1 # Riskier
            
        return min(max(score, 0.0), 1.0)

    def _calculate_sentiment_score(self, analysis: Dict, is_long: bool) -> float:
        if not analysis: return 0.5
        
        # Check 'SMC' structure sentiment from analysis
        smc_details = analysis.get('details', {}).get('smart_structure', {})
        # Or general sentiment score if available
        # The 'analyze' method in SMCAnalyzer returns 'sentiment_score' (-2 to 2)
        
        sentiment_val = analysis.get('sentiment_score', 0) # Assumed field from SMCAnalyzer
        
        score = 0.5
        if is_long:
            if sentiment_val > 0: score += (sentiment_val * 0.2) # +0.2 or +0.4
            elif sentiment_val < 0: score -= (abs(sentiment_val) * 0.2)
        else:
            if sentiment_val < 0: score += (abs(sentiment_val) * 0.2)
            elif sentiment_val > 0: score -= (sentiment_val * 0.2)
            
        return min(max(score, 0.0), 1.0)

    def _calculate_smc_score(self, analysis: Dict, is_long: bool) -> float:
        if not analysis: return 0.5
        
        score = 0.5
        details = analysis.get('details', {})
        
        # Check for Order Blocks
        obs = details.get('ob', {}).get('active_obs', [])
        # If Long, and price is near Bullish OB -> Good
        # How to check "near"? The analysis dict usually returns 'signal' based on retest.
        
        ob_signal = details.get('ob', {}).get('signal', 'neutral')
        fvg_signal = details.get('fvg', {}).get('signal', 'neutral')
        bos_signal = details.get('bos', {}).get('signal', 'neutral')
        
        if is_long:
            if ob_signal == 'buy': score += 0.2
            if fvg_signal == 'buy': score += 0.1
            if bos_signal == 'buy': score += 0.2
            if bos_signal == 'sell': score -= 0.3 # Break of structure against us
        else:
            if ob_signal == 'sell': score += 0.2
            if fvg_signal == 'sell': score += 0.1
            if bos_signal == 'sell': score += 0.2
            if bos_signal == 'buy': score -= 0.3
            
        return min(max(score, 0.0), 1.0)

    def _calculate_mfe_score(self, mae_stats: Optional[Dict], base_tp: float) -> float:
        """
        Calculate MFE Score: Does historical MFE support this Target?
        """
        if not mae_stats: return 0.5
        
        # We need MFE stats. Let's assume passed dict has 'mfe_target' or similar.
        # If not, try to infer from what we have.
        # In main.py, we only passed 'mae_95'. We need to update main.py to pass MFE.
        
        mfe_target = mae_stats.get('mfe_target', base_tp * 1.5) 
        
        if mfe_target > base_tp * 1.2:
            return 0.8 # History says we can hit higher
        elif mfe_target < base_tp * 0.8:
            return 0.2 # History says this is too ambitious
        else:
            return 0.5 # Neutral

    def _calculate_mae_score(self, mae_stats: Optional[Dict], current_drawdown: float, base_sl: float) -> float:
        # If no stats, return neutral
        if not mae_stats: return 0.5
        
        # Example MAE Stat: "95% trades have MAE < $50"
        # If current drawdown is $40, we are within normal noise -> Score High (Don't panic)
        # If current drawdown is $60, we are outlier -> Score Low (Panic/Cut)
        
        mae_95 = mae_stats.get('mae_95', base_sl * 0.8) # Default to 80% of SL
        
        if current_drawdown < mae_95:
            return 0.8 # Safe zone
        elif current_drawdown < base_sl:
            # Between 95% MAE and Hard SL -> Danger Zone
            return 0.2 
        else:
            return 0.0 # Breached

