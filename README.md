# RedisM v1.1.4

<div align="center">

**现代化的Redis管理工具**

[![Version](https://img.shields.io/badge/version-1.1.4-blue.svg)](#)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Redis](https://img.shields.io/badge/Redis-5.0+-red.svg)](https://redis.io)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)](#)

一个功能完整、界面现代的Redis数据库管理应用

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用指南](#-使用指南) • [更新日志](#-更新日志)

</div>

---

## ✨ 功能特性

### 🔗 连接管理
- **多连接支持**: 管理多个Redis服务器连接配置
- **SSH隧道**: 支持通过SSH隧道安全连接远程Redis服务器
- **连接测试**: 保存前一键测试连接有效性和配置正确性
- **智能重连**: 连接断开时自动异步重连，操作无缝继续，避免UI冻结
- **安全认证**: 密码查看需要系统认证，保护敏感信息安全

### 🗄️ 数据管理
- **全类型支持**: 完整支持String、Hash、List、Set、ZSet所有Redis数据类型
- **可视化编辑**: 表格形式直观展示和编辑结构化数据
- **批量操作**: 支持批量添加、删除和编辑数据项
- **实时过滤**: 对所有数据类型提供实时搜索和过滤功能，显示统计信息
- **JSON处理**: 内置JSON格式化、压缩和语法高亮显示
- **PHP Serialize支持**: 完整的PHP序列化数据格式化和压缩功能

### 🔑 键管理
- **树形结构**: 按分隔符自动组织键的层级结构显示
- **智能搜索**: 支持通配符模式匹配和关键词搜索
- **批量删除**: 支持按模式批量删除键 ⭐ 新功能
- **数据库一致性**: 确保所有操作在正确的数据库中执行，避免意外切换
- **一键创建**: 支持创建所有类型的Redis键，包含TTL设置

### 🎨 用户界面
- **现代设计**: 简洁美观的现代化界面设计
- **自适应对话框**: 所有编辑对话框支持真正的自适应高度调整
- **响应式布局**: 自适应窗口大小的响应式界面布局
- **JSON语法高亮**: 所有JSON文本区域支持彩色语法高亮显示
- **搜索功能**: 所有文本编辑窗口支持⌘F快速搜索，支持向前/向后查找

### 💻 命令行界面 ⭐ 增强
- **完整命令支持**: 内置完整的Redis命令行，支持所有Redis命令
- **自定义命令**: 支持 DELPATTERN 和 COUNTPATTERN 扩展命令
- **危险命令保护**: FLUSHDB、FLUSHALL、DELPATTERN 执行前需确认
- **实时执行**: 命令即时执行和结果显示
- **智能补全**: Tab键自动补全命令
- **大数据集优化**: 优化 SMEMBERS 等返回大量数据的命令处理

### 🆕 PHP Serialize 支持 (v1.1.2+)

RedisM现在完整支持PHP序列化数据的处理：

#### Format PHP 按钮
- 将PHP序列化数据解析并显示为可读的JSON格式
- 自动应用JSON语法高亮，提升可读性
- 支持嵌套数组和复杂数据结构

#### Minify PHP 按钮
- 智能检测输入格式（JSON或PHP serialize）
- JSON格式 → 自动转换为PHP序列化格式
- PHP格式 → 重新序列化（压缩）
- 支持往返转换：PHP ↔ JSON ↔ PHP

#### 使用示例

```
原始PHP数据:
a:2:{s:4:"name";s:4:"test";s:3:"age";i:25;}

↓ 点击 "Format PHP"

格式化显示:
{
  "name": "test",
  "age": 25
}

↓ 编辑数据

↓ 点击 "Minify PHP"

转换回PHP格式:
a:2:{s:4:"name";s:4:"test";s:3:"age";i:30;}
```

#### 可用位置
- ✅ String值编辑器（主界面）
- ✅ Hash字段编辑和添加对话框
- ✅ Set成员编辑和添加对话框
- ✅ List元素编辑对话框
- ✅ ZSet成员编辑和添加对话框
- ✅ 添加新键对话框（String类型）

详细使用说明请查看 [PHP Serialize使用文档](docs/PHP_SERIALIZE_USAGE.md)

### 🆕 CLI 扩展命令 (v1.1.4+)

RedisM 命令行界面支持以下扩展命令：

#### DELPATTERN - 批量删除键
按模式批量删除匹配的键，使用 SCAN 命令避免阻塞 Redis。

```bash
# 删除所有以 user: 开头的键
redis> DELPATTERN user:*
Scanning keys matching pattern: user:*...
Successfully deleted 150 keys matching 'user:*'

# 删除所有以 cache: 开头的键
redis> DELPATTERN cache:*
```

⚠️ **安全提示**: 执行前会弹出确认对话框，防止误删除。

#### COUNTPATTERN - 统计匹配键数量
统计匹配指定模式的键数量，不会删除任何数据。

```bash
# 统计所有以 session: 开头的键
redis> COUNTPATTERN session:*
Counting keys matching pattern: session:*...
Found 1234 keys matching 'session:*'

# 统计所有键
redis> COUNTPATTERN *
```

#### 危险命令保护
以下命令执行前需要确认：
- **FLUSHDB** - 删除当前数据库所有键
- **FLUSHALL** - 删除所有数据库的所有键
- **DELPATTERN** - 批量删除匹配的键

## 🚀 快速开始

### 环境要求
- **Python**: 3.8或更高版本
- **Redis**: 5.0或更高版本
- **系统**: macOS、Linux或Windows
- **GUI**: tkinter支持（通常随Python安装）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/your-repo/RedisM.git
   cd RedisM
   ```

2. **创建虚拟环境**（推荐）
   ```bash
   python -m venv venv
   
   # macOS/Linux
   source venv/bin/activate
   
   # Windows
   venv\Scripts\activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动应用**
   ```bash
   python main.py
   ```

### 打包应用

使用PyInstaller将应用打包为独立可执行文件：

```bash
# 使用提供的构建脚本（推荐）
chmod +x build_python.sh
./build_python.sh

# 或手动执行PyInstaller
pyinstaller RedisM.spec
```

打包后的应用位于 `dist/` 目录中。

详细打包说明请查看 [重新打包指南](docs/REBUILD_INSTRUCTIONS.md)

## 📖 使用指南

### 连接Redis服务器

1. **添加连接配置**
   - 点击左侧面板的"➕ Add"按钮
   - 系统自动填充默认值：
     - Redis主机：localhost
     - Redis端口：6379
     - 最大键数：0（无限制）
     - 数据库数：16
     - SSH端口：22
     - SSH用户名：root

2. **配置连接信息**
   - 修改连接名称便于识别
   - 根据需要调整主机地址和端口
   - 设置认证信息（如需要）
   - 使用👁按钮查看已保存的密码（需要系统认证）

3. **配置SSH隧道**（可选）
   - 勾选"Enable SSH Tunnel"
   - 填写SSH服务器信息
   - 选择密码或私钥认证方式

4. **测试和连接**
   - 点击"Test Connection"验证连接
   - 测试成功后点击"Save"保存配置
   - 选择连接后点击"🔌 Connect"

### 管理Redis数据

#### 数据库切换
- **切换数据库**: 使用顶部数据库下拉菜单
- **实时更新**: 切换后键列表和服务器信息自动更新
- **状态显示**: 当前数据库在服务器信息中高亮显示
- **操作一致性**: 所有操作确保在当前选择的数据库中执行

#### 创建和编辑数据
- **创建新键**: 点击"➕ Add New Key"支持所有数据类型
- **自适应对话框**: 所有编辑对话框支持真正的自适应高度
- **JSON语法高亮**: JSON文本区域支持彩色语法高亮显示
- **PHP Serialize**: 支持PHP序列化数据的格式化和压缩
- **实时统计**: 结构化数据显示总数统计和过滤结果

### 高级功能

#### 数据库一致性保障
- **智能状态管理**: 自动确保所有操作在正确的数据库中执行
- **防止意外切换**: 修复了删除、创建操作可能导致的数据库切换问题
- **状态同步**: 连接池和应用状态完全同步

#### JSON和PHP Serialize处理
- **JSON语法高亮**: 字符串(绿色)、键(深蓝)、数字(蓝色)、布尔值(红色)、null(紫色)
- **格式化工具**: Format JSON、Minify JSON、Format PHP、Minify PHP按钮
- **实时高亮**: 编辑过程中实时应用语法高亮
- **智能转换**: PHP序列化数据与JSON格式之间的无缝转换

#### 连接稳定性
- **异步重连**: 连接断开时自动在后台重连，不阻塞UI
- **超时设置**: 5秒连接超时，避免长时间等待
- **状态反馈**: 重连过程中显示清晰的状态信息
- **操作恢复**: 重连成功后自动继续之前的操作

## 🏗️ 项目结构

```
RedisM/
├── src/                    # 源代码目录
│   ├── config.py          # 应用配置和常量
│   ├── main.py            # 应用程序入口点
│   ├── dialogs/           # 对话框组件
│   │   ├── base_dialog.py      # 基础对话框类
│   │   ├── simple_dialog.py    # 简单对话框类（自适应）
│   │   ├── search_mixin.py     # 搜索功能混入
│   │   ├── connection_dialog.py # 连接配置对话框
│   │   └── key_dialogs.py      # 键编辑对话框
│   ├── redis/             # Redis操作模块
│   │   ├── connection.py       # Redis连接管理
│   │   └── operations.py       # Redis数据操作
│   ├── ui/                # 用户界面组件
│   │   ├── left_panel.py       # 左侧面板（连接和键列表）
│   │   ├── right_panel.py      # 右侧面板（数据管理）
│   │   ├── key_manager.py      # 键管理器
│   │   ├── cli_interface.py    # 命令行界面
│   │   ├── main_window.py      # 主窗口
│   │   └── styles.py           # 样式管理
│   └── utils/             # 工具函数
│       └── helpers.py          # 辅助函数（JSON/PHP处理）
├── docs/                  # 文档目录
│   ├── README.md               # 文档说明
│   ├── PHP_SERIALIZE_USAGE.md  # PHP序列化使用指南
│   └── REBUILD_INSTRUCTIONS.md # 重新打包指南
├── main.py               # 主程序入口
├── requirements.txt      # Python依赖列表
├── RedisM.spec          # PyInstaller打包配置
├── build_python.sh      # 自动构建脚本
├── CHANGELOG.md         # 更新日志
└── README.md            # 项目说明文档
```

## 🔧 技术栈

- **GUI框架**: tkinter（Python标准库）
- **Redis客户端**: redis-py 5.0.1
- **SSH支持**: paramiko 3.4.0
- **PHP序列化**: phpserialize 1.3+
- **图像处理**: Pillow 10.0+
- **打包工具**: PyInstaller 6.0+
- **开发语言**: Python 3.8+

## 📝 更新日志

### v1.1.4 (2026-04-13) - 当前版本
- 🚀 **CLI增强**: 命令行界面功能扩展
  - 新增 DELPATTERN 命令：按模式批量删除键
  - 新增 COUNTPATTERN 命令：统计匹配键数量
  - 危险命令保护：FLUSHDB、FLUSHALL、DELPATTERN 执行前需确认
  - 修复 SMEMBERS 等命令返回大数据集时的卡死问题
  - 优化命令结果格式化，支持 set 类型返回值

- 🔧 **搜索修复**: 文本搜索功能完善
  - 修复 Find Previous 按钮不工作的问题
  - 优化搜索光标位置管理
  - 所有搜索框统一修复

- 🛠️ **稳定性**: 连接和操作优化
  - 改进连接超时处理
  - 优化大数据集的 UI 更新

### v1.1.3 (2025-01-19)
- 🧹 **维护**: 项目清理和文档重组
  - 删除临时测试文件
  - 整理文档结构到docs目录
  - 优化项目组织结构

- 📚 **文档**: 全面更新README
  - 添加PHP Serialize功能文档
  - 更新功能特性列表
  - 完善使用指南和示例
  - 改进故障排除说明

### v1.1.2 (2025-01-19)
- 🚀 **新增**: PHP Serialize支持
  - Format PHP按钮解析PHP序列化数据为JSON
  - Minify PHP按钮智能转换JSON/PHP格式
  - 所有编辑对话框支持PHP序列化操作
  - 智能格式检测和往返转换

- 🔧 **修复**: 智能格式检测
  - 自动识别JSON或PHP serialize格式
  - 防止"unexpected opcode"错误
  - 友好的中文错误提示

- 🛠️ **构建**: 打包配置优化
  - 添加phpserialize到hiddenimports
  - 更新构建脚本使用requirements.txt
  - 完善PyInstaller配置

### v1.1.1 (2025-01-19)
- 🔧 **修复**: 连接稳定性
  - 异步重连机制，避免UI冻结
  - 连接超时设置（5秒）
  - 所有关键操作支持自动重连
  - 改进错误恢复和状态反馈

### v1.1.0 (2025-01-19)
- 🔧 **修复**: 数据库切换一致性
  - 集中化数据库状态管理
  - 修复Add/Delete操作的数据库切换问题
  - 确保所有操作在正确数据库中执行

- 🎨 **增强**: 自适应对话框完善
  - 所有Add对话框转换为自适应布局
  - 统一的用户体验
  - JSON语法高亮支持

- 🔐 **安全**: 连接密码保护
  - 密码查看需要系统认证
  - 👁图标提供安全的密码查看
  - 保护敏感信息安全

- ✨ **美化**: JSON语法高亮
  - 全面的彩色语法高亮
  - 实时高亮更新
  - 提升数据可读性

### v1.0.5 (2025-01-05)
- 🔧 修复关键UI布局问题
- 🐛 修复Hash编辑对话框错误
- 🚫 优化标签导航体验
- 🎨 简化Key Manager布局

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是bug报告、功能建议还是代码贡献。

### 如何贡献
1. **Fork** 本项目到你的GitHub账户
2. **创建分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

## 🔧 故障排除

### 常见问题

**连接问题**:
- ✅ 确认Redis服务正在运行
- ✅ 检查主机地址和端口配置
- ✅ 验证用户名和密码正确性
- ✅ 检查防火墙和网络连接
- ✅ 查看连接超时设置（默认5秒）

**数据库一致性问题**:
- ✅ 系统自动确保操作在正确数据库中
- ✅ 检查数据库切换后的状态同步
- ✅ 验证键列表显示的数据库内容

**PHP Serialize问题**:
- ✅ 确保输入的是有效的PHP序列化格式
- ✅ Format PHP后可以直接Minify PHP转回
- ✅ 支持JSON和PHP格式的智能转换
- ✅ 查看详细错误提示了解问题

**界面问题**:
- ✅ 确保Python环境支持tkinter
- ✅ 检查显示器分辨率和缩放设置
- ✅ 尝试调整窗口大小以触发自适应布局

**打包问题**:
- ✅ 确保所有依赖已安装（pip install -r requirements.txt）
- ✅ 检查PyInstaller版本（需要6.0+）
- ✅ 查看[重新打包指南](docs/REBUILD_INSTRUCTIONS.md)
- ✅ 验证phpserialize已添加到hiddenimports

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **Redis团队** - 提供优秀的内存数据库
- **Python社区** - 丰富的开源库和工具
- **tkinter开发者** - 跨平台GUI框架
- **phpserialize作者** - PHP序列化支持
- **所有贡献者** - 代码贡献和问题反馈
- **用户社区** - 使用反馈和功能建议

---

<div align="center">

**RedisM v1.1.4** - 让Redis管理变得简单而优雅 ✨

Made with ❤️ for Redis developers worldwide

[⬆️ 回到顶部](#redism-v114)

</div>
