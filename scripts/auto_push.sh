#!/bin/bash

# 获取当前脚本所在目录的上一级目录（因为脚本在 scripts/ 下）
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# 切换到项目根目录
cd "$PROJECT_ROOT" || { echo "❌ Failed to change directory to project root: $PROJECT_ROOT"; exit 1; }

echo "========================================================"
echo "🚀 Starting auto-push process for project: $(basename "$PROJECT_ROOT")"
echo "📂 Location: $PROJECT_ROOT"
echo "========================================================"

# 检查是否为 Git 仓库
if [ ! -d ".git" ]; then
    echo "❌ Error: This is not a git repository."
    exit 1
fi

# 检查 Git 状态
if [ -z "$(git status --porcelain)" ]; then 
  echo "✨ No changes to commit. Working tree is clean."
  exit 0
fi

# 显示变更文件
echo "📝 Detected changes in the following files:"
git status --short
echo "--------------------------------------------------------"

# 询问提交信息
echo "💡 Enter commit message below."
read -p "💬 Message (Press Enter for default 'Auto update'): " USER_MSG
COMMIT_MSG=${USER_MSG:-"Auto update"}

# 执行 Git 命令序列
echo "--------------------------------------------------------"
echo "⏳ Step 1: Adding all files..."
git add .

echo "📦 Step 2: Committing..."
git commit -m "$COMMIT_MSG"

echo "⬇️  Step 3: Pulling latest changes from remote (rebase)..."
# 使用 rebase 避免产生不必要的 merge commit，保持提交历史整洁
if ! git pull --rebase origin master; then
    echo "⚠️  Conflict detected during pull. Please resolve conflicts manually."
    exit 1
fi

echo "⬆️  Step 4: Pushing to GitHub..."
if git push origin master; then
    echo "--------------------------------------------------------"
    echo "✅ Success! Code has been pushed to GitHub."
    echo "🔗 View at: $(git remote get-url origin)"
else
    echo "❌ Failed to push code. Please check your network or permissions."
    exit 1
fi
