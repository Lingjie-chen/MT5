import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import platform

# Only attempt to import MetaTrader5 on Windows systems
try:
    if platform.system() == 'Windows':
        import MetaTrader5 as mt5
    else:
        # On non-Windows systems, set mt5 to None
        mt5 = None
        print("MetaTrader5 library not available on this platform, using mock data")
except ImportError:
    # If import fails even on Windows, use mock data
    mt5 = None
    print("Failed to import MetaTrader5, using mock data")

class MT5DataProcessor:
    def __init__(self):
        """Initialize the MT5 data processor"""
        self.initialized = False
        if mt5 is not None:
            self.initialized = self._initialize_mt5()

    def _initialize_mt5(self):
        """Initialize MT5 connection"""
        if mt5 is None:
            return False
        if not mt5.initialize():
            print("Failed to initialize MT5")
            return False
        return True

    def get_historical_data(self, symbol, timeframe, start_date, end_date):
        """Get historical data, using mock data if MT5 is unavailable
        
        Args:
            symbol (str): 交易品种，如 'EURUSD'
            timeframe (int): 时间周期，如 mt5.TIMEFRAME_H1
            start_date (datetime): 开始日期
            end_date (datetime): 结束日期
        
        Returns:
            pd.DataFrame: 包含OHLCV数据的DataFrame
        """
        # Try to get real data if MT5 is available
        if self.initialized:
            try:
                rates = mt5.copy_rates_range(symbol, timeframe, start_date, end_date)
                if rates is not None:
                    df = pd.DataFrame(rates)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df.set_index('time', inplace=True)
                    return df
            except Exception as e:
                print(f"Error getting MT5 data: {e}")
        
        # Generate mock data if real data unavailable
        print(f"Generating mock data for {symbol}")
        dates = pd.date_range(start=start_date, end=end_date, freq='H')
        n = len(dates)
        
        np.random.seed(42)
        close = 1900 + np.cumsum(np.random.randn(n) * 2)
        high = close + np.random.rand(n) * 3
        low = close - np.random.rand(n) * 3
        open_price = close.shift(1).fillna(1900)
        volume = np.random.randint(100000, 1000000, n)
        
        df = pd.DataFrame({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }, index=dates)
        
        return df

    def calculate_ema(self, df, period, price_column='close'):
        """Calculate Exponential Moving Average
        
        Args:
            df (pd.DataFrame): 价格数据
            period (int): EMA周期
            price_column (str): 价格列名
        
        Returns:
            pd.Series: EMA值
        """
        return df[price_column].ewm(span=period, adjust=False).mean()

    def calculate_atr(self, df, period=14):
        """Calculate Average True Range
        
        Args:
            df (pd.DataFrame): 价格数据
            period (int): ATR周期
        
        Returns:
            pd.Series: ATR值
        """
        df = df.copy()
        df['tr1'] = abs(df['high'] - df['low'])
        df['tr2'] = abs(df['high'] - df['close'].shift(1))
        df['tr3'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        atr = df['tr'].ewm(span=period, adjust=False).mean()
        return atr

    def calculate_rsi(self, df, period=14, price_column='close'):
        """Calculate Relative Strength Index
        
        Args:
            df (pd.DataFrame): 价格数据
            period (int): RSI周期
            price_column (str): 价格列名
        
        Returns:
            pd.Series: RSI值
        """
        delta = df[price_column].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_features(self, df, fast_ema=12, slow_ema=26, atr_period=14, rsi_period=14):
        """Generate trading features
        
        Args:
            df (pd.DataFrame): 原始价格数据
            fast_ema (int): 快速EMA周期
            slow_ema (int): 慢速EMA周期
            atr_period (int): ATR周期
            rsi_period (int): RSI周期
        
        Returns:
            pd.DataFrame: 包含原始数据和特征的DataFrame
        """
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
        
        return df.dropna()

    def prepare_model_input(self, df, lookback_period=20):
        """Prepare input data for ML models
        
        Args:
            df (pd.DataFrame): 包含特征的数据
            lookback_period (int): 回溯期
        
        Returns:
            np.array: 模型输入数据
        """
        features = ['close', 'high', 'low', 'volume', 'ema_fast', 'ema_slow', 'atr', 'rsi', 'volatility', 'price_change']
        X = []
        for i in range(lookback_period, len(df)):
            X.append(df[features].iloc[i-lookback_period:i].values.flatten())
        return np.array(X)

    def close(self):
        """Close MT5 connection if open"""
        if self.initialized and mt5 is not None:
            mt5.shutdown()

def main():
    """Test the data processor"""
    processor = MT5DataProcessor()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    df = processor.get_historical_data('GOLD', None, start_date, end_date)
    print(f"Raw data shape: {df.shape}")
    
    df_with_features = processor.generate_features(df)
    print(f"Features data shape: {df_with_features.shape}")
    print(df_with_features.head())
    
    processor.close()

if __name__ == "__main__":
    main()
