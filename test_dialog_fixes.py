#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试对话框修复"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from src.dialogs.connection_dialog import ConnectionDialog
from src.dialogs.key_dialogs import HashEditDialog

def test_connection_dialog():
    """测试连接对话框"""
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Test Connection Dialog")
    
    def open_dialog():
        dialog = ConnectionDialog(root)
        result = dialog.show()
        print(f"Dialog result: {result}")
    
    btn = tk.Button(root, text="Open Connection Dialog (Test Resizing)", command=open_dialog)
    btn.pack(pady=20)
    
    info_label = tk.Label(root, text="测试说明:\n1. 点击按钮打开连接对话框\n2. 启用SSH隧道\n3. 选择Private Key认证\n4. 验证内容完整显示", 
                         justify=tk.LEFT, font=('Arial', 12))
    info_label.pack(pady=10)
    
    root.mainloop()

def test_key_dialog():
    """测试键编辑对话框"""
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Test Key Dialog")
    
    class MockMainWindow:
        def get_redis_client(self):
            return None
    
    def open_dialog():
        mock_main = MockMainWindow()
        dialog = HashEditDialog(root, "test_key", "test_field", "test_value_with_long_content_to_test_resizing_behavior", mock_main)
        result = dialog.show()
        print(f"Dialog result: {result}")
    
    btn = tk.Button(root, text="Open Hash Edit Dialog (Test Resizing)", command=open_dialog)
    btn.pack(pady=20)
    
    info_label = tk.Label(root, text="测试说明:\n1. 点击按钮打开编辑对话框\n2. 手动拖拽对话框边缘调整大小\n3. 验证文本框自动跟随调整", 
                         justify=tk.LEFT, font=('Arial', 12))
    info_label.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    print("Testing dialog fixes...")
    print("1. Connection Dialog (Size & Layout)")
    print("2. Key Edit Dialog (Auto-Resize)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_connection_dialog()
    elif choice == "2":
        test_key_dialog()
    else:
        print("Invalid choice")