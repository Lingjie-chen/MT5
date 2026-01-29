import os
import sys
import logging
import subprocess
from datetime import datetime
from sqlalchemy import create_engine, text
import csv

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
    Uses server-side SQL to deduplicate and streams results to CSV (no pandas).
    """
    try:
        engine = create_engine(POSTGRES_URL)
        with engine.connect() as conn:
            logger.info("✅ Connected to PostgreSQL.")
            
            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)
            
            files_changed = False
            
            # TRADES: keep latest per ticket
            logger.info("📦 Backing up table: trades...")
            trades_sql = text("""
                SELECT t.*
                FROM trades t
                WHERE NOT EXISTS (
                    SELECT 1 FROM trades t2
                    WHERE t2.ticket = t.ticket
                      AND t2.ctid > t.ctid
                )
                ORDER BY t.ticket
            """)
            filepath = os.path.join(BACKUP_DIR, "trades_backup.csv")
            _stream_query_to_csv(conn, trades_sql, filepath)
            files_changed = True

            # SIGNALS: keep latest per (symbol,timeframe,timestamp)
            logger.info("📦 Backing up table: signals...")
            signals_sql = text("""
                SELECT s.*
                FROM signals s
                WHERE NOT EXISTS (
                    SELECT 1 FROM signals s2
                    WHERE s2.symbol = s.symbol
                      AND s2.timeframe = s.timeframe
                      AND s2.timestamp = s.timestamp
                      AND s2.ctid > s.ctid
                )
                ORDER BY s.symbol, s.timeframe, s.timestamp
            """)
            filepath = os.path.join(BACKUP_DIR, "signals_backup.csv")
            _stream_query_to_csv(conn, signals_sql, filepath)
            files_changed = True

            # ACCOUNT_METRICS: keep latest per timestamp
            logger.info("📦 Backing up table: account_metrics...")
            metrics_sql = text("""
                SELECT m.*
                FROM account_metrics m
                WHERE NOT EXISTS (
                    SELECT 1 FROM account_metrics m2
                    WHERE m2.timestamp = m.timestamp
                      AND m2.ctid > m.ctid
                )
                ORDER BY m.timestamp
            """)
            filepath = os.path.join(BACKUP_DIR, "account_metrics_backup.csv")
            _stream_query_to_csv(conn, metrics_sql, filepath)
            files_changed = True

        # Push to GitHub
        if files_changed:
            logger.info("🔄 Pushing backups to GitHub...")
            subprocess.run(["git", "add", "scripts/postgres_backup/"], cwd=PROJECT_ROOT, check=True)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"backup: update postgres data {timestamp}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=PROJECT_ROOT, check=False)
            subprocess.run(["git", "push", "origin", "master"], cwd=PROJECT_ROOT, check=True)
            logger.info("✅ Backup pushed to GitHub successfully.")
        else:
            logger.info("No data found to backup.")
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")

def _stream_query_to_csv(conn, sql_text, csv_path):
    """
    Execute query and stream rows to CSV without loading all into memory.
    """
    result = conn.execution_options(stream_results=True).execute(sql_text)
    cols = result.keys()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for row in result:
            writer.writerow(list(row))

if __name__ == "__main__":
    backup_postgres_to_csv()
