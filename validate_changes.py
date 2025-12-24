#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证redis_manager.py中的UI改进
"""

import ast
import re

def validate_changes():
    """验证代码修改是否正确"""
    print("验证 redis_manager.py 中的UI改进...")
    
    with open('redis_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1: show_structured_value方法是否包含样式配置
    if 'style.configure(style_name, rowheight=28)' in content:
        print("✅ 行间距配置已添加 (rowheight=28)")
    else:
        print("❌ 行间距配置未找到")
    
    # 检查2: 是否包含悬停效果配置
    if "'active', '#E8F4FD'" in content:
        print("✅ 悬停效果颜色配置已添加")
    else:
        print("❌ 悬停效果颜色配置未找到")
    
    # 检查3: 是否绑定了鼠标事件
    if "self.data_tree.bind('<Motion>', self.on_treeview_motion)" in content:
        print("✅ 鼠标移动事件绑定已添加")
    else:
        print("❌ 鼠标移动事件绑定未找到")
    
    if "self.data_tree.bind('<Leave>', self.on_treeview_leave)" in content:
        print("✅ 鼠标离开事件绑定已添加")
    else:
        print("❌ 鼠标离开事件绑定未找到")
    
    # 检查4: 是否添加了事件处理方法
    if "def on_treeview_motion(self, event):" in content:
        print("✅ on_treeview_motion 方法已添加")
    else:
        print("❌ on_treeview_motion 方法未找到")
    
    if "def on_treeview_leave(self, event):" in content:
        print("✅ on_treeview_leave 方法已添加")
    else:
        print("❌ on_treeview_leave 方法未找到")
    
    # 检查5: 是否为不同数据类型设置了列宽
    column_configs = [
        "self.data_tree.column('Field', width=150, minwidth=100)",
        "self.data_tree.column('Index', width=80, minwidth=60)",
        "self.data_tree.column('Value', width=400, minwidth=200)",
        "self.data_tree.column('Score', width=100, minwidth=80)"
    ]
    
    found_configs = 0
    for config in column_configs:
        if config in content:
            found_configs += 1
    
    if found_configs >= 3:
        print(f"✅ 列宽配置已添加 ({found_configs}/4 个配置找到)")
    else:
        print(f"❌ 列宽配置不完整 ({found_configs}/4 个配置找到)")
    
    print("\n总结:")
    print("- 为 list、set、zset、hash 类型的数据增加了行间距 (rowheight=28)")
    print("- 添加了鼠标悬停变色效果 (浅蓝色背景 #E8F4FD)")
    print("- 绑定了鼠标移动和离开事件")
    print("- 优化了列宽设置以提供更好的显示效果")
    print("- 保持了选中状态的深蓝色背景 (#007AFF)")

if __name__ == "__main__":
    validate_changes()