# String 类型 Key 保存按钮消失问题修复

## 问题描述
在查看 string 类型的 key 时，界面底部的 Update、Delete、Refresh 按钮没有显示。

## 问题原因

### 布局结构分析
在 `_show_key_details` 方法中，界面使用 grid 布局分为 4 个区域：
- **第 0 行**：键信息（固定高度）
- **第 1 行**：查询框架（固定高度）
- **第 2 行**：值编辑区域（可扩展，weight=1）
- **第 3 行**：操作按钮（固定高度）

### 根本原因
第 2 行的值编辑区域设置了 `weight=1`，使其可以扩展填充所有可用空间。当窗口高度有限时，这个可扩展区域会占据所有空间，将第 3 行的操作按钮推到视图外，导致按钮不可见。

### 代码问题
```python
# 原代码
def _create_action_buttons(self, key, key_type):
    btn_section = self._create_fixed_section(3)
    btn_frame = ttk.Frame(btn_section)
    btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    # 按钮没有设置最小高度，容易被挤出视图
```

## 修复方案

### 修复代码
```python
def _create_action_buttons(self, key, key_type):
    """创建操作按钮 - 确保始终可见"""
    btn_section = self._create_fixed_section(3)
    
    # 创建按钮容器，设置最小高度确保可见
    btn_frame = ttk.Frame(btn_section, height=50)
    btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=10)
    btn_frame.pack_propagate(False)  # 防止子组件改变容器大小
    
    # 创建按钮
    ttk.Button(btn_frame, text="Update", 
              command=lambda: self._update_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5), pady=10)
    ttk.Button(btn_frame, text="Delete", 
              command=lambda: self._delete_key(key)).pack(side=tk.LEFT, padx=(0, 5), pady=10)
    ttk.Button(btn_frame, text="Refresh", 
              command=lambda: self.load_key_details(key)).pack(side=tk.LEFT, pady=10)
```

### 关键修复点

1. **设置固定高度**：
   ```python
   btn_frame = ttk.Frame(btn_section, height=50)
   ```
   为按钮容器设置 50 像素的固定高度，确保有足够空间显示按钮。

2. **禁用自动调整**：
   ```python
   btn_frame.pack_propagate(False)
   ```
   防止子组件（按钮）改变容器大小，保持固定高度。

3. **增加内边距**：
   ```python
   btn_frame.grid(..., pady=10)
   ```
   增加垂直内边距，使按钮区域更明显。

4. **按钮内边距**：
   ```python
   .pack(side=tk.LEFT, padx=(0, 5), pady=10)
   ```
   为每个按钮添加垂直内边距，确保按钮在容器中居中显示。

## 修复效果

### 修复前
- 操作按钮可能被值编辑区域挤到视图外
- 用户无法看到 Update、Delete、Refresh 按钮
- 需要调整窗口大小才能看到按钮

### 修复后
- 操作按钮始终可见，固定在界面底部
- 按钮区域有 50 像素的固定高度
- 即使窗口很小，按钮也不会被挤出视图
- 更好的视觉间距和布局

## 影响范围

这个修复影响所有类型的 key：
- ✅ string 类型
- ✅ hash 类型
- ✅ list 类型
- ✅ set 类型
- ✅ zset 类型

所有类型的 key 都使用相同的 `_create_action_buttons` 方法，因此修复对所有类型都有效。

## 测试建议

1. **基本测试**：
   - 打开 RedisM
   - 连接到 Redis 服务器
   - 选择不同类型的 key（string、hash、list、set、zset）
   - 验证每种类型都显示 Update、Delete、Refresh 按钮

2. **窗口大小测试**：
   - 调整窗口大小，使其变小
   - 验证按钮始终可见
   - 验证按钮不会被值编辑区域覆盖

3. **功能测试**：
   - 点击 Update 按钮，验证可以保存修改
   - 点击 Delete 按钮，验证可以删除 key
   - 点击 Refresh 按钮，验证可以刷新数据

## 相关文件

- `src/ui/key_manager.py` - 包含 `_create_action_buttons` 方法的修复

## 技术细节

### Tkinter Frame 高度控制

```python
# 设置固定高度
frame = ttk.Frame(parent, height=50)

# 禁用自动调整大小
frame.pack_propagate(False)  # 对于 pack 布局
frame.grid_propagate(False)  # 对于 grid 布局
```

### Grid 布局权重

```python
# weight=0: 固定大小，不扩展
# weight=1: 可扩展，占据剩余空间
parent.grid_rowconfigure(row, weight=0)  # 固定行
parent.grid_rowconfigure(row, weight=1)  # 可扩展行
```

## 总结

通过为按钮容器设置固定高度并禁用自动调整，确保操作按钮始终可见，不会被可扩展的值编辑区域挤出视图。这个修复提高了用户体验，使界面更加稳定和可预测。