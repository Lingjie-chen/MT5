import numpy as np
from scipy import stats
import logging

logger = logging.getLogger("MathLib")

"""
GOLD_ORB Strategy Math Library Integration.
Ported from Include/Math/Stat/Normal.mqh
"""

def math_probability_density_normal(x, mu, sigma, log_mode=False):
    """
    Normal probability density function (PDF).
    Equivalent to MathProbabilityDensityNormal.
    """
    if sigma <= 0:
        logger.error("Invalid sigma <= 0")
        return np.nan
        
    try:
        val = stats.norm.pdf(x, loc=mu, scale=sigma)
        if log_mode:
            return np.log(val)
        return val
    except Exception as e:
        logger.error(f"Error in math_probability_density_normal: {e}")
        return np.nan

def math_cumulative_distribution_normal(x, mu, sigma, tail=True, log_mode=False):
    """
    Normal cumulative distribution function (CDF).
    Equivalent to MathCumulativeDistributionNormal.
    """
    if sigma <= 0:
        return np.nan
        
    try:
        if tail: # Lower tail (default for CDF)
            val = stats.norm.cdf(x, loc=mu, scale=sigma)
        else: # Upper tail (Survival function)
            val = stats.norm.sf(x, loc=mu, scale=sigma)
            
        if log_mode:
            return np.log(val)
        return val
    except Exception as e:
        logger.error(f"Error in math_cumulative_distribution_normal: {e}")
        return np.nan

def math_quantile_normal(probability, mu, sigma, tail=True, log_mode=False):
    """
    Normal distribution quantile function (inverse CDF).
    Equivalent to MathQuantileNormal.
    """
    if sigma <= 0 or probability < 0 or probability > 1:
        return np.nan
        
    try:
        p = probability
        if log_mode:
            p = np.exp(p)
            
        if tail:
            return stats.norm.ppf(p, loc=mu, scale=sigma)
        else:
            return stats.norm.isf(p, loc=mu, scale=sigma)
    except Exception as e:
        logger.error(f"Error in math_quantile_normal: {e}")
        return np.nan

def math_random_normal(mu, sigma, count=1):
    """
    Random variate from the Normal distribution.
    Equivalent to MathRandomNormal.
    """
    if sigma < 0:
        return None
    try:
        return stats.norm.rvs(loc=mu, scale=sigma, size=count)
    except Exception as e:
        logger.error(f"Error in math_random_normal: {e}")
        return None

def math_moments_normal(mu, sigma):
    """
    Normal distribution moments.
    Returns: (mean, variance, skewness, kurtosis)
    Equivalent to MathMomentsNormal.
    """
    if sigma <= 0:
        return None
    try:
        # Normal distribution:
        # Mean = mu
        # Variance = sigma^2
        # Skewness = 0
        # Kurtosis (Fisher) = 0
        return mu, sigma**2, 0.0, 0.0
    except Exception as e:
        logger.error(f"Error in math_moments_normal: {e}")
        return None
