#!/bin/bash

# 获取当前脚本所在目录的上一级目录
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 切换到项目根目录
cd "$PROJECT_ROOT" || { echo "❌ Failed to change directory to project root: $PROJECT_ROOT"; exit 1; }

echo "========================================================"
echo "🚀 Git Auto-Sync Tool"
echo "📂 Location: $PROJECT_ROOT"
echo "========================================================"

# 检查是否为 Git 仓库
if [ ! -d ".git" ]; then
    echo "❌ Error: This is not a git repository."
    exit 1
fi

# 帮助函数：单次同步逻辑
perform_sync() {
    local COMMIT_MSG="$1"
    
    # 1. Checkpoint Database (Mac/Linux only, for Windows called by .bat)
    if [ -f "scripts/checkpoint_dbs.py" ]; then
        echo "🛠  Running Database Checkpoint..."
        python3 scripts/checkpoint_dbs.py
    fi

    # 2. Pull Remote Changes
    echo "⬇️  Checking for remote updates..."
    if ! git pull --rebase origin master; then
        echo "⚠️  Conflict detected during pull. Please resolve manually."
        return 1
    fi

    # 3. Check & Commit Local Changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "📝 Detected changes..."
        git add .
        
        # 如果没有提供 commit message，且处于交互模式，则询问
        if [ -z "$COMMIT_MSG" ]; then
            echo "💡 Enter commit message below."
            read -p "💬 Message (Press Enter for default 'Auto update'): " USER_MSG
            COMMIT_MSG=${USER_MSG:-"Auto update"}
        fi
        
        # 如果还是空的（自动模式下），生成默认 message
        if [ -z "$COMMIT_MSG" ]; then
            COMMIT_MSG="auto: sync updates $(date '+%Y-%m-%d %H:%M:%S')"
        fi

        echo "📦 Committing: $COMMIT_MSG"
        git commit -m "$COMMIT_MSG"
    else
        echo "✨ No local changes to commit."
    fi

    # 4. Push to Remote
    echo "⬆️  Pushing to GitHub..."
    if git push origin master; then
        echo "✅ Sync successful."
        echo "🔗 View at: $(git remote get-url origin)"
        return 0
    else
        echo "❌ Push failed."
        return 1
    fi
}

# --- 主逻辑 ---

# 模式 1: 自动循环模式 (Auto Loop Mode)
if [ "$1" == "--loop" ] || [ "$1" == "auto" ]; then
    echo "🔄 Starting Loop Mode (Interval: 60s)..."
    while true; do
        echo ""
        echo "==================================================="
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Sync Cycle..."
        
        # 在循环模式下，自动生成 commit message
        perform_sync "auto: sync updates $(date '+%Y-%m-%d %H:%M:%S')"
        
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cycle Complete."
        echo "==================================================="
        echo "⏳ Waiting 60 seconds..."
        sleep 60
    done

# 模式 2: 单次手动/自动模式 (Single Run)
else
    # 如果提供了参数作为 commit message
    perform_sync "$1"
fi
