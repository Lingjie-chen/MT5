import os
import sys
import logging
# Remove pandas import since it's not strictly needed for this script and causes memory issues
# import pandas as pd 
from sqlalchemy import create_engine, text
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PostgresCleaner")

# Configuration
POSTGRES_URL = os.getenv("POSTGRES_CONNECTION_STRING", "postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot")

def clean_postgres_db():
    """
    Connects to PostgreSQL and removes duplicate records using SQL logic.
    """
    try:
        engine = create_engine(POSTGRES_URL)
        conn = engine.connect()
        logger.info("✅ Connected to PostgreSQL for cleanup.")
        
        # 1. Clean Trades (Deduplicate by ticket)
        # Strategy: Keep the row with the largest ctid (latest physical row) for each ticket
        logger.info("🧹 Cleaning 'trades' table...")
        sql_trades = """
            DELETE FROM trades a 
            USING trades b 
            WHERE a.ctid < b.ctid 
            AND a.ticket = b.ticket;
        """
        res_trades = conn.execute(text(sql_trades))
        conn.commit()
        logger.info(f"   Removed duplicate trades.") # Row count requires result proxy check if supported

        # 2. Clean Signals (Deduplicate by symbol, timeframe, timestamp)
        logger.info("🧹 Cleaning 'signals' table...")
        sql_signals = """
            DELETE FROM signals a 
            USING signals b 
            WHERE a.ctid < b.ctid 
            AND a.symbol = b.symbol 
            AND a.timeframe = b.timeframe
            AND a.timestamp = b.timestamp;
        """
        res_signals = conn.execute(text(sql_signals))
        conn.commit()
        logger.info(f"   Removed duplicate signals.")

        # 3. Clean Account Metrics (Deduplicate by timestamp)
        logger.info("🧹 Cleaning 'account_metrics' table...")
        sql_metrics = """
            DELETE FROM account_metrics a 
            USING account_metrics b 
            WHERE a.ctid < b.ctid 
            AND a.timestamp = b.timestamp;
        """
        res_metrics = conn.execute(text(sql_metrics))
        conn.commit()
        logger.info(f"   Removed duplicate account metrics.")

        conn.close()
        logger.info("✅ PostgreSQL cleanup complete.")

    except Exception as e:
        logger.error(f"❌ PostgreSQL cleanup failed: {e}")

if __name__ == "__main__":
    clean_postgres_db()
