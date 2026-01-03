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
    # 使用临时变量捕获 git pull 的输出和退出码，区分网络错误和冲突
    if ! git pull --rebase origin master; then
        EXIT_CODE=$?
        echo "⚠️  Git pull failed with exit code $EXIT_CODE."
        
        # 尝试检测是否为网络相关错误 (LibreSSL, connection refused, time out, etc.)
        # 注意: 这里的检测比较粗略，主要为了防止网络波动中断自动流程
        # 如果是 conflict (通常 exit code 1)，则需要人工干预，但如果是网络问题，我们希望重试
        
        # 简单策略：在 Loop 模式下，如果是网络错误，我们不应该 return 1 (因为这会中断某些逻辑)，
        # 而是应该仅仅打印警告并继续尝试提交本地代码（也许下次 push 能成功或再次失败）
        # 但如果是冲突，必须解决。
        
        # 让我们检查是否是冲突状态
        if git status | grep -q "Unmerged paths"; then
             echo "❌  MERGE CONFLICT detected! Please resolve manually."
             # 冲突时必须停止，否则会提交冲突标记文件
             return 1
        else
             echo "⚠️  Likely a network error or no upstream changes. Skipping pull and proceeding to push..."
             # 网络错误不应阻止尝试推送本地变更 (虽然通常 pull 失败 push 也会失败，但值得一试)
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
