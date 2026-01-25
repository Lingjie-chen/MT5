import sqlite3
import os
import glob
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DBMerger")

def merge_databases():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    main_db_path = os.path.join(base_dir, "trading_data.db")
    
    # Check if main DB exists
    if not os.path.exists(main_db_path):
        logger.error(f"Main database not found at {main_db_path}")
        return

    # Find all other trading_data_*.db files
    pattern = os.path.join(base_dir, "trading_data_*.db")
    all_dbs = glob.glob(pattern)
    
    # Filter out the main DB and make sure we don't process it
    dbs_to_merge = [db for db in all_dbs if os.path.abspath(db) != os.path.abspath(main_db_path)]
    
    if not dbs_to_merge:
        logger.info("No databases found to merge.")
        return

    logger.info(f"Found {len(dbs_to_merge)} databases to merge: {[os.path.basename(db) for db in dbs_to_merge]}")

    conn = sqlite3.connect(main_db_path)
    cursor = conn.cursor()

    # Enable foreign keys just in case, though not strictly needed for this
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Ensure tables exist in main DB (just in case it's empty/new)
    # We rely on the existing schema in main_db. 
    # If main_db is empty, we might need to initialize it. 
    # Assuming it's initialized as it exists.

    for db_path in dbs_to_merge:
        db_filename = os.path.basename(db_path)
        logger.info(f"Processing {db_filename}...")
        
        try:
            # Attach the source database
            # We use a simple alias 'source_db'
            # Note: paths in SQL statements should be escaped or passed as parameters if possible, 
            # but ATTACH statement usually requires string literal. 
            # We'll use f-string but assume paths are safe (local files).
            attach_sql = f"ATTACH DATABASE '{db_path}' AS source_db"
            cursor.execute(attach_sql)
            
            # 1. Merge market_data
            logger.info(f"  Merging market_data from {db_filename}...")
            cursor.execute("""
                INSERT OR IGNORE INTO main.market_data 
                SELECT * FROM source_db.market_data
            """)
            logger.info(f"  Merged market_data rows: {cursor.rowcount}")

            # 2. Merge trades
            logger.info(f"  Merging trades from {db_filename}...")
            cursor.execute("""
                INSERT OR IGNORE INTO main.trades 
                SELECT * FROM source_db.trades
            """)
            logger.info(f"  Merged trades rows: {cursor.rowcount}")

            # 3. Merge account_metrics
            logger.info(f"  Merging account_metrics from {db_filename}...")
            cursor.execute("""
                INSERT OR IGNORE INTO main.account_metrics 
                SELECT * FROM source_db.account_metrics
            """)
            logger.info(f"  Merged account_metrics rows: {cursor.rowcount}")

            # 4. Merge signals
            # signals table has no primary key. We want to avoid duplicates.
            # We'll assume if timestamp, symbol, timeframe, signal, and strength match, it's a duplicate.
            logger.info(f"  Merging signals from {db_filename}...")
            cursor.execute("""
                INSERT INTO main.signals 
                SELECT * FROM source_db.signals s
                WHERE NOT EXISTS (
                    SELECT 1 FROM main.signals m 
                    WHERE m.timestamp = s.timestamp 
                    AND m.symbol = s.symbol 
                    AND m.timeframe = s.timeframe 
                    AND m.signal = s.signal
                )
            """)
            logger.info(f"  Merged signals rows: {cursor.rowcount}")

            conn.commit()
            
            # Detach
            cursor.execute("DETACH DATABASE source_db")
            
            # Close connection to file (implied by detach) so we can delete it
            
            # Delete the file
            logger.info(f"  Deleting {db_filename}...")
            os.remove(db_path)
            logger.info(f"  Successfully processed and deleted {db_filename}")

        except sqlite3.OperationalError as e:
            logger.error(f"  SQLite Error processing {db_filename}: {e}")
            # Try to detach if failed
            try:
                cursor.execute("DETACH DATABASE source_db")
            except:
                pass
        except Exception as e:
            logger.error(f"  Error processing {db_filename}: {e}")
            try:
                cursor.execute("DETACH DATABASE source_db")
            except:
                pass

    conn.close()
    logger.info("Database merge completed.")

if __name__ == "__main__":
    merge_databases()
