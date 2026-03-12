# 文本搜索 "Find Previous" 功能修复 - 完整版

## 问题描述
在 RedisM 的所有文本框搜索功能中，点击 "Find Next" 按钮正常工作，但点击 "Find Previous" 按钮没有反应。

## 影响范围
搜索功能存在于以下文件中：
1. **`src/ui/key_manager.py`** - 键值编辑器的搜索功能
2. **`src/dialogs/search_mixin.py`** - 通用搜索混入类，被多个对话框使用
3. **`src/dialogs/simple_dialog.py`** - 继承了 SearchMixin，用于各种编辑对话框

## 根本原因分析

### 核心问题：光标位置管理错误
原代码在找到匹配文本后，无论是向前还是向后搜索，都将光标移到匹配文本的**末尾**：
```python
# 错误的做法
self.text_widget.mark_set(tk.INSERT, end_pos)  # 总是移到末尾
```

这导致：
- **Find Next** 正常：光标在末尾，下次搜索从末尾向后找，符合预期
- **Find Previous** 失败：光标在末尾，下次向后搜索时，会再次找到同一个匹配

### 次要问题：搜索起始位置处理不当
向后搜索时，没有正确处理选中文本的情况，导致重复找到同一个结果。

## 修复方案

### 1. 修复 `src/ui/key_manager.py` 中的 `_find_text` 方法

**关键修复点**：
```python
# 根据搜索方向设置光标位置
if forward:
    # 向前搜索：光标移到匹配文本后面，便于下次继续向前搜索
    self.value_text.mark_set(tk.INSERT, end_pos)
else:
    # 向后搜索：光标移到匹配文本前面，便于下次继续向后搜索
    self.value_text.mark_set(tk.INSERT, pos)
```

**改进的向后搜索起始位置处理**：
```python
# 如果当前位置有选中的文本，从选中文本的开始位置搜索
try:
    sel_start = self.value_text.index(tk.SEL_FIRST)
    sel_end = self.value_text.index(tk.SEL_LAST)
    # 如果光标在选中文本的末尾，从选中文本的开始位置搜索
    if current_pos == sel_end:
        search_start = sel_start
except tk.TclError:
    # 没有选中文本，使用当前光标位置
    pass
```

### 2. 修复 `src/dialogs/search_mixin.py` 中的 `_find_in_text_widget` 方法

应用了相同的修复逻辑：
- 区分向前和向后搜索的光标位置
- 添加文本选中功能
- 改进搜索起始位置处理

### 3. 添加文本选中功能

**新增代码**：
```python
# 选中找到的文本
text_widget.tag_remove(tk.SEL, "1.0", tk.END)
text_widget.tag_add(tk.SEL, pos, end_pos)
```

这样做的好处：
- 用户可以清楚看到当前匹配的文本（蓝色选中 + 黄色高亮）
- 下次搜索时可以基于选中文本的位置进行

## 修复效果对比

### 修复前的行为
1. 用户搜索 "test"
2. 点击 "Find Next" - 找到第一个匹配 ✅
3. 点击 "Find Next" - 找到第二个匹配 ✅
4. 点击 "Find Previous" - 没反应或找到同一个匹配 ❌

### 修复后的行为
1. 用户搜索 "test"
2. 点击 "Find Next" - 找到第一个匹配，文本被选中 ✅
3. 点击 "Find Next" - 找到第二个匹配，文本被选中 ✅
4. 点击 "Find Previous" - 返回第一个匹配，文本被选中 ✅
5. 点击 "Find Previous" - 循环到最后一个匹配 ✅

## 用户体验改进

1. **视觉反馈增强**：
   - 匹配的文本现在会被选中（蓝色高亮）
   - 同时保持黄色背景高亮
   - 双重高亮让用户更容易看到当前匹配

2. **正确的导航**：
   - 向前和向后搜索都能正确工作
   - 不会重复找到同一个匹配

3. **循环搜索**：
   - 到达文件末尾时自动循环到开头
   - 到达文件开头时自动循环到末尾

4. **状态提示**：
   - 显示 "Search wrapped to beginning/end" 提示
   - 显示匹配位置信息

## 测试方法

### 使用测试脚本
运行提供的测试脚本：
```bash
python3 test_search_fix.py
```

### 手动测试步骤
1. **基本测试**：
   - 在任意文本框中输入重复文本（如 "test test test"）
   - 搜索 "test"
   - 连续点击 "Find Next" 验证向前搜索
   - 连续点击 "Find Previous" 验证向后搜索

2. **边界测试**：
   - 搜索到最后一个匹配后，点击 "Find Next" 验证循环到开头
   - 搜索到第一个匹配后，点击 "Find Previous" 验证循环到末尾

3. **快捷键测试**：
   - 按 Enter 键验证向前搜索
   - 按 Shift+Enter 验证向后搜索

4. **多对话框测试**：
   - 在键值编辑器中测试搜索
   - 在各种编辑对话框中测试搜索
   - 确保所有搜索功能都正常工作

## 技术细节

### Tkinter Text Widget 搜索 API 的正确使用

```python
# 向前搜索
text.search(pattern, start_index, end_index, nocase=True)

# 向后搜索 - 关键是正确设置起始位置
text.search(pattern, start_index, end_index, backwards=True, nocase=True)
```

### 光标和选择管理的最佳实践

```python
# 获取光标位置
current_pos = text.index(tk.INSERT)

# 区分搜索方向设置光标位置
if forward:
    text.mark_set(tk.INSERT, end_pos)  # 向前搜索：光标在末尾
else:
    text.mark_set(tk.INSERT, pos)      # 向后搜索：光标在开头

# 选中文本提供视觉反馈
text.tag_remove(tk.SEL, "1.0", tk.END)
text.tag_add(tk.SEL, start, end)
```

## 相关文件

- `src/ui/key_manager.py` - 键值编辑器搜索功能
- `src/dialogs/search_mixin.py` - 通用搜索混入类
- `src/dialogs/simple_dialog.py` - 使用搜索混入的对话框基类
- `test_search_fix.py` - 搜索功能测试脚本

## 总结

通过这次修复，RedisM 的所有文本搜索功能现在都能正常工作：

1. **Find Next** 和 **Find Previous** 都能正确导航
2. **循环搜索** 在到达边界时自动换行
3. **视觉反馈** 通过双重高亮增强用户体验
4. **快捷键支持** Enter 和 Shift+Enter 正常工作
5. **统一体验** 所有对话框和编辑器的搜索行为一致

这个修复解决了一个影响用户体验的重要问题，让文本搜索功能变得真正可用。