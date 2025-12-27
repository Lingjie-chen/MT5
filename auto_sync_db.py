import time
import subprocess
import os
import logging
from datetime import datetime

# 配置
FILES_TO_SYNC = [
    "trading_data.db",
    "trading_data.db-shm",
    "trading_data.db-wal"
]
# 同步间隔（秒）。建议不要太频繁，以免给 GitHub 服务器造成压力或触发限制。
# 300秒 = 5分钟
SYNC_INTERVAL = 300 
REPO_PATH = os.path.dirname(os.path.abspath(__file__))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("auto_sync.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def run_git_command(args):
    """运行 Git 命令并处理异常"""
    try:
        # 在 Windows 上，git 命令可能需要完整的环境，subprocess.run 通常能找到 path 中的 git
        result = subprocess.run(
            ["git"] + args,
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            encoding='utf-8', # 强制使用 utf-8 处理输出
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # 忽略 "nothing to commit" 的错误，但这通常在 status 检查中被过滤
        if "nothing to commit" not in e.stderr and "clean" not in e.stderr:
            logging.error(f"Git command failed: git {' '.join(args)}\nError: {e.stderr}")
        return None
    except Exception as e:
        logging.error(f"Execution error: {e}")
        return None

def sync_files():
    logging.info("Checking for changes...")
    
    # 1. Add 指定文件
    # 使用 -f 强制添加，即使在 .gitignore 中（虽然我们已经移除了）
    add_args = ["add"] + FILES_TO_SYNC
    if run_git_command(add_args) is None:
        return

    # 2. 检查是否有变更需要提交
    status = run_git_command(["status", "--porcelain"])
    if not status:
        logging.info("No changes detected in database files.")
        return

    # 3. Commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"Auto update trading data: {timestamp}"
    logging.info(f"Committing changes: {message}")
    
    commit_result = run_git_command(["commit", "-m", message])
    if commit_result is None:
        return

    # 4. Push to GitHub
    logging.info("Pushing to remote (origin master)...")
    push_result_origin = run_git_command(["push", "origin", "master"])
    
    if push_result_origin is not None:
        logging.info("✅ Successfully pushed to GitHub.")
    else:
        logging.warning("⚠️ GitHub Push failed.")

    # 5. Push to MQL5
    logging.info("Pushing to remote (mql5 master)...")
    push_result_mql5 = run_git_command(["push", "mql5", "master"])
    
    if push_result_mql5 is not None:
        logging.info("✅ Successfully pushed to MQL5.")
    else:
        logging.warning("⚠️ MQL5 Push failed.")

def main():
    logging.info("="*50)
    logging.info(f"Starting Auto-Sync Service")
    logging.info(f"Target Files: {FILES_TO_SYNC}")
    logging.info(f"Interval: {SYNC_INTERVAL} seconds")
    logging.info(f"Repository: {REPO_PATH}")
    logging.info("="*50)
    
    while True:
        try:
            sync_files()
        except KeyboardInterrupt:
            logging.info("Auto-sync service stopped by user.")
            break
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
        
        # 等待下一次同步
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
