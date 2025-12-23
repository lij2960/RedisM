#!/bin/bash

# Redis Manager 启动脚本

echo "启动 Redis Manager..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3环境"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import redis, paramiko, tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装依赖..."
    pip3 install -r requirements.txt
fi

# 启动应用
echo "启动应用程序..."
python3 redis_manager.py