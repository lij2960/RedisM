# RedisM

<div align="center">

**现代化的Redis管理工具**

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](#)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](https://www.apple.com/macos)

一个功能完整、界面现代的Redis数据库管理应用

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [使用指南](#-使用指南) • [开发文档](#-开发文档)

</div>

---

## 🌟 功能特性

### 🔗 连接管理
- **多连接支持**: 管理多个Redis实例连接
- **SSH隧道**: 支持通过SSH隧道安全连接远程Redis
- **自动重连**: 连接断开时自动重连机制
- **连接测试**: 保存前测试连接有效性

### 📊 数据管理
- **全类型支持**: String、Hash、List、Set、ZSet所有Redis数据类型
- **实时操作**: 添加、编辑、删除操作即时生效
- **数据过滤**: 所有数据类型的实时搜索和过滤
- **JSON支持**: 内置JSON格式化和验证

### 🎨 用户界面
- **现代化设计**: 符合macOS设计规范的原生界面
- **树形显示**: 键名按分隔符自动分组显示
- **响应式布局**: 自适应窗口大小的界面布局
- **键盘支持**: 完整的键盘快捷键支持

### 💻 命令行界面
- **内置CLI**: 完整的Redis命令行界面
- **命令补全**: 智能命令提示和自动补全
- **历史记录**: 命令执行历史和结果显示

## 🚀 快速开始

### 系统要求
- macOS 10.14+ (主要支持平台)
- Python 3.8+
- 支持tkinter的Python环境

### 安装运行

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/RedisM.git
cd RedisM

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python main.py
```

### 构建应用包
```bash
# 构建macOS应用包
./build_python.sh

# 生成的应用在 dist/RedisM.app
```

## 📖 使用指南

### 连接Redis

1. **启动RedisM**
2. **添加连接**: 点击左侧"Add"按钮
3. **配置连接**:
   - 连接名称: 为连接起一个易识别的名称
   - Redis主机: 服务器地址 (如 localhost)
   - 端口: Redis端口 (默认 6379)
   - 认证: 用户名和密码 (可选)

4. **SSH隧道** (可选):
   - 勾选"Enable SSH Tunnel"
   - 配置SSH服务器信息
   - 选择密码或私钥认证

5. **测试并保存**: 点击"Test Connection"验证后保存

### 数据操作

#### 浏览数据
- **搜索键**: 在搜索框输入模式 (支持 `*` 通配符)
- **分组显示**: 键名按 `:` 分隔符自动分组
- **展开/收起**: 点击文件夹图标管理分组

#### 编辑数据
- **查看详情**: 单击键名查看数据内容
- **编辑值**: 双击表格行进行编辑
- **添加项**: 点击"Add Item"添加新数据
- **删除项**: 选中后点击删除按钮

#### 过滤功能
- **实时过滤**: 在"Find"框中输入搜索内容
- **支持类型**: Hash字段、List项、Set成员、ZSet成员
- **即时生效**: 输入时立即显示过滤结果

### 对话框操作

RedisM的对话框支持多种滚动方式：
- **键盘滚动**: 使用 ↑↓ 箭头键
- **快速滚动**: Page Up/Down 键
- **按钮滚动**: 点击右侧 ▲▼ 按钮
- **传统滚动**: 拖拽滚动条

### 命令行使用
1. 切换到"Command Line"标签页
2. 输入Redis命令 (如 `GET mykey`)
3. 按Enter执行
4. 查看执行结果

## 🛠 开发文档

### 项目结构
```
RedisM/
├── src/                    # 源代码
│   ├── config.py          # 应用配置
│   ├── main.py            # 应用入口
│   ├── ui/                # UI组件
│   ├── redis/             # Redis操作
│   ├── dialogs/           # 对话框
│   └── utils/             # 工具函数
├── docs/                  # 详细文档
├── main.py                # 启动文件
├── test.py                # 功能测试
└── requirements.txt       # 依赖列表
```

### 开发环境
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test.py

# 启动开发版本
python main.py
```

### 核心依赖
- **redis**: Redis Python客户端
- **paramiko**: SSH连接支持
- **tkinter**: GUI框架 (Python内置)

## 📚 文档

- [功能文档](docs/) - 详细功能说明和技术文档
- [项目状态](PROJECT_STATUS.md) - 当前开发状态
- [更新日志](CHANGELOG.md) - 版本更新记录

## 🔧 故障排除

### 常见问题

**连接失败**:
- 检查Redis服务是否运行
- 验证主机地址和端口
- 确认认证信息正确

**SSH隧道问题**:
- 验证SSH服务器可访问
- 检查SSH认证信息
- 确认私钥格式正确

**界面问题**:
- 确保Python支持tkinter
- 在macOS上使用系统Python或正确配置的Python

### 获取帮助
1. 运行 `python test.py` 检查环境
2. 查看 [docs/](docs/) 目录下的详细文档
3. 提交Issue报告问题

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情

---

<div align="center">

**RedisM** - 让Redis管理变得简单高效

Made with ❤️ for Redis developers

</div>