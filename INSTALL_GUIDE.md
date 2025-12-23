# Redis Manager - 安装和使用指南

## 🎉 构建完成！

你的Redis Manager应用程序已经成功构建为Mac Intel芯片的原生应用程序。

## 📦 构建产物

- **应用程序**: `dist/RedisManager.app` (16MB)
- **安装包**: `RedisManager.dmg`
- **源代码**: `redis_manager.py`

## 🚀 安装方法

### 方法1：使用DMG安装包（推荐）
1. 双击 `RedisManager.dmg` 文件
2. 将 RedisManager.app 拖拽到 Applications 文件夹
3. 从启动台或应用程序文件夹启动

### 方法2：直接安装
```bash
cp -r dist/RedisManager.app /Applications/
```

## 🔐 首次运行

由于macOS安全机制，首次运行可能需要：

1. **如果提示"无法打开"**：
   - 右键点击应用程序 → 选择"打开"
   - 或在"系统偏好设置" → "安全性与隐私" → "通用"中点击"仍要打开"

2. **如果仍有问题**，运行以下命令：
```bash
xattr -cr /Applications/RedisManager.app
```

## ✨ 主要功能

### 连接管理
- ✅ 多Redis连接配置
- ✅ 用户名/密码认证
- ✅ SSH隧道支持
- ✅ SSH密钥认证
- ✅ 连接配置持久化

### 数据浏览
- ✅ 16个数据库切换
- ✅ 键搜索和过滤
- ✅ 分层键显示
- ✅ 支持所有Redis数据类型

### 数据操作
- ✅ 查看键详情
- ✅ 编辑键值
- ✅ 删除键
- ✅ TTL管理

### 命令行
- ✅ 完整Redis命令支持
- ✅ 结果格式化显示
- ✅ 命令历史

## 🔧 开发信息

### 技术栈
- **GUI框架**: tkinter
- **Redis客户端**: redis-py 7.1.0
- **SSH支持**: paramiko 4.0.0
- **打包工具**: PyInstaller 6.17.0

### 系统要求
- macOS 10.13 或更高版本
- Intel x86_64 架构

### 源码运行
如需修改或调试：
```bash
# 激活虚拟环境
source venv/bin/activate

# 直接运行源码
python redis_manager.py
```

### 重新构建
```bash
bash build_python.sh
```

## 📝 使用技巧

### 连接Redis
1. 点击"Add"添加新连接
2. 填写连接信息（主机、端口、密码等）
3. 如需SSH隧道，勾选相应选项
4. 保存并连接

### 浏览数据
1. 选择数据库（DB 0-15）
2. 使用搜索框过滤键（支持通配符*）
3. 调整分隔符来改变键的分组显示
4. 点击键查看详情

### 执行命令
1. 切换到"Command Line"标签
2. 输入Redis命令（如：GET key1）
3. 按回车或点击Execute执行

## 🐛 故障排除

### 连接问题
- 检查Redis服务状态
- 验证网络连接
- 确认防火墙设置
- 检查Redis配置中的bind设置

### SSH问题
- 验证SSH服务器连接
- 检查SSH用户权限
- 确认密钥文件路径和权限

### 应用启动问题
- 查看控制台错误日志
- 尝试从终端启动查看错误信息
- 重新下载或重新构建应用

## 📞 支持

如遇到问题，请检查：
1. 系统日志（控制台应用程序）
2. Redis服务器日志
3. 网络连接状态

---

**Redis Manager** - 让Redis管理变得简单！ 🚀