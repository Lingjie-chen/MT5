import os
import subprocess
import sys
import shutil

def run_git_cmd(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return e.stderr.strip()

def fix_git_lock():
    lock_file = os.path.join(".git", "index.lock")
    if os.path.exists(lock_file):
        print(f"⚠️  Found stale git lock file: {lock_file}")
        try:
            os.remove(lock_file)
            print("✅ Deleted stale lock file.")
        except Exception as e:
            print(f"❌ Failed to delete lock file: {e}")

def resolve_conflicts():
    print("🔧 Checking for Git conflicts...")
    
    # 1. Check status
    status = run_git_cmd(["git", "status"])
    
    if "Unmerged paths" in status or "deleted by them" in status:
        print("⚠️  Conflicts detected! Attempting auto-resolution...")
        
        # Strategy: Always keep local DB files
        # Get list of unmerged files
        lines = status.split('\n')
        db_files = []
        for line in lines:
            if "deleted by them:" in line or "both modified:" in line:
                parts = line.split(':')
                if len(parts) > 1:
                    fname = parts[-1].strip()
                    if fname.endswith('.db'):
                        db_files.append(fname)
        
        if db_files:
            print(f"📦 Preserving local DB files: {db_files}")
            # Add them to stage (this keeps the local version in 'deleted by them' case)
            run_git_cmd(["git", "add"] + db_files)
            
            # Commit
            print("💾 Committing resolution...")
            run_git_cmd(["git", "commit", "-m", "Auto-resolve: Keep local DB files"])
            print("✅ Conflicts resolved.")
        else:
            print("ℹ️  No DB conflicts found. If there are code conflicts, manual intervention might be needed.")
            
    elif "rebase in progress" in status:
        print("⚠️  Git Rebase in progress detected.")
        print("🛑 Aborting rebase to restore stability...")
        run_git_cmd(["git", "rebase", "--abort"])
        print("✅ Rebase aborted.")
        
    elif "Merge" in status and "You have unmerged paths" in status:
        # Catch-all for other merge states
        print("⚠️  Merge state detected.")
        run_git_cmd(["git", "commit", "--no-edit"]) 

    else:
        print("✅ No conflicts detected.")

if __name__ == "__main__":
    # Ensure we are in root
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    
    fix_git_lock()
    resolve_conflicts()
