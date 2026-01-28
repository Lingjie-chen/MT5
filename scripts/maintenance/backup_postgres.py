import os
import sys
import logging
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import subprocess

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PostgresBackup")

# Configuration
POSTGRES_URL = os.getenv("POSTGRES_CONNECTION_STRING", "postgresql://chenlingjie:clj568741230@localhost:5432/trading_bot")
# Changed BACKUP_DIR to point to scripts/postgres_backup to unify locations
# Previous location was project_root/postgres_backup (c:\Users\Administrator\Desktop\MT5\postgres_backup)
# New location: project_root/scripts/postgres_backup (c:\Users\Administrator\Desktop\MT5\scripts\postgres_backup)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKUP_DIR = os.path.join(PROJECT_ROOT, "scripts", "postgres_backup")

def backup_postgres_to_csv():
    """
    Dumps PostgreSQL tables to CSV files and pushes them to GitHub.
    Unifies backup location to scripts/postgres_backup.
    """
    try:
        # 1. Connect to Postgres
        engine = create_engine(POSTGRES_URL)
        logger.info("✅ Connected to PostgreSQL.")
        
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            
        # 2. Define tables to backup
        tables = ["trades", "signals", "account_metrics"]
        
        files_changed = False
        
        for table in tables:
            try:
                logger.info(f"📦 Backing up table: {table}...")
                query = f"SELECT * FROM {table} ORDER BY 1 DESC" # Default sort
                df = pd.read_sql_query(query, engine)
                
                if df.empty:
                    logger.warning(f"   Table {table} is empty, skipping.")
                    continue
                
                # Remove duplicates (keep first occurrence)
                # Assuming 'ticket' is unique for trades, 'id' for signals/metrics if available.
                # If no specific unique key, drop exact duplicates.
                initial_len = len(df)
                df.drop_duplicates(inplace=True)
                final_len = len(df)
                if initial_len > final_len:
                    logger.info(f"   Removed {initial_len - final_len} duplicate rows.")
                
                # Save to CSV
                filename = f"{table}_backup.csv"
                filepath = os.path.join(BACKUP_DIR, filename)
                df.to_csv(filepath, index=False)
                logger.info(f"   Saved {len(df)} rows to {filename}")
                files_changed = True
                
            except Exception as e:
                logger.error(f"   Failed to backup {table}: {e}")

        # 3. Push to GitHub
        if files_changed:
            logger.info("🔄 Pushing backups to GitHub...")
            # Git needs to run from project root or handle paths correctly
            
            # Git Add
            subprocess.run(["git", "add", "scripts/postgres_backup/"], cwd=PROJECT_ROOT, check=True)
            
            # Git Commit
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"backup: update postgres data {timestamp}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=False) 
            
            # Git Push
            subprocess.run(["git", "push", "origin", "master"], cwd=PROJECT_ROOT, check=True)
            logger.info("✅ Backup pushed to GitHub successfully.")
        else:
            logger.info("No data found to backup.")
            
        # 4. Cleanup old directory if empty or redundant
        old_backup_dir = os.path.join(PROJECT_ROOT, "postgres_backup")
        if os.path.exists(old_backup_dir):
            try:
                # Optional: Remove old directory if we want to enforce the move
                # subprocess.run(["git", "rm", "-r", "postgres_backup/"], cwd=PROJECT_ROOT, check=False)
                pass 
            except Exception: pass

    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    backup_postgres_to_csv()