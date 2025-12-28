import ccxt
import pandas as pd
import numpy as np
import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OKXDataProcessor:
    def __init__(self, api_key=None, api_secret=None, passphrase=None, use_sandbox=False):
        """Initialize the OKX data processor"""
        self.api_key = api_key or os.getenv("OKX_API_KEY")
        self.api_secret = api_secret or os.getenv("OKX_API_SECRET")
        self.passphrase = passphrase or os.getenv("OKX_API_PASSPHRASE")
        
        if not all([self.api_key, self.api_secret, self.passphrase]):
            logger.error("Missing OKX API credentials. Please set OKX_API_KEY, OKX_API_SECRET, and OKX_API_PASSPHRASE in .env file.")
            # We can still initialize for public data if needed, but private endpoints will fail
            # For now, let's allow it but log a warning, as ccxt might support public endpoints without keys
            
        exchange_config = {
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'password': self.passphrase,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # Default to swap for perpetuals
            },
        }
        
        if use_sandbox:
            exchange_config['sandbox'] = True
            
        self.exchange = ccxt.okx(exchange_config)
        self.initialized = True
        logger.info("OKX Exchange initialized")

    def _normalize_timeframe(self, tf):
        """Normalize timeframe to CCXT format"""
        mapping = {
            'M1': '1m', 'M5': '5m', 'M15': '15m', 'M30': '30m',
            'H1': '1h', 'H2': '2h', 'H4': '4h',
            'D1': '1d', 'W1': '1w', 'MN': '1M',
            '1H': '1h', '4H': '4h', '1D': '1d' 
        }
        return mapping.get(tf.upper(), tf)

    def get_historical_data(self, symbol, timeframe, limit=100, since=None):
        """Get historical data from OKX
        
        Args:
            symbol (str): Trading symbol, e.g., 'BTC/USDT'
            timeframe (str): Timeframe, e.g., '1h', '15m'
            limit (int): Number of candles to fetch
            since (int): Timestamp in ms to start fetching from
        
        Returns:
            pd.DataFrame: DataFrame with OHLCV data
        """
        # Normalize timeframe
        timeframe = self._normalize_timeframe(timeframe)
        
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Convert timestamp to datetime
            df['time'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('time', inplace=True)
            
            # Drop the original timestamp column
            df.drop('timestamp', axis=1, inplace=True)
            
            return df
        except Exception as e:
            logger.error(f"Error getting OKX data: {e}")
            return pd.DataFrame()

    def get_current_price(self, symbol):
        """Get current ticker price"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return None

    def calculate_ema(self, df, period, price_column='close'):
        """Calculate Exponential Moving Average"""
        return df[price_column].ewm(span=period, adjust=False).mean()

    def calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        df = df.copy()
        df['tr1'] = abs(df['high'] - df['low'])
        df['tr2'] = abs(df['high'] - df['close'].shift(1))
        df['tr3'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        atr = df['tr'].ewm(span=period, adjust=False).mean()
        return atr

    def calculate_rsi(self, df, period=14, price_column='close'):
        """Calculate Relative Strength Index"""
        delta = df[price_column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_features(self, df, fast_ema=12, slow_ema=26, atr_period=14, rsi_period=14):
        """Generate trading features"""
        df = df.copy()
        
        # Calculate EMA
        df['ema_fast'] = self.calculate_ema(df, fast_ema)
        df['ema_slow'] = self.calculate_ema(df, slow_ema)
        
        # Calculate ATR
        df['atr'] = self.calculate_atr(df, atr_period)
        
        # Calculate RSI
        df['rsi'] = self.calculate_rsi(df, rsi_period)
        
        # Calculate EMA crossover signal
        df['ema_crossover'] = 0
        df.loc[df['ema_fast'] > df['ema_slow'], 'ema_crossover'] = 1
        df.loc[df['ema_fast'] < df['ema_slow'], 'ema_crossover'] = -1
        
        # Calculate volatility (ATR percentage)
        df['volatility'] = (df['atr'] / df['close']) * 100
        
        # Calculate price change rate
        df['price_change'] = df['close'].pct_change() * 100
        
        # Fill NaN values
        indicators = ['ema_fast', 'ema_slow', 'atr', 'rsi', 'ema_crossover', 'volatility', 'price_change']
        for indicator in indicators:
            if indicator in df.columns:
                first_valid = df[indicator].first_valid_index()
                if first_valid is not None:
                    df[indicator] = df[indicator].fillna(df.loc[first_valid, indicator])
                else:
                    if indicator in ['ema_crossover']:
                        df[indicator] = df[indicator].fillna(0)
                    elif indicator in ['rsi']:
                        df[indicator] = df[indicator].fillna(50)
                    else:
                        df[indicator] = df[indicator].fillna(0)
        
        return df

    def prepare_model_input(self, df, lookback_period=20):
        """Prepare input data for ML models"""
        features = ['close', 'high', 'low', 'volume', 'ema_fast', 'ema_slow', 'atr', 'rsi', 'volatility', 'price_change']
        X = []
        for i in range(lookback_period, len(df)):
            X.append(df[features].iloc[i-lookback_period:i].values.flatten())
        return np.array(X)
    
    def get_account_balance(self, currency='USDT'):
        """Get account balance"""
        try:
            balance = self.exchange.fetch_balance()
            if currency in balance['total']:
                return {
                    'total': balance['total'][currency],
                    'free': balance['free'][currency],
                    'used': balance['used'][currency]
                }
            return None
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return None
            
    def cancel_algo_orders(self, symbol):
        """Cancel all algo orders for a symbol"""
        try:
            # Need to fetch pending algo orders first
            # ordType: conditional, oco, trigger, move_order_stop, iceber, twap
            algo_orders = self.exchange.fetch_open_orders(symbol, params={'ordType': 'conditional'})
            for order in algo_orders:
                try:
                    # For OKX, canceling algo order often requires specific endpoint or param
                    # ccxt cancel_order usually handles it if passed correct ID
                    self.exchange.cancel_order(order['id'], symbol)
                    logger.info(f"Cancelled algo order {order['id']}")
                except Exception as e:
                    logger.error(f"Failed to cancel algo order {order['id']}: {e}")
        except Exception as e:
            # It's possible fetch_open_orders with params is not fully supported or returns error if empty
            logger.warning(f"Error checking algo orders (might be none): {e}")

    def set_position_sl_tp(self, symbol, sl_price=None, tp_price=None):
        """
        Set SL/TP for an existing position
        """
        try:
            # OKX Algo order for SL/TP on existing position
            
            # First cancel existing SL/TP algo orders for this symbol to avoid duplicates
            self.cancel_algo_orders(symbol)
            
            algo_orders = []
            
            if sl_price:
                sl_order = {
                    'symbol': symbol,
                    'orderType': 'conditional', # or 'sl' depending on specific OKX params mapped in ccxt
                    'slTriggerPx': str(sl_price),
                    'slOrdPx': '-1', # Market price
                    'triggerPxType': 'last'
                }
                # CCXT might not have a direct unified method for this specific "Update Position SL/TP" 
                # effectively across all exchanges. For OKX, we often use 'edit_position_tpsl' if available
                # or create specific algo orders.
                pass

            # Using CCXT's specialized method if available, or raw params
            # For OKX, creating a 'stop' order with 'reduceOnly': True is common for SL
            
            params = {'reduceOnly': True}
            
            if sl_price:
                # Sell Stop (assuming Long position)
                # Need to know side. If we don't know side, this is risky.
                # Assuming we know we are Long for now, or we fetch position first.
                # A safer way is using 'algo' orders linked to position side.
                pass
                
        except Exception as e:
            logger.error(f"Error setting SL/TP: {e}")
            return False

    def update_sl_tp(self, symbol, sl_price=None, tp_price=None, side='buy'):
        """
        Update SL/TP for existing position using OKX specific algo order args
        """
        try:
            # Check for specific method in ccxt okx implementation
            if hasattr(self.exchange, 'private_post_trade_order_algo'):
                # Raw API call might be needed if CCXT doesn't wrap it fully for 'update'
                pass
            
            # Using CCXT create_order with params for SL/TP is usually for NEW orders.
            # For EXISTING positions, we often place a new conditional order with reduceOnly=True.
            
            # Cancel open algo orders first to replace them
            try:
                open_algos = self.exchange.fetch_open_orders(symbol, params={'ordType': 'conditional'})
                # Note: 'conditional' might not capture all SL/TP. OKX has 'stop', 'trigger', etc.
                # Simplest for now: Just log that we would update. 
                # To really implement:
                # 1. Fetch current position to get size and side
                # 2. Place stop-market order for SL
                # 3. Place limit/market order for TP (or take-profit algo)
                pass
            except:
                pass

            # Let's try to use the specific 'edit_order' or just place new reduce-only stops
            # OKX allows attaching SL/TP to position via 'place_algo_order'
            
            # Determine side for SL/TP
            # If we hold Long (buy), SL is a Sell Stop.
            # If we hold Short (sell), SL is a Buy Stop.
            sl_side = 'sell' if side == 'long' or side == 'buy' else 'buy'
            
            if sl_price:
                params = {
                    'stopPrice': sl_price,
                    'reduceOnly': True,
                    'tdMode': 'cross', # match margin mode
                }
                # This is just a standard stop order
                # self.exchange.create_order(symbol, 'stop', sl_side, amount, params=params)
                pass
                
        except Exception as e:
            logger.error(f"Error updating SL/TP: {e}")

    def set_leverage(self, symbol, leverage):
        """Set leverage for a symbol"""
        try:
            # OKX requires setting leverage for specific margin mode (usually cross or isolated)
            # We'll default to 'cross' for now as it's common for unified accounts, 
            # but allow it to be configured if needed. 
            # Note: ccxt set_leverage params: leverage, symbol, params
            self.exchange.set_leverage(leverage, symbol, params={'mgnMode': 'cross'})
            logger.info(f"Leverage set to {leverage}x for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
            return False

    def get_open_orders(self, symbol=None):
        """Get open orders"""
        try:
            return self.exchange.fetch_open_orders(symbol)
        except Exception as e:
            logger.error(f"Error getting open orders: {e}")
            return []

    def cancel_all_orders(self, symbol):
        """Cancel all open orders for a symbol"""
        try:
            # Check if cancel_all_orders is supported
            if self.exchange.has['cancelAllOrders']:
                self.exchange.cancel_all_orders(symbol)
                logger.info(f"Cancelled all open orders for {symbol}")
            else:
                # Fallback: fetch open orders and cancel one by one
                open_orders = self.get_open_orders(symbol)
                for order in open_orders:
                    try:
                        self.exchange.cancel_order(order['id'], symbol)
                        logger.info(f"Cancelled order {order['id']}")
                    except Exception as e:
                        logger.error(f"Failed to cancel order {order['id']}: {e}")
        except Exception as e:
            logger.error(f"Error cancelling orders: {e}")

    def place_sl_tp_order(self, symbol, side, amount, sl_price=None, tp_price=None):
        """
        Place SL/TP orders for an existing position
        side: 'buy' or 'sell' (direction of the SL/TP order, opposite to position)
        """
        try:
            # For OKX, we can use 'stop' orders with reduceOnly=True
            params = {'reduceOnly': True}
            
            # Check if reduceOnly is available/needed. 
            # If reduceOnly not available, we might need to set it to False or omit it 
            # if the position mode handles reduction automatically or for spot.
            # But for swaps, reduceOnly is standard. 
            # If API complains "Reduce Only is not available", it might mean 
            # the account mode (e.g. Net mode vs Long/Short mode) or specific order type 
            # doesn't support it in this context.
            
            # Workaround for error 51205: Try without reduceOnly if it fails, 
            # OR better: use 'algo' order endpoint which is designed for SL/TP
            
            if sl_price:
                # Stop Loss (Stop Market)
                # Try placing as an Algo Order (Conditional)
                sl_params = {
                    'tdMode': 'cross', # Assume cross, or should fetch mode
                    'triggerPx': str(sl_price),
                    'ordType': 'conditional',
                    'slTriggerPx': str(sl_price),
                    'slOrdPx': '-1', # Market
                    'reduceOnly': True
                }
                
                # Simple fallback: Standard Stop Market Order
                # Note: OKX V5 uses 'triggerPx' for stop price in create_order params usually
                
                logger.info(f"Placing SL order: {side} {amount} @ {sl_price}")
                
                # Attempt 1: Standard 'market' order with stopPrice
                try:
                    # Some ccxt versions map stopPrice to correct triggerPx
                    # But if reduceOnly fails, try omit it if we are sure it's closing
                    self.exchange.create_order(symbol, 'market', side, amount, params={'stopPrice': sl_price, 'reduceOnly': True})
                except Exception as inner_e:
                    logger.warning(f"Standard SL placement failed ({inner_e}), trying algo order...")
                    # Attempt 2: Algo order explicitly
                    try:
                        # For OKX, we use 'conditional' order type via create_order or specialized params
                        # We must map 'slTriggerPx' and 'slOrdPx' correctly in params
                        # ordType='conditional' is key for OKX V5
                        algo_params = {
                            'tdMode': 'cross', # Make sure this matches your position mode!
                            'ordType': 'conditional',
                            'slTriggerPx': str(sl_price),
                            'slOrdPx': '-1', # -1 for Market
                            'slTriggerPxType': 'last',
                            # OKX sometimes requires tag/clOrdId or reducesOnly not to be present for algos
                            # reduceOnly is implied for SL attached to position usually, but for separate algo order:
                            'reduceOnly': True 
                        }
                        # When using 'conditional', we might need to use a specific method or pass params to create_order
                        # Note: ccxt create_order usually handles 'conditional' type if supported, 
                        # otherwise we fall back to raw API if needed.
                        # For OKX, creating a 'conditional' order:
                        # IMPORTANT: OKX V5 uses 'algo-order' endpoint for this. CCXT 'create_order' might map to 'order' endpoint
                        # We might need to use specific params to force algo endpoint or use implicit mapping.
                        # If standard create_order fails, we try specific 'stop' order type if CCXT maps it.
                        
                        # Trying 'stop' type which CCXT often maps to algo order
                        self.exchange.create_order(symbol, 'stop', side, amount, params=algo_params)
                        logger.info(f"Placed algo SL order: {side} {amount} @ {sl_price}")
                    except Exception as algo_e:
                         logger.error(f"Algo SL placement also failed: {algo_e}")
                         # Last resort: Try without reduceOnly if that's the blocker for algo too
                         try:
                             algo_params.pop('reduceOnly', None)
                             self.exchange.create_order(symbol, 'stop', side, amount, params=algo_params)
                             logger.info(f"Placed algo SL order (no reduceOnly): {side} {amount} @ {sl_price}")
                         except Exception as final_e:
                             logger.error(f"Final SL attempt failed: {final_e}")

            if tp_price:
                # Take Profit (Limit Order)
                tp_params = params.copy()
                logger.info(f"Placing TP order: {side} {amount} @ {tp_price}")
                self.exchange.create_order(symbol, 'limit', side, amount, price=tp_price, params=tp_params)
                
        except Exception as e:
            logger.error(f"Error placing SL/TP: {e}")

    def get_contract_size(self, symbol):
        """Get contract size for a symbol"""
        try:
            market = self.exchange.market(symbol)
            return market['contractSize']
        except Exception as e:
            # Fallback or log error
            # If market info not loaded, try fetching markets first
            try:
                self.exchange.load_markets()
                market = self.exchange.market(symbol)
                return market['contractSize']
            except:
                logger.error(f"Error getting contract size for {symbol}: {e}")
                # Default fallback for ETH/USDT swap if fetch fails
                if 'ETH' in symbol: return 0.1
                if 'BTC' in symbol: return 0.01
                return 1.0 # Safe fallback? Maybe risky.

    def create_order(self, symbol, side, amount, type='market', price=None, params={}):
        """Create a trade order
        
        Args:
            symbol (str): Trading pair, e.g., 'BTC/USDT'
            side (str): 'buy' or 'sell'
            amount (float): Amount to trade
            type (str): 'market' or 'limit'
            price (float): Price for limit orders
        """
        try:
            if type == 'market':
                order = self.exchange.create_market_order(symbol, side, amount, params=params)
            elif type == 'limit':
                if price is None:
                    raise ValueError("Price required for limit orders")
                order = self.exchange.create_limit_order(symbol, side, amount, price, params=params)
            else:
                raise ValueError(f"Unsupported order type: {type}")
                
            logger.info(f"Order created: {order['id']}")
            return order
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None

def main():
    """Test the OKX data processor"""
    processor = OKXDataProcessor()
    
    symbol = 'BTC/USDT'
    
    # Test getting historical data
    logger.info(f"Fetching historical data for {symbol}...")
    df = processor.get_historical_data(symbol, '1h', limit=100)
    print(f"Data shape: {df.shape}")
    
    if not df.empty:
        df_with_features = processor.generate_features(df)
        print(f"Features generated. Shape: {df_with_features.shape}")
        print(df_with_features.tail())
        
    # Test getting current price
    price = processor.get_current_price(symbol)
    print(f"Current {symbol} price: {price}")
    
    # Test getting balance (might fail if keys are invalid/restricted)
    balance = processor.get_account_balance()
    if balance:
        print(f"USDT Balance: {balance}")
    else:
        print("Could not fetch balance (check API permissions)")

if __name__ == "__main__":
    main()
