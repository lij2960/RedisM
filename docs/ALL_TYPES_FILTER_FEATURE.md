# 所有数据类型过滤功能说明

## 功能概述

为 Redis Manager 的 Key Manager 窗口中的所有结构化数据类型（Hash、List、Set、ZSet）添加了统一的过滤功能，提供一致的用户体验和强大的搜索能力。

## 支持的数据类型

### 1. Hash 类型
- **过滤范围**: 字段名（Field）和值（Value）
- **匹配方式**: 模糊匹配，大小写不敏感
- **示例**: 输入 "user" 可匹配字段名包含 "user" 或值包含 "user" 的项目

### 2. List 类型
- **过滤范围**: 列表值（Value）
- **匹配方式**: 模糊匹配，大小写不敏感
- **示例**: 输入 "test" 可匹配所有包含 "test" 的列表项

### 3. Set 类型
- **过滤范围**: 集合成员值（Value）
- **匹配方式**: 模糊匹配，大小写不敏感
- **示例**: 输入 "item" 可匹配所有包含 "item" 的集合成员

### 4. ZSet 类型
- **过滤范围**: 成员名（Member）和分数（Score）
- **匹配方式**: 模糊匹配，大小写不敏感
- **示例**: 输入 "100" 可匹配分数包含 "100" 或成员名包含 "100" 的项目

## 用户界面

### 统一的操作界面
- **输入框标签**: 
  - Hash: "Hash Key:"
  - List/Set/ZSet: "Filter:"
- **操作按钮**: 统一使用 "Find" 按钮
- **快捷键**: 支持 Enter 键快速执行过滤

### 状态反馈
- **过滤统计**: 显示 "Showing X of Y items (filtered by: 'keyword')"
- **实时更新**: 过滤结果立即在下方列表中显示
- **清空恢复**: 输入为空时自动显示所有数据

## 技术实现

### 数据存储结构
```python
# 为每种数据类型存储原始数据
self.original_hash_data = {}    # Hash类型
self.original_list_data = []    # List类型
self.original_set_data = []     # Set类型
self.original_zset_data = []    # ZSet类型
```

### 数据加载方法
```python
def load_hash_data_to_tree(self, hash_data)    # Hash数据加载
def load_list_data_to_tree(self, list_data)    # List数据加载
def load_set_data_to_tree(self, set_data)      # Set数据加载
def load_zset_data_to_tree(self, zset_data)    # ZSet数据加载
```

### 过滤方法
```python
def filter_hash_data(self, key)                    # Hash过滤
def filter_list_zset_data(self, key, key_type)     # List和ZSet过滤
def filter_set_data(self, key)                     # Set过滤
```

### 统一状态管理
```python
def _update_filter_status(self, filtered_count, total_count, filter_text)
```

## 过滤逻辑示例

### Hash 类型过滤
```python
for field, value in self.original_hash_data.items():
    field_str = str(field).lower()
    value_str = str(value).lower()
    
    if filter_lower in field_str or filter_lower in value_str:
        filtered_data[field] = value
```

### List 类型过滤
```python
for val in self.original_list_data:
    value_str = str(val).lower()
    if filter_lower in value_str:
        filtered_data.append(val)
```

### Set 类型过滤
```python
for val in self.original_set_data:
    value_str = str(val).lower()
    if filter_lower in value_str:
        filtered_data.append(val)
```

### ZSet 类型过滤
```python
for i in range(0, len(self.original_zset_data), 2):
    member = self.original_zset_data[i]
    score = self.original_zset_data[i + 1]
    
    member_str = str(member).lower()
    score_str = str(score).lower()
    
    if filter_lower in member_str or filter_lower in score_str:
        filtered_data.extend([member, score])
```

## 使用场景

### 1. 快速定位数据
- 在大量数据中快速找到特定项目
- 支持部分关键词匹配

### 2. 数据分析
- 过滤出符合条件的数据子集
- 便于数据检查和验证

### 3. 调试和开发
- 快速查找特定的配置项或数据
- 验证数据的存在性和正确性

## 用户体验优势

### 1. 一致性
- 所有数据类型使用相同的操作方式
- 统一的界面布局和交互逻辑

### 2. 直观性
- 过滤结果直接在原位置显示
- 实时的状态反馈和统计信息

### 3. 高效性
- 支持键盘快捷键操作
- 大小写不敏感的智能匹配

### 4. 灵活性
- 支持多种匹配模式
- 空输入时自动恢复全量显示

## 兼容性保证

- **保持原有功能**: 所有编辑、添加、删除功能完全保留
- **不影响性能**: 过滤操作在内存中进行，不影响Redis操作
- **状态管理**: 切换不同key时自动清理过滤状态
- **错误处理**: 提供友好的错误提示和异常处理

## 扩展性

该过滤系统设计具有良好的扩展性：
- 可轻松添加新的数据类型支持
- 可扩展更复杂的过滤条件（如正则表达式）
- 可添加排序和高级搜索功能