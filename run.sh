#!/bin/bash

# RedisM 启动脚本

echo "启动 RedisM..."

# 检查依赖
if ! python3 -c "import redis, paramiko, tkinter" 2>/dev/null; then
    echo "安装依赖..."
    pip3 install -r requirements.txt
fi

# 启动应用
python3 redis_manager.py