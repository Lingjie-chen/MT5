import logging
import json
import pandas as pd
from .advanced_analysis import SMCAnalyzer, AdvancedMarketAnalysisAdapter
from .breakout_quality_filter import BreakoutQualityFilter

logger = logging.getLogger("SMCValidator")

class SMCQualityValidator:
    """
    SMC Data Verification & Quality Scoring System
    Validates ORB signals against Smart Money Concepts.
    """
    
    def __init__(self, min_score_threshold=70):
        self.smc_analyzer = SMCAnalyzer()
        self.advanced_analyzer = AdvancedMarketAnalysisAdapter()
        self.quality_filter = BreakoutQualityFilter()
        self.min_score_threshold = min_score_threshold
        
    def calculate_trade_quality_score(self, signal_type, current_price, smc_data, sentiment_score, volatility_context, df_m15=None, current_time=None):
        """
        Calculate Trade Quality Score (0-100) based on multiple dimensions.
        Updated Dimensions:
        1. SMC Structure (20 pts)
        2. Liquidity/Order Flow (20 pts)
        3. Sentiment (15 pts)
        4. Volatility/Momentum (15 pts)
        5. [NEW] Breakout Quality (30 pts)
        Total potential > 100, capped at 100.
        """
        score = 0
        details = []
        
        # --- 0. [NEW] Breakout Quality (Max 30) ---
        # RVOL, Displacement, FVG Formation
        if df_m15 is not None and current_time is not None:
            quality_result = self.quality_filter.validate_breakout_quality(df_m15, signal_type, current_time)
            
            # Kill Zone Check removed as per user request (Gate 1 bypassed)
            # if not quality_result.metrics.get('kill_zone', 0):
            #      details.append("❌ Outside Kill Zone (Penalty -50)")
            #      score -= 50
            
            # Add Quality Score (already 0-30 based on 3 metrics * 10)
            q_score = quality_result.score
            score += q_score
            details.extend(quality_result.details)
        
        # 1. SMC Structure Alignment (Max 20)
        # If signal is BUY, we want to be in Discount or have Bullish Structure
        # If signal is SELL, we want to be in Premium or have Bearish Structure
        
        structure_signal = smc_data.get('signal', 'neutral')
        active_strategy = smc_data.get('active_strategy', 'ALL')
        smc_reason = smc_data.get('reason', '')
        
        # Base alignment
        if signal_type == structure_signal:
            score += 20
            details.append(f"SMC Structure Aligned ({smc_reason})")
        elif structure_signal == 'neutral':
            score += 10
            details.append("SMC Neutral (No Conflict)")
        else:
            details.append(f"SMC Conflict ({smc_reason})")
            
        # Premium/Discount Check
        pd_info = smc_data.get('details', {}).get('premium_discount', {})
        zone = pd_info.get('zone', 'equilibrium')
        
        if signal_type == 'buy':
            if zone == 'discount':
                score += 10
                details.append("Price in Discount Zone (Good for Buy)")
            elif zone == 'equilibrium':
                score += 5
        elif signal_type == 'sell':
            if zone == 'premium':
                score += 10
                details.append("Price in Premium Zone (Good for Sell)")
            elif zone == 'equilibrium':
                score += 5
                
        # 2. Liquidity & Order Flow (Max 20)
        # Check if we are reacting to OB or FVG
        obs = smc_data.get('details', {}).get('ob', {}).get('active_obs', [])
        fvgs = smc_data.get('details', {}).get('fvg', {}).get('active_fvgs', [])
        
        # Check proximity to supporting structures
        has_support = False
        min_dist = float('inf')
        
        for ob in obs:
            if signal_type == 'buy' and ob['type'] == 'bullish':
                # Check if price is near/above this OB
                if current_price >= ob['bottom']:
                    has_support = True
                    details.append("Supported by Bullish OB")
                    break
            if signal_type == 'sell' and ob['type'] == 'bearish':
                if current_price <= ob['top']:
                    has_support = True
                    details.append("Supported by Bearish OB")
                    break
                    
        if has_support:
            score += 15
        
        # FVG Filling?
        for fvg in fvgs:
             if signal_type == 'buy' and fvg['type'] == 'bullish': # Gap to fill below? Or bouncing off?
                 # If we are in FVG, it's a rebalance buy
                 if fvg['bottom'] <= current_price <= fvg['top']:
                     score += 10
                     details.append("Reacting in Bullish FVG")
             if signal_type == 'sell' and fvg['type'] == 'bearish':
                 if fvg['bottom'] <= current_price <= fvg['top']:
                     score += 10
                     details.append("Reacting in Bearish FVG")
                     
        # 3. Sentiment & Momentum (Max 15)
        # Sentiment Score: -1 to 1
        if signal_type == 'buy':
            if sentiment_score > 0.2:
                score += 15
                details.append(f"Strong Bullish Sentiment ({sentiment_score:.2f})")
            elif sentiment_score > -0.2:
                score += 5
            else:
                details.append("Sentiment Divergence (Bearish Sentiment for Buy)")
                
        elif signal_type == 'sell':
            if sentiment_score < -0.2:
                score += 15
                details.append(f"Strong Bearish Sentiment ({sentiment_score:.2f})")
            elif sentiment_score < 0.2:
                score += 5
            else:
                details.append("Sentiment Divergence (Bullish Sentiment for Sell)")
                
        # 4. Volatility / Breakout Strength (Max 15) - UPDATED for ORB Momentum Focus
        # This comes from 'volatility_context' (e.g. Z-Score, Breakout Score)
        breakout_score = volatility_context.get('breakout_score', 0) # 0-100
        z_score = volatility_context.get('z_score', 0)
        
        # Normalize breakout score contribution
        if breakout_score > 90:
            score += 15
            details.append(f"Extreme Breakout Momentum (Score {breakout_score:.1f})")
        elif breakout_score > 70:
            score += 10
            details.append(f"Very Strong Breakout (Score {breakout_score:.1f})")
        elif breakout_score > 50:
            score += 5
            details.append(f"Strong Breakout Metrics (Score {breakout_score:.1f})")
        elif breakout_score > 30:
            score += 2
            
        # Z-Score Check (Avoid extreme extensions unless momentum is super strong)
        # If momentum is extreme (>90), we ignore over-extension penalty because "Trend is your friend"
        if abs(z_score) > 3.0 and breakout_score < 90:
            score -= 10 # Penalty for over-extension (Reversion Risk)
            details.append("Penalty: Extreme Z-Score (Overextended)")
            
        return score, details
        
    def validate_signal(self, df_m15, current_price, signal_type, volatility_stats=None, current_time=None):
        """
        Main validation entry point.
        Returns: (is_valid, score, details_dict)
        """
        if df_m15 is None or len(df_m15) < 50:
            return False, 0, {"error": "Insufficient Data"}
            
        # 1. Run SMC Analysis
        smc_result = self.smc_analyzer.analyze(df_m15)
        sentiment_score = smc_result.get('sentiment_score', 0)
        
        # 2. Context
        vol_context = volatility_stats if volatility_stats else {}
        
        # 3. Calculate Score
        score, details = self.calculate_trade_quality_score(
            signal_type, 
            current_price, 
            smc_result, 
            sentiment_score, 
            vol_context,
            df_m15=df_m15,
            current_time=current_time
        )

        
        is_valid = score >= self.min_score_threshold
        
        result_details = {
            "score": score,
            "threshold": self.min_score_threshold,
            "breakdown": details,
            "smc_signal": smc_result.get('signal'),
            "sentiment": sentiment_score
        }
        
        if is_valid:
            logger.info(f"SMC Validation PASSED: Score {score}/{self.min_score_threshold} ({', '.join(details)})")
        else:
            logger.debug(f"SMC Validation FAILED: Score {score}/{self.min_score_threshold} ({', '.join(details)})")
            
        return is_valid, score, result_details
