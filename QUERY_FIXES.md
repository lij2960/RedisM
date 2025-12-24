# Query 功能修复说明

## 修复的问题

### 1. Key Manager 窗口 Query 按钮执行指令不正确

**问题描述**：
- Query输入框默认显示key名称
- 用户点击Query按钮时，期望查询该key的值
- 但原来的逻辑会将key名称作为Redis命令执行，导致错误

**修复方案**：
- 当查询内容就是key本身时，直接重新加载key详情
- 改进命令解析逻辑，支持更多Redis命令格式
- 为不同数据类型添加专门的命令支持

**支持的命令**：
- **Hash类型**: `HGET field`, `HKEYS`, `HVALS`, `HGETALL`, `HLEN`
- **List类型**: `LRANGE start end`, `LLEN`, `LINDEX index`
- **Set类型**: `SMEMBERS`, `SCARD`, `SISMEMBER member`
- **ZSet类型**: `ZRANGE start end [WITHSCORES]`, `ZCARD`, `ZSCORE member`
- **通用命令**: `GET`, `TYPE`, `TTL`, `EXISTS`

### 2. Hash Key 的 Get Value 按钮弹窗与双击不一致

**问题描述**：
- "Get Value"按钮显示只读的查询结果窗口
- 双击hash列表行显示可编辑的对话框
- 用户体验不一致

**修复方案**：
- 创建新的 `show_hash_field_dialog` 方法
- 与双击行为使用相同的编辑对话框
- 支持查看、编辑和保存hash字段值

## 技术实现

### execute_key_query 方法改进

```python
def execute_key_query(self, key, key_type):
    """执行键查询"""
    query = self.query_var.get().strip()
    
    # 如果查询内容就是key本身，直接重新加载key详情
    if query == key:
        self.load_key_details(key)
        return
    
    # 智能命令解析
    parts = query.split()
    cmd = parts[0].upper()
    
    # 根据数据类型处理不同命令...
```

### show_hash_field_dialog 方法

```python
def show_hash_field_dialog(self, key, field, value):
    """显示hash字段查看/编辑对话框，与双击行为一致"""
    # 创建与双击一致的编辑对话框
    # 支持JSON格式化
    # 支持保存功能
    # 保存后自动刷新显示
```

## 用户体验改进

### Query 按钮改进
1. **智能查询**：当输入是key名称时，直接显示key详情
2. **简化命令**：支持简化的Redis命令格式（如 `HGET field` 而不需要 `HGET key field`）
3. **更多命令**：支持更多常用的Redis查询命令
4. **错误处理**：提供更友好的错误提示

### Hash Get Value 改进
1. **一致体验**：与双击行为完全一致的编辑对话框
2. **可编辑**：不仅可以查看，还可以直接编辑字段值
3. **JSON支持**：内置JSON格式化和压缩功能
4. **即时保存**：修改后可直接保存到Redis
5. **自动刷新**：保存后自动刷新key详情显示

## 兼容性

- 保持与现有功能的完全兼容
- 不影响其他数据类型的查询功能
- 保留所有原有的编辑和操作功能
- 向后兼容原有的Redis命令格式