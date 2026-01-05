import sqlite3
import logging
import json
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages the SQLite database for the Crypto Trading Bot.
    Ensures data is stored separately from other strategies (e.g. Gold strategy).
    """
    
    def __init__(self, db_name='crypto_trading.db'):
        """
        Initialize the database manager.
        
        Args:
            db_name (str): Name of the database file. Defaults to 'crypto_trading.db'.
        """
        self.db_name = db_name
        self.conn = None
        self._initialize_db()
        
    def _get_connection(self):
        """Create a database connection"""
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency and consistency
            conn.execute('PRAGMA journal_mode=WAL;')
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database {self.db_name}: {e}")
            return None

    def perform_checkpoint(self):
        """Force a WAL checkpoint to merge data into the main DB file"""
        conn = self._get_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            res = cursor.fetchone()
            logger.info(f"WAL Checkpoint executed: {res}")
            return True
        except sqlite3.Error as e:
            logger.warning(f"WAL Checkpoint failed: {e}")
            return False
        finally:
            conn.close()

    def _initialize_db(self):
        """Initialize database tables"""
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Table for recording executed trades
            # Added mfe, mae, close_time, close_price, profit columns for performance tracking
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                order_type TEXT NOT NULL,
                contracts REAL,
                price REAL,
                leverage INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                order_id TEXT,
                strategy_rationale TEXT,
                pnl REAL,
                close_price REAL,
                close_time DATETIME,
                profit REAL,
                mfe REAL,
                mae REAL
            )
            ''')
            
            # Check if columns exist (migration for existing db)
            cursor.execute("PRAGMA table_info(trades)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'mfe' not in columns:
                logger.info("Migrating database: Adding MFE/MAE columns...")
                cursor.execute("ALTER TABLE trades ADD COLUMN mfe REAL")
                cursor.execute("ALTER TABLE trades ADD COLUMN mae REAL")
                cursor.execute("ALTER TABLE trades ADD COLUMN close_price REAL")
                cursor.execute("ALTER TABLE trades ADD COLUMN close_time DATETIME")
                cursor.execute("ALTER TABLE trades ADD COLUMN profit REAL")
            
            # Table for recording market analysis logs
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                market_state TEXT,
                structure_score INTEGER,
                ai_decision TEXT,
                raw_analysis TEXT
            )
            ''')
            
            conn.commit()
            logger.info(f"Database {self.db_name} initialized successfully.")
            
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
        finally:
            conn.close()

    def log_trade(self, trade_data):
        """
        Log a trade to the database.
        
        Args:
            trade_data (dict): Dictionary containing trade details
        """
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO trades (symbol, action, order_type, contracts, price, leverage, order_id, strategy_rationale)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade_data.get('symbol'),
                trade_data.get('action'),
                trade_data.get('order_type'),
                trade_data.get('contracts'),
                trade_data.get('price'),
                trade_data.get('leverage'),
                trade_data.get('order_id'),
                trade_data.get('strategy_rationale')
            ))
            conn.commit()
            logger.info(f"Trade logged to database: {trade_data.get('action')} {trade_data.get('symbol')}")
        except sqlite3.Error as e:
            logger.error(f"Error logging trade: {e}")
        finally:
            conn.close()

    def log_analysis(self, symbol, market_state, structure_score, ai_decision, raw_analysis):
        """Log market analysis results"""
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO market_analysis (symbol, market_state, structure_score, ai_decision, raw_analysis)
            VALUES (?, ?, ?, ?, ?)
            ''', (symbol, market_state, structure_score, json.dumps(ai_decision), json.dumps(raw_analysis)))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error logging analysis: {e}")
        finally:
            conn.close()
            
    def get_recent_trades(self, limit=10):
        """Get recent trades"""
        conn = self._get_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching trades: {e}")
            return []
        finally:
            conn.close()

    def update_trade_performance(self, order_id, data):
        """Update trade with closing info (profit, MFE, MAE)"""
        conn = self._get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE trades 
                SET close_price = ?, close_time = ?, profit = ?, mfe = ?, mae = ?
                WHERE order_id = ?
            ''', (
                data.get('close_price'),
                data.get('close_time'),
                data.get('profit'),
                data.get('mfe'),
                data.get('mae'),
                order_id
            ))
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error updating trade performance: {e}")
        finally:
            conn.close()

    def save_trade_history_batch(self, trades):
        """Batch insert/update historical trades"""
        conn = self._get_connection()
        if not conn: return
        try:
            cursor = conn.cursor()
            count = 0
            for t in trades:
                # CCXT unified trade structure usually has 'id' as order id
                order_id = t.get('id') or t.get('order_id') or t.get('orderId')
                if not order_id: continue
                
                # Check if exists
                cursor.execute("SELECT id FROM trades WHERE order_id = ?", (str(order_id),))
                if cursor.fetchone():
                    continue
                    
                cursor.execute('''
                INSERT INTO trades (symbol, action, order_type, contracts, price, timestamp, order_id, profit, mfe, mae)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    t.get('symbol'),
                    t.get('side'),
                    t.get('type') or 'market', # Default to market if type is missing
                    t.get('amount'),
                    t.get('price'),
                    t.get('datetime') or datetime.fromtimestamp(t.get('timestamp')/1000).isoformat(), # Use datetime field if available
                    str(order_id),
                    t.get('info', {}).get('profit', 0) if t.get('info') else 0, # CCXT info often has raw exchange data
                    0, # mfe
                    0  # mae
                ))
                count += 1
            conn.commit()
            if count > 0:
                logger.info(f"Synced {count} historical trades to DB")
        except sqlite3.Error as e:
            logger.error(f"Error syncing history: {e}")
        finally:
            conn.close()

    def get_trade_performance_stats(self, limit=50):
        """Get statistics of recently closed trades for AI learning"""
        conn = self._get_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            # Fetch trades that have been closed (have MFE/MAE recorded)
            cursor.execute('''
                SELECT mfe, mae, profit, strategy_rationale, action
                FROM trades 
                WHERE mfe IS NOT NULL 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching trade stats: {e}")
            return []
        finally:
            conn.close()
