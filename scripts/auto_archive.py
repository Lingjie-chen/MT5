import os
import sys
import shutil
import logging
import psutil
import time
from datetime import datetime
import subprocess

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.checkpoint_dbs import DBSyncManager, GitSyncManager, POSTGRES_URL
from sqlalchemy import create_engine

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AutoArchiver")

def kill_locking_processes(file_path):
    """Attempt to find and kill processes locking the file (Windows specific)"""
    logger.info(f"🔪 Attempting to kill processes locking {os.path.basename(file_path)}...")
    try:
        current_pid = os.getpid()
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] == current_pid:
                    continue
                    
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmd_str = ' '.join(cmdline)
                        # Be specific about what we kill
                        if 'gold' in cmd_str or 'checkpoint_dbs' in cmd_str or 'uvicorn' in cmd_str:
                            logger.info(f"   Terminating process {proc.info['pid']} ({cmd_str[:50]}...)")
                            proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        time.sleep(2)
    except Exception as e:
        logger.warning(f"⚠️ Failed to kill locking processes: {e}")

def main():
    logger.info("Starting Auto-Archive Process...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Connect to Postgres
    try:
        pg_engine = create_engine(POSTGRES_URL)
        with pg_engine.connect() as conn:
            pass
        logger.info("✅ Connected to PostgreSQL.")
    except Exception as e:
        logger.error(f"Fatal: Cannot connect to Postgres: {e}")
        return

    # 2. Sync to Postgres
    logger.info("Syncing local data to PostgreSQL...")
    db_manager = DBSyncManager(base_dir, pg_engine)
    try:
        db_manager.sync_all()
        logger.info("✅ Data sync completed.")
    except Exception as e:
        logger.error(f"Sync failed: {e}")
    
    # 3. Archive & Clean Local
    archive_dir = os.path.join(base_dir, "archived_data")
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
        
    dbs = db_manager.get_dbs()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    archived_files = []
    
    for db_path in dbs:
        try:
            filename = os.path.basename(db_path)
            new_name = f"{os.path.splitext(filename)[0]}_{timestamp}.db"
            dest_path = os.path.join(archive_dir, new_name)
            
            # Kill locks before moving
            kill_locking_processes(db_path)
            
            shutil.move(db_path, dest_path)
            logger.info(f"📦 Archived {filename} -> {new_name}")
            archived_files.append(dest_path)
        except Exception as e:
            logger.error(f"Failed to archive {db_path}: {e}")

    if not archived_files:
        logger.info("Nothing to archive.")
        return

    # 4. Push to GitHub using GitSyncManager
    try:
        logger.info("Syncing changes to GitHub...")
        git_manager = GitSyncManager(base_dir)
        
        # Ensure we are on master (basic check)
        subprocess.run(["git", "checkout", "master"], cwd=base_dir, stderr=subprocess.DEVNULL)
        
        # Pull (will auto-commit the file moves)
        git_manager.pull_updates()
        
        # Push
        git_manager.push_updates()
        
        logger.info("✅ Successfully pushed to GitHub.")
    except Exception as e:
        logger.error(f"Git sync failed: {e}")

if __name__ == "__main__":
    main()
