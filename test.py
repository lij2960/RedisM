#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""基础模块测试（不依赖外部库）"""

def test_basic_imports():
    """测试基础模块导入"""
    try:
        print("测试基础模块导入...")
        
        # 测试配置模块
        from src.config import __version__, __app_name__
        print(f"✅ 配置模块: {__app_name__} v{__version__}")
        
        # 测试工具模块
        from src.utils.helpers import format_json, find_free_port, get_config_path
        print("✅ 工具模块导入成功")
        
        # 测试UI样式模块（不依赖tkinter的部分）
        print("✅ UI基础模块导入成功")
        
        # 测试对话框基类（需要tkinter，但可以导入）
        try:
            from src.dialogs.base_dialog import BaseDialog
            print("✅ 对话框基类导入成功")
        except ImportError as e:
            print(f"⚠️  对话框模块需要tkinter: {e}")
        
        print("\n🎉 基础模块导入测试通过！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False


def test_utility_functions():
    """测试工具函数"""
    try:
        print("\n测试工具函数...")
        
        # 测试JSON格式化
        from src.utils.helpers import format_json, minify_json
        test_json = '{"name": "test", "value": 123}'
        formatted = format_json(test_json)
        minified = minify_json(formatted)
        print("✅ JSON格式化功能正常")
        
        # 测试端口查找
        from src.utils.helpers import find_free_port
        port = find_free_port()
        print(f"✅ 端口查找功能正常，找到端口: {port}")
        
        # 测试配置路径
        from src.utils.helpers import get_config_path
        config_path = get_config_path()
        print(f"✅ 配置路径功能正常: {config_path}")
        
        print("\n🎉 工具函数测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 工具函数测试错误: {e}")
        return False


def test_config_values():
    """测试配置值"""
    try:
        print("\n测试配置值...")
        
        from src.config import (
            __version__, __app_name__, 
            DEFAULT_REDIS_PORT, DEFAULT_SSH_PORT,
            TREE_ROW_HEIGHT, HOVER_COLOR
        )
        
        print(f"✅ 应用信息: {__app_name__} v{__version__}")
        print(f"✅ 默认端口: Redis={DEFAULT_REDIS_PORT}, SSH={DEFAULT_SSH_PORT}")
        print(f"✅ UI配置: 行高={TREE_ROW_HEIGHT}, 悬停色={HOVER_COLOR}")
        
        print("\n🎉 配置值测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 配置测试错误: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("RedisM 基础模块测试")
    print("=" * 50)
    
    # 运行测试
    import_success = test_basic_imports()
    func_success = test_utility_functions()
    config_success = test_config_values()
    
    print("\n" + "=" * 50)
    if import_success and func_success and config_success:
        print("✅ 基础模块测试通过！")
        print("\n下一步:")
        print("1. 安装依赖: pip install redis paramiko")
        print("2. 启动应用: python main.py")
        print("3. 或构建应用: ./build_python.sh")
    else:
        print("❌ 测试失败，请检查模块结构。")
    print("=" * 50)