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
            return conn
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database {self.db_name}: {e}")
            return None

    def _initialize_db(self):
        """Initialize database tables"""
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Table for recording executed trades
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
                pnl REAL
            )
            ''')
            
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
