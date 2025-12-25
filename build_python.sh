#!/bin/bash

# RedisM Mac应用打包脚本

PYTHON_SCRIPT="redis_manager.py"
ICON_SCRIPT="create_icon.py"
VENV_DIR="venv"
PYTHON_BIN="/usr/local/bin/python3.14"

echo "开始构建RedisM..."

# 检查Python环境
if ! command -v "$PYTHON_BIN" &> /dev/null; then
    echo "错误: 未找到支持tkinter的Python环境"
    echo "请运行: brew install python-tk@3.14"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "$VENV_DIR" ]; then
    echo "创建虚拟环境..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 从配置文件中读取应用名称和版本号
APP_NAME=$(python3 -c "from config import __app_name__; print(__app_name__)")
VERSION=$(python3 -c "from config import __version__; print(__version__)")

echo "构建 $APP_NAME v$VERSION..."

# 安装依赖
echo "安装Python依赖..."
pip install redis paramiko pyinstaller

# 创建图标
echo "创建应用图标..."
python "$ICON_SCRIPT"

# 设置图标文件
ICON_FILE=""
if [ -f "icon_512.png" ]; then
    ICON_FILE="--icon=icon_512.png"
fi

# 清理之前的构建
echo "清理之前的构建文件..."
rm -rf build dist *.spec

# 创建应用程序包
echo "创建Mac应用程序包..."

pyinstaller --onedir --windowed \
    --name="$APP_NAME" \
    $ICON_FILE \
    --osx-bundle-identifier="com.redismanager.app" \
    --target-arch=x86_64 \
    --hidden-import=config \
    "$PYTHON_SCRIPT"

# 检查构建结果
if [ -d "dist/$APP_NAME.app" ]; then
    echo "构建成功!"
    echo "应用程序位置: dist/$APP_NAME.app"
    echo "应用大小: $(du -sh dist/$APP_NAME.app | cut -f1)"
    echo ""
    echo "安装说明:"
    echo "1. 拖拽 dist/$APP_NAME.app 到 Applications 文件夹"
    echo "2. 首次运行可能需要在系统偏好设置中允许运行"
    echo "3. 如果遇到权限问题，请运行: xattr -cr dist/$APP_NAME.app"
    
    # 创建DMG安装包（可选）
    if command -v hdiutil &> /dev/null; then
        echo ""
        echo "创建DMG安装包..."
        rm -f "$APP_NAME.dmg"
        hdiutil create -volname "$APP_NAME" -srcfolder "dist/$APP_NAME.app" -ov -format UDZO "$APP_NAME.dmg"
        if [ -f "$APP_NAME.dmg" ]; then
            echo "DMG安装包已创建: $APP_NAME.dmg"
        fi
    fi
else
    echo "构建失败，请检查错误信息"
    exit 1
fi

echo ""
echo "构建完成！"