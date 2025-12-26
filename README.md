# RedisM

<div align="center">

![RedisM Logo](icon_placeholder.txt)

**现代化的Redis管理工具**

[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://github.com/your-repo/RedisM)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
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
- **批量操作**: 支持批量更新和删除
- **数据过滤**: 所有数据类型的实时搜索和过滤

### 🎨 用户界面
- **现代化设计**: 符合macOS设计规范的原生界面
- **树形显示**: 键名按分隔符自动分组显示
- **JSON支持**: 内置JSON格式化和验证
- **响应式布局**: 自适应窗口大小的界面布局

### 💻 命令行界面
- **内置CLI**: 完整的Redis命令行界面
- **命令补全**: 智能命令提示和自动补全
- **历史记录**: 命令执行历史和结果显示
- **语法高亮**: 清晰的命令和结果显示

## 🚀 快速开始

### 系统要求
- macOS 10.14+
- Python 3.8+
- 支持tkinter的Python环境

### 安装方式

#### 方式一：直接运行（推荐）
```bash
# 1. 克隆项目
git clone https://github.com/your-repo/RedisM.git
cd RedisM

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python main.py
```

#### 方式二：构建应用包
```bash
# 构建macOS应用包
./build_python.sh

# 安装到Applications文件夹
cp -r dist/RedisM.app /Applications/
```

### 首次使用
1. 启动RedisM
2. 点击"Add"添加Redis连接
3. 配置连接信息（主机、端口、认证等）
4. 可选：配置SSH隧道
5. 点击"Test Connection"测试连接
6. 保存并连接

## 📖 使用指南

### 连接配置

#### 基本连接
- **连接名称**: 为连接起一个易识别的名称
- **Redis主机**: Redis服务器地址
- **端口**: Redis端口（默认6379）
- **用户名/密码**: Redis认证信息

#### SSH隧道配置
当Redis服务器在内网或需要通过跳板机访问时：

1. 勾选"Enable SSH Tunnel"
2. 配置SSH服务器信息
3. 选择认证方式：
   - **密码认证**: 输入SSH密码
   - **私钥认证**: 选择私钥文件或粘贴私钥内容

### 数据操作

#### 浏览数据
- **键搜索**: 在搜索框输入模式（支持通配符）
- **分组显示**: 键名按分隔符自动分组
- **展开/收起**: 点击文件夹图标展开或收起分组

#### 编辑数据
- **查看详情**: 单击键名查看详情
- **编辑值**: 双击表格行进行编辑
- **添加项**: 点击"Add Item"添加新项
- **删除项**: 选中后删除

#### 过滤功能
- **Hash过滤**: 按字段名或值过滤
- **List/Set过滤**: 按值内容过滤
- **ZSet过滤**: 按成员名或分数过滤

### 命令行使用
1. 切换到"Command Line"标签页
2. 在命令行输入Redis命令
3. 按Enter执行命令
4. 查看执行结果

支持的命令包括但不限于：
```redis
GET key
SET key value
HGETALL hash_key
LRANGE list_key 0 -1
SMEMBERS set_key
ZRANGE zset_key 0 -1 WITHSCORES
```

## 🛠 开发文档

### 项目结构
```
RedisM/
├── src/                    # 源代码
│   ├── config.py          # 配置文件
│   ├── main.py            # 应用入口
│   ├── ui/                # UI组件
│   ├── redis/             # Redis操作
│   ├── dialogs/           # 对话框
│   └── utils/             # 工具函数
├── docs/                  # 文档
├── main.py                # 启动文件
├── test.py                # 测试脚本
└── requirements.txt       # 依赖列表
```

### 开发环境设置
```bash
# 1. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装开发依赖
pip install -r requirements.txt

# 3. 运行测试
python test.py

# 4. 启动开发版本
python main.py
```

### 添加新功能
1. **UI组件**: 在`src/ui/`目录下创建新组件
2. **Redis操作**: 在`src/redis/operations.py`中添加新方法
3. **对话框**: 继承`BaseDialog`类创建新对话框
4. **工具函数**: 在`src/utils/helpers.py`中添加

### 代码规范
- 使用Python 3.8+语法
- 遵循PEP 8代码风格
- 添加类型注释
- 编写文档字符串

## 📚 文档

- [项目状态](PROJECT_STATUS.md) - 当前开发状态和计划
- [更新日志](CHANGELOG.md) - 版本更新记录
- [功能文档](docs/) - 详细功能说明文档

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情

## 🙏 致谢

- [Redis](https://redis.io/) - 优秀的内存数据库
- [Paramiko](https://www.paramiko.org/) - SSH连接库
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - Python GUI框架

## 📞 支持

如果遇到问题或有建议：

1. 查看[文档](docs/)
2. 运行`python test.py`检查环境
3. 提交[Issue](https://github.com/your-repo/RedisM/issues)

---

<div align="center">

**RedisM** - 让Redis管理变得简单高效

Made with ❤️ by RedisM Team

</div>