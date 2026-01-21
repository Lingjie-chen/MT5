import sqlite3
import os
import glob
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ArchiveMerger")

def merge_archives_to_main(base_dir):
    """
    Merges all archived SQLite databases into the main trading_data.db
    """
    main_db_path = os.path.join(base_dir, "gold", "trading_data.db")
    archive_dir = os.path.join(base_dir, "archived_data")
    
    if not os.path.exists(main_db_path):
        logger.error(f"Main DB not found at {main_db_path}")
        return

    # Find all archived DBs
    archive_files = glob.glob(os.path.join(archive_dir, "*.db"))
    if not archive_files:
        logger.info("No archived files found to merge.")
        return

    logger.info(f"Found {len(archive_files)} archived databases to merge into main DB...")
    
    try:
        # Connect to Main DB
        main_conn = sqlite3.connect(main_db_path)
        main_cursor = main_conn.cursor()
        
        # Ensure tables exist in main DB (using schema from one of the archives or hardcoded)
        # We assume main DB is initialized. If not, DatabaseManager would have done it.
        
        total_trades_merged = 0
        
        for arch_file in archive_files:
            try:
                logger.info(f"Merging {os.path.basename(arch_file)}...")
                arch_conn = sqlite3.connect(f"file:{arch_file}?mode=ro", uri=True)
                
                # 1. Merge Trades
                # Read from archive
                try:
                    df_trades = pd.read_sql_query("SELECT * FROM trades", arch_conn)
                    if not df_trades.empty:
                        # Write to main (IGNORE duplicates based on ticket/PK)
                        # We use 'INSERT OR IGNORE' logic via pandas 'to_sql' is tricky, 
                        # so we use raw SQL for better control or append + drop duplicates.
                        # But 'ticket' is PK. 
                        
                        # Let's iterate and insert safely
                        count = 0
                        for _, row in df_trades.iterrows():
                            try:
                                # Construct INSERT OR IGNORE statement dynamically based on columns
                                cols = ', '.join(row.index)
                                placeholders = ', '.join(['?'] * len(row))
                                sql = f"INSERT OR IGNORE INTO trades ({cols}) VALUES ({placeholders})"
                                main_cursor.execute(sql, tuple(row.values))
                                count += main_cursor.rowcount
                            except Exception as e_insert:
                                # logger.warning(f"Insert failed: {e_insert}")
                                pass
                        
                        logger.info(f"  -> Merged {count} trades.")
                        total_trades_merged += count
                except Exception as e_trades:
                    logger.warning(f"  No trades table or error: {e_trades}")

                # 2. Merge Signals (Optional, usually high volume, maybe skip or filter?)
                # For now, let's merge signals too if needed.
                try:
                    df_signals = pd.read_sql_query("SELECT * FROM signals", arch_conn)
                    if not df_signals.empty:
                         # Signals might not have a PK, so duplicates are possible.
                         # We can check if timestamp+symbol+timeframe exists?
                         # For simplicity, let's append.
                         df_signals.to_sql('signals', main_conn, if_exists='append', index=False)
                         logger.info(f"  -> Merged {len(df_signals)} signals.")
                except: pass
                
                arch_conn.close()
                
            except Exception as e_file:
                logger.error(f"Failed to process archive {os.path.basename(arch_file)}: {e_file}")

        main_conn.commit()
        main_conn.close()
        logger.info(f"✅ Merge completed. Total new trades added: {total_trades_merged}")

    except Exception as e:
        logger.error(f"Merge process failed: {e}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    merge_archives_to_main(project_root)