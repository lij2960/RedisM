#!/bin/bash

# RedisM 快速安装脚本 - 绕过 DMG 安装问题

APP_NAME="RedisM"
APP_PATH="dist/RedisM.app"

echo "🚀 RedisM 快速安装脚本"
echo "========================"

# 检查应用是否存在
if [ ! -d "$APP_PATH" ]; then
    echo "❌ 错误: 找不到应用程序 $APP_PATH"
    echo "请先运行构建脚本: ./build_python.sh"
    echo "或检查 dist/ 目录中是否有 RedisM.app"
    exit 1
fi

echo "📱 找到应用程序: $APP_PATH"

# 检查 Applications 目录权限
if [ ! -w "/Applications" ]; then
    echo "⚠️  需要管理员权限来安装到 Applications 文件夹"
    echo "请输入密码："
    SUDO_PREFIX="sudo"
else
    SUDO_PREFIX=""
fi

# 移除现有安装（如果存在）
if [ -d "/Applications/RedisM.app" ]; then
    echo "🗑️  移除现有安装..."
    $SUDO_PREFIX rm -rf "/Applications/RedisM.app"
fi

# 清除应用的扩展属性（移除隔离标记）
echo "🔧 清理应用扩展属性..."
xattr -cr "$APP_PATH"

# 复制应用到 Applications 文件夹
echo "📦 安装应用到 Applications 文件夹..."
$SUDO_PREFIX cp -R "$APP_PATH" "/Applications/"

# 设置正确的权限
echo "🔐 设置应用权限..."
$SUDO_PREFIX chmod +x "/Applications/RedisM.app/Contents/MacOS/RedisM"
$SUDO_PREFIX chown -R $(whoami):staff "/Applications/RedisM.app" 2>/dev/null || true

# 验证安装
if [ -d "/Applications/RedisM.app" ]; then
    echo "✅ 安装成功！"
    echo ""
    echo "📍 应用位置: /Applications/RedisM.app"
    echo "📊 应用大小: $(du -sh "/Applications/RedisM.app" | cut -f1)"
    echo ""
    echo "🎉 现在可以从以下位置启动 RedisM："
    echo "   • Launchpad"
    echo "   • Applications 文件夹"
    echo "   • Spotlight 搜索"
    echo ""
    echo "💡 首次运行提示："
    echo "   如果系统提示'无法验证开发者'，请："
    echo "   1. 打开'系统偏好设置' > '安全性与隐私'"
    echo "   2. 点击'仍要打开'按钮"
    echo "   或者运行: xattr -cr /Applications/RedisM.app"
    
    # 尝试打开应用
    read -p "🚀 是否现在启动 RedisM？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "启动 RedisM..."
        open "/Applications/RedisM.app"
    fi
    
else
    echo "❌ 安装失败，请检查权限或手动复制文件"
    echo ""
    echo "手动安装步骤："
    echo "1. 在 Finder 中打开项目文件夹"
    echo "2. 导航到 dist/"
    echo "3. 将 RedisM.app 拖拽到 Applications 文件夹"
    echo "4. 运行: xattr -cr /Applications/RedisM.app"
    exit 1
fi