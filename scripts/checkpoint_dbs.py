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
        os.path.join(base_dir, 'gold', 'trading_data_ETHUSD.db'),
        os.path.join(base_dir, 'gold', 'trading_data_EURUSD.db')
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

def main():
    parser = argparse.ArgumentParser(description="SQLite WAL Checkpoint Tool")
    parser.add_argument("--loop", action="store_true", help="Run in a loop")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds for loop mode")
    
    args = parser.parse_args()
    
    base_dir = os.getcwd()
    
    if args.loop:
        print(f"Starting Checkpoint Service (Interval: {args.interval}s)...")
        try:
            while True:
                print(f"\n--- Checkpoint Run at {time.strftime('%H:%M:%S')} ---")
                run_checkpoints(base_dir)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopping Checkpoint Service.")
    else:
        run_checkpoints(base_dir)

if __name__ == "__main__":
    main()
