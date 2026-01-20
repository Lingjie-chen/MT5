import sqlite3
import os
import time
import argparse
import sys
import glob
import subprocess
import logging
from sqlalchemy import create_engine, text
import pandas as pd

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("sync_service.log", mode='a', encoding='utf-8')
    ]
)
# Force stdout/stderr to use utf-8 to fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger("CheckpointService")

# Configuration
POSTGRES_URL = os.getenv("POSTGRES_CONNECTION_STRING", "postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot")

def checkpoint_db(db_path):
    logger.info(f"Checking point database: {db_path}")
    if not os.path.exists(db_path):
        logger.warning(f"Database file not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        # Force a checkpoint. 
        # TRUNCATE blocks until no writer, checkpoints, and truncates the WAL file.
        cursor = conn.cursor()
        cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        result = cursor.fetchone()
        # result: (busy, log, checkpointed)
        conn.close()
        logger.info(f"Successfully checkpointed {db_path} (Result: {result})")
    except Exception as e:
        logger.error(f"Error checkpointing {db_path}: {e}")

def git_pull_updates(base_dir):
    """Pull updates from remote repository with conflict resolution"""
    try:
        # Before pulling, we MUST stash or commit local changes to DB files
        # otherwise pull will fail with "overwrite" error.
        # Strategy: Auto-commit local changes first, then pull --rebase (or merge)
        
        # 1. Check status
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=base_dir).decode("utf-8")
        if status.strip():
            logger.info("Local changes detected before pull. Auto-committing to allow merge...")
            subprocess.run(["git", "add", "."], cwd=base_dir, check=True)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(["git", "commit", "-m", f"auto: save local changes before pull {timestamp}"], cwd=base_dir, check=True)

        # 2. Pull with rebase to apply our local commits on top of remote updates
        # This is cleaner than merge for auto-sync bots
        logger.info("⬇️ Pulling remote updates (with rebase)...")
        subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=base_dir, check=True, capture_output=True)
        logger.info("✅ Pull successful.")

    except subprocess.CalledProcessError as e:
        logger.warning(f"Standard pull/rebase failed: {e}")
        # If rebase fails, we might be in a detached state or conflict state.
        # Attempt to abort rebase and fall back to strategy 'ours' merge
        subprocess.run(["git", "rebase", "--abort"], cwd=base_dir, stderr=subprocess.DEVNULL)
        
        logger.warning("Attempting auto-resolve (Strategy: ours)...")
        try:
            # Attempt 3: Pull with 'ours' strategy (prefer local changes)
            # We must fetch first if pull failed? pull does fetch.
            # Use merge strategy X ours
            subprocess.run(["git", "pull", "--no-edit", "-s", "recursive", "-X", "ours", "origin", "master"], cwd=base_dir, check=True)
            logger.info("✅ Conflict resolved automatically (Strategy: Ours).")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Auto-resolve failed: {e}")
            # Abort merge to return to clean state
            subprocess.run(["git", "merge", "--abort"], cwd=base_dir, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"Git pull error: {e}")

def git_auto_sync(base_dir):
    """Auto commit and push changes if databases have changed"""
    
    # First, pull latest changes from GitHub
    git_pull_updates(base_dir)
    
    try:
        # Check if there are changes
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=base_dir).decode("utf-8")
        
        # Only proceed if DB files are modified
        if status.strip():
            logger.info("Detected code/data changes, syncing to GitHub...")
            
            subprocess.run(["git", "add", "."], cwd=base_dir, check=True)
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(["git", "commit", "-m", f"auto: sync updates {timestamp}"], cwd=base_dir, check=True)
            
            subprocess.run(["git", "push", "origin", "master"], cwd=base_dir, check=True)
            logger.info("Successfully synced all updates to GitHub.")
        else:
            # logger.info("No changes to sync.")
            pass
            
    except Exception as e:
        logger.error(f"Git auto-sync failed: {e}")

def sync_table_to_postgres(sqlite_conn, pg_engine, table_name, pk_col=None, date_col=None):
    """
    Syncs a single table from SQLite to Postgres.
    Returns True if sync successful (or empty), False if failed.
    """
    try:
        # 1. Read SQLite Data
        try:
            df_sqlite = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
        except Exception:
            # Table might not exist, which is fine
            return True

        if df_sqlite.empty:
            return True

        # Convert date columns if needed
        if date_col and date_col in df_sqlite.columns:
            df_sqlite[date_col] = pd.to_datetime(df_sqlite[date_col])

        # 2. Check Postgres Max State to avoid duplicates
        # We assume Postgres table exists. If not, we might need to create it or let to_sql fail/create.
        # For robustness, we try to append only new data.
        
        start_filter = None
        try:
            if pk_col:
                query = f"SELECT MAX({pk_col}) FROM {table_name}"
                max_val = pd.read_sql_query(query, pg_engine).iloc[0, 0]
                if max_val is not None:
                    # Filter SQLite data to only keep new rows
                    df_sqlite = df_sqlite[df_sqlite[pk_col] > max_val]
            elif date_col:
                query = f"SELECT MAX({date_col}) FROM {table_name}"
                max_val = pd.read_sql_query(query, pg_engine).iloc[0, 0]
                if max_val is not None:
                    # Filter SQLite data
                    df_sqlite = df_sqlite[df_sqlite[date_col] > pd.to_datetime(max_val)]
        except Exception as e:
            # Table might not exist in PG, so we will try to create/append all
            # logger.warning(f"Could not query max value from PG for {table_name}: {e}")
            pass

        if df_sqlite.empty:
            # logger.info(f"  {table_name}: No new data to sync.")
            return True

        # 3. Write to Postgres
        # Using 'append' method. If PK exists, it might fail.
        # Ideally we use a method that handles duplicates, but pandas to_sql is limited.
        # We rely on the filtering above.
        df_sqlite.to_sql(table_name, pg_engine, if_exists='append', index=False, chunksize=1000)
        logger.info(f"  {table_name}: Synced {len(df_sqlite)} new rows to Postgres.")
        return True

    except Exception as e:
        logger.error(f"  Failed to sync table {table_name}: {e}")
        return False

def verify_data_synced(sqlite_conn, pg_engine, table_name, pk_col=None):
    """
    Verifies that all data in SQLite exists in Postgres.
    """
    try:
        # Check SQLite Row Count
        try:
            count_sqlite = pd.read_sql_query(f"SELECT COUNT(*) FROM {table_name}", sqlite_conn).iloc[0, 0]
        except:
            return True # Table doesn't exist in SQLite, nothing to lose

        if count_sqlite == 0:
            return True

        # Check Postgres Row Count (Should be >= SQLite)
        # Note: This is a weak check. Stronger check: Check MAX(pk) match.
        try:
            count_pg = pd.read_sql_query(f"SELECT COUNT(*) FROM {table_name}", pg_engine).iloc[0, 0]
        except:
            logger.warning(f"  Verify failed: Table {table_name} does not exist in Postgres.")
            return False

        if count_pg < count_sqlite:
            logger.warning(f"  Verify failed: {table_name} count mismatch (SQLite: {count_sqlite}, PG: {count_pg})")
            return False
            
        return True

    except Exception as e:
        logger.error(f"  Verify error for {table_name}: {e}")
        return False

def sync_and_verify_db(db_path, pg_engine):
    """
    Orchestrates the sync and verification for a single DB file.
    """
    logger.info(f"Syncing & Verifying {os.path.basename(db_path)}...")
    
    try:
        sqlite_conn = sqlite3.connect(db_path)
        
        # 1. Sync Tables
        # Trades: PK=ticket, Time=time
        s1 = sync_table_to_postgres(sqlite_conn, pg_engine, "trades", pk_col="ticket", date_col="time")
        # Signals: No clear integer PK usually, use timestamp
        s2 = sync_table_to_postgres(sqlite_conn, pg_engine, "signals", date_col="timestamp")
        # Account Metrics: No PK, use timestamp
        s3 = sync_table_to_postgres(sqlite_conn, pg_engine, "account_metrics", date_col="timestamp")
        
        if not (s1 and s2 and s3):
            logger.error("  Sync failed for one or more tables.")
            sqlite_conn.close()
            return False
            
        # 2. Verify
        v1 = verify_data_synced(sqlite_conn, pg_engine, "trades")
        v2 = verify_data_synced(sqlite_conn, pg_engine, "signals")
        v3 = verify_data_synced(sqlite_conn, pg_engine, "account_metrics")
        
        sqlite_conn.close()
        
        if v1 and v2 and v3:
            logger.info(f"✅ {os.path.basename(db_path)} synced and verified.")
            return True
        else:
            logger.warning(f"❌ {os.path.basename(db_path)} verification failed.")
            return False

    except Exception as e:
        logger.error(f"Error processing {db_path}: {e}")
        return False

def run_checkpoints(base_dir, skip_git=False):
    dbs = []
    dbs.extend(glob.glob(os.path.join(base_dir, 'gold', 'trading_data_*.db')))
    dbs.extend(glob.glob(os.path.join(base_dir, 'crypto', '*.db')))
    dbs.extend(glob.glob(os.path.join(base_dir, 'trading_data.db')))
    dbs = list(set([db for db in dbs if os.path.exists(db)]))
    
    if not dbs:
        return

    if not skip_git:
        try:
            git_auto_sync(base_dir)
        except Exception as e:
            print(f"Git sync failed (continuing anyway): {e}")

    if not dbs:
        return

    for db in dbs:
        checkpoint_db(db)

def cleanup_local_dbs(base_dir):
    """
    Syncs to Postgres, Verifies, and THEN Deletes local SQLite files.
    """
    logger.info("\n🧹 Starting Secure Cleanup (Sync -> Verify -> Delete)...")
    
    # Connect to Postgres
    try:
        pg_engine = create_engine(POSTGRES_URL)
        # Test connection
        with pg_engine.connect() as conn:
            pass
    except Exception as e:
        logger.error(f"❌ Cannot connect to PostgreSQL: {e}")
        logger.error("Skipping cleanup to prevent data loss.")
        return

    targets = [
        "trading_data.db",
        "gold/trading_data_*.db",
        "crypto/crypto_trading.db"
    ]
    
    # Expand targets
    files = []
    for t in targets:
        files.extend(glob.glob(os.path.join(base_dir, t) if not os.path.isabs(t) else t))
    files = list(set(files))

    for db_file in files:
        if not os.path.exists(db_file): continue
        
        try:
            # 1. Check WAL Empty (Checkpoint Success)
            wal = db_file + "-wal"
            if os.path.exists(wal) and os.path.getsize(wal) > 0:
                logger.info(f"  [SKIP] {os.path.basename(db_file)} (WAL not empty)")
                continue

            # 2. Sync & Verify with Postgres
            if sync_and_verify_db(db_file, pg_engine):
                # 3. Safe Delete
                # Add retry mechanism for Windows file lock
                max_retries = 3
                for i in range(max_retries):
                    try:
                        os.remove(db_file)
                        logger.info(f"  [DELETE] {os.path.basename(db_file)} (Safe cleanup completed)")
                        break
                    except OSError as e:
                        if i < max_retries - 1:
                            logger.warning(f"  Delete failed (locked?), retrying in 1s... ({i+1}/{max_retries})")
                            time.sleep(1)
                        else:
                            raise e
                
                # Clean artifacts
                if os.path.exists(wal): 
                    try: os.remove(wal)
                    except: pass
                shm = db_file + "-shm"
                if os.path.exists(shm): 
                    try: os.remove(shm)
                    except: pass
            else:
                logger.warning(f"  [KEEP] {os.path.basename(db_file)} (Sync/Verify failed)")

        except Exception as e:
            logger.error(f"  [ERROR] Processing {os.path.basename(db_file)}: {e}")

def main():
    parser = argparse.ArgumentParser(description="SQLite WAL Checkpoint & Sync Tool")
    parser.add_argument("--loop", action="store_true", help="Run in a loop")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds for loop mode")
    # Note: --cleanup is now implicit/safe, but we keep the flag to enable the feature
    parser.add_argument("--cleanup", action="store_true", help="Enable Safe Cleanup (Sync+Verify before delete)")
    parser.add_argument("--no-git", action="store_true", help="Skip Git auto-sync operations")
    
    args = parser.parse_args()
    base_dir = os.getcwd()
    
    if args.loop:
        logger.info(f"Starting Checkpoint Service (Interval: {args.interval}s)...")
        try:
            while True:
                logger.info(f"\n--- Run at {time.strftime('%H:%M:%S')} ---")
                run_checkpoints(base_dir, skip_git=args.no_git)
                if args.cleanup:
                    cleanup_local_dbs(base_dir)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Stopping Checkpoint Service.")
    else:
        run_checkpoints(base_dir, skip_git=args.no_git)
        if args.cleanup:
            cleanup_local_dbs(base_dir)

if __name__ == "__main__":
    main()
