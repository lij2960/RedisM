#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试连接对话框修复"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import tkinter as tk
from src.dialogs.connection_dialog import ConnectionDialog

def test_connection_dialog_fixes():
    """测试连接对话框修复"""
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Test Connection Dialog Fixes")
    
    def open_new_dialog():
        dialog = ConnectionDialog(root)
        result = dialog.show()
        print(f"New connection result: {result}")
    
    def open_edit_dialog():
        # 模拟一个带SSH私钥的连接配置
        test_connection = {
            'name': 'Test SSH Connection',
            'host': 'localhost',
            'port': 6379,
            'username': '',
            'password': '',
            'max_keys': 0,
            'db_count': 16,
            'use_ssh': True,
            'ssh_host': 'example.com',
            'ssh_port': 22,
            'ssh_user': 'testuser',
            'ssh_password': '',
            'ssh_key': '',
            'ssh_key_content': '''-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAFwAAAAdzc2gtcn
NhAAAAAwEAAQAAAQEA1234567890abcdef...
-----END OPENSSH PRIVATE KEY-----''',
            'ssh_key_passphrase': ''
        }
        
        dialog = ConnectionDialog(root, test_connection)
        result = dialog.show()
        print(f"Edit connection result: {result}")
    
    # 创建测试按钮
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)
    
    new_btn = tk.Button(btn_frame, text="New Connection Dialog", command=open_new_dialog)
    new_btn.pack(side=tk.LEFT, padx=10)
    
    edit_btn = tk.Button(btn_frame, text="Edit SSH Connection Dialog", command=open_edit_dialog)
    edit_btn.pack(side=tk.LEFT, padx=10)
    
    # 测试说明
    info_text = """测试说明:

1. 对话框高度修复测试:
   - 点击按钮打开连接对话框
   - 验证默认高度适中（700px）
   - 验证可以使用鼠标滚轮上下滚动

2. Test Connection按钮修复测试:
   - 点击"Edit SSH Connection Dialog"
   - 启用SSH隧道
   - 选择Private Key认证方式
   - 点击"Test Connection"按钮
   - 验证按钮正常工作（不会无效）

注意: 实际的连接测试可能会失败（因为是测试数据），
但按钮应该能正常响应并显示错误信息。"""
    
    info_label = tk.Label(root, text=info_text, justify=tk.LEFT, font=('Arial', 11))
    info_label.pack(pady=20, padx=20)
    
    root.mainloop()

if __name__ == "__main__":
    print("Testing connection dialog fixes...")
    test_connection_dialog_fixes()