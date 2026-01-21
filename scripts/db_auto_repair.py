import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join("gold", "trading_data.db")

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
        # If we can't open it, it might be locked or really bad
        print(f"⚠️ Warning: Unable to check database (might be locked): {e}")
        return

    if is_corrupt:
        print("🚑 Attempting automatic repair...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{DB_PATH}.corrupt.{timestamp}"
        
        try:
            # Force close any lingering connections if possible (not easy from outside process)
            # But since this runs at startup, we should be fine.
            shutil.move(DB_PATH, backup_path)
            print(f"✅ Corrupted database moved to {backup_path}")
            print("✨ A new database will be created and synced automatically from Remote.")
        except Exception as e:
            print(f"❌ Failed to move corrupted database: {e}")
            # Try force delete if move fails
            try:
                os.remove(DB_PATH)
                print("✅ Corrupted database deleted (move failed).")
            except Exception as e2:
                print(f"❌ Failed to delete corrupted database: {e2}")

if __name__ == "__main__":
    # Ensure we are in project root
    # The script is in scripts/, so up one level
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    check_and_repair_db()
