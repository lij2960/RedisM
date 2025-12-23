# RedisM

一个现代化的Redis管理工具，使用Python和tkinter开发，支持SSH隧道连接，可编译为macOS原生应用程序。

![RedisM Logo](https://img.shields.io/badge/RedisM-v1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 📸 应用截图

### 主界面
- 左侧连接管理面板，支持多连接配置
- 右侧键值管理和命令行界面
- 树形结构显示Redis键，支持分组折叠

### 键值编辑
- Hash类型专用编辑器，支持JSON格式化
- 所有Redis数据类型的可视化编辑
- 实时查询和命令执行

## 🎯 核心亮点

- **🚀 高性能**: 流式加载大量键，最多支持100,000个键的高效管理
- **🔐 安全连接**: 完整的SSH隧道支持，可安全访问内网Redis服务器
- **🎨 用户友好**: 现代化GUI界面，直观的操作流程
- **⚡ 实时响应**: 非阻塞UI设计，大数据量下依然流畅
- **🔧 专业工具**: 内置Redis命令行，支持所有Redis命令

## ✨ 功能特性

### 🔗 连接管理
- 支持多个Redis连接配置
- 支持用户名/密码认证
- 支持SSH隧道连接（密码和私钥认证）
- 支持多种私钥格式（PEM、OpenSSH、Ed25519等）
- 私钥文件浏览器选择
- 连接配置自动保存和加载
- 自动连接保活机制

### 🗄️ 数据库操作
- 支持16个Redis数据库切换
- 键搜索和模式匹配（支持通配符*）
- 多级分隔符分组显示键（树形结构，默认收起）
- 支持所有Redis数据类型（String、List、Set、Hash、ZSet）
- 智能键数量管理（最多100,000个键，自动批量加载）
- 实时显示当前数据库键数统计

### 🔧 键值管理
- 查看键详情（类型、TTL、值大小）
- 可视化编辑各种数据类型
- Hash类型专用编辑器（支持字段和值同时编辑）
- JSON格式化和压缩功能
- Redis命令查询支持（HGET、LRANGE、ZRANGE等）
- 批量操作和更新
- 键的添加、删除、刷新

### 💻 命令行界面
- 内置Redis命令行终端
- 支持所有Redis命令
- 命令历史记录
- 结果格式化显示
- 实时命令执行

### 🎨 用户界面
- 现代化的GUI界面
- 响应式布局设计
- 大窗口支持（1600x1000）
- 滚动支持的对话框
- 直观的操作流程

## 🖥️ 系统要求

- **操作系统**: macOS 10.14+ (Mojave或更高版本)
- **Python**: 3.8+ (推荐3.14)
- **架构**: Intel x86_64 或 Apple Silicon (M1/M2)
- **内存**: 最少512MB可用内存
- **磁盘**: 100MB可用空间

## 📦 安装依赖

```bash
# 安装Python依赖
pip3 install -r requirements.txt

# 或者手动安装
pip3 install redis paramiko pyinstaller
```

## 🚀 快速开始

### 方式一：直接下载使用（推荐）

1. **下载应用**
   - 从 [Releases](https://github.com/your-repo/RedisM/releases) 页面下载最新版本
   - 或者下载 DMG 安装包

2. **安装应用**
   ```bash
   # 方法1：拖拽安装
   # 将 RedisM.app 拖拽到 Applications 文件夹
   
   # 方法2：命令行安装
   cp -r RedisM.app /Applications/
   ```

3. **首次运行**
   - 双击打开 RedisM
   - 如遇到安全提示，参考 [首次运行配置](#-首次运行配置)

### 方式二：开发者模式
```bash
# 克隆项目
git clone <repository-url>
cd RedisM

# 安装依赖
pip3 install -r requirements.txt

# 运行应用
python3 redis_manager.py
```

### 编译为Mac应用程序

1. **准备环境**
```bash
# 确保已安装所有依赖
pip3 install -r requirements.txt

# 给构建脚本执行权限
chmod +x build_python.sh
```

2. **执行构建**
```bash
# 运行构建脚本
./build_python.sh
```

3. **安装应用**
```bash
# 方法1：拖拽安装
cp -r dist/RedisM.app /Applications/

# 方法2：使用DMG安装包
open RedisM.dmg
```

## 🔧 首次运行配置

由于macOS的安全机制，首次运行可能需要额外步骤：

### 方法1：系统偏好设置
1. 打开"系统偏好设置" → "安全性与隐私" → "通用"
2. 点击"仍要打开"按钮

### 方法2：命令行移除隔离
```bash
xattr -cr /Applications/RedisM.app
```

## 📖 使用指南

### 添加Redis连接
1. 点击左侧"Add"按钮
2. 填写连接信息：
   - **连接名称**: 自定义连接标识
   - **Redis主机**: 服务器地址（支持内网地址）
   - **端口**: 默认6379
   - **用户名**: 可选，Redis 6.0+支持
   - **密码**: Redis认证密码
   - **最大键数**: 限制显示的键数量（0=无限制）

### SSH隧道配置
1. 勾选"Use SSH Tunnel"
2. 填写SSH服务器信息：
   - **SSH主机**: SSH服务器地址
   - **SSH端口**: 默认22
   - **SSH用户名**: SSH登录用户
3. 选择认证方式：
   - **密码认证**: 输入SSH密码
   - **私钥认证**: 选择私钥文件或粘贴私钥内容
4. 如使用加密私钥，输入密钥密码

### 数据浏览和管理
1. **连接Redis**: 选择连接后点击"Connect"或双击连接名
2. **选择数据库**: 使用下拉菜单切换DB 0-15
3. **搜索键**: 输入模式（支持*通配符）
4. **浏览数据**: 点击树形结构中的键查看详情
5. **编辑数据**: 双击Hash字段进入编辑模式

### 命令行操作
1. 切换到"Command Line"标签
2. 输入Redis命令（如：`GET mykey`、`HGETALL myhash`）
3. 按回车或点击"Execute"执行
4. 查看格式化的执行结果

## 📊 性能特性

### 智能键管理
- **流式加载**: 采用分批流式加载技术，支持大量键的高效管理
- **智能限制**: 自动限制最多100,000个键，防止内存溢出
- **实时统计**: 显示当前数据库的键数统计信息
- **非阻塞UI**: 后台加载数据，界面始终保持响应

### 连接优化
- **连接池**: 自动管理Redis连接池，提高性能
- **保活机制**: 自动保持连接活跃，防止超时断开
- **SSH优化**: 高效的SSH隧道管理，支持多种认证方式

## 🔌 支持的Redis版本

- ✅ Redis 2.6+
- ✅ Redis 3.0+
- ✅ Redis 4.0+
- ✅ Redis 5.0+
- ✅ Redis 6.0+ (支持用户名认证)
- ✅ Redis 7.0+
- ✅ Redis Stack
- ✅ AWS ElastiCache
- ✅ Azure Cache for Redis
- ✅ Google Cloud Memorystore
- ✅ 阿里云Redis
- ✅ 腾讯云Redis

## 🛠️ 故障排除

### 连接问题
- ❌ **连接超时**: 检查Redis服务状态和网络连通性
- ❌ **认证失败**: 验证用户名密码是否正确
- ❌ **权限错误**: 检查Redis配置文件的bind和protected-mode设置
- ❌ **防火墙**: 确认6379端口（或自定义端口）已开放

### SSH隧道问题
- ❌ **SSH连接失败**: 验证SSH服务器地址、端口、用户名
- ❌ **私钥认证失败**: 检查私钥文件格式和权限（应为600）
- ❌ **隧道建立失败**: 确认SSH用户有端口转发权限

### 性能问题
- ✅ **大量键加载慢**: 调整最大键数限制，或使用搜索模式缩小范围
- ✅ **界面卡顿**: 应用采用流式加载，最多支持10万个键的高效管理
- ✅ **内存占用高**: 关闭不需要的连接，清理键缓存
- ✅ **SSH连接超时**: 检查网络连接和防火墙设置

### 配置文件位置
```bash
# 用户配置文件
~/.redis_manager_config.json

# 清除配置（重置应用）
rm ~/.redis_manager_config.json
```

## 📝 更新日志

### v1.0.0 (2024-12-19)

#### 新增功能
- ✨ 初始版本发布
- ✨ 支持多连Redis接配置管理
- ✨ SSH隧道连接支持（密码和私钥认证）
- ✨ 所有Redis数据类型的可视化编辑
- ✨ Hash类型专用编辑器和JSON格式化
- ✨ 内置Redis命令行终端

#### 性能优化
- ⚡ 流式加载大量键（最多100,000个）
- ⚡ 非阻塞UI设计，界面始终响应
- ⚡ 智能批量加载和实时进度显示
- ⚡ 自动连接保活机制

#### 用户体验
- 🎨 现代化GUI界面设计
- 🎨 树形结构显示键，支持分组折叠
- 🎨 响应式布局，支持大窗口显示
- 🎨 滚动支持的对话框和表单

## 🏗️ 开发信息

### 项目结构
```
RedisM/
├── redis_manager.py      # 主应用程序
├── create_icon.py        # 图标生成脚本
├── requirements.txt      # Python依赖清单
├── build_python.sh       # macOS构建脚本
├── RedisManager.spec     # PyInstaller配置
├── .gitignore           # Git忽略文件
├── README.md            # 项目文档
└── INSTALL_GUIDE.md     # 安装指南
```

### 技术栈
- **GUI框架**: tkinter (Python标准库)
- **Redis客户端**: redis-py
- **SSH连接**: paramiko
- **打包工具**: PyInstaller
- **图标生成**: PIL/Pillow

### 版本信息
- **当前版本**: v1.0.0
- **Python版本**: 3.8+
- **支持平台**: macOS (Intel/Apple Silicon)

### 添加新功能
1. 修改 `redis_manager.py` 主程序
2. 更新 `requirements.txt` 依赖（如需要）
3. 测试功能完整性
4. 更新版本号常量
5. 重新构建应用程序

### 构建配置
- **应用名称**: 在 `__app_name__` 常量中定义
- **版本号**: 在 `__version__` 常量中定义
- **Bundle ID**: com.redismanager.app
- **目标架构**: x86_64 (可修改为universal2支持Apple Silicon)

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 贡献指南
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 问题反馈
- 🐛 **Bug报告**: 请提供详细的复现步骤
- 💡 **功能建议**: 描述期望的功能和使用场景
- 📚 **文档改进**: 帮助完善文档和示例

## 🙏 致谢

感谢以下开源项目：
- [redis-py](https://github.com/redis/redis-py) - Redis Python客户端
- [paramiko](https://github.com/paramiko/paramiko) - SSH连接库
- [PyInstaller](https://github.com/pyinstaller/pyinstaller) - Python应用打包工具

---

**RedisM** - 让Redis管理更简单 🚀