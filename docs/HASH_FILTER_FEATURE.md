# Hash 过滤功能说明

## 功能概述

在 Key Manager 窗口中，为 Hash 类型数据添加了过滤功能，将原来的 "Get Value" 按钮改为 "Find" 按钮，支持实时过滤和搜索 Hash 字段。

## 主要改进

### 1. 按钮名称变更
- **原来**: "Get Value" 按钮 → 弹出编辑对话框
- **现在**: "Find" 按钮 → 直接在列表中过滤数据

### 2. 过滤功能
- **模糊匹配**: 支持字段名（Field）和值（Value）的模糊搜索
- **实时过滤**: 过滤结果直接在下方的列表中显示
- **大小写不敏感**: 搜索时忽略大小写
- **全量显示**: 输入为空时显示所有数据

### 3. 用户交互
- **Find 按钮**: 点击执行过滤
- **Enter 键**: 在输入框中按 Enter 键快速执行过滤
- **状态反馈**: 显示过滤结果统计信息

## 技术实现

### 数据存储
```python
# 存储原始hash数据以便过滤
self.original_hash_data = value if isinstance(value, dict) else {}
```

### 过滤逻辑
```python
def filter_hash_data(self, key):
    """过滤hash数据"""
    filter_text = self.struct_query_var.get().strip()
    
    # 模糊匹配字段名和值
    filtered_data = {}
    filter_lower = filter_text.lower()
    
    for field, value in self.original_hash_data.items():
        field_str = str(field).lower()
        value_str = str(value).lower()
        
        if filter_lower in field_str or filter_lower in value_str:
            filtered_data[field] = value
    
    # 更新显示
    self.load_hash_data_to_tree(filtered_data)
```

### 状态显示
```python
# 显示过滤结果统计
self.filter_status_label = ttk.Label(parent_frame, 
    text=f"Showing {filtered_count} of {total_count} items" + 
         (f" (filtered by: '{filter_text}')" if filter_text else ""))
```

## 使用场景

### 1. 快速查找字段
- 输入字段名的部分内容
- 快速定位到相关字段

### 2. 搜索特定值
- 输入值的部分内容
- 找到包含该值的所有字段

### 3. 组合搜索
- 输入关键词
- 同时匹配字段名和值

## 用户体验

### 操作流程
1. 在 "Hash Key" 输入框中输入搜索关键词
2. 点击 "Find" 按钮或按 Enter 键
3. 查看过滤后的结果列表
4. 查看底部的统计信息

### 状态反馈
- **过滤前**: 显示所有 Hash 字段
- **过滤中**: 实时更新列表显示
- **过滤后**: 显示匹配的字段和统计信息
- **清空输入**: 恢复显示所有字段

### 示例
```
输入: "user"
结果: 显示所有字段名或值包含 "user" 的项目
状态: "Showing 3 of 10 items (filtered by: 'user')"
```

## 兼容性

- **保持原有功能**: 双击行仍可编辑字段
- **不影响其他类型**: List、Set、ZSet 类型不受影响
- **状态管理**: 切换不同 key 时自动清理过滤状态
- **错误处理**: 提供友好的错误提示

## 优势

1. **提高效率**: 快速定位目标字段，无需滚动查找
2. **直观显示**: 过滤结果直接在原位置显示，保持操作连贯性
3. **灵活搜索**: 支持字段名和值的双重匹配
4. **即时反馈**: 实时显示过滤结果和统计信息
5. **操作简便**: 支持按钮点击和键盘快捷键