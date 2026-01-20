import os
import sys
import logging
import argparse
from sqlalchemy import create_engine, text

# Add project root to path to allow importing from scripts package
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Try to import from the enhanced checkpoint_dbs
try:
    from scripts.checkpoint_dbs import DBSyncManager
except ImportError:
    # If running from project root, scripts might be a package
    try:
        from scripts.checkpoint_dbs import DBSyncManager
    except ImportError:
        print("Error: Could not import DBSyncManager from scripts/checkpoint_dbs.py")
        print("Please ensure scripts/checkpoint_dbs.py exists and is updated.")
        sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MigrationTool")

def main():
    parser = argparse.ArgumentParser(description="Manual SQLite to Postgres Migration Tool")
    parser.add_argument("--reset", action="store_true", help="WARNING: Truncate Postgres tables before syncing (Fresh Start)")
    args = parser.parse_args()

    # Configuration
    POSTGRES_URL = os.getenv("POSTGRES_CONNECTION_STRING", "postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Project root

    logger.info("Initializing Migration Tool...")
    
    try:
        pg_engine = create_engine(POSTGRES_URL)
        with pg_engine.connect() as conn:
            pass
    except Exception as e:
        logger.error(f"Fatal: Cannot connect to Postgres: {e}")
        return

    # Initialize Manager
    db_manager = DBSyncManager(BASE_DIR, pg_engine)
    
    if args.reset:
        logger.warning("⚠️  RESET FLAG DETECTED. Truncating target tables in 5 seconds...")
        import time
        time.sleep(5)
        try:
            with pg_engine.connect() as conn:
                for table in db_manager.tables_to_sync.keys():
                    logger.info(f"Truncating {table}...")
                    conn.execute(f"TRUNCATE TABLE {table} CASCADE")
        except Exception as e:
            logger.error(f"Failed to truncate tables: {e}")
            return

    logger.info("Starting Full Sync...")
    
    # Run Sync
    db_manager.sync_all()
    
    logger.info("Migration Completed Successfully.")

if __name__ == "__main__":
    main()
