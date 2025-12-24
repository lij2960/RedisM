#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试UI改进的脚本
主要测试list、set、zset、hash类型数据的行间距和悬停效果
"""

import tkinter as tk
from tkinter import ttk

def test_treeview_styling():
    """测试Treeview样式改进"""
    root = tk.Tk()
    root.title("测试 - Redis数据类型显示改进")
    root.geometry("800x600")
    
    # 创建notebook来展示不同数据类型
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 测试数据
    test_data = {
        'hash': [('field1', 'value1'), ('field2', 'value2'), ('field3', 'value3'), ('field4', 'value4')],
        'list': [(0, 'item1'), (1, 'item2'), (2, 'item3'), (3, 'item4')],
        'set': [('member1',), ('member2',), ('member3',), ('member4',)],
        'zset': [(1.0, 'member1'), (2.5, 'member2'), (3.2, 'member3'), (4.8, 'member4')]
    }
    
    for data_type, items in test_data.items():
        # 创建标签页
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=f"{data_type.upper()} 类型")
        
        # 创建样式
        style = ttk.Style()
        style_name = f"Structured.{data_type}.Treeview"
        
        # 配置行高（增加间距）
        style.configure(style_name, rowheight=28)
        
        # 配置选中和悬停颜色
        style.map(style_name,
                 background=[('selected', '#007AFF'),
                           ('active', '#E8F4FD')],  # 悬停时的浅蓝色背景
                 foreground=[('selected', 'white'),
                           ('active', 'black')])
        
        # 创建Treeview
        if data_type == 'hash':
            columns = ('Field', 'Value')
            tree = ttk.Treeview(frame, columns=columns, show='headings', style=style_name)
            tree.heading('Field', text='Field')
            tree.heading('Value', text='Value')
            tree.column('Field', width=150, minwidth=100)
            tree.column('Value', width=300, minwidth=200)
        elif data_type == 'list':
            columns = ('Index', 'Value')
            tree = ttk.Treeview(frame, columns=columns, show='headings', style=style_name)
            tree.heading('Index', text='Index')
            tree.heading('Value', text='Value')
            tree.column('Index', width=80, minwidth=60)
            tree.column('Value', width=400, minwidth=200)
        elif data_type == 'set':
            columns = ('Value',)
            tree = ttk.Treeview(frame, columns=columns, show='headings', style=style_name)
            tree.heading('Value', text='Value')
            tree.column('Value', width=400, minwidth=200)
        elif data_type == 'zset':
            columns = ('Score', 'Member')
            tree = ttk.Treeview(frame, columns=columns, show='headings', style=style_name)
            tree.heading('Score', text='Score')
            tree.heading('Member', text='Member')
            tree.column('Score', width=100, minwidth=80)
            tree.column('Member', width=300, minwidth=200)
        
        # 添加测试数据
        for item in items:
            tree.insert('', tk.END, values=item)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 添加说明标签
        info_label = ttk.Label(frame, text=f"测试 {data_type.upper()} 类型数据显示：\n• 行间距已增加到28px\n• 鼠标悬停时显示浅蓝色背景\n• 选中时显示深蓝色背景")
        info_label.pack(pady=5)
    
    root.mainloop()

if __name__ == "__main__":
    test_treeview_styling()