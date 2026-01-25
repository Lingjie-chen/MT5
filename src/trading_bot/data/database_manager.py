import sqlite3
import pandas as pd
import json
from datetime import datetime
import logging
import os
from ..utils.remote_storage import RemoteStorage

logger = logging.getLogger("DatabaseManager")

class DatabaseManager:
    def __init__(self, db_path="trading_data.db"):
        # Initialize Remote Storage
        self.remote_storage = RemoteStorage()
        
        # 如果传入的是默认文件名（非绝对路径），将其转换为基于当前文件所在目录的绝对路径
        if not os.path.isabs(db_path):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.db_path = os.path.join(current_dir, os.path.basename(db_path))
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
                self.conn.execute('PRAGMA synchronous=NORMAL;') # Reduce fsyncs
                self.conn.execute('PRAGMA temp_store=MEMORY;') # Use RAM for temp store
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
            
            # [Remote Sync]
            self.remote_storage.save_account_metrics(metrics)
        except sqlite3.OperationalError as e:
            if "database or disk is full" in str(e):
                logger.warning(f"Database full error in save_account_metrics, attempting checkpoint: {e}")
                self.perform_checkpoint()
            logger.error(f"Failed to save account metrics: {e}")
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
            
            # [Remote Sync]
            self.remote_storage.save_market_data_batch(df.copy(), symbol, timeframe)
        except sqlite3.OperationalError as e:
            if "database or disk is full" in str(e):
                logger.warning(f"Database full error in save_market_data, attempting checkpoint: {e}")
                self.perform_checkpoint()
            logger.error(f"Failed to save market data: {e}")
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
            
            # [Remote Sync]
            # Normalize signal data for remote storage
            try:
                remote_signal = {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'final_signal': signal_data['final_signal'],
                    'strength': signal_data['strength'],
                    'source': 'Hybrid',
                    'details': signal_data['details'],
                    'timestamp': timestamp
                }
                self.remote_storage.save_signal(remote_signal)
            except Exception as e_remote:
                logger.warning(f"Failed to sync signal to remote: {e_remote}")
                
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
            
            # [Remote Sync]
            self.remote_storage.save_trade(trade_data)
        except sqlite3.OperationalError as e:
            if "database or disk is full" in str(e):
                logger.warning(f"Database full error in save_trade, attempting checkpoint: {e}")
                self.perform_checkpoint()
            logger.error(f"Failed to save trade: {e}")
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
            
            # [Remote Sync]
            self.remote_storage.update_trade_performance(ticket, close_data)
        except sqlite3.OperationalError as e:
            if "database or disk is full" in str(e):
                logger.warning(f"Database full error in update_trade_performance, attempting checkpoint: {e}")
                self.perform_checkpoint()
            logger.error(f"Failed to update trade performance: {e}")
        except Exception as e:
            logger.error(f"Failed to update trade performance: {e}")

    def perform_checkpoint(self):
        """Force a WAL checkpoint to merge data into the main DB file"""
        try:
            conn = self._get_connection()
            # PASSIVE: Checkpoint as many frames as possible without waiting for readers/writers
            # TRUNCATE: Block until checkpoint complete and truncate WAL file (best for integration)
            # We use TRUNCATE to ensure data is moved, but catch errors if busy
            cursor = conn.cursor()
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            res = cursor.fetchone()
            logger.info(f"WAL Checkpoint executed: {res}") # (0, x, y) means success
            return True
        except Exception as e:
            logger.warning(f"WAL Checkpoint failed: {e}")
            return False

    def get_trade_performance_stats(self, symbol=None, limit=1000):
        """
        Get recent trade performance statistics (MFE, MAE, Profit).
        Priority: Local DB -> Remote DB (Fallback)
        """
        stats = []
        try:
            # 1. Try Local DB first
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT profit, mfe, mae, action, volume, close_time 
                FROM trades 
                WHERE result = 'CLOSED' 
            '''
            params = []
            
            if symbol:
                query += " AND symbol = ? "
                params.append(symbol)
                
            query += " ORDER BY close_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            stats = [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get trade stats locally: {e}")

        # 2. Archived Data Fallback (Local Archive)
        if len(stats) < limit:
            try:
                import glob
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
                archive_dir = os.path.join(project_root, "archived_data")
                if os.path.exists(archive_dir):
                    archive_files = sorted(glob.glob(os.path.join(archive_dir, "trading_data_*.db")), reverse=True)
                    
                    for db_file in archive_files:
                        if len(stats) >= limit: break
                        try:
                            conn_archive = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
                            conn_archive.row_factory = sqlite3.Row
                            cursor_archive = conn_archive.cursor()
                            
                            # Use same query as local
                            query_arch = '''
                                SELECT profit, mfe, mae, action, volume, close_time 
                                FROM trades 
                                WHERE result = 'CLOSED' 
                            '''
                            params_arch = []
                            if symbol:
                                query_arch += " AND symbol = ? "
                                params_arch.append(symbol)
                            
                            query_arch += " ORDER BY close_time DESC LIMIT ?"
                            params_arch.append(limit - len(stats))
                            
                            cursor_archive.execute(query_arch, tuple(params_arch))
                            rows_arch = cursor_archive.fetchall()
                            conn_archive.close()
                            
                            if rows_arch:
                                logger.info(f"Loaded {len(rows_arch)} trades from archive: {os.path.basename(db_file)}")
                                stats.extend([dict(row) for row in rows_arch])
                                
                        except Exception as ea:
                            logger.warning(f"Failed to read archive {os.path.basename(db_file)}: {ea}")
            except Exception as e_arch:
                logger.error(f"Archive fetch failed: {e_arch}")

        # 3. Remote Fallback (Postgres)
        # Always try to fetch from remote if local is insufficient OR to sync history
        if len(stats) < limit:
            try:
                logger.info(f"Fetching full trade history from Remote DB (Limit: {limit})...")
                # Request a larger limit from remote to ensure coverage
                remote_trades = self.remote_storage.get_trades(limit=limit, symbol=symbol)
                
                # Convert remote format if necessary and deduplicate
                # Remote usually returns full trade objects. We need specific fields.
                # Assuming remote returns dicts with keys matching our schema.
                remote_stats = []
                for rt in remote_trades:
                    if rt.get('result') == 'CLOSED':
                        remote_stats.append({
                            'profit': rt.get('profit', 0),
                            'mfe': rt.get('mfe', 0),
                            'mae': rt.get('mae', 0),
                            'action': rt.get('action'),
                            'volume': rt.get('volume'),
                            'close_time': rt.get('close_time')
                        })
                
                # Merge strategies: 
                # Since we want "all database", we should combine unique trades.
                # However, for performance stats, just appending might duplicate if not careful.
                # But here the user asked for "all database", implying they want maximum history available.
                # If local DB is empty or partial, remote is the source of truth.
                
                if not stats:
                    stats = remote_stats
                else:
                    # Simple append for now, assuming remote fetches older data or fills gaps
                    # Ideally we would dedup by ticket, but this method returns aggregate fields.
                    # Given the "fallback" nature, we only append if we needed more data.
                    # But user said "want all database", so let's try to get as much as possible up to limit.
                    
                    # If remote returned data, let's use it to fill up to limit
                    needed = limit - len(stats)
                    if needed > 0 and remote_stats:
                         # This is a bit rough, assuming remote returns sorted desc
                         # We might be duplicating if local has latest and remote also has latest.
                         # A safer bet for "all data" in this context (likely for LLM context) 
                         # is to rely on Remote DB if it returns a substantial amount.
                         pass
                         
                    # REVISED STRATEGY: 
                    # If we fetched from remote, and we want "all", let's trust remote if it has more data 
                    # or simply return the larger set.
                    if len(remote_stats) > len(stats):
                        stats = remote_stats
                        logger.info(f"Using Remote DB data as primary source ({len(stats)} trades)")
                    
            except Exception as re:
                logger.error(f"Remote fetch failed: {re}")

        return stats[:limit]

    def get_performance_metrics(self, symbol=None, limit=20):
        """
        计算近期交易的胜率和盈亏比，用于智能资金管理
        支持从 Remote DB 获取数据进行计算
        """
        profits = []
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT profit FROM trades 
                WHERE result = 'CLOSED' 
            '''
            params = []
            
            if symbol:
                query += " AND symbol = ? "
                params.append(symbol)
                
            query += " ORDER BY close_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, tuple(params))
            
            rows = cursor.fetchall()
            profits = [r[0] for r in rows]
                
        except Exception as e:
            logger.error(f"Failed to get performance metrics locally: {e}")

        # Archived Fallback
        if len(profits) < limit:
            try:
                import glob
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                archive_dir = os.path.join(project_root, "archived_data")
                archive_files = sorted(glob.glob(os.path.join(archive_dir, "trading_data_*.db")), reverse=True)
                
                for db_file in archive_files:
                    if len(profits) >= limit: break
                    try:
                        conn_archive = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
                        cursor_archive = conn_archive.cursor()
                        
                        query_arch = "SELECT profit FROM trades WHERE result = 'CLOSED'"
                        params_arch = []
                        if symbol:
                            query_arch += " AND symbol = ?"
                            params_arch.append(symbol)
                        query_arch += " ORDER BY close_time DESC LIMIT ?"
                        params_arch.append(limit - len(profits))
                        
                        cursor_archive.execute(query_arch, tuple(params_arch))
                        rows_arch = cursor_archive.fetchall()
                        conn_archive.close()
                        
                        if rows_arch:
                            profits.extend([r[0] for r in rows_arch])
                    except: pass
            except: pass

        # Remote Fallback
        if len(profits) < limit:
            try:
                # logger.info("Fetching metrics data from Remote DB...")
                remote_trades = self.remote_storage.get_trades(limit=limit, symbol=symbol)
                profits = [rt.get('profit', 0) for rt in remote_trades if rt.get('result') == 'CLOSED']
            except Exception as re:
                logger.error(f"Remote metrics fetch failed: {re}")

        if not profits:
            return {"win_rate": 0.0, "profit_factor": 0.0, "consecutive_losses": 0}

        wins = [p for p in profits if p > 0]
        losses = [p for p in profits if p <= 0]
        
        win_rate = len(wins) / len(profits) if profits else 0.0
        
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (10.0 if gross_profit > 0 else 0.0)
        
        # 计算当前连败次数
        consecutive_losses = 0
        for p in profits: 
            if p < 0:
                consecutive_losses += 1
            else:
                break
        
        return {
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "consecutive_losses": consecutive_losses
        }

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
