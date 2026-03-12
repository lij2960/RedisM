#!/bin/bash

# RedisM 一键修复和安装脚本

echo "🔧 RedisM 安装问题修复工具"
echo "================================"

# 检查当前问题
echo "🔍 检查当前状态..."

# 检查是否有应用包
if [ -d "dist/RedisM.app" ]; then
    echo "✅ 找到应用包: dist/RedisM.app"
    APP_PATH="dist/RedisM.app"
elif [ -d "build/RedisM/RedisM.app" ]; then
    echo "✅ 找到应用包: build/RedisM/RedisM.app"
    APP_PATH="build/RedisM/RedisM.app"
else
    echo "❌ 未找到应用包，请先构建应用"
    echo "运行: ./build_python.sh"
    exit 1
fi

# 检查是否有问题的 DMG
if [ -f "RedisM.dmg" ]; then
    echo "⚠️  发现可能有问题的 DMG 文件"
    read -p "是否删除现有的 RedisM.dmg？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "RedisM.dmg"
        echo "🗑️  已删除 RedisM.dmg"
    fi
fi

echo ""
echo "请选择解决方案："
echo "1. 快速安装到 Applications 文件夹（推荐）"
echo "2. 创建新的 DMG 安装包"
echo "3. 手动修复现有安装"
echo "4. 显示详细的修复说明"

read -p "请输入选择 (1-4): " -n 1 -r
echo

case $REPLY in
    1)
        echo "🚀 执行快速安装..."
        ./quick_install.sh
        ;;
    2)
        echo "📦 创建新的 DMG 安装包..."
        ./create_dmg.sh
        ;;
    3)
        echo "🔧 手动修复步骤："
        echo ""
        echo "1. 清理应用扩展属性："
        echo "   xattr -cr \"$APP_PATH\""
        echo ""
        echo "2. 复制到 Applications："
        echo "   cp -R \"$APP_PATH\" /Applications/"
        echo ""
        echo "3. 设置权限："
        echo "   chmod +x /Applications/RedisM.app/Contents/MacOS/RedisM"
        echo ""
        echo "4. 如果遇到安全提示："
        echo "   xattr -cr /Applications/RedisM.app"
        
        read -p "是否现在执行这些步骤？(y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "执行修复..."
            xattr -cr "$APP_PATH"
            cp -R "$APP_PATH" /Applications/
            chmod +x /Applications/RedisM.app/Contents/MacOS/RedisM
            echo "✅ 修复完成"
        fi
        ;;
    4)
        echo "📖 显示详细修复说明..."
        cat fix_installer_error.md
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 处理完成！"
echo ""
echo "如果仍有问题，请查看 fix_installer_error.md 文件获取详细说明。"