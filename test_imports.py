#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试所有导入是否正常"""

import sys

def test_imports():
    """测试所有必需的模块导入"""
    errors = []
    
    # 测试标准库
    try:
        import tkinter
        import tkinter.ttk
        import tkinter.messagebox
        print("✓ tkinter 导入成功")
    except Exception as e:
        errors.append(f"✗ tkinter 导入失败: {e}")
    
    # 测试第三方库
    try:
        import redis
        print("✓ redis 导入成功")
    except Exception as e:
        errors.append(f"✗ redis 导入失败: {e}")
    
    try:
        import paramiko
        print("✓ paramiko 导入成功")
    except Exception as e:
        errors.append(f"✗ paramiko 导入失败: {e}")
    
    try:
        import phpserialize
        print("✓ phpserialize 导入成功")
    except Exception as e:
        errors.append(f"✗ phpserialize 导入失败: {e}")
    
    # 测试应用模块
    try:
        from src.config import __version__, __app_name__
        print(f"✓ src.config 导入成功 - {__app_name__} v{__version__}")
    except Exception as e:
        errors.append(f"✗ src.config 导入失败: {e}")
    
    try:
        from src.utils.helpers import format_php_serialize, minify_php_serialize
        print("✓ src.utils.helpers (PHP functions) 导入成功")
    except Exception as e:
        errors.append(f"✗ src.utils.helpers 导入失败: {e}")
    
    try:
        from src.dialogs.simple_dialog import SimpleDialog
        print("✓ src.dialogs.simple_dialog 导入成功")
    except Exception as e:
        errors.append(f"✗ src.dialogs.simple_dialog 导入失败: {e}")
    
    try:
        from src.dialogs.key_dialogs import HashEditDialog
        print("✓ src.dialogs.key_dialogs 导入成功")
    except Exception as e:
        errors.append(f"✗ src.dialogs.key_dialogs 导入失败: {e}")
    
    try:
        from src.ui.main_window import MainWindow
        print("✓ src.ui.main_window 导入成功")
    except Exception as e:
        errors.append(f"✗ src.ui.main_window 导入失败: {e}")
    
    # 测试 PHP serialize 功能
    try:
        test_data = 'a:2:{s:4:"name";s:4:"test";s:3:"age";i:25;}'
        formatted = format_php_serialize(test_data)
        print("✓ PHP serialize 格式化功能正常")
        
        minified = minify_php_serialize(test_data)
        print("✓ PHP serialize 压缩功能正常")
    except Exception as e:
        errors.append(f"✗ PHP serialize 功能测试失败: {e}")
    
    # 输出结果
    print("\n" + "="*50)
    if errors:
        print("发现以下错误:")
        for error in errors:
            print(error)
        return False
    else:
        print("✓ 所有导入测试通过！")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
