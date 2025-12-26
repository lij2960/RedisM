# UI对话框修复文档

## 修复的问题

### 1. 连接对话框文本框宽度不一致

**问题描述：**
在SSH认证方式中，选择private key后，整个输入区域会拉长，与password模式的宽度不一致。

**根本原因：**
- 私钥内容的Text组件使用了`fill=tk.X, expand=True`导致布局扩展
- 两种认证方式的pack配置不一致

**解决方案：**
1. 将私钥内容Text组件的宽度固定为40字符
2. 移除`expand=True`参数，只使用`pack(side=tk.LEFT)`
3. 确保两种认证方式使用相同的`pack(fill=tk.X)`配置

**修改的文件：**
- `src/dialogs/connection_dialog.py`

### 2. 连接对话框默认尺寸不足

**问题描述：**
选择private key时，默认框体大小展示不完整，私钥内容区域被截断。

**解决方案：**
将连接对话框的默认尺寸从 `600x800` 增加到 `650x900`，确保私钥认证模式下所有内容都能完整显示。

**修改的文件：**
- `src/dialogs/connection_dialog.py`

**具体修改：**
```python
# 修改前
super().__init__(parent, title, "600x800")

# 修改后
super().__init__(parent, title, "650x900")
```

### 3. 键编辑对话框闪烁和文本框超出问题

**问题描述：**
- 键编辑对话框弹出时会闪动一下
- 文本输入框超出默认框体大小

**根本原因：**
- 对话框创建后立即显示，然后再调用`update_idletasks()`进行居中，导致闪烁
- Text组件的width设置过大，超出了对话框的默认宽度

**解决方案：**

#### 3.1 修复对话框闪烁
1. 在对话框创建后立即隐藏（`withdraw()`）
2. 预先计算居中位置，避免使用`update_idletasks()`
3. 设置完所有属性后再显示（`deiconify()`）

**修改的文件：**
- `src/dialogs/base_dialog.py`

#### 3.2 修复文本框尺寸
移除所有编辑对话框中Text组件的固定宽度，让它们能够自动适应对话框大小。

**修改的文件：**
- `src/dialogs/key_dialogs.py`

### 4. 键编辑对话框自动调整大小

**问题描述：**
编辑key时，输入框无法随着框体手动调整大小自动跟随调整。

**解决方案：**
1. 启用对话框可调整大小功能（`resizable(True, True)`）
2. 配置Canvas自动调整内容宽度
3. 移除Text组件的固定宽度限制，使用`fill=tk.BOTH, expand=True`

**修改的文件：**
- `src/dialogs/base_dialog.py` - 启用调整大小和Canvas自适应
- `src/dialogs/key_dialogs.py` - 移除Text组件固定宽度

**具体修改：**

#### 基础对话框支持调整大小
```python
# 在_setup_geometry方法中添加
self.dialog.resizable(True, True)

# 在_create_scrollable_frame方法中添加Canvas自适应
def _on_canvas_configure(event):
    canvas_width = event.width
    self.canvas.itemconfig(self.canvas.find_all()[0], width=canvas_width)

self.canvas.bind('<Configure>', _on_canvas_configure)
```

#### Text组件自适应宽度
```python
# 修改前 - 固定宽度
self.value_text = tk.Text(text_frame, wrap=tk.WORD, height=20, width=70)

# 修改后 - 自适应宽度
self.value_text = tk.Text(text_frame, wrap=tk.WORD, height=20)
self.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
```

## 测试验证

### 连接对话框测试
1. 打开连接编辑对话框
2. 启用SSH隧道
3. 选择Private Key认证方式
4. 验证所有内容完整显示，无截断
5. 在Password和Private Key之间切换，验证宽度一致

### 键编辑对话框测试
1. 双击任意键值（hash、set、list、zset）
2. 验证对话框打开时没有闪烁
3. 手动拖拽对话框边缘调整大小
4. 验证文本输入框自动跟随调整
5. 验证滚动条正常工作

## 技术细节

### 对话框自适应布局
```python
def _on_canvas_configure(event):
    # 设置scrollable_frame的宽度跟随canvas
    canvas_width = event.width
    self.canvas.itemconfig(self.canvas.find_all()[0], width=canvas_width)
```

### 文本框自适应配置
- 移除固定`width`参数
- 使用`fill=tk.BOTH, expand=True`
- 保持固定`height`以控制垂直尺寸

### 对话框尺寸标准
- **连接对话框**：650x900（增加50px宽度，100px高度）
- **Hash编辑对话框**：900x700（保持不变，但支持调整）
- **其他编辑对话框**：600x400-500（保持不变，但支持调整）

## 预期效果

修复后的对话框应该具有以下特性：
1. **完整显示**：连接对话框在私钥模式下内容完整显示
2. **宽度一致**：不同认证方式下保持相同宽度
3. **无闪烁**：对话框打开时平滑显示
4. **自动调整**：文本框随对话框大小自动调整
5. **用户友好**：支持手动调整对话框大小以适应不同内容需求