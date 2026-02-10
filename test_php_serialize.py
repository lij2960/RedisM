#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试PHP序列化功能"""

import sys
import json

# 测试数据
test_cases = [
    {
        "name": "简单数组",
        "php": 'a:2:{s:4:"name";s:4:"test";s:3:"age";i:25;}',
        "expected_json": {"name": "test", "age": 25}
    },
    {
        "name": "嵌套数组",
        "php": 'a:2:{s:4:"user";a:2:{s:2:"id";i:1;s:4:"name";s:4:"John";}s:5:"roles";a:2:{i:0;s:5:"admin";i:1;s:4:"user";}}',
        "expected_json": {
            "user": {"id": 1, "name": "John"},
            "roles": ["admin", "user"]
        }
    }
]

def test_php_serialize():
    """测试PHP序列化功能"""
    try:
        from src.utils.helpers import format_php_serialize, minify_php_serialize
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请先安装依赖: pip install phpserialize")
        return False
    
    print("="*60)
    print("测试 PHP Serialize 功能")
    print("="*60)
    print()
    
    all_passed = True
    
    for i, test in enumerate(test_cases, 1):
        print(f"测试 {i}: {test['name']}")
        print("-" * 60)
        
        # 测试1: Format PHP (PHP -> JSON)
        try:
            formatted = format_php_serialize(test['php'])
            parsed_json = json.loads(formatted)
            
            if parsed_json == test['expected_json']:
                print("✅ Format PHP: 通过")
                print(f"   输入: {test['php'][:50]}...")
                print(f"   输出: {formatted[:100]}...")
            else:
                print("❌ Format PHP: 失败")
                print(f"   期望: {test['expected_json']}")
                print(f"   实际: {parsed_json}")
                all_passed = False
        except Exception as e:
            print(f"❌ Format PHP: 异常 - {e}")
            all_passed = False
        
        # 测试2: Minify PHP (PHP -> PHP压缩)
        try:
            minified = minify_php_serialize(test['php'])
            # 验证压缩后的数据可以被解析
            re_formatted = format_php_serialize(minified)
            re_parsed = json.loads(re_formatted)
            
            if re_parsed == test['expected_json']:
                print("✅ Minify PHP (PHP输入): 通过")
                print(f"   输入: {test['php'][:50]}...")
                print(f"   输出: {minified[:50]}...")
            else:
                print("❌ Minify PHP (PHP输入): 失败")
                all_passed = False
        except Exception as e:
            print(f"❌ Minify PHP (PHP输入): 异常 - {e}")
            all_passed = False
        
        # 测试3: Minify PHP (JSON -> PHP) - 这是用户遇到的场景
        try:
            # 先格式化为JSON
            formatted_json = format_php_serialize(test['php'])
            # 然后尝试压缩（应该将JSON转回PHP格式）
            minified_from_json = minify_php_serialize(formatted_json)
            # 验证结果
            re_formatted = format_php_serialize(minified_from_json)
            re_parsed = json.loads(re_formatted)
            
            if re_parsed == test['expected_json']:
                print("✅ Minify PHP (JSON输入): 通过")
                print(f"   输入: {formatted_json[:50]}...")
                print(f"   输出: {minified_from_json[:50]}...")
            else:
                print("❌ Minify PHP (JSON输入): 失败")
                all_passed = False
        except Exception as e:
            print(f"❌ Minify PHP (JSON输入): 异常 - {e}")
            all_passed = False
        
        print()
    
    # 测试4: 工作流测试（模拟用户操作）
    print("测试 3: 完整工作流（模拟用户操作）")
    print("-" * 60)
    try:
        original_php = test_cases[0]['php']
        print(f"1. 原始PHP数据: {original_php}")
        
        # 用户点击 Format PHP
        formatted = format_php_serialize(original_php)
        print(f"2. 点击 Format PHP: {formatted[:80]}...")
        
        # 用户点击 Minify PHP（此时文本框中是JSON）
        minified = minify_php_serialize(formatted)
        print(f"3. 点击 Minify PHP: {minified}")
        
        # 验证可以再次格式化
        re_formatted = format_php_serialize(minified)
        print(f"4. 再次 Format PHP: {re_formatted[:80]}...")
        
        print("✅ 完整工作流: 通过")
    except Exception as e:
        print(f"❌ 完整工作流: 失败 - {e}")
        all_passed = False
    
    print()
    print("="*60)
    if all_passed:
        print("✅ 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = test_php_serialize()
    sys.exit(0 if success else 1)
