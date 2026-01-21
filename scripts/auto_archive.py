import os
import sys
import shutil
import logging
import time
import subprocess
from datetime import datetime
from sqlalchemy import create_engine

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import DBSyncManager from checkpoint_dbs
try:
    from scripts.checkpoint_dbs import DBSyncManager, POSTGRES_URL
except ImportError:
    # Handle case where scripts module might not be directly importable
    sys.path.append(os.path.join(project_root, 'scripts'))
    from checkpoint_dbs import DBSyncManager, POSTGRES_URL

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - AutoArchiver - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutoArchiver")

def git_push_archive(archive_dir, files):
    """Commit and push archived files to GitHub"""
    try:
        # 1. Add files
        subprocess.run(["git", "add", archive_dir], cwd=project_root, check=True)
        
        # 2. Commit
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg = f"archive: backup trading data {timestamp}"
        subprocess.run(["git", "commit", "-m", msg], cwd=project_root, check=True)
        
        # 3. Push
        logger.info("Pushing archive to GitHub...")
        result = subprocess.run(["git", "push", "origin", "master"], cwd=project_root, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ Archive pushed to GitHub successfully.")
        else:
            logger.warning(f"⚠️ Git Push failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Git operation failed: {e}")

def main():
    logger.info("Starting Auto-Archive Process...")
    
    # 1. Initialize Postgres Connection
    try:
        pg_engine = create_engine(POSTGRES_URL)
        # Test connection
        with pg_engine.connect() as conn:
            pass
        logger.info("✅ Connected to PostgreSQL.")
    except Exception as e:
        logger.error(f"❌ Cannot connect to Postgres: {e}")
        logger.warning("Skipping archive to prevent data loss (Postgres sync required).")
        return

    # 2. Sync to Postgres
    sync_manager = DBSyncManager(project_root, pg_engine)
    logger.info("Syncing local data to PostgreSQL...")
    try:
        sync_manager.sync_all()
        logger.info("✅ Data sync completed.")
    except Exception as e:
        logger.error(f"❌ Data sync failed: {e}")
        return

    # 3. Archive Local Files
    archive_dir = os.path.join(project_root, "archived_data")
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)

    # Define files to archive
    db_files = sync_manager.get_dbs()
    archived_files = []

    if not db_files:
        logger.info("No database files found to archive.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for db_path in db_files:
        try:
            filename = os.path.basename(db_path)
            # Create archive name: trading_data_20260121_120000.db
            name, ext = os.path.splitext(filename)
            new_name = f"{name}_{timestamp}{ext}"
            dest_path = os.path.join(archive_dir, new_name)
            
            # Move file
            shutil.move(db_path, dest_path)
            logger.info(f"📦 Archived: {filename} -> {new_name}")
            archived_files.append(dest_path)
            
        except Exception as e:
            logger.error(f"Failed to archive {db_path}: {e}")

    # 4. Push to GitHub
    if archived_files:
        git_push_archive(archive_dir, archived_files)
        logger.info("🎉 Archive process finished. Local DBs cleared.")
    else:
        logger.info("Nothing to archive.")

if __name__ == "__main__":
    main()
