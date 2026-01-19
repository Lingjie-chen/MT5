import sqlite3
import os
import time
import argparse
import sys

def checkpoint_db(db_path):
    print(f"Checking point database: {db_path}")
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        # Force a checkpoint. 
        # TRUNCATE blocks until no writer, checkpoints, and truncates the WAL file.
        cursor = conn.cursor()
        cursor.execute("PRAGMA wal_checkpoint(TRUNCATE);")
        result = cursor.fetchone()
        print(f"Checkpoint result: {result}") # (busy, log, checkpointed)
        conn.close()
        print(f"Successfully checkpointed {db_path}")
    except Exception as e:
        print(f"Error checkpointing {db_path}: {e}")

import subprocess

def git_pull_updates(base_dir):
    """Pull updates from remote repository"""
    try:
        print("⬇️ Checking for remote updates...")
        subprocess.run(["git", "pull", "origin", "master"], cwd=base_dir, check=True)
    except Exception as e:
        print(f"⚠️ Git pull failed: {e}")

def git_auto_sync(base_dir):
    """Auto commit and push changes if databases have changed"""
    
    # First, pull latest changes from GitHub
    git_pull_updates(base_dir)
    
    try:
        # Check if there are changes
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=base_dir).decode("utf-8")
        
        # Only proceed if DB files are modified
        if status.strip():
            print("Detected code/data changes, syncing to GitHub...")
            
            subprocess.run(["git", "add", "."], cwd=base_dir, check=True)
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            subprocess.run(["git", "commit", "-m", f"auto: sync updates {timestamp}"], cwd=base_dir, check=True)
            
            subprocess.run(["git", "push", "origin", "master"], cwd=base_dir, check=True)
            print("Successfully synced all updates to GitHub.")
        else:
            print("No changes to sync.")
            
    except Exception as e:
        print(f"Git auto-sync failed: {e}")

def run_checkpoints(base_dir):
    # List of databases to checkpoint
    # Now includes separate DBs for each symbol
    dbs = [
        os.path.join(base_dir, 'crypto', 'crypto_trading.db'),
        os.path.join(base_dir, 'gold', 'trading_data_GOLD.db'),
        os.path.join(base_dir, 'gold', 'trading_data_XAUUSDm.db'), # Exness Gold
        os.path.join(base_dir, 'gold', 'trading_data_ETHUSD.db'),
        os.path.join(base_dir, 'gold', 'trading_data_ETHUSDm.db'), # Exness ETH
        os.path.join(base_dir, 'gold', 'trading_data_EURUSD.db'),
        os.path.join(base_dir, 'gold', 'trading_data_EURUSDm.db')  # Exness EUR
    ]

    for db in dbs:
        checkpoint_db(db)
        
        # Check if WAL/SHM files still exist
        wal_file = db + "-wal"
        shm_file = db + "-shm"
        
        if os.path.exists(wal_file):
            # print(f"WAL file still exists: {wal_file}")
            try:
                size = os.path.getsize(wal_file)
                if size == 0:
                     pass # Empty WAL is fine
                else:
                     print(f"WAL file size: {size} bytes (Should be 0 if truncated)")
            except Exception as e:
                print(f"Could not check WAL file: {e}")
        else:
            print(f"WAL file gone for {db}")

        if os.path.exists(shm_file):
            try:
                size = os.path.getsize(shm_file)
                # SHM file exists as long as there is an active connection
                # It doesn't contain persistent data itself, just the WAL index
                # print(f"SHM file exists (Active Index): {shm_file} ({size} bytes)")
                pass
            except Exception as e:
                print(f"Could not check SHM file: {e}")
        else:
            print(f"SHM file gone for {db}")

    # After checkpointing, try to sync with git
    git_auto_sync(base_dir)

def cleanup_local_dbs(base_dir):
    """
    Delete local SQLite files if data is fully migrated to Remote PostgreSQL.
    Assuming the bot architecture has shifted to Remote-First for history.
    This keeps the local environment lightweight (cache only).
    """
    import shutil
    
    # List of DB patterns or specific files to clean
    # Be careful not to delete config files
    targets = [
        "trading_data.db",
        "trading_data_*.db", # Matches trading_data_GOLD.db, etc.
        "crypto/crypto_trading.db"
    ]
    
    import glob
    print("\n🧹 Checking for local DB cleanup (Remote-First Mode)...")
    
    deleted_count = 0
    for pattern in targets:
        full_pattern = os.path.join(base_dir, pattern) if not os.path.isabs(pattern) else pattern
        # Handle glob inside subdirs if needed
        if "crypto/" in pattern:
             full_pattern = os.path.join(base_dir, pattern)
        else:
             full_pattern = os.path.join(base_dir, "gold", pattern) # Assuming most are in gold/ or root
             
        # Check root as well for trading_data.db
        if pattern == "trading_data.db":
             full_pattern = os.path.join(base_dir, "gold", pattern)

        # Glob expansion
        files = glob.glob(full_pattern)
        # Also check root for generic matches if not found
        if not files and "gold" in full_pattern:
             files = glob.glob(os.path.join(base_dir, pattern))

        for db_file in files:
            try:
                # Basic safety check: Don't delete if it's currently locked by another process?
                # Actually, in Windows, we might not be able to delete if locked.
                # But here we assume the bot re-creates them as temp cache, so deletion is safe if bot is stopped or we just want to clear history.
                # NOTE: If the bot is running, deleting the DB might cause errors or be blocked.
                # Strategy: Only delete if WAL file is empty (checkpointed) AND we want to enforce remote-only history.
                
                # Check if WAL exists and is empty (implies successful checkpoint)
                wal = db_file + "-wal"
                if os.path.exists(wal) and os.path.getsize(wal) > 0:
                    print(f"  [SKIP] {os.path.basename(db_file)} (WAL not empty, data pending)")
                    continue
                    
                # In this specific task context: User requested auto-delete to rely on Remote DB.
                # We perform the delete.
                os.remove(db_file)
                deleted_count += 1
                print(f"  [DELETE] {os.path.basename(db_file)} (Cleaned up for Remote-First mode)")
                
                # Also clean WAL/SHM if they exist
                if os.path.exists(wal): os.remove(wal)
                shm = db_file + "-shm"
                if os.path.exists(shm): os.remove(shm)
                
            except Exception as e:
                print(f"  [ERROR] Failed to delete {os.path.basename(db_file)}: {e}")

    if deleted_count == 0:
        print("  (No eligible DB files found for cleanup)")

def main():
    parser = argparse.ArgumentParser(description="SQLite WAL Checkpoint Tool")
    parser.add_argument("--loop", action="store_true", help="Run in a loop")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds for loop mode")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup local DB files after checkpoint (Remote-First Mode)")
    
    args = parser.parse_args()
    
    base_dir = os.getcwd()
    
    if args.loop:
        print(f"Starting Checkpoint Service (Interval: {args.interval}s)...")
        try:
            while True:
                print(f"\n--- Checkpoint Run at {time.strftime('%H:%M:%S')} ---")
                run_checkpoints(base_dir)
                if args.cleanup:
                    cleanup_local_dbs(base_dir)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopping Checkpoint Service.")
    else:
        run_checkpoints(base_dir)
        if args.cleanup:
            cleanup_local_dbs(base_dir)

if __name__ == "__main__":
    main()
