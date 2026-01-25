import sqlite3
import os
import glob
import logging
import pandas as pd
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DBConsolidator")

def consolidate_dbs(project_root):
    # Main DB location
    main_db_path = os.path.join(project_root, "gold", "trading_data.db")
    
    # Define paths to search for other DBs
    search_paths = [
        project_root, # Root directory
        os.path.join(project_root, "archived_data")
    ]
    
    # Find all .db files
    candidate_files = []
    for path in search_paths:
        if os.path.exists(path):
            # Search for .db files
            files = glob.glob(os.path.join(path, "*.db"))
            candidate_files.extend(files)
            
    # Filter out the main DB itself to avoid self-merge
    candidate_files = [f for f in candidate_files if os.path.abspath(f) != os.path.abspath(main_db_path)]
    
    if not candidate_files:
        logger.info("No other database files found to consolidate.")
        return

    logger.info(f"Found {len(candidate_files)} database files to process.")
    
    # Ensure main DB exists
    if not os.path.exists(main_db_path):
        logger.error(f"Main DB not found at {main_db_path}. Please initialize it first.")
        return

    try:
        # Connect to Main DB
        main_conn = sqlite3.connect(main_db_path)
        main_cursor = main_conn.cursor()
        
        # Enable WAL for performance
        main_cursor.execute('PRAGMA journal_mode=WAL;')
        main_cursor.execute('PRAGMA synchronous=NORMAL;')
        
        # Tables we want to merge
        tables_to_merge = ['trades', 'signals', 'account_metrics', 'market_data']
        
        for db_file in candidate_files:
            file_name = os.path.basename(db_file)
            logger.info(f"Processing {file_name}...")
            
            # 1. Check if file is empty (0 bytes)
            if os.path.getsize(db_file) == 0:
                logger.info(f"  -> File is empty (0 bytes). Deleting...")
                try:
                    os.remove(db_file)
                    logger.info("  -> Deleted.")
                except Exception as e:
                    logger.error(f"  -> Failed to delete: {e}")
                continue

            try:
                # 2. Open candidate DB in read-only mode
                src_conn = sqlite3.connect(f"file:{db_file}?mode=ro", uri=True)
                
                # Check if it has any tables
                src_cursor = src_conn.cursor()
                src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = src_cursor.fetchall()
                
                if not tables:
                    logger.info(f"  -> No tables found (empty DB). Deleting...")
                    src_conn.close()
                    os.remove(db_file)
                    continue
                
                # 3. Merge Data
                for table in tables_to_merge:
                    try:
                        # Read data from source
                        df = pd.read_sql_query(f"SELECT * FROM {table}", src_conn)
                        if not df.empty:
                            
                            # TRADES: ticket is PK
                            if table == 'trades':
                                count = 0
                                for _, row in df.iterrows():
                                    try:
                                        cols = ', '.join(row.index)
                                        placeholders = ', '.join(['?'] * len(row))
                                        sql = f"INSERT OR IGNORE INTO trades ({cols}) VALUES ({placeholders})"
                                        main_cursor.execute(sql, tuple(row.values))
                                        count += main_cursor.rowcount
                                    except Exception: pass
                                logger.info(f"  -> Merged {count} trades.")
                                
                            # MARKET_DATA: timestamp, symbol, timeframe is PK
                            elif table == 'market_data':
                                count = 0
                                for _, row in df.iterrows():
                                    try:
                                        cols = ', '.join(row.index)
                                        placeholders = ', '.join(['?'] * len(row))
                                        sql = f"INSERT OR IGNORE INTO market_data ({cols}) VALUES ({placeholders})"
                                        main_cursor.execute(sql, tuple(row.values))
                                        count += main_cursor.rowcount
                                    except Exception: pass
                                logger.info(f"  -> Merged {count} market_data rows.")

                            # SIGNALS: No PK usually, just append
                            elif table == 'signals':
                                # To avoid duplicates if we re-run, maybe we should check?
                                # But for now, user wants to integrate.
                                df.to_sql('signals', main_conn, if_exists='append', index=False)
                                logger.info(f"  -> Appended {len(df)} signals.")
                                
                            # ACCOUNT_METRICS: timestamp is PK
                            elif table == 'account_metrics':
                                count = 0
                                for _, row in df.iterrows():
                                    try:
                                        cols = ', '.join(row.index)
                                        placeholders = ', '.join(['?'] * len(row))
                                        sql = f"INSERT OR IGNORE INTO account_metrics ({cols}) VALUES ({placeholders})"
                                        main_cursor.execute(sql, tuple(row.values))
                                        count += main_cursor.rowcount
                                    except Exception: pass
                                logger.info(f"  -> Merged {count} account_metrics rows.")
                                
                    except Exception as e_table:
                        # Table might not exist in source, which is normal
                        pass
                
                src_conn.close()
                
                # 4. Delete the file after successful processing
                logger.info(f"  -> Successfully processed. Deleting file.")
                os.remove(db_file)
                
            except Exception as e_file:
                logger.error(f"  -> Failed to process {file_name}: {e_file}")

        main_conn.commit()
        main_conn.close()
        logger.info("Consolidation complete.")

    except Exception as e:
        logger.error(f"Critical error during consolidation: {e}")

if __name__ == "__main__":
    # Assuming this script is in scripts/, so project root is one level up
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    print(f"Project Root: {project_root}")
    consolidate_dbs(project_root)
