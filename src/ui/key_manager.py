#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""键管理器UI"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import json

from ..config import *
from ..redis.operations import RedisOperations
from ..utils.helpers import format_json, minify_json
from ..dialogs.key_dialogs import HashEditDialog, SetEditDialog, AddHashDialog, ListEditDialog, ZSetEditDialog


class KeyManager:
    """键管理器类"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        self.key_details_frame = ttk.Frame(self.parent)
        self.key_details_frame.pack(fill=tk.BOTH, expand=True)
        
        # 初始提示
        self._show_welcome()
    
    def _show_welcome(self):
        """显示欢迎界面"""
        welcome_frame = ttk.Frame(self.key_details_frame)
        welcome_frame.pack(expand=True)
        
        ttk.Label(welcome_frame, text="🔑", 
                 font=self.main_window.style_manager.get_font(48)).pack(pady=(0, 10))
        ttk.Label(welcome_frame, text="Select a key to view details", 
                 style='Title.TLabel').pack()
    
    def clear_details(self):
        """清空详情"""
        for widget in self.key_details_frame.winfo_children():
            widget.destroy()
        self._show_welcome()
    
    def load_key_details(self, key):
        """加载键详情"""
        redis_client = self.main_window.get_redis_client()
        if not redis_client:
            return
        
        def load_thread():
            try:
                # 检查连接状态，如果断开则尝试重连
                if not self.main_window.redis_conn.check_and_reconnect():
                    return
                
                redis_ops = RedisOperations(redis_client)
                
                # 获取键信息
                key_info = redis_ops.get_key_info(key)
                if not key_info:
                    self.main_window.root.after(0, lambda: messagebox.showerror("Error", f"Key '{key}' does not exist"))
                    return
                
                # 获取值
                value = redis_ops.get_key_value(key, key_info['type'])
                
                self.main_window.root.after(0, lambda: self._show_key_details(key, key_info, value))
                
            except Exception as e:
                error_msg = f"Failed to load key '{key}': {str(e)}"
                self.main_window.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _show_key_details(self, key, key_info, value):
        """显示键详情"""
        # 清空详情框架
        for widget in self.key_details_frame.winfo_children():
            widget.destroy()
        
        key_type = key_info['type']
        ttl = key_info['ttl']
        
        # 键信息 - 显示完整键名
        info_frame = ttk.Frame(self.key_details_frame)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 使用文本框显示完整键名
        ttk.Label(info_frame, text="Key:").pack(anchor=tk.W)
        key_text = tk.Text(info_frame, height=2, wrap=tk.WORD)
        key_text.pack(fill=tk.X, pady=(0, 5))
        key_text.insert(tk.END, key)
        key_text.config(state=tk.DISABLED)
        
        ttk.Label(info_frame, text=f"Type: {key_type}").pack(anchor=tk.W)
        ttl_text = ttl if ttl > 0 else 'Never expires'
        ttk.Label(info_frame, text=f"TTL: {ttl_text}").pack(anchor=tk.W)
        
        # 查询框架
        query_frame = ttk.LabelFrame(self.key_details_frame, text="Query & Edit")
        query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 查询输入
        query_input_frame = ttk.Frame(query_frame)
        query_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(query_input_frame, text="Query:").pack(side=tk.LEFT)
        self.query_var = tk.StringVar(value=key)  # 设置默认值为当前键
        query_entry = ttk.Entry(query_input_frame, textvariable=self.query_var)
        query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        query_entry.bind('<Return>', lambda e: self._execute_key_query(key, key_type))
        
        ttk.Button(query_input_frame, text="Query", 
                  command=lambda: self._execute_key_query(key, key_type)).pack(side=tk.RIGHT)
        
        # 值编辑区域
        value_frame = ttk.LabelFrame(self.key_details_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 根据数据类型选择显示方式
        if key_type in ['list', 'set', 'zset', 'hash']:
            self._show_structured_value(value_frame, key, key_type, value)
        else:
            self._show_text_value(value_frame, key, key_type, value)
        
        # 操作按钮
        self._create_action_buttons(key, key_type)
    
    def _show_structured_value(self, parent, key, key_type, value):
        """显示结构化数据（表格形式）"""
        # 清理之前的过滤状态标签
        if hasattr(self, 'filter_status_label'):
            self.filter_status_label.destroy()
            delattr(self, 'filter_status_label')
        
        # 查询框架
        query_frame = ttk.Frame(parent)
        query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 根据类型创建过滤输入
        self._create_filter_input(query_frame, key, key_type)
        
        # 表格显示
        self._create_data_table(parent, key, key_type, value)
        
        # 操作按钮
        self._create_table_buttons(parent, key, key_type)
    
    def _create_filter_input(self, parent, key, key_type):
        """创建过滤输入"""
        if key_type == 'hash':
            ttk.Label(parent, text="Hash Key:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(parent, textvariable=self.struct_query_var)
            query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self._filter_hash_data(key))
            ttk.Button(parent, text="Find", 
                      command=lambda: self._filter_hash_data(key)).pack(side=tk.RIGHT)
        elif key_type in ['list', 'zset']:
            ttk.Label(parent, text="Filter:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(parent, textvariable=self.struct_query_var)
            query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self._filter_list_zset_data(key, key_type))
            ttk.Button(parent, text="Find", 
                      command=lambda: self._filter_list_zset_data(key, key_type)).pack(side=tk.RIGHT)
        elif key_type == 'set':
            ttk.Label(parent, text="Filter:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(parent, textvariable=self.struct_query_var)
            query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self._filter_set_data(key))
            ttk.Button(parent, text="Find", 
                      command=lambda: self._filter_set_data(key)).pack(side=tk.RIGHT)
    
    def _create_data_table(self, parent, key, key_type, value):
        """创建数据表格"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置Treeview样式
        style_name = self.main_window.style_manager.configure_treeview_style(key_type)
        
        # 根据类型创建表格
        if key_type == 'hash':
            columns = ('Field', 'Value')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name)
            self.data_tree.heading('Field', text='Field')
            self.data_tree.heading('Value', text='Value')
            self.data_tree.column('Field', width=150, minwidth=100)
            self.data_tree.column('Value', width=300, minwidth=200)
            
            # 存储原始数据
            self.original_hash_data = value if isinstance(value, dict) else {}
            self._load_hash_data_to_tree(self.original_hash_data)
            
        elif key_type == 'list':
            columns = ('Index', 'Value')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name)
            self.data_tree.heading('Index', text='Index')
            self.data_tree.heading('Value', text='Value')
            self.data_tree.column('Index', width=80, minwidth=60)
            self.data_tree.column('Value', width=400, minwidth=200)
            
            self.original_list_data = value if isinstance(value, list) else []
            self._load_list_data_to_tree(self.original_list_data)
            
        elif key_type == 'set':
            columns = ('Value',)
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name)
            self.data_tree.heading('Value', text='Value')
            self.data_tree.column('Value', width=400, minwidth=200)
            
            self.original_set_data = list(value) if isinstance(value, (list, set)) else []
            self._load_set_data_to_tree(self.original_set_data)
            
        elif key_type == 'zset':
            columns = ('Score', 'Member')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name)
            self.data_tree.heading('Score', text='Score')
            self.data_tree.heading('Member', text='Member')
            self.data_tree.column('Score', width=100, minwidth=80)
            self.data_tree.column('Member', width=300, minwidth=200)
            
            self.original_zset_data = value if isinstance(value, list) else []
            self._load_zset_data_to_tree(self.original_zset_data)
        
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 绑定双击事件
        self.data_tree.bind('<Double-1>', lambda e: self._edit_table_item(key, key_type))
    
    def _create_table_buttons(self, parent, key, key_type):
        """创建表格操作按钮"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add Item", 
                  command=lambda: self._add_table_item(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Update All", 
                  command=lambda: self._update_structured_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", 
                  command=lambda: self.load_key_details(key)).pack(side=tk.LEFT)
    
    def _show_text_value(self, parent, key, key_type, value):
        """显示文本数据"""
        # JSON格式化按钮
        format_frame = ttk.Frame(parent)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(format_frame, text="Format JSON", 
                  command=lambda: self._format_json_value()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(format_frame, text="Minify JSON", 
                  command=lambda: self._minify_json_value()).pack(side=tk.LEFT)
        
        # 文本编辑器
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.value_text = tk.Text(text_frame, wrap=tk.WORD)
        self.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.value_text.insert(tk.END, str(value))
        
        value_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.value_text.yview)
        value_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.value_text.configure(yscrollcommand=value_scroll.set)
    
    def _create_action_buttons(self, key, key_type):
        """创建操作按钮"""
        btn_frame = ttk.Frame(self.key_details_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Update", 
                  command=lambda: self._update_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Delete", 
                  command=lambda: self._delete_key(key)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", 
                  command=lambda: self.load_key_details(key)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Add New Key", 
                  command=self._add_new_key).pack(side=tk.LEFT)
    
    # 数据加载方法
    def _load_hash_data_to_tree(self, hash_data):
        """将hash数据加载到树形控件"""
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if isinstance(hash_data, dict):
            for field, val in hash_data.items():
                self.data_tree.insert('', tk.END, values=(field, val))
    
    def _load_list_data_to_tree(self, list_data):
        """将list数据加载到树形控件"""
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if isinstance(list_data, list):
            for i, val in enumerate(list_data):
                self.data_tree.insert('', tk.END, values=(i, val))
    
    def _load_set_data_to_tree(self, set_data):
        """将set数据加载到树形控件"""
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if isinstance(set_data, list):
            for val in sorted(set_data):
                self.data_tree.insert('', tk.END, values=(val,))
    
    def _load_zset_data_to_tree(self, zset_data):
        """将zset数据加载到树形控件"""
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if isinstance(zset_data, list):
            for i in range(0, len(zset_data), 2):
                if i + 1 < len(zset_data):
                    self.data_tree.insert('', tk.END, values=(zset_data[i+1], zset_data[i]))
    
    # 过滤方法
    def _filter_hash_data(self, key):
        """过滤hash数据"""
        filter_text = self.struct_query_var.get().strip()
        
        if not filter_text:
            self._load_hash_data_to_tree(self.original_hash_data)
            self._update_filter_status(len(self.original_hash_data), len(self.original_hash_data), filter_text)
            return
        
        try:
            filtered_data = {}
            filter_lower = filter_text.lower()
            
            for field, value in self.original_hash_data.items():
                field_str = str(field).lower()
                value_str = str(value).lower()
                
                if filter_lower in field_str or filter_lower in value_str:
                    filtered_data[field] = value
            
            self._load_hash_data_to_tree(filtered_data)
            self._update_filter_status(len(filtered_data), len(self.original_hash_data), filter_text)
            
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to filter hash data: {e}")
    
    def _filter_list_zset_data(self, key, key_type):
        """过滤list和zset数据"""
        filter_text = self.struct_query_var.get().strip()
        
        try:
            if key_type == 'list':
                if not filter_text:
                    self._load_list_data_to_tree(self.original_list_data)
                    self._update_filter_status(len(self.original_list_data), len(self.original_list_data), filter_text)
                    return
                
                filtered_data = []
                filter_lower = filter_text.lower()
                
                for val in self.original_list_data:
                    value_str = str(val).lower()
                    if filter_lower in value_str:
                        filtered_data.append(val)
                
                self._load_list_data_to_tree(filtered_data)
                self._update_filter_status(len(filtered_data), len(self.original_list_data), filter_text)
                
            elif key_type == 'zset':
                if not filter_text:
                    self._load_zset_data_to_tree(self.original_zset_data)
                    total_count = len(self.original_zset_data) // 2
                    self._update_filter_status(total_count, total_count, filter_text)
                    return
                
                filtered_data = []
                filter_lower = filter_text.lower()
                
                for i in range(0, len(self.original_zset_data), 2):
                    if i + 1 < len(self.original_zset_data):
                        member = self.original_zset_data[i]
                        score = self.original_zset_data[i + 1]
                        
                        member_str = str(member).lower()
                        score_str = str(score).lower()
                        
                        if filter_lower in member_str or filter_lower in score_str:
                            filtered_data.extend([member, score])
                
                self._load_zset_data_to_tree(filtered_data)
                filtered_count = len(filtered_data) // 2
                total_count = len(self.original_zset_data) // 2
                self._update_filter_status(filtered_count, total_count, filter_text)
                
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to filter {key_type} data: {e}")
    
    def _filter_set_data(self, key):
        """过滤set数据"""
        filter_text = self.struct_query_var.get().strip()
        
        if not filter_text:
            self._load_set_data_to_tree(self.original_set_data)
            self._update_filter_status(len(self.original_set_data), len(self.original_set_data), filter_text)
            return
        
        try:
            filtered_data = []
            filter_lower = filter_text.lower()
            
            for val in self.original_set_data:
                value_str = str(val).lower()
                if filter_lower in value_str:
                    filtered_data.append(val)
            
            self._load_set_data_to_tree(filtered_data)
            self._update_filter_status(len(filtered_data), len(self.original_set_data), filter_text)
            
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to filter set data: {e}")
    
    def _update_filter_status(self, filtered_count, total_count, filter_text):
        """更新过滤状态显示"""
        if hasattr(self, 'filter_status_label'):
            self.filter_status_label.destroy()
        
        parent_frame = self.data_tree.master.master
        self.filter_status_label = ttk.Label(parent_frame, 
                                            text=f"Showing {filtered_count} of {total_count} items" + 
                                                 (f" (filtered by: '{filter_text}')" if filter_text else ""),
                                            font=self.main_window.style_manager.get_font(FONT_SIZE_SMALL),
                                            foreground='#666666')
        self.filter_status_label.pack(pady=(5, 0))
    
    # 编辑和操作方法
    def _edit_table_item(self, key, key_type):
        """编辑表格项"""
        selection = self.data_tree.selection()
        if not selection:
            return
        
        item = self.data_tree.item(selection[0])
        values = item['values']
        
        if key_type == 'hash':
            field, value = values[0], values[1]
            dialog = HashEditDialog(self.main_window.root, key, field, value, self.main_window)
            result = dialog.show()
            if result:
                self._refresh_current_display(key, key_type)
        elif key_type == 'set':
            old_value = values[0]
            dialog = SetEditDialog(self.main_window.root, key, old_value, self.main_window)
            result = dialog.show()
            if result:
                self._refresh_current_display(key, key_type)
        elif key_type == 'list':
            index, value = values[0], values[1]
            dialog = ListEditDialog(self.main_window.root, key, index, value, self.main_window)
            result = dialog.show()
            if result:
                self._refresh_current_display(key, key_type)
        elif key_type == 'zset':
            score, member = values[0], values[1]
            dialog = ZSetEditDialog(self.main_window.root, key, member, score, self.main_window)
            result = dialog.show()
            if result:
                self._refresh_current_display(key, key_type)
    
    def _add_table_item(self, key, key_type):
        """添加表格项"""
        if key_type == 'hash':
            dialog = AddHashDialog(self.main_window.root, key, self.main_window)
            result = dialog.show()
            if result:
                self._refresh_current_display(key, key_type)
        # 其他类型的添加...
    
    def _refresh_current_display(self, key, key_type):
        """刷新当前显示"""
        redis_client = self.main_window.get_redis_client()
        if not redis_client:
            return
        
        try:
            redis_ops = RedisOperations(redis_client)
            new_data = redis_ops.get_key_value(key, key_type)
            
            # 更新原始数据并重新加载
            if key_type == 'hash':
                self.original_hash_data = new_data
                if hasattr(self, 'struct_query_var') and self.struct_query_var.get().strip():
                    self._filter_hash_data(key)
                else:
                    self._load_hash_data_to_tree(new_data)
            elif key_type == 'list':
                self.original_list_data = new_data
                if hasattr(self, 'struct_query_var') and self.struct_query_var.get().strip():
                    self._filter_list_zset_data(key, key_type)
                else:
                    self._load_list_data_to_tree(new_data)
            elif key_type == 'set':
                self.original_set_data = new_data
                if hasattr(self, 'struct_query_var') and self.struct_query_var.get().strip():
                    self._filter_set_data(key)
                else:
                    self._load_set_data_to_tree(new_data)
            elif key_type == 'zset':
                self.original_zset_data = new_data
                if hasattr(self, 'struct_query_var') and self.struct_query_var.get().strip():
                    self._filter_list_zset_data(key, key_type)
                else:
                    self._load_zset_data_to_tree(new_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh display: {e}")
    
    def _update_key(self, key, key_type):
        """更新键"""
        try:
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                return
            
            redis_ops = RedisOperations(redis_client)
            
            if hasattr(self, 'value_text'):
                # 文本类型
                new_value = self.value_text.get(1.0, tk.END).strip()
                redis_ops.set_key_value(key, new_value, key_type)
            else:
                # 结构化类型 - 使用Update All逻辑
                self._update_structured_key(key, key_type)
                return
            
            messagebox.showinfo("Success", "Key updated successfully!")
            self.load_key_details(key)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update key: {e}")
    
    def _update_structured_key(self, key, key_type):
        """更新结构化键"""
        # 这里实现复杂的结构化数据更新逻辑
        # 包括过滤状态的处理等
        pass
    
    def _delete_key(self, key):
        """删除键"""
        if messagebox.askyesno("Delete Key", f"Are you sure you want to delete '{key}'?"):
            try:
                redis_client = self.main_window.get_redis_client()
                if not redis_client:
                    return
                
                redis_ops = RedisOperations(redis_client)
                redis_ops.delete_key(key)
                
                messagebox.showinfo("Success", "Key deleted successfully!")
                
                # 刷新键列表
                self.main_window.left_panel.search_keys()
                
                # 清空详情
                self.clear_details()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete key: {e}")
    
    def _add_new_key(self):
        """添加新键"""
        # 实现添加新键的对话框
        pass
    
    def _execute_key_query(self, key, key_type):
        """执行键查询"""
        # 实现查询逻辑
        pass
    
    def _format_json_value(self):
        """格式化JSON值"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            formatted = format_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, formatted)
        except ValueError as e:
            messagebox.showerror("JSON Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format JSON: {e}")
    
    def _minify_json_value(self):
        """压缩JSON值"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            minified = minify_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, minified)
        except ValueError as e:
            messagebox.showerror("JSON Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify JSON: {e}")