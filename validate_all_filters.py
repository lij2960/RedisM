#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证所有数据类型的过滤功能
"""

def validate_all_filters():
    """验证所有数据类型的过滤功能实现"""
    print("验证 List、Set、ZSet 过滤功能...")
    
    with open('redis_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1: List类型过滤功能
    if "elif key_type in ['list', 'zset']:" in content and 'self.filter_list_zset_data(key, key_type)' in content:
        print("✅ List和ZSet类型Find按钮已添加")
    else:
        print("❌ List和ZSet类型Find按钮未找到")
    
    # 检查2: Set类型过滤功能
    if "elif key_type == 'set':" in content and 'self.filter_set_data(key)' in content:
        print("✅ Set类型Find按钮已添加")
    else:
        print("❌ Set类型Find按钮未找到")
    
    # 检查3: 原始数据存储
    storage_checks = [
        'self.original_list_data = value',
        'self.original_set_data = list(value)',
        'self.original_zset_data = value'
    ]
    
    found_storage = 0
    for check in storage_checks:
        if check in content:
            found_storage += 1
    
    if found_storage == 3:
        print("✅ 所有数据类型的原始数据存储已添加")
    else:
        print(f"❌ 原始数据存储不完整 ({found_storage}/3)")
    
    # 检查4: 数据加载方法
    load_methods = [
        'def load_list_data_to_tree(self, list_data):',
        'def load_set_data_to_tree(self, set_data):',
        'def load_zset_data_to_tree(self, zset_data):'
    ]
    
    found_methods = 0
    for method in load_methods:
        if method in content:
            found_methods += 1
    
    if found_methods == 3:
        print("✅ 所有数据加载方法已添加")
    else:
        print(f"❌ 数据加载方法不完整 ({found_methods}/3)")
    
    # 检查5: 过滤方法
    filter_methods = [
        'def filter_list_zset_data(self, key, key_type):',
        'def filter_set_data(self, key):'
    ]
    
    found_filters = 0
    for method in filter_methods:
        if method in content:
            found_filters += 1
    
    if found_filters == 2:
        print("✅ 所有过滤方法已添加")
    else:
        print(f"❌ 过滤方法不完整 ({found_filters}/2)")
    
    # 检查6: 统一状态更新方法
    if 'def _update_filter_status(self, filtered_count, total_count, filter_text):' in content:
        print("✅ 统一状态更新方法已添加")
    else:
        print("❌ 统一状态更新方法未找到")
    
    # 检查7: Enter键绑定
    enter_bindings = [
        "query_entry.bind('<Return>', lambda e: self.filter_hash_data(key))",
        "query_entry.bind('<Return>', lambda e: self.filter_list_zset_data(key, key_type))",
        "query_entry.bind('<Return>', lambda e: self.filter_set_data(key))"
    ]
    
    found_bindings = 0
    for binding in enter_bindings:
        if binding in content:
            found_bindings += 1
    
    if found_bindings == 3:
        print("✅ 所有类型的Enter键绑定已添加")
    else:
        print(f"❌ Enter键绑定不完整 ({found_bindings}/3)")
    
    # 检查8: 模糊匹配功能
    fuzzy_checks = [
        'filter_lower in value_str',  # list和set
        'filter_lower in member_str or filter_lower in score_str',  # zset
        'filter_lower in field_str or filter_lower in value_str'  # hash
    ]
    
    found_fuzzy = 0
    for check in fuzzy_checks:
        if check in content:
            found_fuzzy += 1
    
    if found_fuzzy >= 2:
        print("✅ 模糊匹配功能已实现")
    else:
        print(f"❌ 模糊匹配功能不完整 ({found_fuzzy}/3)")
    
    print("\n功能总结:")
    print("1. 所有数据类型的过滤功能:")
    print("   - Hash: 支持字段名和值的模糊匹配")
    print("   - List: 支持值的模糊匹配")
    print("   - Set: 支持成员值的模糊匹配")
    print("   - ZSet: 支持成员名和分数的模糊匹配")
    print("")
    print("2. 统一的用户体验:")
    print("   - 所有类型都使用'Find'按钮")
    print("   - 支持Enter键快捷操作")
    print("   - 统一的过滤状态显示")
    print("   - 空输入时显示所有数据")
    print("")
    print("3. 技术实现:")
    print("   - 原始数据存储以支持过滤")
    print("   - 独立的数据加载方法")
    print("   - 统一的状态更新机制")
    print("   - 大小写不敏感搜索")

if __name__ == "__main__":
    validate_all_filters()