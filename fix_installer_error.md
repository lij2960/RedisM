# 修复 macOS 安装程序错误 (com.apple.installer.pagecontroller错误-1)

## 问题描述
在尝试安装 RedisM.dmg 时遇到 `com.apple.installer.pagecontroller错误-1` 错误。

## 解决方案

### 方案 1: 直接安装应用（推荐）

不使用 DMG 文件，直接从 build 目录安装：

```bash
# 1. 清除应用的扩展属性（移除隔离标记）
xattr -cr build/RedisM/RedisM.app

# 2. 直接复制到 Applications 文件夹
cp -R build/RedisM/RedisM.app /Applications/

# 3. 设置正确的权限
chmod +x /Applications/RedisM.app/Contents/MacOS/RedisM
```

### 方案 2: 重新创建 DMG 文件

如果需要 DMG 安装包，重新创建一个：

```bash
# 1. 删除现有的 DMG 文件
rm -f RedisM.dmg

# 2. 清理应用的扩展属性
xattr -cr build/RedisM/RedisM.app

# 3. 创建新的 DMG 文件
hdiutil create -volname "RedisM" -srcfolder build/RedisM/RedisM.app -ov -format UDZO RedisM_fixed.dmg

# 4. 验证 DMG 文件
hdiutil verify RedisM_fixed.dmg
```

### 方案 3: 使用快速安装脚本（最简单）

运行快速安装脚本，绕过 DMG 问题：

```bash
./quick_install.sh
```

这个脚本会：
- 自动清理应用的扩展属性
- 复制应用到 Applications 文件夹
- 设置正确的权限
- 提供启动选项

### 方案 4: 使用改进的 DMG 创建脚本

如果需要重新创建 DMG 安装包：

```bash
./create_dmg.sh
```

## 常见问题解决

### 问题 1: "无法验证开发者"
```bash
xattr -cr /Applications/RedisM.app
```

### 问题 2: 权限被拒绝
```bash
sudo chown -R $(whoami):staff /Applications/RedisM.app
chmod +x /Applications/RedisM.app/Contents/MacOS/RedisM
```

### 问题 3: 应用无法启动
```bash
# 检查应用完整性
codesign --verify --verbose /Applications/RedisM.app

# 重新设置权限
xattr -cr /Applications/RedisM.app
chmod +x /Applications/RedisM.app/Contents/MacOS/RedisM
```

## 预防措施

为了避免将来出现类似问题，建议：

1. **使用代码签名**：
```bash
# 在 build_python.sh 中添加
codesign --force --deep --sign - build/RedisM/RedisM.app
```

2. **创建公证的应用**：
```bash
# 需要 Apple Developer 账户
xcrun altool --notarize-app --primary-bundle-id "com.redismanager.app" \
    --username "your-apple-id" --password "app-specific-password" \
    --file RedisM.dmg
```

3. **使用更好的打包工具**：
考虑使用 `create-dmg` 或 `appdmg` 等专业工具。

## 总结

`com.apple.installer.pagecontroller错误-1` 通常是由于：
- 应用的隔离属性 (quarantine attributes)
- 不正确的文件权限
- 损坏的 DMG 文件结构

使用上述任一方案都可以解决问题，推荐使用**方案 3**（快速安装脚本）作为最简单的解决方案。