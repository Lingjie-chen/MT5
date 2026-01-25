import MetaTrader5 as mt5
import logging

logger = logging.getLogger("WindowsBot")

class SymbolCache:
    """
    Cache static symbol information to reduce IPC overhead with MT5 terminal.
    Contract specifications (Point, Digits, Contract Size) rarely change during a session.
    """
    _cache = {}

    @classmethod
    def get_info(cls, symbol):
        """
        Get symbol info from cache or fetch from MT5 if not cached.
        """
        if symbol not in cls._cache:
            info = mt5.symbol_info(symbol)
            if info is None:
                logger.error(f"Failed to get symbol info for {symbol}")
                return None
            
            # Determine best filling mode
            filling = mt5.ORDER_FILLING_FOK
            if not (info.filling_mode & filling):
                filling = mt5.ORDER_FILLING_IOC
            if not (info.filling_mode & filling):
                filling = mt5.ORDER_FILLING_RETURN
                
            cls._cache[symbol] = {
                'point': info.point,
                'digits': info.digits,
                'contract_size': info.trade_contract_size,
                'trade_stops_level': info.trade_stops_level,
                'trade_tick_value': info.trade_tick_value,
                'trade_tick_size': info.trade_tick_size,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'volume_step': info.volume_step,
                'filling_mode': filling,
                'ask': info.ask, # Note: Ask/Bid are dynamic, but sometimes we need a fallback baseline
                'bid': info.bid
            }
            logger.info(f"Cached static info for {symbol}")
            
        return cls._cache[symbol]

    @classmethod
    def update_dynamic_info(cls, symbol):
        """
        Update only dynamic parts (Ask/Bid) if needed, 
        though usually we use symbol_info_tick for that.
        """
        info = mt5.symbol_info(symbol)
        if info:
            cls._cache[symbol]['ask'] = info.ask
            cls._cache[symbol]['bid'] = info.bid
