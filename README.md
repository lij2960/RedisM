# RedisM v1.0.3

<div align="center">

**现代化的Redis管理工具**

[![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)](#)
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
- **自动重连**: 连接断开时智能重连机制，保持会话连续性

### 🗄️ 数据管理
- **全类型支持**: 完整支持String、Hash、List、Set、ZSet所有Redis数据类型
- **可视化编辑**: 表格形式直观展示和编辑结构化数据
- **批量操作**: 支持批量添加、删除和编辑数据项
- **实时过滤**: 对所有数据类型提供实时搜索和过滤功能
- **JSON处理**: 内置JSON格式化、压缩和语法验证

### 🔑 键管理
- **树形结构**: 按分隔符自动组织键的层级结构显示
- **智能搜索**: 支持通配符模式匹配和关键词搜索
- **一键创建**: 支持创建所有类型的Redis键，包含TTL设置
- **批量创建**: 快速创建多个相关键和数据

### 🎨 用户界面
- **现代设计**: 简洁美观的现代化界面设计
- **响应式布局**: 自适应窗口大小的响应式界面布局，文本区域真正自适应窗口变化
- **丰富交互**: 鼠标悬停效果、右键菜单、键盘快捷键
- **用户友好**: 直观的操作流程和清晰的状态反馈
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
   - 填写连接基本信息：
     - 连接名称：便于识别的连接名
     - 主机地址：Redis服务器IP或域名
     - 端口：Redis端口（默认6379）
     - 认证：用户名和密码（如需要）

2. **配置SSH隧道**（可选）
   - 勾选"Enable SSH Tunnel"
   - 填写SSH服务器信息：
     - SSH主机、端口、用户名
     - 选择密码或私钥认证方式
   - 配置本地端口转发

3. **测试和保存**
   - 点击"Test Connection"验证连接
   - 测试成功后点击"Save"保存配置

4. **连接服务器**
   - 在连接列表中选择目标连接
   - 点击"🔌 Connect"按钮连接
   - 连接成功后状态显示"✅ Connected"

### 管理Redis数据

#### 浏览和搜索键
- **查看键列表**: 连接成功后左侧自动显示键的树形结构
- **搜索键**: 在搜索框中输入模式（支持`*`和`?`通配符）
- **分组浏览**: 键按分隔符（默认`:`）自动分组
- **展开/收起**: 点击文件夹图标管理分组显示

#### 创建新键
1. 点击左侧面板的"➕ Add New Key"按钮
2. 输入键名（如：`user:1001`）
3. 选择数据类型：
   - **String**: 字符串数据，支持JSON格式化
   - **Hash**: 字段-值对，格式：`field=value`
   - **List**: 列表数据，每行一个元素
   - **Set**: 集合数据，自动去重
   - **ZSet**: 有序集合，格式：`score member`
4. 输入初始数据
5. 可选设置TTL过期时间
6. 点击"Create Key"完成创建

#### 编辑数据
- **查看详情**: 点击键名在右侧查看完整数据
- **编辑单项**: 双击表格行进行编辑
- **添加项目**: 点击"Add Item"按钮添加新数据
- **批量删除**: 
  - 使用Ctrl/Cmd+点击选择多个项目
  - 点击"Delete Item"或使用右键菜单删除
- **右键操作**: 右键点击获取编辑、删除等快捷操作

#### 数据过滤
- **实时过滤**: 在"Find"输入框中输入搜索内容
- **支持类型**: 
  - Hash：按字段名或值过滤
  - List：按元素内容过滤
  - Set：按成员内容过滤
  - ZSet：按成员或分数过滤
- **过滤统计**: 显示过滤结果数量和总数

### 高级功能

#### JSON数据处理
- **自动识别**: 自动识别JSON格式的数据
- **格式化**: 点击"Format JSON"美化JSON显示
- **压缩**: 点击"Minify JSON"压缩JSON格式
- **语法检查**: 自动检测和提示JSON语法错误

#### 命令行模式
1. 切换到右侧的"💻 Command Line"标签页
2. 在命令输入框中输入Redis命令
3. 按Enter键执行命令
4. 查看命令执行结果和状态
5. 使用上下箭头键浏览命令历史

#### 对话框操作
RedisM的对话框支持多种滚动方式：
- **键盘滚动**: 使用↑↓箭头键逐行滚动
- **快速滚动**: Page Up/Down键快速翻页
- **按钮滚动**: 点击右侧▲▼按钮滚动
- **滚动条**: 传统的拖拽滚动条操作

## 🏗️ 项目结构

```
RedisM/
├── src/                    # 源代码目录
│   ├── config.py          # 应用配置和常量
│   ├── main.py            # 应用程序入口点
│   ├── dialogs/           # 对话框组件
│   │   ├── base_dialog.py      # 基础对话框类
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
│       └── helpers.py          # 辅助函数
├── docs/                  # 文档目录
│   ├── README.md               # 文档说明
│   └── *.md                    # 功能文档
├── main.py               # 主程序入口
├── test.py               # 功能测试脚本
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

### v1.0.3 (2024-12-30)
- ✨ **新增**: 对话框文本区域真正自适应窗口大小功能
- 🎨 **改进**: 所有编辑对话框（Hash、Set、List、ZSet）现在支持文本区域随窗口大小实时调整
- 🔍 **增强**: 所有文本编辑窗口支持⌘F快速搜索功能
- 📏 **优化**: 调整Set、List、ZSet编辑对话框的默认窗口大小，提供更好的编辑体验
- 🧹 **整理**: 清理项目结构，删除开发过程中的临时文件和文档
- 🏗️ **架构**: 引入SimpleDialog架构，为编辑对话框提供更好的布局管理

### v1.0.2 (2024-12-29)
- 🐛 **修复**: Add New Key按钮移动到左侧面板后无法正常工作的问题
- 🔧 **优化**: 清理代码结构，删除无用的临时文件和测试文件
- 📚 **文档**: 重写README文档，提供更详细和结构化的使用说明
- ✨ **完善**: Add New Key功能现在完全支持所有Redis数据类型的创建
- 🎨 **改进**: 优化用户界面的操作流程和交互体验

### v1.0.1 (2024-12-28)
- ✨ **新增**: 完整的Add New Key功能，支持String、Hash、List、Set、ZSet类型
- 🎨 **改进**: 将Add New Key按钮移动到左侧面板，提供更符合逻辑的用户体验
- 🐛 **修复**: List和Set类型的Add Item按钮失效问题
- 📖 **文档**: 添加详细的功能文档和使用说明
- ✨ **增强**: 支持TTL设置、键存在检查、输入验证等高级功能

### v1.0.0 (2024-12-27)
- 🎉 **发布**: 首个正式版本发布
- ✨ **功能**: 完整的Redis连接管理功能
- ✨ **支持**: 支持所有Redis数据类型的CRUD操作
- 🎨 **界面**: 现代化的用户界面设计
- 🔒 **安全**: SSH隧道连接支持
- 💻 **工具**: 内置Redis命令行界面
- 🔍 **搜索**: 实时数据过滤和搜索功能
- 📱 **响应**: 响应式界面布局和交互设计

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是bug报告、功能建议还是代码贡献。

### 如何贡献
1. **Fork** 本项目到你的GitHub账户
2. **创建分支** (`git checkout -b feature/AmazingFeature`)
3. **提交更改** (`git commit -m 'Add some AmazingFeature'`)
4. **推送分支** (`git push origin feature/AmazingFeature`)
5. **创建Pull Request**

### 开发环境设置
```bash
# 克隆你的fork
git clone https://github.com/your-username/RedisM.git
cd RedisM

# 创建开发环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt

# 运行测试
python test.py

# 启动开发版本
python main.py
```

### 代码规范
- 遵循PEP 8 Python代码规范
- 添加适当的注释和文档字符串
- 确保新功能包含相应的测试
- 保持代码简洁和可读性

## 🔧 故障排除

### 常见问题

**连接问题**:
- ✅ 确认Redis服务正在运行
- ✅ 检查主机地址和端口配置
- ✅ 验证用户名和密码正确性
- ✅ 检查防火墙和网络连接

**SSH隧道问题**:
- ✅ 验证SSH服务器可访问性
- ✅ 检查SSH认证信息正确性
- ✅ 确认私钥文件格式和权限
- ✅ 测试SSH连接独立可用性

**界面问题**:
- ✅ 确保Python环境支持tkinter
- ✅ 在macOS上使用系统Python或正确配置的Python
- ✅ 检查显示器分辨率和缩放设置

**性能问题**:
- ✅ 调整最大键数限制
- ✅ 使用过滤功能减少显示数据量
- ✅ 关闭不必要的连接

### 获取帮助
1. 运行 `python test.py` 检查环境配置
2. 查看 [docs/](docs/) 目录下的详细技术文档
3. 在GitHub上提交Issue报告问题
4. 查看已有的Issue和解决方案

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

**RedisM v1.0.3** - 让Redis管理变得简单而优雅 ✨

Made with ❤️ for Redis developers worldwide

[⬆️ 回到顶部](#redism-v103)

</div>