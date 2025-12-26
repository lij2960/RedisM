#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试滚动修复"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from src.dialogs.connection_dialog import ConnectionDialog

def test_scrolling_fix():
    """测试滚动修复"""
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Test Scrolling Fix")
    
    def open_dialog():
        dialog = ConnectionDialog(root)
        result = dialog.show()
        print(f"Dialog result: {result}")
    
    btn = tk.Button(root, text="Open Connection Dialog", command=open_dialog, font=('Arial', 14))
    btn.pack(pady=30)
    
    info_text = """滚动测试说明:

1. 点击按钮打开连接对话框
2. 将鼠标放在对话框内容区域（不是滚动条上）
3. 使用鼠标滚轮上下滚动
4. 验证内容能够正常滚动

如果滚动仍然不工作，请尝试：
- 点击对话框内容区域获得焦点
- 使用触控板滚动（如果是MacBook）
- 检查系统滚轮设置"""
    
    info_label = tk.Label(root, text=info_text, justify=tk.LEFT, font=('Arial', 12))
    info_label.pack(pady=20, padx=20)
    
    root.mainloop()

if __name__ == "__main__":
    print("Testing scrolling fix...")
    test_scrolling_fix()