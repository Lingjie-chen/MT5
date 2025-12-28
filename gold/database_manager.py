import sqlite3
import pandas as pd
import json
from datetime import datetime
import logging
import os

logger = logging.getLogger("DatabaseManager")

class DatabaseManager:
    def __init__(self, db_path="trading_data.db"):
        # 如果传入的是默认相对路径，将其转换为基于项目根目录的绝对路径
        if db_path == "trading_data.db":
            # 假设当前文件在 python/ 目录下，项目根目录在上一级
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            self.db_path = os.path.join(project_root, db_path)
        else:
            self.db_path = db_path
            
        # 确保路径存在
        logger.info(f"Database path: {self.db_path}")
        self.conn = None
        self._init_db()

    def _get_connection(self):
        """Helper to get a database connection with proper timeout and retry"""
        import time
        max_retries = 5
        
        # If we already have a connection, check if it's valid
        if self.conn:
            try:
                self.conn.execute("SELECT 1")
                return self.conn
            except Exception:
                # Connection might be broken, try to reconnect
                try:
                    self.conn.close()
                except: pass
                self.conn = None

        for i in range(max_retries):
            try:
                # check_same_thread=False allows Streamlit to use connection across threads
                self.conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
                # Enable WAL mode for better concurrency immediately upon connection
                self.conn.execute('PRAGMA journal_mode=WAL;')
                return self.conn
            except sqlite3.OperationalError as e:
                if "unable to open database file" in str(e) or "database is locked" in str(e):
                    if i < max_retries - 1:
                        time.sleep(1.0) # Increase wait time
                        continue
                logger.error(f"Connection failed after {i+1} attempts: {e}")
                raise e
        raise sqlite3.OperationalError("Failed to connect to database after retries")

    def _init_db(self):
        """Initialize the database tables"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Table for market data (OHLCV)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    timestamp DATETIME,
                    symbol TEXT,
                    timeframe TEXT,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    PRIMARY KEY (timestamp, symbol, timeframe)
                )
            ''')
            
            # Table for signals and analysis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    timestamp DATETIME,
                    symbol TEXT,
                    timeframe TEXT,
                    signal TEXT,
                    strength REAL,
                    source TEXT, -- 'CRT', 'PriceEq', 'DeepSeek', 'Qwen', 'Hybrid'
                    details TEXT -- JSON string with extra details
                )
            ''')
            
            # Table for trades
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    ticket INTEGER PRIMARY KEY,
                    symbol TEXT,
                    action TEXT, -- 'BUY', 'SELL'
                    volume REAL,
                    price REAL,
                    time DATETIME,
                    result TEXT, -- 'OPEN', 'CLOSED', 'ERROR'
                    close_price REAL,
                    close_time DATETIME,
                    profit REAL,
                    mfe REAL, -- Maximum Favorable Excursion
                    mae REAL  -- Maximum Adverse Excursion
                )
            ''')
            
            # Attempt to add columns if they don't exist (for existing DB)
            try:
                cursor.execute("ALTER TABLE trades ADD COLUMN close_price REAL")
            except: pass
            try:
                cursor.execute("ALTER TABLE trades ADD COLUMN close_time DATETIME")
            except: pass
            try:
                cursor.execute("ALTER TABLE trades ADD COLUMN profit REAL")
            except: pass
            try:
                cursor.execute("ALTER TABLE trades ADD COLUMN mfe REAL")
            except: pass
            try:
                cursor.execute("ALTER TABLE trades ADD COLUMN mae REAL")
            except: pass
            
            # Table for account metrics (Balance, Equity, etc.)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS account_metrics (
                    timestamp DATETIME,
                    balance REAL,
                    equity REAL,
                    margin REAL,
                    free_margin REAL,
                    margin_level REAL,
                    total_profit REAL, -- Floating PnL
                    symbol_pnl REAL, -- PnL for specific symbol (optional)
                    PRIMARY KEY (timestamp)
                )
            ''')
            
            conn.commit()
            # conn.close() # Persistent connection, do not close
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def save_account_metrics(self, metrics):
        """Save account metrics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO account_metrics (timestamp, balance, equity, margin, free_margin, margin_level, total_profit, symbol_pnl)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('timestamp', datetime.now()),
                metrics.get('balance', 0),
                metrics.get('equity', 0),
                metrics.get('margin', 0),
                metrics.get('free_margin', 0),
                metrics.get('margin_level', 0),
                metrics.get('total_profit', 0),
                metrics.get('symbol_pnl', 0)
            ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save account metrics: {e}")

    def get_latest_account_metrics(self):
        """Get the most recent account metrics"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM account_metrics ORDER BY timestamp DESC LIMIT 1')
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get account metrics: {e}")
            return None

    def get_historical_account_metrics(self, hours_ago=24):
        """Get account metrics from N hours ago"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # SQLite datetime modifier
            cursor.execute(f"SELECT * FROM account_metrics WHERE timestamp <= datetime('now', '-{hours_ago} hours') ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            logger.error(f"Failed to get historical metrics: {e}")
            return None

    def get_start_of_day_metrics(self):
        """Get account metrics from the start of the current day"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM account_metrics WHERE date(timestamp) = date('now') ORDER BY timestamp ASC LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            # If no record today, try last record of yesterday
            cursor.execute("SELECT * FROM account_metrics WHERE date(timestamp) < date('now') ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                return dict(row)
                
            return None
        except Exception as e:
            logger.error(f"Failed to get start of day metrics: {e}")
            return None

    def save_market_data(self, df, symbol, timeframe):
        try:
            conn = self._get_connection()
            # Add symbol and timeframe columns if they don't exist in df
            data_to_save = df.copy()
            data_to_save['symbol'] = symbol
            data_to_save['timeframe'] = timeframe
            data_to_save['timestamp'] = data_to_save.index
            
            cursor = conn.cursor()
            for index, row in data_to_save.iterrows():
                cursor.execute('''
                    REPLACE INTO market_data (timestamp, symbol, timeframe, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['timestamp'].to_pydatetime(), symbol, timeframe, row['open'], row['high'], row['low'], row['close'], row['volume']))
            
            conn.commit()
            # conn.close()
        except Exception as e:
            logger.error(f"Failed to save market data: {e}")

    def save_signal(self, symbol, timeframe, signal_data):
        """Save analysis signal"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now()
            
            # Save Hybrid result
            cursor.execute('''
                INSERT INTO signals (timestamp, symbol, timeframe, signal, strength, source, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, symbol, timeframe, signal_data['final_signal'], signal_data['strength'], 'Hybrid', json.dumps(signal_data['details'])))
            
            conn.commit()
            # conn.close()
        except Exception as e:
            logger.error(f"Failed to save signal: {e}")

    def save_trade(self, trade_data):
        """Save trade execution"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO trades (ticket, symbol, action, volume, price, time, result)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data['ticket'], 
                trade_data['symbol'], 
                trade_data['action'], 
                trade_data['volume'], 
                trade_data['price'], 
                datetime.now(), 
                trade_data.get('result', 'OPEN')
            ))
            
            conn.commit()
            # conn.close()
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")

    def update_trade_performance(self, ticket, close_data):
        """Update trade with close info and performance metrics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE trades 
                SET result = 'CLOSED',
                close_price = ?,
                close_time = ?,
                profit = ?,
                mfe = ?,
                mae = ?
                WHERE ticket = ?
            ''', (
                close_data.get('close_price'),
                close_data.get('close_time'),
                close_data.get('profit'),
                close_data.get('mfe'),
                close_data.get('mae'),
                ticket
            ))
            
            conn.commit()
            # conn.close()
        except Exception as e:
            logger.error(f"Failed to update trade performance: {e}")

    def get_trade_performance_stats(self, limit=50):
        """Get aggregated performance stats (MFE, MAE) for recent closed trades"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    AVG(mfe) as avg_mfe,
                    AVG(mae) as avg_mae,
                    AVG(profit) as avg_profit,
                    COUNT(*) as count
                FROM trades 
                WHERE result = 'CLOSED' AND mfe IS NOT NULL
                ORDER BY close_time DESC
                LIMIT ?
            ''', (limit,))
            
            row = cursor.fetchone()
            
            stats = None
            if row and row['count'] > 0:
                stats = {
                    "avg_mfe": row['avg_mfe'],
                    "avg_mae": row['avg_mae'],
                    "avg_profit": row['avg_profit'],
                    "trade_count": row['count']
                }
            
            # 获取最近的 MFE/MAE 数据列表用于分布分析
            cursor.execute('''
                SELECT ticket, mfe, mae, profit, action 
                FROM trades 
                WHERE result = 'CLOSED' AND mfe IS NOT NULL 
                ORDER BY close_time DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            details = []
            for r in rows:
                details.append({
                    "ticket": r['ticket'],
                    "mfe": r['mfe'],
                    "mae": r['mae'],
                    "profit": r['profit'],
                    "action": r['action']
                })
            
            if stats:
                stats["recent_trades"] = details
                
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get trade stats: {e}")
            return None

    def get_open_trades(self):
        """Get all trades that are currently marked as OPEN in the database"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM trades 
                WHERE result = 'OPEN' OR result IS NULL
            ''')
            
            rows = cursor.fetchall()
            # conn.close()
            
            # Convert rows to list of dicts
            trades = []
            for row in rows:
                trades.append(dict(row))
            return trades
        except Exception as e:
            logger.error(f"Failed to get open trades: {e}")
            return []

    def get_latest_signals(self, limit=50):
        """Get recent signals for dashboard"""
        try:
            conn = self._get_connection()
            query = "SELECT * FROM signals ORDER BY timestamp DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=(limit,))
            # conn.close()
            return df
        except Exception as e:
            logger.error(f"Failed to get signals: {e}")
            return pd.DataFrame()

    def get_market_data(self, symbol, limit=100):
        """Get market data for dashboard"""
        try:
            conn = self._get_connection()
            query = "SELECT * FROM market_data WHERE symbol = ? ORDER BY timestamp DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=(symbol, limit))
            # conn.close()
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            return df
        except Exception as e:
            logger.error(f"Failed to get market data: {e}")
            return pd.DataFrame()

    def get_trades(self, limit=50):
        """Get trade history from local DB"""
        try:
            conn = self._get_connection()
            query = "SELECT * FROM trades ORDER BY time DESC LIMIT ?"
            df = pd.read_sql_query(query, conn, params=(limit,))
            # conn.close()
            return df
        except Exception as e:
            logger.error(f"Failed to get trades: {e}")
            return pd.DataFrame()
