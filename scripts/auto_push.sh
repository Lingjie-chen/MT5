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
    # 尝试标准拉取
    if ! git pull --no-edit origin master; then
        echo "⚠️  Git pull failed or conflict detected."
        
        # 尝试自动解决冲突
        # 策略: -s recursive -X ours
        # 含义: 尝试合并远程代码，如果遇到具体行的冲突，保留本地的版本 (Ours)，丢弃远程的冲突部分。
        # 这能确保本地机器人的配置/代码不会被破坏，同时尽可能合并远程的新功能。
        echo "🔧 Attempting to auto-resolve conflict (Strategy: Keep Local/Ours)..."
        
        if git pull --no-edit -s recursive -X ours origin master; then
             echo "✅ Conflict resolved automatically (Merge commit created)."
        else
             echo "❌ Auto-resolve failed. Aborting."
             # 尝试清理合并状态
             git merge --abort 2>/dev/null
             return 1
        fi
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

# 解析参数
MODE="loop"
COMMIT_MSG=""

if [ "$1" == "--once" ]; then
    MODE="once"
    COMMIT_MSG="$2"
elif [ -n "$1" ] && [ "$1" != "auto" ] && [ "$1" != "--loop" ]; then
    # 如果提供了参数且不是 auto/--loop，则视为 commit message 并执行单次同步
    MODE="once"
    COMMIT_MSG="$1"
fi

# 模式 1: 自动循环模式 (Auto Loop Mode)
if [ "$MODE" == "loop" ]; then
    echo "🔄 Starting Loop Mode (Interval: 60s)..."
    echo "💡 Tip: Use './auto_push.sh \"message\"' for single run."
    
    while true; do
        echo ""
        echo "==================================================="
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Sync Cycle..."
        
        # 在循环模式下，自动生成 commit message
        perform_sync "auto: sync updates $(date '+%Y-%m-%d %H:%M:%S')"
        
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cycle Complete."
        echo "==================================================="
        echo "⏳ Waiting 60 seconds... (Press Ctrl+C to stop)"
        sleep 60
    done

# 模式 2: 单次手动模式 (Single Run)
else
    echo "▶️  Starting Single Run..."
    perform_sync "$COMMIT_MSG"
fi
