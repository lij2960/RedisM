# 编辑功能修复文档

## 修复的问题

### 1. 编辑对话框Redis客户端访问问题

**问题描述：**
- 编辑list key提示：`Failed to update list item: 'NoneType' object has no attribute 'get_redis_client'`
- 编辑set key提示：`Failed to update set value: 'NoneType' object has no attribute 'get_redis_client'`
- 编辑hash key提示：`Failed to update hash field: 'NoneType' object has no attribute 'get_redis_client'`

**根本原因：**
对话框类无法正确找到主窗口实例来获取Redis客户端连接。

**解决方案：**
1. 修改所有编辑对话框的构造函数，直接传入主窗口实例
2. 更新KeyManager中调用对话框的代码，传递main_window参数
3. 简化对话框中的Redis客户端获取逻辑

**修改的文件：**
- `src/dialogs/key_dialogs.py` - 所有对话框类的构造函数和保存方法
- `src/ui/key_manager.py` - 调用对话框的方法

**修改的对话框类：**
- `HashEditDialog` - Hash字段编辑
- `SetEditDialog` - Set成员编辑  
- `ListEditDialog` - List元素编辑
- `ZSetEditDialog` - ZSet成员编辑
- `AddHashDialog` - 添加Hash字段

### 2. 连接对话框文本框宽度不一致问题

**问题描述：**
在SSH认证方式中，选择password和private key后，文本框的宽度不统一，private key的文本框过宽。

**根本原因：**
Text组件使用了`fill=tk.BOTH, expand=True`导致布局不一致。

**解决方案：**
1. 为私钥内容的Text组件设置固定宽度（width=50）
2. 使用`fill=tk.X, expand=True`而不是`fill=tk.BOTH, expand=True`
3. 保持与其他输入框一致的布局行为

**修改的文件：**
- `src/dialogs/connection_dialog.py` - SSH私钥内容输入框配置

## 功能验证

### 编辑功能测试
1. **Hash编辑**：双击hash表格中的任意行，应该能打开编辑对话框并成功保存
2. **Set编辑**：双击set表格中的任意行，应该能打开编辑对话框并成功保存
3. **List编辑**：双击list表格中的任意行，应该能打开编辑对话框并成功保存
4. **ZSet编辑**：双击zset表格中的任意行，应该能打开编辑对话框并成功保存

### 连接对话框测试
1. 打开连接编辑对话框
2. 启用SSH隧道
3. 在认证方式之间切换（Password ↔ Private Key）
4. 验证文本框宽度保持一致

## 技术细节

### 对话框参数传递模式
```python
# 修改前
dialog = HashEditDialog(parent, key, field, value)

# 修改后  
dialog = HashEditDialog(parent, key, field, value, main_window)
```

### Redis客户端获取方式
```python
# 修改前 - 复杂的父窗口查找
def _get_main_window(self):
    parent = self.parent
    while parent and not hasattr(parent, 'get_redis_client'):
        parent = parent.master if hasattr(parent, 'master') else None
    return parent

# 修改后 - 直接使用传入的实例
redis_client = self.main_window.get_redis_client()
```

### 文本框布局配置
```python
# 修改前 - 导致宽度不一致
self.fields['ssh_key_content'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 修改后 - 保持一致的宽度
self.fields['ssh_key_content'] = tk.Text(frame, height=3, width=50, ...)
self.fields['ssh_key_content'].pack(side=tk.LEFT, fill=tk.X, expand=True)
```

## 测试结果

所有修复已通过自动化测试验证：
- ✅ 导入测试通过
- ✅ 对话框构造函数测试通过
- ✅ 参数传递正确
- ✅ 布局配置正确

修复后的应用应该能够正常进行所有类型的键值编辑操作，并且连接对话框的UI布局保持一致。