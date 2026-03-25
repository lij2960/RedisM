# String 类型 Key 保存按钮消失问题诊断

## 问题描述
在查看 string 类型的 key 时，Update、Delete、Refresh 按钮没有显示。

## 代码分析

### 布局结构
在 `_show_key_details` 方法中，界面分为 4 个区域：
- **第 0 行**：键信息（固定高度）
- **第 1 行**：查询框架（固定高度）
- **第 2 行**：值编辑区域（可扩展，weight=1）
- **第 3 行**：操作按钮（固定高度）

### 按钮创建代码
```python
def _create_action_buttons(self, key, key_type):
    """创建操作按钮"""
    btn_section = self._create_fixed_section(3)  # 第3行
    btn_frame = ttk.Frame(btn_section)
    btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    
    ttk.Button(btn_frame, text="Update", 
              command=lambda: self._update_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(btn_frame, text="Delete", 
              command=lambda: self._delete_key(key)).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(btn_frame, text="Refresh", 
              command=lambda: self.load_key_details(key)).pack(side=tk.LEFT)
```

## 可能的原因

### 1. 值区域过度扩展
第 2 行的值编辑区域设置了 `weight=1`，可能占据了所有可用空间，将第 3 行的按钮推到了视图外。

### 2. 父容器高度不足
`key_details_frame` 的高度可能不足以容纳所有 4 行内容。

### 3. Grid 配置问题
`_create_fixed_section(3)` 创建的 section 可能没有正确显示。

## 解决方案

### 方案 1：确保按钮区域可见
修改 `_create_action_buttons` 方法，确保按钮区域始终可见：

```python
def _create_action_buttons(self, key, key_type):
    """创建操作按钮"""
    btn_section = self._create_fixed_section(3)
    btn_frame = ttk.Frame(btn_section)
    btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=10)  # 增加 pady
    
    # 确保按钮框架有最小高度
    btn_frame.grid_propagate(True)
    
    ttk.Button(btn_frame, text="Update", 
              command=lambda: self._update_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(btn_frame, text="Delete", 
              command=lambda: self._delete_key(key)).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(btn_frame, text="Refresh", 
              command=lambda: self.load_key_details(key)).pack(side=tk.LEFT)
```

### 方案 2：调整值区域的最大高度
限制值编辑区域的扩展，确保按钮区域有空间：

```python
# 在 _show_text_value 或 _show_structured_value 中
# 设置值区域的最大高度
value_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
# 不要让值区域占据所有空间
```

### 方案 3：使用 pack 而不是 grid
将操作按钮改为使用 pack 布局，确保它们始终在底部：

```python
def _create_action_buttons(self, key, key_type):
    """创建操作按钮"""
    # 使用 pack 而不是 grid
    btn_frame = ttk.Frame(self.key_details_frame)
    btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)
    
    ttk.Button(btn_frame, text="Update", 
              command=lambda: self._update_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(btn_frame, text="Delete", 
              command=lambda: self._delete_key(key)).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Button(btn_frame, text="Refresh", 
              command=lambda: self.load_key_details(key)).pack(side=tk.LEFT)
```

## 测试步骤

1. 打开 RedisM
2. 连接到 Redis 服务器
3. 选择一个 string 类型的 key
4. 检查界面底部是否显示 Update、Delete、Refresh 按钮
5. 如果没有显示，尝试调整窗口大小
6. 检查是否可以滚动到按钮位置

## 临时解决方法

如果按钮被推到视图外，用户可以：
1. 调整窗口大小，使其更高
2. 尝试滚动界面（如果有滚动条）
3. 使用键盘快捷键（如果有）

## 需要检查的文件

- `src/ui/key_manager.py` - 主要的键管理器文件
- 特别关注 `_show_key_details`、`_create_action_buttons`、`_show_text_value` 方法