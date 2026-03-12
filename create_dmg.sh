#!/bin/bash

# 创建 RedisM DMG 安装包的改进脚本

APP_NAME="RedisM"
APP_PATH="dist/RedisM.app"
DMG_NAME="RedisM_Installer.dmg"
TEMP_DMG="temp_${DMG_NAME}"
VOLUME_NAME="RedisM Installer"

echo "创建 RedisM DMG 安装包..."

# 检查应用是否存在
if [ ! -d "$APP_PATH" ]; then
    echo "错误: 找不到应用程序 $APP_PATH"
    echo "请先运行构建脚本: ./build_python.sh"
    exit 1
fi

# 清理之前的文件
rm -f "$DMG_NAME" "$TEMP_DMG"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "使用临时目录: $TEMP_DIR"

# 复制应用到临时目录
echo "复制应用程序..."
cp -R "$APP_PATH" "$TEMP_DIR/"

# 清除应用的扩展属性
echo "清理应用扩展属性..."
xattr -cr "$TEMP_DIR/RedisM.app"

# 创建 Applications 文件夹的符号链接
echo "创建 Applications 链接..."
ln -s /Applications "$TEMP_DIR/Applications"

# 创建安装说明文件
cat > "$TEMP_DIR/安装说明.txt" << EOF
RedisM 安装说明
===============

1. 将 RedisM.app 拖拽到 Applications 文件夹
2. 首次运行时，如果系统提示"无法验证开发者"：
   - 打开"系统偏好设置" > "安全性与隐私"
   - 点击"仍要打开"按钮
3. 或者在终端中运行以下命令：
   xattr -cr /Applications/RedisM.app

如有问题，请访问项目主页获取帮助。

版本: $(python3 -c "from src.config import __version__; print(__version__)" 2>/dev/null || echo "1.1.3")
EOF

# 计算需要的磁盘空间
APP_SIZE=$(du -sm "$TEMP_DIR" | cut -f1)
DMG_SIZE=$((APP_SIZE + 50))  # 额外50MB空间

echo "应用大小: ${APP_SIZE}MB，DMG大小: ${DMG_SIZE}MB"

# 创建临时 DMG
echo "创建临时 DMG..."
hdiutil create -srcfolder "$TEMP_DIR" -volname "$VOLUME_NAME" -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" -format UDRW -size ${DMG_SIZE}m "$TEMP_DMG"

# 挂载临时 DMG
echo "挂载 DMG 进行配置..."
DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "$TEMP_DMG" | \
    egrep '^/dev/' | sed 1q | awk '{print $1}')

# 设置 DMG 窗口属性
echo "配置 DMG 窗口..."
sleep 2

# 使用 AppleScript 设置窗口外观
osascript << EOF
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 900, 400}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 72
        set background picture of viewOptions to file ".background:background.png"
        make new alias file at container window to POSIX file "/Applications" with properties {name:"Applications"}
        set position of item "RedisM.app" of container window to {150, 200}
        set position of item "Applications" of container window to {350, 200}
        set position of item "安装说明.txt" of container window to {250, 300}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF

# 卸载 DMG
echo "卸载临时 DMG..."
hdiutil detach "$DEVICE"

# 转换为只读 DMG
echo "创建最终 DMG..."
hdiutil convert "$TEMP_DMG" -format UDZO -imagekey zlib-level=9 -o "$DMG_NAME"

# 清理临时文件
rm -f "$TEMP_DMG"
rm -rf "$TEMP_DIR"

# 验证 DMG
echo "验证 DMG..."
if hdiutil verify "$DMG_NAME"; then
    echo "✅ DMG 创建成功: $DMG_NAME"
    echo "文件大小: $(du -sh "$DMG_NAME" | cut -f1)"
    
    # 显示安装说明
    echo ""
    echo "安装说明:"
    echo "1. 双击 $DMG_NAME 打开安装程序"
    echo "2. 将 RedisM.app 拖拽到 Applications 文件夹"
    echo "3. 如果遇到安全提示，请在系统偏好设置中允许运行"
    
else
    echo "❌ DMG 验证失败"
    exit 1
fi