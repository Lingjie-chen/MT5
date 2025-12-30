import sqlite3
import os
import time

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

def main():
    base_dir = os.getcwd()
    
    # List of databases to checkpoint
    dbs = [
        os.path.join(base_dir, 'crypto', 'crypto_trading.db'),
        os.path.join(base_dir, 'gold', 'trading_data.db')
    ]

    for db in dbs:
        checkpoint_db(db)
        
        # Check if WAL/SHM files still exist
        wal_file = db + "-wal"
        shm_file = db + "-shm"
        
        if os.path.exists(wal_file):
            print(f"WAL file still exists: {wal_file}")
            try:
                # Try to remove if empty or check size
                size = os.path.getsize(wal_file)
                print(f"WAL file size: {size} bytes")
                if size == 0:
                     print("WAL file is empty.")
            except Exception as e:
                print(f"Could not check WAL file: {e}")
        else:
            print(f"WAL file gone for {db}")

if __name__ == "__main__":
    main()
