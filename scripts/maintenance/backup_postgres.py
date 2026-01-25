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
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "postgres_backup")

def backup_postgres_to_csv():
    """
    Dumps PostgreSQL tables to CSV files and pushes them to GitHub.
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
            base_dir = os.path.dirname(BACKUP_DIR)
            
            # Git Add
            subprocess.run(["git", "add", "postgres_backup/"], cwd=base_dir, check=True)
            
            # Git Commit
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"backup: update postgres data {timestamp}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=base_dir, check=False) # Check=False in case no changes
            
            # Git Push
            subprocess.run(["git", "push", "origin", "master"], cwd=base_dir, check=True)
            logger.info("✅ Backup pushed to GitHub successfully.")
        else:
            logger.info("No data found to backup.")

    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")

if __name__ == "__main__":
    backup_postgres_to_csv()