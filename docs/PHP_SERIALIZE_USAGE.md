# PHP Serialize 功能使用说明

## 功能概述

RedisM v1.1.2 新增了 PHP 序列化数据的格式化和压缩功能，支持在所有值编辑对话框中使用。

## 按钮说明

### Format PHP 按钮
- **功能**: 将 PHP 序列化数据解析并显示为可读的 JSON 格式
- **输入**: PHP serialize 格式的字符串
- **输出**: 格式化的 JSON（带语法高亮）

### Minify PHP 按钮
- **功能**: 将数据压缩为 PHP 序列化格式
- **智能处理**:
  - 如果当前是 JSON 格式 → 转换为 PHP serialize 格式
  - 如果当前是 PHP serialize 格式 → 重新序列化（压缩）

## 使用场景

### 场景 1: 查看 PHP 序列化数据

1. 从 Redis 中读取到 PHP 序列化的值：
   ```
   a:2:{s:4:"name";s:4:"test";s:3:"age";i:25;}
   ```

2. 点击 **Format PHP** 按钮，显示为可读的 JSON：
   ```json
   {
     "name": "test",
     "age": 25
   }
   ```

### 场景 2: 编辑并保存为 PHP 格式

1. 点击 **Format PHP** 查看数据（JSON 格式）
2. 编辑 JSON 数据
3. 点击 **Minify PHP** 转换回 PHP 序列化格式
4. 保存到 Redis

### 场景 3: 压缩 PHP 序列化数据

如果你有一个带空格的 PHP 序列化字符串，可以直接点击 **Minify PHP** 进行压缩。

## 工作流示例

### 示例 1: 完整的编辑流程

```
原始数据 (Redis中):
a:2:{s:4:"name";s:4:"test";s:3:"age";i:25;}

↓ 点击 "Format PHP"

格式化显示:
{
  "name": "test",
  "age": 25
}

↓ 编辑数据（例如修改 age）

{
  "name": "test",
  "age": 30
}

↓ 点击 "Minify PHP"

转换为 PHP 格式:
a:2:{s:4:"name";s:4:"test";s:3:"age";i:30;}

↓ 点击 "Save"

保存到 Redis ✓
```

### 示例 2: 查看复杂数据

```
原始 PHP 数据:
a:2:{s:4:"user";a:2:{s:2:"id";i:1;s:4:"name";s:4:"John";}s:5:"roles";a:2:{i:0;s:5:"admin";i:1;s:4:"user";}}

↓ 点击 "Format PHP"

格式化显示:
{
  "user": {
    "id": 1,
    "name": "John"
  },
  "roles": {
    "0": "admin",
    "1": "user"
  }
}
```

## 支持的数据类型

### PHP 类型 → JSON 类型映射

| PHP 类型 | JSON 类型 | 示例 |
|---------|----------|------|
| string | string | `s:4:"test"` → `"test"` |
| integer | number | `i:25;` → `25` |
| double | number | `d:3.14;` → `3.14` |
| boolean | boolean | `b:1;` → `true` |
| array | object/array | `a:2:{...}` → `{...}` 或 `[...]` |
| null | null | `N;` → `null` |

### 注意事项

1. **PHP 数组的特殊性**:
   - PHP 的数字索引数组在转换时可能显示为对象
   - 例如: `a:2:{i:0;s:5:"admin";i:1;s:4:"user";}` 
   - 会显示为: `{"0": "admin", "1": "user"}`

2. **字符编码**:
   - 支持 UTF-8 编码
   - 特殊字符会正确处理

3. **数据完整性**:
   - Format PHP → Minify PHP 往返转换保持数据完整性
   - 可以安全地编辑和保存

## 错误处理

### 常见错误及解决方案

#### 错误 1: "无法解析 PHP 序列化数据"
**原因**: 输入的不是有效的 PHP serialize 格式
**解决**: 
- 检查数据格式是否正确
- 确保数据完整（没有被截断）
- 尝试使用 Format JSON 按钮（可能是 JSON 格式）

#### 错误 2: "无法解析数据格式"
**原因**: 数据既不是 JSON 也不是 PHP serialize 格式
**解决**: 
- 检查数据来源
- 确认数据类型
- 可能需要手动编辑

## 可用位置

PHP Serialize 功能在以下对话框中可用：

- ✅ String 值编辑器（主界面）
- ✅ Hash 字段编辑对话框
- ✅ Hash 字段添加对话框
- ✅ Set 成员编辑对话框
- ✅ Set 成员添加对话框
- ✅ List 元素编辑对话框
- ✅ ZSet 成员编辑对话框
- ✅ ZSet 成员添加对话框
- ✅ 添加新键对话框（String 类型）

## 快捷键

- **Format JSON**: 无快捷键（点击按钮）
- **Minify JSON**: 无快捷键（点击按钮）
- **Format PHP**: 无快捷键（点击按钮）
- **Minify PHP**: 无快捷键（点击按钮）

## 技术细节

### 使用的库
- `phpserialize>=1.3` - Python 的 PHP 序列化库

### 实现原理
1. **Format PHP**: 
   - 使用 `phpserialize.loads()` 解析 PHP 数据
   - 转换为 Python 对象
   - 使用 `json.dumps()` 格式化为 JSON

2. **Minify PHP**:
   - 智能检测输入格式（JSON 或 PHP）
   - JSON → 转换为 Python 对象 → PHP serialize
   - PHP → 重新序列化（自动压缩）

## 更新日志

### v1.1.2 (2025-01-19)
- ✨ 新增 PHP Serialize 格式化功能
- ✨ 新增 PHP Serialize 压缩功能
- 🔧 智能格式检测（JSON/PHP）
- 🔧 友好的错误提示
- 🔧 支持往返转换（Format ↔ Minify）

## 反馈

如果遇到问题或有建议，请提供：
1. 操作步骤
2. 输入的数据
3. 错误信息
4. 期望的结果
