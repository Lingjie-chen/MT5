import yfinance as yf
from decimal import Decimal
from cachetools import TTLCache, cached
from .config import settings
import logging

logger = logging.getLogger("RiskManager")
cache = TTLCache(maxsize=100, ttl=settings.CACHE_TTL)

class ExchangeRateService:
    @cached(cache)
    def get_realtime_rate(self, base: str, target: str) -> Decimal:
        """获取汇率: 1 base = ? target (集成 Yahoo Finance)"""
        if base == target:
            return Decimal("1.0")

        pair_direct = f"{base}{target}=X"
        pair_reverse = f"{target}{base}=X"

        try:
            tickers = yf.Tickers(f"{pair_direct} {pair_reverse}")
            
            # 正向查询
            if tickers.tickers.get(pair_direct) and tickers.tickers[pair_direct].info.get('regularMarketPrice'):
                rate = tickers.tickers[pair_direct].info['regularMarketPrice']
                return Decimal(str(rate))
            
            # 反向查询取倒数
            if tickers.tickers.get(pair_reverse) and tickers.tickers[pair_reverse].info.get('regularMarketPrice'):
                rate = tickers.tickers[pair_reverse].info['regularMarketPrice']
                return Decimal("1.0") / Decimal(str(rate))

            # Crypto 兜底
            if base in ["BTC", "ETH", "BNB"]:
                ticker = yf.Ticker(f"{base}-{target}")
                rate = ticker.info.get('regularMarketPrice')
                if rate: return Decimal(str(rate))

        except Exception as e:
            logger.error(f"Error fetching rate {base}/{target}: {e}")
        
        raise ValueError(f"无法获取汇率: {base}/{target}")
