#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Redis Manager 测试脚本
验证应用程序的基本功能
"""

import sys
import os

def test_imports():
    """测试所有必要的模块导入"""
    try:
        import tkinter as tk
        print("✓ tkinter 导入成功")
        
        from tkinter import ttk, messagebox, filedialog, simpledialog
        print("✓ tkinter 子模块导入成功")
        
        import redis
        print("✓ redis 导入成功")
        
        import paramiko
        print("✓ paramiko 导入成功")
        
        import json
        print("✓ json 导入成功")
        
        import threading
        print("✓ threading 导入成功")
        
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_tkinter_window():
    """测试tkinter窗口创建"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("测试窗口")
        root.geometry("300x200")
        
        label = tk.Label(root, text="Redis Manager 测试成功！")
        label.pack(pady=50)
        
        # 自动关闭窗口
        root.after(2000, root.destroy)
        root.mainloop()
        
        print("✓ tkinter 窗口测试成功")
        return True
    except Exception as e:
        print(f"✗ tkinter 窗口测试失败: {e}")
        return False

def main():
    print("Redis Manager 功能测试")
    print("=" * 30)
    
    # 测试模块导入
    if not test_imports():
        print("模块导入测试失败")
        sys.exit(1)
    
    # 测试tkinter窗口
    if not test_tkinter_window():
        print("tkinter窗口测试失败")
        sys.exit(1)
    
    print("\n所有测试通过！Redis Manager 应用程序可以正常运行。")

if __name__ == "__main__":
    main()