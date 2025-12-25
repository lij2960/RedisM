# RedisM

一个现代化的Redis管理工具，使用Python和tkinter开发，支持SSH隧道连接和实时数据操作，可编译为macOS原生应用程序。

![RedisM Logo](https://img.shields.io/badge/RedisM-v1.0.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

## 🎯 核心特性

### 🚀 高性能数据管理
- **流式加载**: 支持100,000+键的高效管理
- **智能分组**: 自动按分隔符分组显示，支持树形结构
- **实时操作**: 添加、编辑操作直接作用于Redis，无需批量更新
- **过滤搜索**: 所有数据类型支持实时过滤和模糊搜索

### 🔐 安全连接支持
- **SSH隧道**: 完整的SSH隧道支持，安全访问内网Redis
- **多种认证**: 支持密码和私钥认证
- **连接管理**: 多连接配置保存和快速切换

### 🎨 现代化界面
- **直观操作**: 现代化GUI界面，流畅的用户体验
- **数据类型支持**: 完整支持String、Hash、List、Set、ZSet
- **JSON格式化**: 内置JSON编辑器，支持格式化和压缩
- **实时反馈**: 操作即时生效，友好的成功/错误提示

### ⚡ 专业工具
- **内置命令行**: 支持所有Redis命令，智能提示和自动完成
- **数据编辑**: 双击编辑，支持字段名修改和值更新
- **批量操作**: 保留批量更新功能，适用于复杂场景

## 🖥️ 系统要求

- **操作系统**: macOS 10.14+ (Mojave或更高版本)
- **Python**: 3.8+ (推荐3.9+)
- **架构**: Intel x86_64 或 Apple Silicon (M1/M2/M3)
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

### 方式一：直接运行（开发模式）
```bash
# 克隆项目
git clone <repository-url>
cd RedisM

# 安装依赖
pip3 install -r requirements.txt

# 运行应用
python3 redis_manager.py
```

### 方式二：编译为Mac应用程序

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

### 连接管理
1. **添加连接**: 点击左侧"Add"按钮
2. **连接信息**:
   - **连接名称**: 自定义连接标识
   - **Redis主机**: 服务器地址（支持内网地址）
   - **端口**: 默认6379
   - **用户名**: 可选，Redis 6.0+支持
   - **密码**: Redis认证密码
   - **最大键数**: 限制显示的键数量（0=无限制）
   - **数据库数量**: 配置数据库数量（1-128）

### SSH隧道配置
1. **启用SSH**: 勾选"Use SSH Tunnel"
2. **SSH服务器**:
   - **SSH主机**: SSH服务器地址
   - **SSH端口**: 默认22
   - **SSH用户名**: SSH登录用户
3. **认证方式**:
   - **密码认证**: 输入SSH密码
   - **私钥认证**: 选择私钥文件或粘贴私钥内容
   - **密钥密码**: 如使用加密私钥，输入密钥密码

### 数据管理

#### 浏览和搜索
1. **连接Redis**: 选择连接后点击"Connect"或双击连接名
2. **选择数据库**: 使用下拉菜单切换数据库
3. **搜索键**: 输入模式（支持*通配符）
4. **树形浏览**: 点击树形结构中的键查看详情
5. **过滤数据**: 使用Find按钮过滤显示的数据

#### 实时操作
- **添加数据**: 点击"Add Item"直接添加到Redis
- **编辑数据**: 双击任意项目进行编辑，保存即时生效
- **删除数据**: 选择项目后删除
- **批量操作**: 使用"Update All"进行批量更新（可选）

#### 数据类型支持
- **Hash**: 字段名和值的编辑，支持JSON格式化
- **List**: 按索引编辑，支持追加和修改
- **Set**: 成员编辑，自动去重
- **ZSet**: 成员和分数编辑
- **String**: 文本编辑，支持JSON格式化

### 命令行操作
1. 切换到"Command Line"标签
2. 输入Redis命令（如：`GET mykey`、`HGETALL myhash`）
3. 支持命令自动完成和智能提示
4. 按回车或点击"Execute"执行
5. 查看格式化的执行结果

## 🏗️ 项目结构

```
RedisM/
├── redis_manager.py      # 主应用程序
├── config.py            # 配置文件
├── connection_manager.py # 连接管理模块
├── key_manager.py       # 键管理模块
├── create_icon.py       # 图标生成脚本
├── requirements.txt     # Python依赖清单
├── build_python.sh      # macOS构建脚本
├── run.sh              # 运行脚本
├── RedisM.spec         # PyInstaller配置
├── docs/               # 功能文档
│   ├── UI_IMPROVEMENTS.md
│   ├── HASH_FILTER_FEATURE.md
│   ├── ALL_TYPES_FILTER_FEATURE.md
│   ├── QUERY_FIXES.md
│   ├── REALTIME_OPERATIONS.md
│   └── UPDATE_ALL_FIX.md
├── .gitignore          # Git忽略文件
└── README.md           # 项目文档
```

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

### 配置文件位置
```bash
# 用户配置文件
~/.redis_manager_config.json

# 清除配置（重置应用）
rm ~/.redis_manager_config.json
```

## 📝 更新日志

### v1.0.0 (2024-12-25)

#### 🎉 新增功能
- ✨ 初始版本发布
- ✨ 支持多Redis连接配置管理
- ✨ SSH隧道连接支持（密码和私钥认证）
- ✨ 所有Redis数据类型的可视化编辑
- ✨ **实时操作**: 添加、编辑操作直接作用于Redis
- ✨ **智能过滤**: 所有数据类型支持实时过滤搜索
- ✨ **JSON编辑器**: Hash和Set类型支持JSON格式化
- ✨ **Query修复**: 改进查询按钮逻辑和Hash字段查询
- ✨ 内置Redis命令行终端，支持智能提示

#### ⚡ 性能优化
- ⚡ 流式加载大量键（最多100,000个）
- ⚡ 非阻塞UI设计，界面始终响应
- ⚡ 智能批量加载和实时进度显示
- ⚡ 自动连接保活机制
- ⚡ 大Hash数据分批读取优化
- ⚡ **实时数据同步**: Redis、缓存、UI三层同步

#### 🎨 用户体验
- 🎨 现代化GUI界面设计，增加行间距和悬停效果
- 🎨 树形结构显示键，支持分组折叠
- 🎨 智能分组优化（单键分组自动展开）
- 🎨 响应式布局，支持大窗口显示
- 🎨 **即时反馈**: 操作成功/失败的友好提示
- 🎨 **状态保持**: 过滤状态下的数据完整性保证

#### 🔧 技术改进
- 🔧 **Update All修复**: 过滤状态下不再丢失隐藏数据
- 🔧 **模块化设计**: 清晰的代码结构和文档组织
- 🔧 **错误处理**: 完善的异常处理和用户提示
- 🔧 **数据一致性**: 确保操作的原子性和一致性

## 📚 详细文档

更多详细功能说明请查看 `docs/` 目录：

- [UI界面改进](docs/UI_IMPROVEMENTS.md) - 界面优化和用户体验改进
- [Hash过滤功能](docs/HASH_FILTER_FEATURE.md) - Hash类型的过滤搜索功能
- [全类型过滤功能](docs/ALL_TYPES_FILTER_FEATURE.md) - 所有数据类型的过滤功能
- [查询功能修复](docs/QUERY_FIXES.md) - Query按钮和Hash查询的修复
- [实时操作功能](docs/REALTIME_OPERATIONS.md) - 实时添加和编辑功能
- [Update All修复](docs/UPDATE_ALL_FIX.md) - 批量更新功能的修复

## 🏗️ 开发信息

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

**RedisM** - 让Redis管理更简单、更高效 🚀