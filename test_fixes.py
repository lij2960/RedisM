#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试修复的功能"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试导入是否正常"""
    try:
        from src.dialogs.key_dialogs import HashEditDialog, SetEditDialog, ListEditDialog, ZSetEditDialog, AddHashDialog
        from src.dialogs.connection_dialog import ConnectionDialog
        from src.ui.key_manager import KeyManager
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_dialog_constructors():
    """测试对话框构造函数"""
    try:
        import tkinter as tk
        
        # 创建一个虚拟的主窗口类
        class MockMainWindow:
            def get_redis_client(self):
                return None
        
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        mock_main = MockMainWindow()
        
        # 测试各个对话框的构造函数
        from src.dialogs.key_dialogs import HashEditDialog, SetEditDialog, ListEditDialog, ZSetEditDialog, AddHashDialog
        
        # 这些应该不会抛出异常
        hash_dialog = HashEditDialog(root, "test_key", "test_field", "test_value", mock_main)
        set_dialog = SetEditDialog(root, "test_key", "test_value", mock_main)
        list_dialog = ListEditDialog(root, "test_key", 0, "test_value", mock_main)
        zset_dialog = ZSetEditDialog(root, "test_key", "test_member", 1.0, mock_main)
        add_hash_dialog = AddHashDialog(root, "test_key", mock_main)
        
        print("✅ All dialog constructors work correctly")
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Dialog constructor error: {e}")
        return False

if __name__ == "__main__":
    print("Testing fixes...")
    
    success = True
    success &= test_imports()
    success &= test_dialog_constructors()
    
    if success:
        print("\n🎉 All tests passed! The fixes should work correctly.")
    else:
        print("\n💥 Some tests failed. Please check the errors above.")