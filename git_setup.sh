#!/bin/bash

# 设置错误时退出
set -e

# 显示执行的命令
set -x

# 进入项目根目录
cd "E:/sleep_vue"

# 初始化 Git 仓库（如果还没有）
if [ ! -d ".git" ]; then
    git init
fi

# 创建 .gitignore 文件
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Vue
.DS_Store
.env.local
.env.*.local
dist/
dist-ssr/
*.local

# IDE
.idea/
.vscode/
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Editor directories and files
.idea
.vscode
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
EOL

# 检查后端文件是否存在
echo "检查后端文件..."
if [ ! -d "backend" ]; then
    echo "错误：找不到 backend 目录！"
    exit 1
fi

# 检查关键后端文件
required_files=(
    "backend/posture_server.py"
    "backend/posture_camera.py"
    "backend/sleep_report_server.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "错误：找不到必需的后端文件 $file！"
        exit 1
    fi
done

# 显示要添加的文件
echo "准备添加以下文件到 Git："
git status

# 添加所有文件到 Git
git add .

# 创建初始提交
git commit -m "Initial commit: Sleep detection project with Vue.js frontend and Python backend"

# 添加远程仓库
git remote add origin git@github.com:xjzhong-027/sleepDetect.git || git remote set-url origin git@github.com:xjzhong-027/sleepDetect.git

# 拉取远程仓库内容
echo "拉取远程仓库内容..."
git pull origin master --allow-unrelated-histories

# 推送到主分支
echo "推送到远程仓库..."
git push -u origin master

echo "项目已成功推送到 GitHub！" 