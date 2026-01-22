import sqlite3
import os
import time
import argparse
import sys
import glob
import subprocess
import logging
import json
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
import pandas as pd
import numpy as np
import importlib.util

# Try to import git_auto_resolve
try:
    from scripts import git_auto_resolve
except ImportError:
    # If run directly from scripts folder
    try:
        import git_auto_resolve
    except ImportError:
        git_auto_resolve = None

# Adjust path to allow importing from gold package
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("auto_sync_engine.log", mode='a', encoding='utf-8')
    ]
)

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logger = logging.getLogger("AutoSyncEngine")

# Configuration
POSTGRES_URL = os.getenv("POSTGRES_CONNECTION_STRING", "postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot")

class GitSyncManager:
    """Handles auto-syncing of local files with GitHub"""
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def sync_code_only(self):
        """Sync ONLY code files (exclude .db), high frequency"""
        try:
            # 1. Add all files
            subprocess.run(["git", "add", "."], cwd=self.base_dir, check=False)
            
            # 2. Unstage Database files (Keep them for full sync later)
            # Using wildcards for root and subdirectories
            # Note: Git pathspec allows '**' for recursive matching
            subprocess.run(["git", "reset", "HEAD", "**/*.db"], cwd=self.base_dir, check=False, stderr=subprocess.DEVNULL)
            # Fallback for simple shells if needed, but git handles **
            
            # 3. Check for staged changes
            status = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=self.base_dir).decode("utf-8")
            
            if status.strip():
                logger.info("Git (Code): Local code changes detected. Syncing...")
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                subprocess.run(["git", "commit", "-m", f"auto: code update {timestamp}"], cwd=self.base_dir, check=True)
                
                # Pull & Push
                self.pull_and_push()
            else:
                # Even if no local changes, pull remote code updates
                # Optimization: Only pull if some time passed? Or always?
                # For "Real-time", maybe just check remote?
                # Let's do a lightweight fetch/pull check
                self.pull_and_push(only_pull_if_needed=True)

        except Exception as e:
            logger.error(f"Git Code Sync Error: {e}")

    def pull_and_push(self, only_pull_if_needed=False):
        """Helper to Pull (Rebase) then Push"""
        try:
            # Pull
            subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=self.base_dir, capture_output=True, check=False)
            # Push
            subprocess.run(["git", "push", "origin", "master"], cwd=self.base_dir, capture_output=True, check=False)
        except Exception as e:
             logger.error(f"Git Pull/Push Error: {e}")

    def pull_updates(self):
        """Full Sync: Pull updates with rebase, auto-committing ALL local changes"""
        try:
            # 1. Check for local changes
            status = subprocess.check_output(["git", "status", "--porcelain"], cwd=self.base_dir).decode("utf-8")
            if status.strip():
                logger.info("Git (Full): Local changes detected. Auto-committing...")
                subprocess.run(["git", "add", "."], cwd=self.base_dir, check=True)
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                subprocess.run(["git", "commit", "-m", f"auto: full sync {timestamp}"], cwd=self.base_dir, check=True)

            # 2. Pull (Rebase)
            result = subprocess.run(["git", "pull", "--rebase", "origin", "master"], cwd=self.base_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"Git: Pull failed: {result.stderr}")
                
                # Attempt auto-resolve if available
                if git_auto_resolve:
                    logger.info("Git: Attempting auto-resolution via git_auto_resolve...")
                    git_auto_resolve.fix_git_state()
                    git_auto_resolve.resolve_conflicts()
                
                # Try aborting rebase just in case
                subprocess.run(["git", "rebase", "--abort"], cwd=self.base_dir, stderr=subprocess.DEVNULL)
                # Fallback: Merge strategy 'ours'
                logger.info("Git: Attempting merge (strategy: ours)...")
                subprocess.run(["git", "pull", "--no-edit", "-s", "recursive", "-X", "ours", "origin", "master"], cwd=self.base_dir, check=True)
            else:
                if "Already up to date" not in result.stdout:
                    logger.info("Git: Successfully updated from remote.")

        except Exception as e:
            logger.error(f"Git Pull Error: {e}")

    def push_updates(self):
        """Push local commits to remote"""
        try:
            # Check if we are ahead
            # git rev-list --count --left-right origin/master...HEAD
            # Simplified: just try push. If up to date, it does nothing.
            result = subprocess.run(["git", "push", "origin", "master"], cwd=self.base_dir, capture_output=True, text=True)
            if result.returncode == 0:
                if "Everything up-to-date" not in result.stderr:
                    logger.info("Git: Pushed local changes to GitHub.")
            else:
                logger.warning(f"Git Push Failed: {result.stderr}")
        except Exception as e:
            logger.error(f"Git Push Error: {e}")

    def sync(self):
        self.pull_updates()

        # --- NEW: Auto-Backup Postgres to GitHub ---
        try:
            # Import dynamically to avoid circular imports if any
            spec = importlib.util.spec_from_file_location("backup_postgres", os.path.join(self.base_dir, "scripts", "backup_postgres.py"))
            if spec and spec.loader:
                backup_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(backup_module)
                backup_module.backup_postgres_to_csv()
        except Exception as e:
            logger.warning(f"Postgres Backup Failed: {e}")
        # -------------------------------------------

        self.push_updates()

    def cleanup_local_dbs(self, db_manager):
        """
        Syncs to Postgres, Verifies, and THEN Deletes local SQLite files.
        Using DBSyncManager for DB operations.
        """
        logger.info("\n🧹 Starting Secure Cleanup (Sync -> Verify -> Delete)...")
        
        dbs = db_manager.get_dbs()
        if not dbs:
            logger.info("  (No local DB files found to clean)")
            return

        for db_file in dbs:
            if not os.path.exists(db_file): continue
            
            try:
                # 1. Check WAL Empty (Checkpoint Success)
                wal = db_file + "-wal"
                if os.path.exists(wal) and os.path.getsize(wal) > 0:
                    # Try one last checkpoint
                    db_manager.checkpoint_wal(db_file)
                    # If still not empty, skip
                    if os.path.exists(wal) and os.path.getsize(wal) > 0:
                        logger.info(f"  [SKIP] {os.path.basename(db_file)} (WAL not empty)")
                        continue

                # 2. Sync & Verify with Postgres
                # First ensure it's synced
                try:
                    conn = sqlite3.connect(db_file)
                    for table, config in db_manager.tables_to_sync.items():
                        db_manager.sync_table(conn, table, config)
                    conn.close()
                except Exception as e:
                    logger.error(f"  [ERROR] Sync failed for {os.path.basename(db_file)}: {e}")
                    continue

                # Then verify
                if self.verify_db_synced(db_file, db_manager):
                    # 3. Safe Delete
                    self.safe_delete_db(db_file)
                else:
                    logger.warning(f"  [KEEP] {os.path.basename(db_file)} (Verification failed)")

            except Exception as e:
                logger.error(f"  [ERROR] Processing {os.path.basename(db_file)}: {e}")

    def verify_db_synced(self, db_path, db_manager):
        """Verify that all data in local DB exists in Postgres"""
        try:
            sqlite_conn = sqlite3.connect(db_path)
            all_synced = True
            
            for table in db_manager.tables_to_sync.keys():
                # Check SQLite count
                try:
                    count_sqlite = pd.read_sql_query(f"SELECT COUNT(*) FROM {table}", sqlite_conn).iloc[0, 0]
                except:
                    continue # Table doesn't exist locally, fine
                
                if count_sqlite == 0: continue

                # Check Postgres count (Simple check: PG count >= SQLite count)
                # Better check: Max ID/Timestamp matches
                try:
                    count_pg = pd.read_sql_query(f"SELECT COUNT(*) FROM {table}", db_manager.pg_engine).iloc[0, 0]
                    if count_pg < count_sqlite:
                        logger.warning(f"    Table {table} mismatch: Local={count_sqlite}, Remote={count_pg}")
                        all_synced = False
                        break
                except:
                    logger.warning(f"    Table {table} missing in Remote")
                    all_synced = False
                    break
            
            sqlite_conn.close()
            return all_synced
        except Exception as e:
            logger.error(f"    Verification error: {e}")
            return False

    def safe_delete_db(self, db_path):
        """Safely delete DB and its artifacts"""
        max_retries = 3
        for i in range(max_retries):
            try:
                os.remove(db_path)
                logger.info(f"  [DELETE] {os.path.basename(db_path)} (Safe cleanup completed)")
                
                # Clean artifacts
                wal = db_path + "-wal"
                shm = db_path + "-shm"
                if os.path.exists(wal): 
                    try: os.remove(wal)
                    except: pass
                if os.path.exists(shm): 
                    try: os.remove(shm)
                    except: pass
                break
            except OSError as e:
                if i < max_retries - 1:
                    logger.warning(f"  Delete failed (locked?), retrying in 1s... ({i+1}/{max_retries})")
                    time.sleep(1)
                else:
                    logger.error(f"  Failed to delete {db_path}: {e}")

class DBSyncManager:
    """Handles SQLite WAL checkpointing and Sync to Postgres"""
    def __init__(self, base_dir, pg_engine):
        self.base_dir = base_dir
        self.pg_engine = pg_engine
        self.tables_to_sync = {
            "trades": {"pk": "ticket", "date_col": "time"},
            "signals": {"pk": None, "date_col": "timestamp"}, # Use timestamp to filter
            "account_metrics": {"pk": None, "date_col": "timestamp"}
        }

    def get_dbs(self):
        """Find all relevant DB files"""
        patterns = [
            os.path.join(self.base_dir, 'gold', 'trading_data_*.db'),
            os.path.join(self.base_dir, 'crypto', '*.db'),
            os.path.join(self.base_dir, 'trading_data.db')
        ]
        files = []
        for p in patterns:
            files.extend(glob.glob(p))
        return list(set([f for f in files if os.path.exists(f)]))

    def checkpoint_wal(self, db_path):
        """Force WAL checkpoint to merge data into main DB file"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # TRUNCATE ensures that -wal and -shm files are reset (merged into .db)
            cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
            conn.close()
            return True
        except Exception as e:
            logger.debug(f"WAL Checkpoint failed for {os.path.basename(db_path)}: {e}")
            return False

    def sync_table(self, sqlite_conn, table_name, config):
        """Sync a single table from SQLite to Postgres"""
        try:
            # 1. Read new data from SQLite
            # Optimization: We only want *new* data.
            # Strategy: Query PG for max timestamp/ID, then query SQLite for > max.
            
            # Check if table exists in SQLite
            try:
                # Quick check
                pd.read_sql_query(f"SELECT 1 FROM {table_name} LIMIT 1", sqlite_conn)
            except:
                return # Table doesn't exist in SQLite
            
            # Get Max from Postgres
            max_val = None
            pk = config['pk']
            date_col = config['date_col']
            
            filter_clause = ""
            
            try:
                # Check if table exists in PG first
                insp = inspect(self.pg_engine)
                if table_name in insp.get_table_names():
                    if pk:
                        query = f"SELECT MAX({pk}) FROM {table_name}"
                        max_val = pd.read_sql_query(query, self.pg_engine).iloc[0, 0]
                        if max_val is not None:
                            filter_clause = f" WHERE {pk} > {max_val}"
                    elif date_col:
                        query = f"SELECT MAX({date_col}) FROM {table_name}"
                        max_val = pd.read_sql_query(query, self.pg_engine).iloc[0, 0]
                        if max_val is not None:
                            # Ensure string format for SQLite comparison
                            filter_clause = f" WHERE {date_col} > '{max_val}'"
            except Exception as e:
                # Table likely doesn't exist in PG yet, sync all
                pass

            # Read filtered data
            query = f"SELECT * FROM {table_name} {filter_clause}"
            df = pd.read_sql_query(query, sqlite_conn)
            
            if df.empty:
                return

            # Data Type Conversion
            if date_col and date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col])
            
            # Specific fix for 'trades' table columns
            if table_name == 'trades':
                for col in ['close_time', 'time']:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
            
            # Write to Postgres
            # method='multi' is faster for inserts
            df.to_sql(table_name, self.pg_engine, if_exists='append', index=False, chunksize=1000, method='multi')
            logger.info(f"DB: Synced {len(df)} rows to {table_name}")

        except Exception as e:
            logger.error(f"DB: Sync error for {table_name}: {e}")

    def sync_all(self):
        dbs = self.get_dbs()
        for db_path in dbs:
            # 1. Checkpoint
            self.checkpoint_wal(db_path)
            
            # 2. Sync
            try:
                conn = sqlite3.connect(db_path)
                for table, config in self.tables_to_sync.items():
                    self.sync_table(conn, table, config)
                conn.close()
            except Exception as e:
                logger.error(f"DB: Failed to process {os.path.basename(db_path)}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Auto Sync Engine")
    parser.add_argument("--interval", type=int, default=10, help="Sync interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run sync once and exit (Migration mode)")
    parser.add_argument("--cleanup", action="store_true", help="Enable Safe Cleanup (Sync+Verify before delete)")
    parser.add_argument("--no-git", action="store_true", help="Skip Git auto-sync operations")
    parser.add_argument("--reset", action="store_true", help="WARNING: Truncate Postgres tables before syncing (Fresh Start)")
    
    args = parser.parse_args()

    # Detect base dir dynamically
    base_dir = project_root
    logger.info(f"Base Directory: {base_dir}")
    
    # --- NEW: Merge Archives to Main DB (Run at startup) ---
    try:
        spec = importlib.util.spec_from_file_location("merge_archives", os.path.join(base_dir, "scripts", "merge_archives.py"))
        if spec and spec.loader:
            merge_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(merge_module)
            merge_module.merge_archives_to_main(base_dir)
    except Exception as e:
        logger.warning(f"Archive Merge Failed: {e}")
    # -------------------------------------------------------

    # Initialize Managers
    git_manager = GitSyncManager(base_dir)
    
    try:
        pg_engine = create_engine(POSTGRES_URL)
        # Test connection
        with pg_engine.connect() as conn:
            pass
    except Exception as e:
        logger.error(f"Fatal: Cannot connect to Postgres: {e}")
        return

    db_manager = DBSyncManager(base_dir, pg_engine)
    
    # Handle Reset (Truncate)
    if args.reset:
        logger.warning("⚠️  RESET FLAG DETECTED. Truncating target tables in 5 seconds...")
        time.sleep(5)
        try:
            with pg_engine.connect() as conn:
                for table in db_manager.tables_to_sync.keys():
                    logger.info(f"Truncating {table}...")
                    conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to truncate tables: {e}")
            return

    if args.once:
        logger.info("Running single sync pass...")
        
        # --- NEW: Merge Archives to Main DB ---
        try:
            spec = importlib.util.spec_from_file_location("merge_archives", os.path.join(base_dir, "scripts", "merge_archives.py"))
            if spec and spec.loader:
                merge_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(merge_module)
                merge_module.merge_archives_to_main(base_dir)
        except Exception as e:
            logger.warning(f"Archive Merge Failed: {e}")
        # --------------------------------------

        db_manager.sync_all()
        if not args.no_git:
            git_manager.sync()
        if args.cleanup:
            git_manager.cleanup_local_dbs(db_manager)
        logger.info("Sync completed.")
        return

    logger.info("🚀 Auto Sync Engine Started...")
    logger.info(f"   - Sync Interval: {args.interval}s")

    last_full_git_sync = 0
    full_git_sync_interval = 300 # 5 minutes
    
    last_code_sync = 0
    code_sync_interval = 30 # 30 seconds (High freq for code)

    if args.cleanup:
        git_manager.cleanup_local_dbs(db_manager)

    try:
        while True:
            current_time = time.time()

            # 1. DB Sync (High Frequency)
            db_manager.sync_all()
            
            if not args.no_git:
                # 2. Code Sync (Real-time)
                if current_time - last_code_sync > code_sync_interval:
                    # logger.debug("Running Code Sync...")
                    git_manager.sync_code_only()
                    last_code_sync = current_time

                # 3. Full Git Sync (Low Frequency)
                if current_time - last_full_git_sync > full_git_sync_interval:
                    logger.info("Running Full Git Sync (Including DBs)...")
                    git_manager.sync()
                    last_full_git_sync = current_time
            
            # 4. Cleanup (if enabled)
            if args.cleanup:
                git_manager.cleanup_local_dbs(db_manager)
            
            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Engine stopped by user.")
    except Exception as e:
        logger.error(f"Engine crashed: {e}")
        # Restart loop or exit? Exit for safety.
        raise e

if __name__ == "__main__":
    main()
