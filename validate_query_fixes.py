#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证Query按钮和Hash Get Value按钮的修复
"""

def validate_query_fixes():
    """验证查询功能的修复"""
    print("验证 Query 按钮和 Hash Get Value 按钮的修复...")
    
    with open('redis_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1: execute_key_query方法是否改进
    if 'if query == key:' in content and 'self.load_key_details(key)' in content:
        print("✅ Query按钮逻辑已改进 - 支持直接查询key本身")
    else:
        print("❌ Query按钮逻辑改进未找到")
    
    # 检查2: 是否支持更多Redis命令
    redis_commands = ['HGETALL', 'LLEN', 'LINDEX', 'SMEMBERS', 'SCARD', 'SISMEMBER', 'ZCARD', 'ZSCORE']
    found_commands = 0
    for cmd in redis_commands:
        if f"cmd == '{cmd}'" in content:
            found_commands += 1
    
    if found_commands >= 6:
        print(f"✅ Redis命令支持已扩展 ({found_commands}/{len(redis_commands)} 个命令找到)")
    else:
        print(f"❌ Redis命令支持不完整 ({found_commands}/{len(redis_commands)} 个命令找到)")
    
    # 检查3: query_hash_field方法是否使用新的对话框
    if 'self.show_hash_field_dialog(key, field, result)' in content:
        print("✅ Hash Get Value按钮已使用一致的编辑对话框")
    else:
        print("❌ Hash Get Value按钮对话框未更新")
    
    # 检查4: 是否添加了show_hash_field_dialog方法
    if 'def show_hash_field_dialog(self, key, field, value):' in content:
        print("✅ show_hash_field_dialog方法已添加")
    else:
        print("❌ show_hash_field_dialog方法未找到")
    
    # 检查5: 新对话框是否支持JSON格式化
    if 'ttk.Button(json_btn_frame, text="Format JSON", command=format_json)' in content:
        print("✅ 新对话框支持JSON格式化功能")
    else:
        print("❌ 新对话框JSON格式化功能未找到")
    
    # 检查6: 新对话框是否支持保存功能
    if 'self.redis_client.hset(key, field, new_value)' in content:
        print("✅ 新对话框支持保存功能")
    else:
        print("❌ 新对话框保存功能未找到")
    
    print("\n修复总结:")
    print("1. Query按钮修复:")
    print("   - 当查询内容是key本身时，直接重新加载key详情")
    print("   - 支持更多Redis命令（HGETALL, LLEN, LINDEX, SMEMBERS等）")
    print("   - 改进了命令解析逻辑，支持简化命令格式")
    print("")
    print("2. Hash Get Value按钮修复:")
    print("   - 使用与双击行为一致的编辑对话框")
    print("   - 支持JSON格式化和压缩")
    print("   - 支持直接编辑和保存hash字段值")
    print("   - 保存后自动刷新key详情显示")

if __name__ == "__main__":
    validate_query_fixes()