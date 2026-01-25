import sqlite3
import os
import shutil
import psutil
from datetime import datetime
import time

DB_PATH = os.path.join("gold", "trading_data.db")

def kill_locking_processes(file_path):
    """Attempt to find and kill processes locking the file (Windows specific)"""
    print(f"🔪 Attempting to kill processes locking {file_path}...")
    
    # 1. First Pass: Kill python processes by name (safer, less permission issues)
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
                        if 'gold' in cmd_str or 'checkpoint_dbs' in cmd_str or 'uvicorn' in cmd_str:
                            print(f"   Terminating process {proc.info['pid']} ({cmd_str[:50]}...)")
                            proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"⚠️ Failed to kill python processes: {e}")

    # 2. Wait a bit
    time.sleep(2)

def check_and_repair_db():
    if not os.path.exists(DB_PATH):
        return

    print(f"🏥 Checking database integrity: {DB_PATH}...")
    is_corrupt = False
    try:
        # Open in read-only mode to check
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] != "ok":
            is_corrupt = True
            print(f"❌ Database integrity check failed: {result[0]}")
    except sqlite3.DatabaseError as e:
        is_corrupt = True
        print(f"❌ Database is malformed: {e}")
    except Exception as e:
        print(f"⚠️ Warning: Unable to check database (might be locked): {e}")
        # If we can't open it, it might be locked. 
        # But if we are running this script, it means we want to START the system.
        # So any lock is likely a stale/zombie process.
        # Let's try to verify if it's corrupt by seeing if we can open it after killing processes.
        kill_locking_processes(os.path.abspath(DB_PATH))
        
        try:
             conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
             conn.close()
        except sqlite3.DatabaseError:
             is_corrupt = True
        except Exception:
             # If still locked, it's problematic, but we might not want to delete it yet unless sure.
             # However, if user is restarting, they usually want a working system.
             # Let's Assume corrupt if we really can't access it.
             print("⚠️ Still cannot access database. Assuming corruption/lock issue.")
             is_corrupt = True

    if is_corrupt:
        print("🚑 Attempting automatic repair...")
        
        # Try to kill zombies again just in case
        kill_locking_processes(os.path.abspath(DB_PATH))
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{DB_PATH}.corrupt.{timestamp}"
        
        try:
            shutil.move(DB_PATH, backup_path)
            print(f"✅ Corrupted database moved to {backup_path}")
            print("✨ A new database will be created and synced automatically from Remote.")
        except Exception as e:
            print(f"❌ Failed to move corrupted database: {e}")
            # Try force delete if move fails
            try:
                if os.path.exists(DB_PATH):
                    os.remove(DB_PATH)
                    print("✅ Corrupted database deleted (move failed).")
            except Exception as e2:
                print(f"❌ Failed to delete corrupted database: {e2}")
                print("⚠️ Please manually delete gold/trading_data.db and restart.")

if __name__ == "__main__":
    # Ensure we are in project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    check_and_repair_db()
