# RedisM v1.1.2 重新打包说明

## 问题原因
打包后应用无法启动的原因是：
1. `phpserialize` 模块没有添加到 PyInstaller 的 `hiddenimports` 列表中
2. 打包脚本没有安装所有必需的依赖

## 已修复的文件
1. ✅ `RedisM.spec` - 添加了 `phpserialize` 到 hiddenimports
2. ✅ `build_python.sh` - 更新为使用 `requirements.txt` 安装所有依赖

## 重新打包步骤

### 1. 清理之前的构建
```bash
rm -rf build dist venv
rm -f RedisM.dmg
```

### 2. 确保所有依赖已安装
```bash
# 如果使用虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt
pip install pyinstaller
```

### 3. 验证依赖安装
```bash
python3 test_imports.py
```
应该看到所有测试通过的消息。

### 4. 重新打包
```bash
# 方法1: 使用打包脚本（推荐）
chmod +x build_python.sh
./build_python.sh

# 方法2: 直接使用 PyInstaller
pyinstaller RedisM.spec
```

### 5. 测试打包后的应用
```bash
# 打开应用
open dist/RedisM.app

# 或者从命令行运行查看错误信息
./dist/RedisM.app/Contents/MacOS/RedisM
```

## 验证清单

打包完成后，请验证以下功能：

- [ ] 应用能够正常启动
- [ ] 能够连接到 Redis 服务器
- [ ] 能够查看和编辑键值
- [ ] JSON 格式化功能正常
- [ ] **PHP Serialize 格式化功能正常** ⭐ 新功能
- [ ] **PHP Serialize 压缩功能正常** ⭐ 新功能

## 测试 PHP Serialize 功能

在应用中测试以下 PHP 序列化数据：

### 测试数据1: 简单数组
```
a:2:{s:4:"name";s:4:"test";s:3:"age";i:25;}
```

点击 "Format PHP" 应该显示：
```json
{
  "name": "test",
  "age": 25
}
```

### 测试数据2: 嵌套数组
```
a:2:{s:4:"user";a:2:{s:2:"id";i:1;s:4:"name";s:4:"John";}s:5:"roles";a:2:{i:0;s:5:"admin";i:1;s:4:"user";}}
```

点击 "Format PHP" 应该显示格式化的 JSON。

## 常见问题

### Q1: 应用启动后立即崩溃
**解决方案**: 
- 检查是否所有依赖都已添加到 `RedisM.spec` 的 `hiddenimports`
- 运行 `./dist/RedisM.app/Contents/MacOS/RedisM` 查看错误信息

### Q2: 提示 "No module named 'phpserialize'"
**解决方案**: 
- 确保 `phpserialize` 已添加到 `RedisM.spec` 的 `hiddenimports` 列表
- 重新运行 `pyinstaller RedisM.spec`

### Q3: PHP Serialize 按钮不工作
**解决方案**: 
- 检查 `src/utils/helpers.py` 中的 PHP 函数是否正确导入
- 检查 `src/dialogs/simple_dialog.py` 中的 PHP 方法是否存在

## 更新日志

### v1.1.2 新增功能
- ✨ 添加 PHP Serialize 格式化支持
- ✨ 添加 PHP Serialize 压缩支持
- ✨ 所有编辑对话框都支持 PHP Serialize 操作
- 🔧 修复打包配置，确保 phpserialize 模块正确打包

## 技术细节

### 新增的 hiddenimports
```python
'phpserialize',                    # PHP 序列化库
'src.dialogs.simple_dialog',       # 简单对话框基类
'src.dialogs.search_mixin',        # 搜索混入类
```

### 依赖版本
- `phpserialize>=1.3` - PHP 序列化支持
- `redis==5.0.1` - Redis 客户端
- `paramiko==3.4.0` - SSH 连接
- `Pillow>=10.0.0` - 图像处理
- `pyinstaller>=6.0.0` - 应用打包

## 支持

如果遇到其他问题，请检查：
1. Python 版本是否为 3.10+
2. 所有依赖是否正确安装
3. PyInstaller 版本是否为 6.0.0+
4. macOS 版本是否支持（建议 macOS 11+）
