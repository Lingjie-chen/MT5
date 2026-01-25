import os
import subprocess
import sys
import shutil

def run_git_cmd(args):
    try:
        # Check if git is available
        if shutil.which("git") is None:
            return "Git not found"
            
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return f"Error: {result.stderr.strip()}"
        return result.stdout.strip()
    except Exception as e:
        return str(e)

def force_delete_path(path):
    if os.path.exists(path):
        print(f"⚠️  Removing stuck path: {path}")
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print("✅ Removed.")
        except Exception as e:
            print(f"❌ Failed to remove {path}: {e}")

def fix_git_state():
    print("🔧 Checking Git state...")
    
    # 1. Remove lock file
    force_delete_path(os.path.join(".git", "index.lock"))
    
    # 2. Check for stuck rebase directories
    rebase_merge = os.path.join(".git", "rebase-merge")
    rebase_apply = os.path.join(".git", "rebase-apply")
    
    if os.path.exists(rebase_merge) or os.path.exists(rebase_apply):
        print("⚠️  Stuck rebase directory detected.")
        # Try abort first
        res = run_git_cmd(["git", "rebase", "--abort"])
        if "Error" in res or os.path.exists(rebase_merge):
            print("🛑 Abort failed or directory persists. Forcing cleanup...")
            force_delete_path(rebase_merge)
            force_delete_path(rebase_apply)

def resolve_conflicts():
    # 1. Check status
    status = run_git_cmd(["git", "status"])
    print(status)
    
    if "Unmerged paths" in status or "deleted by them" in status or "both modified" in status:
        print("⚠️  Conflicts detected! Attempting auto-resolution...")
        
        # Strategy: Always keep local DB files
        # Get list of unmerged files
        lines = status.split('\n')
        files_to_add = []
        
        for line in lines:
            # Parse conflict lines
            # Example: "        deleted by them: gold/trading_data.db"
            # Example: "        both modified:   gold/trading_data.db"
            parts = line.split(':')
            if len(parts) >= 2 and ("deleted by them" in line or "both modified" in line or "modified" in line):
                fname = parts[-1].strip()
                # We prioritize DB files and specific config scripts
                if fname.endswith('.db') or fname.endswith('.bat') or fname.endswith('.sh'):
                    files_to_add.append(fname)
        
        if files_to_add:
            print(f"📦 Preserving local files: {files_to_add}")
            for f in files_to_add:
                if os.path.exists(f):
                    run_git_cmd(["git", "add", f])
            
            # Commit
            print("💾 Committing resolution...")
            run_git_cmd(["git", "commit", "-m", "Auto-resolve: Keep local files"])
            print("✅ Conflicts resolved.")

    elif "deleted by them" in status:
         # Specific catch for when "Unmerged paths" header might be missing or different
         print("⚠️  'Deleted by them' conflict detected (Modify/Delete). Resolving...")
         run_git_cmd(["git", "add", "."])
         run_git_cmd(["git", "commit", "-m", "Auto-resolve: Keep local (Modify/Delete)"])
         print("✅ Resolved.")

    elif "rebase in progress" in status:
        print("⚠️  Git Rebase in progress detected.")
        run_git_cmd(["git", "rebase", "--abort"])
        
    elif "Merge" in status and "You have unmerged paths" in status:
        print("⚠️  Merge state detected.")
        run_git_cmd(["git", "commit", "--no-edit"]) 

    else:
        print("✅ No active conflicts detected.")

if __name__ == "__main__":
    # Ensure we are in root
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(root_dir)
    
    fix_git_state()
    resolve_conflicts()
