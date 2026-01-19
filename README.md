# RedisM v1.1.0

<div align="center">

**现代化的Redis管理工具**

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](#)
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
- **智能重连**: 连接断开时自动重连机制，操作无缝继续
- **安全认证**: 密码查看需要系统认证，保护敏感信息安全

### 🗄️ 数据管理
- **全类型支持**: 完整支持String、Hash、List、Set、ZSet所有Redis数据类型
- **可视化编辑**: 表格形式直观展示和编辑结构化数据
- **批量操作**: 支持批量添加、删除和编辑数据项
- **实时过滤**: 对所有数据类型提供实时搜索和过滤功能，显示统计信息
- **JSON处理**: 内置JSON格式化、压缩和语法高亮显示

### 🔑 键管理
- **树形结构**: 按分隔符自动组织键的层级结构显示
- **智能搜索**: 支持通配符模式匹配和关键词搜索
- **数据库一致性**: 确保所有操作在正确的数据库中执行，避免意外切换
- **一键创建**: 支持创建所有类型的Redis键，包含TTL设置

### 🎨 用户界面
- **现代设计**: 简洁美观的现代化界面设计
- **自适应对话框**: 所有编辑对话框支持真正的自适应高度调整
- **响应式布局**: 自适应窗口大小的响应式界面布局
- **JSON语法高亮**: 所有JSON文本区域支持彩色语法高亮显示
- **搜索功能**: 所有文本编辑窗口支持⌘F快速搜索

### 💻 开发工具
- **命令行界面**: 内置完整的Redis命令行，支持所有Redis命令
- **实时执行**: 命令即时执行和结果显示
- **历史记录**: 命令执行历史和智能补全
- **错误处理**: 详细的错误提示和异常处理机制

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
- **实时统计**: 结构化数据显示总数统计和过滤结果

### 高级功能

#### 数据库一致性保障
- **智能状态管理**: 自动确保所有操作在正确的数据库中执行
- **防止意外切换**: 修复了删除、创建操作可能导致的数据库切换问题
- **状态同步**: 连接池和应用状态完全同步

#### JSON处理增强
- **语法高亮**: 字符串(绿色)、键(深蓝)、数字(蓝色)、布尔值(红色)、null(紫色)
- **格式化工具**: Format JSON和Minify JSON按钮
- **实时高亮**: 编辑过程中实时应用语法高亮

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
│       └── helpers.py          # 辅助函数（包含JSON处理）
├── docs/                  # 文档目录
│   └── README.md               # 文档说明
├── main.py               # 主程序入口
├── requirements.txt      # Python依赖列表
├── RedisM.spec          # PyInstaller打包配置
├── build_python.sh      # 自动构建脚本
└── README.md            # 项目说明文档
```

## 🔧 技术栈

- **GUI框架**: tkinter（Python标准库）
- **Redis客户端**: redis-py 5.0.1
- **SSH支持**: paramiko 3.4.0
- **图像处理**: Pillow 10.0+
- **打包工具**: PyInstaller 6.0+
- **开发语言**: Python 3.8+

## 📝 更新日志

### v1.1.0 (2025-01-19) - 当前版本
- 🔧 **修复**: 数据库切换一致性问题
  - 修复"Add New Key"操作偶尔切换到默认数据库的问题
  - 修复删除key操作导致数据库恢复到默认库的问题
  - 修复删除key后键列表显示错误数据库内容的问题
  - 实现集中化数据库状态管理，确保所有操作的一致性

- 🎨 **增强**: 自适应对话框完善
  - 完成所有Add对话框转换为真正的自适应高度
  - 统一所有编辑对话框的用户体验
  - 添加JSON语法高亮到所有Add对话框

- 🔐 **安全**: 连接密码保护
  - 添加密码查看按钮（👁图标）
  - 实现系统密码验证机制
  - 增强敏感信息的安全管理

- ✨ **美化**: JSON语法高亮
  - 实现全面的JSON彩色语法高亮
  - 统一的颜色方案和实时高亮
  - 提升JSON数据的可读性

- 📊 **改进**: 过滤和统计功能
  - 优化过滤文本框布局（固定25字符宽度）
  - 添加总数统计显示
  - 修复初始统计显示问题

### v1.0.5 (2025-01-05)
- 🔧 **修复**: 关键UI布局问题，显著提升用户体验
- 🐛 **修复**: Hash编辑对话框关键错误
- 🚫 **优化**: 标签导航体验，禁用意外的鼠标滚轮切换
- 🎨 **简化**: Key Manager窗口布局
- ✨ **增强**: 数据类型选择和结构化数据显示

### v1.0.4 (2024-12-31)
- 🔄 **新增**: 智能自动重连功能
- 🗄️ **修复**: 数据库切换问题
- 🎨 **优化**: 服务器信息双面板布局

### v1.0.3 (2024-12-30)
- ✨ **新增**: 对话框真正自适应功能
- 🔍 **增强**: 全局搜索功能
- 🏗️ **架构**: SimpleDialog架构引入

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

**数据库一致性问题**:
- ✅ 确保操作在正确的数据库中执行
- ✅ 检查数据库切换后的状态同步
- ✅ 验证键列表显示的数据库内容

**界面问题**:
- ✅ 确保Python环境支持tkinter
- ✅ 检查显示器分辨率和缩放设置
- ✅ 尝试调整窗口大小以触发自适应布局

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- **Redis团队** - 提供优秀的内存数据库
- **Python社区** - 丰富的开源库和工具
- **tkinter开发者** - 跨平台GUI框架
- **所有贡献者** - 代码贡献和问题反馈
- **用户社区** - 使用反馈和功能建议

---

<div align="center">

**RedisM v1.1.0** - 让Redis管理变得简单而优雅 ✨

Made with ❤️ for Redis developers worldwide

[⬆️ 回到顶部](#redism-v110)

</div>