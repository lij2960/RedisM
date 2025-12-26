# RedisM 项目结构

## 📁 目录结构

```
RedisM/
├── 📄 main.py                     # 应用启动入口
├── 📄 test.py                     # 模块测试脚本
├── 📄 requirements.txt            # Python依赖列表
├── 📄 build_python.sh             # macOS应用构建脚本
├── 📄 README.md                   # 项目说明文档
├── 📄 PROJECT_STATUS.md           # 项目状态和计划
├── 📄 CHANGELOG.md                # 版本更新日志
├── 📄 STRUCTURE.md                # 项目结构说明（本文件）
│
├── 📁 src/                        # 源代码目录
│   ├── 📄 __init__.py
│   ├── 📄 config.py               # 应用配置和常量
│   ├── 📄 main.py                 # 应用主入口
│   │
│   ├── 📁 ui/                     # 用户界面组件
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main_window.py      # 主窗口管理
│   │   ├── 📄 left_panel.py       # 左侧面板（连接、键列表）
│   │   ├── 📄 right_panel.py      # 右侧面板（键管理、CLI）
│   │   ├── 📄 key_manager.py      # 键管理器组件
│   │   ├── 📄 cli_interface.py    # 命令行界面组件
│   │   └── 📄 styles.py           # 统一样式管理
│   │
│   ├── 📁 redis/                  # Redis操作模块
│   │   ├── 📄 __init__.py
│   │   ├── 📄 connection.py       # Redis连接管理
│   │   └── 📄 operations.py       # Redis数据操作
│   │
│   ├── 📁 dialogs/                # 对话框组件
│   │   ├── 📄 __init__.py
│   │   ├── 📄 base_dialog.py      # 基础对话框类
│   │   ├── 📄 connection_dialog.py # 连接配置对话框
│   │   └── 📄 key_dialogs.py      # 键编辑对话框
│   │
│   └── 📁 utils/                  # 工具函数
│       ├── 📄 __init__.py
│       └── 📄 helpers.py          # 辅助函数和工具
│
├── 📁 docs/                       # 文档目录
│   ├── 📄 README.md               # 文档索引
│   ├── 📄 UI_IMPROVEMENTS.md      # UI改进说明
│   ├── 📄 CONNECTION_DIALOG_IMPROVEMENTS.md # 连接对话框改进
│   ├── 📄 ALL_TYPES_FILTER_FEATURE.md # 过滤功能说明
│   ├── 📄 REALTIME_OPERATIONS.md # 实时操作说明
│   └── 📄 ...                     # 其他功能文档
│
├── 📁 build/                      # 构建临时文件（自动生成）
├── 📁 dist/                       # 构建输出目录（自动生成）
└── 📁 venv/                       # Python虚拟环境（可选）
```

## 🔧 核心模块说明

### 启动和配置
- **main.py**: 应用启动入口，包含使用说明
- **src/config.py**: 应用配置、版本信息、UI常量
- **src/main.py**: 应用主逻辑入口

### UI组件模块
- **main_window.py**: 主窗口管理、菜单栏、整体布局
- **left_panel.py**: 连接管理、数据库选择、键搜索和树形显示
- **right_panel.py**: 右侧面板容器，管理键管理器和CLI界面
- **key_manager.py**: 键详情显示、编辑、操作按钮
- **cli_interface.py**: Redis命令行界面、命令补全
- **styles.py**: 统一的样式管理、主题配置

### Redis操作模块
- **connection.py**: Redis连接管理、SSH隧道、自动重连
- **operations.py**: Redis数据操作、CRUD、命令执行

### 对话框模块
- **base_dialog.py**: 基础对话框类、滚动支持、事件处理
- **connection_dialog.py**: 连接配置对话框、SSH设置
- **key_dialogs.py**: 各种键编辑对话框

### 工具模块
- **helpers.py**: JSON处理、端口查找、配置管理等工具函数

## 🎯 模块职责

### 分层架构
```
┌─────────────────┐
│   UI Layer      │  用户界面层
├─────────────────┤
│ Business Layer  │  业务逻辑层
├─────────────────┤
│  Data Layer     │  数据访问层
└─────────────────┘
```

### 依赖关系
- UI组件 → Business Logic → Redis Operations
- 对话框 → UI组件
- 所有模块 → Utils & Config

## 📝 开发指南

### 添加新功能
1. **UI功能**: 在`src/ui/`目录下创建或修改组件
2. **Redis操作**: 在`src/redis/operations.py`中添加方法
3. **对话框**: 继承`BaseDialog`创建新对话框
4. **工具函数**: 在`src/utils/helpers.py`中添加

### 修改现有功能
1. 确定功能所在的模块
2. 修改对应的文件
3. 更新相关的依赖模块
4. 运行测试确保功能正常

### 测试和调试
```bash
# 测试模块结构
python test.py

# 启动应用
python main.py

# 构建应用
./build_python.sh
```

## 🔄 模块化优势

1. **可维护性**: 每个模块职责单一，易于理解和修改
2. **可扩展性**: 新功能可以独立开发，不影响现有功能
3. **可测试性**: 模块可以独立测试，提高代码质量
4. **团队协作**: 不同开发者可以并行开发不同模块
5. **代码复用**: 通用组件可以在多处使用

---

这个结构设计遵循了软件工程的最佳实践，为RedisM的持续发展提供了坚实的基础。