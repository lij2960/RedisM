# RedisM v1.1.3 发布说明

## 🎉 版本发布

**发布日期**: 2025-01-19  
**版本号**: v1.1.3  
**类型**: 维护版本

---

## 📋 本次更新概览

v1.1.3 是一个维护版本，主要专注于项目清理、文档完善和结构优化。

### 🧹 项目清理

#### 删除的文件
- ❌ `test_imports.py` - 临时导入测试脚本
- ❌ `test_php_serialize.py` - PHP序列化功能测试脚本
- ❌ `quick_rebuild.sh` - 快速重建脚本（保留主要的build_python.sh）

#### 文档重组
- ✅ `PHP_SERIALIZE_USAGE.md` → `docs/PHP_SERIALIZE_USAGE.md`
- ✅ `REBUILD_INSTRUCTIONS.md` → `docs/REBUILD_INSTRUCTIONS.md`
- ✅ 所有文档集中到 `docs/` 目录

### 📚 文档完善

#### 主README更新
- ✅ 更新版本号到 v1.1.3
- ✅ 添加 PHP Serialize 功能完整文档
- ✅ 更新功能特性列表，包含所有 v1.1.x 改进
- ✅ 添加详细的 PHP Serialize 使用示例
- ✅ 完善快速开始指南和安装说明
- ✅ 增强故障排除部分
- ✅ 更新项目结构说明
- ✅ 添加技术栈中的 phpserialize 库

#### docs/README更新
- ✅ 更新为 v1.1.3 版本
- ✅ 添加文档导航链接
- ✅ 完善功能对比表格
- ✅ 更新版本历史
- ✅ 添加 PHP Serialize 功能说明
- ✅ 改进使用建议和故障排除

#### CHANGELOG更新
- ✅ 添加 v1.1.3 版本记录
- ✅ 详细记录项目清理内容
- ✅ 记录文档完善工作
- ✅ 记录构建流程改进

### 🛠️ 构建优化

- ✅ 保留主要构建脚本 `build_python.sh`
- ✅ 更新文档引用路径
- ✅ 清理临时构建产物

---

## 📊 当前项目结构

```
RedisM/
├── src/                    # 源代码
│   ├── config.py          # v1.1.3
│   ├── dialogs/           # 对话框组件
│   ├── redis/             # Redis操作
│   ├── ui/                # 用户界面
│   └── utils/             # 工具函数
├── docs/                  # 📚 文档目录
│   ├── README.md          # 文档中心
│   ├── PHP_SERIALIZE_USAGE.md      # PHP序列化指南
│   └── REBUILD_INSTRUCTIONS.md     # 打包指南
├── main.py               # 程序入口
├── requirements.txt      # 依赖列表
├── RedisM.spec          # 打包配置
├── build_python.sh      # 构建脚本
├── CHANGELOG.md         # 更新日志
└── README.md            # 项目说明
```

---

## 🎯 完整功能列表

### v1.1.x 系列功能

#### v1.1.0 - 数据库一致性和UI增强
- ✅ 数据库切换一致性修复
- ✅ 自适应对话框完善
- ✅ 密码安全认证
- ✅ JSON语法高亮

#### v1.1.1 - 连接稳定性
- ✅ 异步重连机制
- ✅ 连接超时设置
- ✅ 错误恢复改进

#### v1.1.2 - PHP Serialize支持
- ✅ Format PHP 按钮
- ✅ Minify PHP 按钮
- ✅ 智能格式检测
- ✅ 往返转换支持

#### v1.1.3 - 项目维护
- ✅ 项目清理
- ✅ 文档完善
- ✅ 结构优化

---

## 📦 依赖列表

```
redis==5.0.1          # Redis客户端
paramiko==3.4.0       # SSH支持
phpserialize>=1.3     # PHP序列化
Pillow>=10.0.0        # 图像处理
pyinstaller>=6.0.0    # 应用打包
```

---

## 🚀 升级指南

### 从 v1.1.2 升级到 v1.1.3

1. **拉取最新代码**
   ```bash
   git pull origin main
   ```

2. **无需更新依赖**
   - v1.1.3 没有新增依赖
   - 现有依赖保持不变

3. **重新打包**（如果需要）
   ```bash
   ./build_python.sh
   ```

4. **查看新文档**
   - 阅读更新后的 README.md
   - 查看 docs/ 目录中的专题文档

### 从更早版本升级

如果从 v1.1.1 或更早版本升级：

1. **更新依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **重新打包**
   ```bash
   ./build_python.sh
   ```

3. **测试新功能**
   - 测试 PHP Serialize 功能
   - 验证数据库一致性
   - 检查连接稳定性

---

## 🔍 测试清单

### 基本功能测试
- [ ] 应用正常启动
- [ ] 连接 Redis 服务器
- [ ] 切换数据库
- [ ] 创建/编辑/删除键

### v1.1.x 功能测试
- [ ] 数据库操作保持一致性
- [ ] 对话框自适应调整
- [ ] 密码查看需要认证
- [ ] JSON 语法高亮正常
- [ ] 连接断开自动重连
- [ ] PHP Serialize 格式化
- [ ] PHP Serialize 压缩

### 文档测试
- [ ] README 链接正常
- [ ] 文档内容准确
- [ ] 示例代码可用
- [ ] 故障排除有效

---

## 📝 已知问题

### 无重大问题

v1.1.3 是一个稳定的维护版本，没有已知的重大问题。

### 注意事项

1. **PHP 数组转换**: PHP 的数字索引数组在转换为 JSON 时可能显示为对象
2. **系统认证**: 密码查看功能需要 macOS 系统认证支持
3. **连接超时**: 默认 5 秒超时，某些慢速网络可能需要调整

---

## 🤝 贡献者

感谢所有为 RedisM v1.1.3 做出贡献的开发者和用户！

### 本版本贡献
- 项目清理和文档完善
- 用户反馈和问题报告
- 功能测试和验证

---

## 📞 获取支持

### 文档资源
- **主文档**: [README.md](README.md)
- **文档中心**: [docs/README.md](docs/README.md)
- **PHP 指南**: [docs/PHP_SERIALIZE_USAGE.md](docs/PHP_SERIALIZE_USAGE.md)
- **打包指南**: [docs/REBUILD_INSTRUCTIONS.md](docs/REBUILD_INSTRUCTIONS.md)
- **更新日志**: [CHANGELOG.md](CHANGELOG.md)

### 社区支持
- **GitHub Issues**: 报告问题和建议
- **GitHub Discussions**: 社区讨论
- **Pull Requests**: 代码贡献

---

## 🎊 下一步计划

### v1.2.0 规划（待定）
- 更多数据类型支持
- 性能优化
- 更多导入/导出格式
- 国际化支持

---

<div align="center">

**RedisM v1.1.3**

让 Redis 管理变得简单而优雅 ✨

感谢使用 RedisM！

</div>
