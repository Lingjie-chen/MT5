import sqlite3
import pandas as pd
import os
from sqlalchemy import create_engine, text
from datetime import datetime
import json
import logging

# Configuration
SQLITE_DB_PATH = "/Users/lenovo/tmp/quant_trading_strategy/gold/trading_data.db"
# If you have symbol-specific DBs, you can add them to a list
ADDITIONAL_DBS = [
    "/Users/lenovo/tmp/quant_trading_strategy/gold/trading_data_GOLD.db",
    "/Users/lenovo/tmp/quant_trading_strategy/gold/trading_data_ETHUSD.db",
    "/Users/lenovo/tmp/quant_trading_strategy/gold/trading_data_EURUSD.db"
]

POSTGRES_URL = "postgresql://postgres:password@localhost:5432/trading_bot"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Migration")

def migrate_db(sqlite_path, pg_engine):
    if not os.path.exists(sqlite_path):
        logger.warning(f"SQLite DB not found: {sqlite_path}")
        return

    logger.info(f"Migrating data from {sqlite_path}...")
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        
        # 1. Migrate Trades
        try:
            logger.info("Migrating Trades...")
            df_trades = pd.read_sql_query("SELECT * FROM trades", sqlite_conn)
            if not df_trades.empty:
                # Ensure correct types
                if 'time' in df_trades.columns:
                    df_trades['time'] = pd.to_datetime(df_trades['time'])
                if 'close_time' in df_trades.columns:
                    df_trades['close_time'] = pd.to_datetime(df_trades['close_time'])
                
                # Write to Postgres (upsert is harder with pandas to_sql, so we use 'append' and handle duplicates via separate logic or clean start)
                # For simplicity in migration, we use 'append'. If table exists, ensure no primary key conflicts or truncate first if fresh start.
                # Here we assume fresh start or just append.
                
                # Check if ticket exists to avoid PK error? 
                # Better: Use simple to_sql with if_exists='append', catching duplicate errors is tricky in bulk.
                # Recommendation: Truncate tables in PG before first migration if acceptable, or use chunking.
                
                df_trades.to_sql('trades', pg_engine, if_exists='append', index=False, chunksize=1000, method='multi')
                logger.info(f"Migrated {len(df_trades)} trades.")
        except Exception as e:
            logger.error(f"Error migrating trades: {e}")

        # 2. Migrate Signals
        try:
            logger.info("Migrating Signals...")
            df_signals = pd.read_sql_query("SELECT * FROM signals", sqlite_conn)
            if not df_signals.empty:
                if 'timestamp' in df_signals.columns:
                    df_signals['timestamp'] = pd.to_datetime(df_signals['timestamp'])
                
                # Handle JSON fields if they are strings in SQLite
                if 'details' in df_signals.columns:
                    # Postgres JSON type expects dict/list objects if using sqlalchemy, or string if raw.
                    # Pandas to_sql with sqlalchemy usually handles JSON type if defined in model, but here we are using raw connection reflection?
                    # Let's try to keep them as strings or convert depending on PG driver behavior.
                    # Usually strings work fine for JSON columns in psycopg2.
                    pass

                df_signals.to_sql('signals', pg_engine, if_exists='append', index=False, chunksize=1000, method='multi')
                logger.info(f"Migrated {len(df_signals)} signals.")
        except Exception as e:
            logger.error(f"Error migrating signals: {e}")

        # 3. Migrate Account Metrics
        try:
            logger.info("Migrating Account Metrics...")
            df_metrics = pd.read_sql_query("SELECT * FROM account_metrics", sqlite_conn)
            if not df_metrics.empty:
                if 'timestamp' in df_metrics.columns:
                    df_metrics['timestamp'] = pd.to_datetime(df_metrics['timestamp'])
                
                df_metrics.to_sql('account_metrics', pg_engine, if_exists='append', index=False, chunksize=1000, method='multi')
                logger.info(f"Migrated {len(df_metrics)} account metrics.")
        except Exception as e:
            logger.error(f"Error migrating account metrics: {e}")

        # 4. Migrate Market Data (Optional - might be huge)
        # Uncomment if you want to migrate OHLCV history
        """
        try:
            logger.info("Migrating Market Data (this may take a while)...")
            df_market = pd.read_sql_query("SELECT * FROM market_data", sqlite_conn)
            if not df_market.empty:
                if 'timestamp' in df_market.columns:
                    df_market['timestamp'] = pd.to_datetime(df_market['timestamp'])
                
                df_market.to_sql('market_data', pg_engine, if_exists='append', index=False, chunksize=5000, method='multi')
                logger.info(f"Migrated {len(df_market)} market data rows.")
        except Exception as e:
            logger.error(f"Error migrating market data: {e}")
        """
        
        sqlite_conn.close()

    except Exception as e:
        logger.error(f"Failed to migrate {sqlite_path}: {e}")

def main():
    # 1. Initialize Postgres Schema
    try:
        pg_engine = create_engine(POSTGRES_URL)
        # Ensure tables exist (we can import models from server folder if available, or just rely on them being created by server startup)
        # For this script, let's assume server started once or use raw SQL to create if missing.
        # But better: Run the server startup logic.
        
        logger.info("Initializing PostgreSQL schema...")
        from gold.server.models import Base
        Base.metadata.create_all(bind=pg_engine)
        
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        return

    # 2. Migrate Main DB
    migrate_db(SQLITE_DB_PATH, pg_engine)

    # 3. Migrate Additional DBs (Symbol specific)
    for db_path in ADDITIONAL_DBS:
        migrate_db(db_path, pg_engine)
    
    logger.info("Migration completed.")

if __name__ == "__main__":
    # Fix python path to allow importing from gold.server
    import sys
    sys.path.append("/Users/lenovo/tmp/quant_trading_strategy")
    main()
