#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""键管理器UI"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import json
import redis
import socket

from ..config import *
from ..redis.operations import RedisOperations
from ..utils.helpers import format_json, minify_json, apply_json_syntax_highlighting, setup_json_text_widget, format_json_with_highlighting
from ..dialogs.key_dialogs import HashEditDialog, SetEditDialog, AddHashDialog, ListEditDialog, ZSetEditDialog, AddListDialog, AddSetDialog, AddZSetDialog, AddNewKeyDialog


class KeyManager:
    """键管理器类"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI - 使用SimpleDialog风格的布局实现真正的自适应"""
        # 配置父容器的grid权重 - 支持灵活的section配置
        self.parent.grid_rowconfigure(0, weight=1)  # 主要内容区域可扩展
        self.parent.grid_columnconfigure(0, weight=1)
        
        # 创建主容器
        self.main_container = ttk.Frame(self.parent)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        
        # 配置主容器的grid权重
        self.main_container.grid_rowconfigure(0, weight=1)  # 内容区域可扩展
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # 创建内容框架
        self.key_details_frame = ttk.Frame(self.main_container)
        self.key_details_frame.grid(row=0, column=0, sticky="nsew")
        
        # 初始提示
        self._show_welcome()
    
    def _create_fixed_section(self, row):
        """创建固定高度的区域"""
        section = ttk.Frame(self.key_details_frame)
        section.grid(row=row, column=0, sticky="ew", pady=5)
        section.grid_columnconfigure(0, weight=1)
        return section
    
    def _create_expandable_section(self, row):
        """创建可扩展的区域"""
        section = ttk.Frame(self.key_details_frame)
        section.grid(row=row, column=0, sticky="nsew", pady=5)
        section.grid_rowconfigure(0, weight=1)
        section.grid_columnconfigure(0, weight=1)
        return section
    
    def _create_auto_text(self, parent, initial_text="", **kwargs):
        """创建真正自适应的文本组件"""
        # 创建文本框架
        text_frame = ttk.Frame(parent)
        text_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置grid权重
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # 创建文本组件 - 不设置height，让grid管理大小
        text_widget = tk.Text(text_frame, wrap=tk.WORD, **kwargs)
        text_widget.grid(row=0, column=0, sticky="nsew")
        
        # 插入初始文本
        if initial_text:
            text_widget.insert(tk.END, initial_text)
        
        # 创建滚动条
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_scroll.grid(row=0, column=1, sticky="ns")
        text_widget.configure(yscrollcommand=text_scroll.set)
        
        # 添加搜索功能 - 添加搜索按钮到父容器，设置固定高度
        search_frame = ttk.Frame(parent, height=35)  # 设置固定高度35像素
        search_frame.grid(row=1, column=0, sticky="ew")
        search_frame.pack_propagate(False)  # 防止子组件改变父容器大小
        
        ttk.Button(search_frame, text="🔍 Search (⌘F)", 
                  command=lambda: self._show_search_dialog()).pack(side=tk.RIGHT, pady=5)
        
        # 绑定⌘F快捷键
        text_widget.bind('<Command-f>', lambda e: self._show_search_dialog())
        text_widget.bind('<Command-F>', lambda e: self._show_search_dialog())
        
        return text_widget, text_frame
    
    def _show_welcome(self):
        """显示Redis服务器信息"""
        # 检查是否有Redis连接
        redis_client = self.main_window.get_redis_client()
        if not redis_client:
            # 没有连接时显示欢迎界面
            welcome_frame = ttk.Frame(self.key_details_frame)
            welcome_frame.pack(expand=True)
            
            ttk.Label(welcome_frame, text="🔑", 
                     font=self.main_window.style_manager.get_font(48)).pack(pady=(0, 10))
            ttk.Label(welcome_frame, text="Connect to Redis to view server information", 
                     style='Title.TLabel').pack()
            return
        
        # 有连接时显示Redis服务器信息
        def load_server_info():
            try:
                redis_ops = RedisOperations(redis_client)
                
                # 获取当前数据库编号
                current_db = 0  # 默认值
                try:
                    # 从左侧面板的数据库选择器获取当前数据库
                    if hasattr(self.main_window, 'left_panel') and hasattr(self.main_window.left_panel, 'db_var'):
                        db_text = self.main_window.left_panel.db_var.get()
                        if db_text and db_text.startswith('DB '):
                            current_db = int(db_text.split()[1])
                except:
                    current_db = 0
                
                server_info = redis_ops.get_server_info(current_db)
                self.main_window.root.after(0, lambda: self._display_server_info(server_info))
            except Exception as e:
                error_info = {'error': str(e)}
                self.main_window.root.after(0, lambda: self._display_server_info(error_info))
        
        # 显示加载中
        loading_frame = ttk.Frame(self.key_details_frame)
        loading_frame.pack(expand=True)
        ttk.Label(loading_frame, text="Loading Redis server information...", 
                 style='Title.TLabel').pack()
        
        # 在后台线程中加载服务器信息
        import threading
        threading.Thread(target=load_server_info, daemon=True).start()
    
    def _display_server_info(self, server_info):
        """显示Redis服务器信息 - 网格布局铺满整屏"""
        # 清空当前内容
        for widget in self.key_details_frame.winfo_children():
            widget.destroy()
        
        if 'error' in server_info:
            # 显示错误信息
            error_frame = ttk.Frame(self.key_details_frame)
            error_frame.pack(expand=True)
            
            ttk.Label(error_frame, text="❌", 
                     font=self.main_window.style_manager.get_font(48)).pack(pady=(0, 10))
            ttk.Label(error_frame, text="Failed to load Redis server information", 
                     style='Title.TLabel').pack()
            ttk.Label(error_frame, text=f"Error: {server_info['error']}", 
                     foreground='red').pack(pady=(5, 0))
            return
        
        # 主容器 - 使用grid布局铺满整屏
        main_container = ttk.Frame(self.key_details_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置网格权重，让内容填满整个区域
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # 标题栏 - 跨两列
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        
        ttk.Label(title_frame, text="🗄️ Redis Server Information", 
                 font=self.main_window.style_manager.get_font(16, 'bold')).pack(side=tk.LEFT)
        
        # 刷新按钮放在标题右侧
        ttk.Button(title_frame, text="🔄 Refresh", 
                  command=self._refresh_server_info).pack(side=tk.RIGHT)
        
        # 左侧信息面板
        left_panel = ttk.Frame(main_container)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 3))
        
        # 右侧信息面板
        right_panel = ttk.Frame(main_container)
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(3, 0))
        
        # 左侧面板内容
        self._create_left_info_panel(left_panel, server_info)
        
        # 右侧面板内容
        self._create_right_info_panel(right_panel, server_info)
    
    def _create_left_info_panel(self, parent, server_info):
        """创建左侧信息面板"""
        # 基本信息
        basic_frame = ttk.LabelFrame(parent, text="Basic Information", padding=5)
        basic_frame.pack(fill=tk.X, pady=(0, 5))
        
        basic_info = [
            ("Redis Version", server_info.get('redis_version', 'Unknown')),
            ("Mode", server_info.get('redis_mode', 'standalone')),
            ("Operating System", server_info.get('os', 'Unknown')),
            ("Architecture", f"{server_info.get('arch_bits', 'Unknown')} bit"),
            ("Process ID", str(server_info.get('process_id', 'Unknown'))),
            ("TCP Port", str(server_info.get('tcp_port', 'Unknown'))),
            ("Current Database", f"db{server_info.get('current_db', 0)}"),
        ]
        
        self._create_info_grid(basic_frame, basic_info)
        
        # 运行时信息
        runtime_frame = ttk.LabelFrame(parent, text="Runtime Information", padding=5)
        runtime_frame.pack(fill=tk.X, pady=(0, 5))
        
        uptime_days = server_info.get('uptime_in_days', 0)
        uptime_seconds = server_info.get('uptime_in_seconds', 0)
        uptime_hours = (uptime_seconds % 86400) // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        uptime_text = f"{uptime_days}d {uptime_hours}h {uptime_minutes}m"
        
        runtime_info = [
            ("Uptime", uptime_text),
            ("Connected Clients", str(server_info.get('connected_clients', 0))),
            ("Commands Processed", f"{server_info.get('total_commands_processed', 0):,}"),
            ("Operations/sec", str(server_info.get('instantaneous_ops_per_sec', 0))),
        ]
        
        self._create_info_grid(runtime_frame, runtime_info)
        
        # 内存信息
        memory_frame = ttk.LabelFrame(parent, text="Memory Information", padding=5)
        memory_frame.pack(fill=tk.BOTH, expand=True)
        
        memory_info = [
            ("Used Memory", server_info.get('used_memory_human', 'Unknown')),
            ("Peak Memory", server_info.get('used_memory_peak_human', 'Unknown')),
            ("System Memory", server_info.get('total_system_memory_human', 'Unknown')),
            ("Max Memory", server_info.get('maxmemory_human', 'Not set') if server_info.get('maxmemory_human') else 'Not set'),
        ]
        
        self._create_info_grid(memory_frame, memory_info)
    
    def _create_right_info_panel(self, parent, server_info):
        """创建右侧信息面板"""
        # 统计信息
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding=5)
        stats_frame.pack(fill=tk.X, pady=(0, 5))
        
        stats_info = [
            ("Keyspace Hits", f"{server_info.get('keyspace_hits', 0):,}"),
            ("Keyspace Misses", f"{server_info.get('keyspace_misses', 0):,}"),
            ("Hit Rate", f"{server_info.get('hit_rate', 0)}%"),
            ("Expired Keys", f"{server_info.get('expired_keys', 0):,}"),
            ("Evicted Keys", f"{server_info.get('evicted_keys', 0):,}"),
        ]
        
        self._create_info_grid(stats_frame, stats_info)
        
        # 数据库信息
        databases = server_info.get('databases', {})
        if databases:
            db_frame = ttk.LabelFrame(parent, text="Database Information", padding=5)
            db_frame.pack(fill=tk.BOTH, expand=True)
            
            # 创建数据库信息表格
            db_tree_frame = ttk.Frame(db_frame)
            db_tree_frame.pack(fill=tk.BOTH, expand=True)
            
            # 数据库信息表格
            columns = ('Database', 'Keys', 'Expires')
            db_tree = ttk.Treeview(db_tree_frame, columns=columns, show='headings', height=8)
            
            # 设置列标题和宽度
            db_tree.heading('Database', text='Database')
            db_tree.heading('Keys', text='Keys')
            db_tree.heading('Expires', text='With TTL')
            
            db_tree.column('Database', width=80, minwidth=60)
            db_tree.column('Keys', width=80, minwidth=60)
            db_tree.column('Expires', width=80, minwidth=60)
            
            # 添加数据库信息
            for db_num, db_info in sorted(databases.items(), key=lambda x: int(x[0])):
                current_marker = " (current)" if int(db_num) == server_info.get('current_db', 0) else ""
                db_name = f"db{db_num}{current_marker}"
                keys_count = f"{db_info['keys']:,}"
                expires_count = f"{db_info['expires']:,}" if db_info['expires'] > 0 else "0"
                
                # 高亮当前数据库
                tags = ('current',) if int(db_num) == server_info.get('current_db', 0) else ()
                db_tree.insert('', tk.END, values=(db_name, keys_count, expires_count), tags=tags)
            
            # 配置当前数据库的样式
            db_tree.tag_configure('current', background='#E8F4FD')
            
            db_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # 滚动条
            db_scroll = ttk.Scrollbar(db_tree_frame, orient=tk.VERTICAL, command=db_tree.yview)
            db_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            db_tree.configure(yscrollcommand=db_scroll.set)
        else:
            # 如果没有数据库信息，显示占位内容
            placeholder_frame = ttk.LabelFrame(parent, text="Additional Information", padding=5)
            placeholder_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(placeholder_frame, text="No additional database information available", 
                     foreground='#666666').pack(expand=True)
    
    def _create_info_grid(self, parent, info_list):
        """创建信息网格布局"""
        for i, (label, value) in enumerate(info_list):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill=tk.X, pady=1)
            
            # 标签
            label_widget = ttk.Label(row_frame, text=f"{label}:", width=18, anchor='w')
            label_widget.pack(side=tk.LEFT)
            
            # 值
            value_widget = ttk.Label(row_frame, text=str(value), foreground='#0066CC', anchor='w')
            value_widget.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
    
    def _refresh_server_info(self):
        """刷新服务器信息"""
        self.clear_details()
        self._show_welcome()
    
    def clear_details(self):
        """清空详情"""
        for widget in self.key_details_frame.winfo_children():
            widget.destroy()
        self._show_welcome()
    
    def load_key_details(self, key):
        """加载键详情"""
        def load_thread():
            try:
                # 先尝试快速检查连接
                redis_client = self.main_window.get_redis_client()
                if not redis_client:
                    self.main_window.root.after(0, lambda: messagebox.showerror("Error", "No Redis connection available"))
                    return
                
                # 使用短超时进行快速ping测试，避免阻塞UI
                import socket
                original_timeout = redis_client.connection_pool.connection_kwargs.get('socket_timeout', 5)
                
                # 临时设置短超时进行连接测试
                redis_client.connection_pool.connection_kwargs['socket_timeout'] = 2
                redis_client.connection_pool.connection_kwargs['socket_connect_timeout'] = 2
                
                try:
                    # 快速ping测试
                    redis_client.ping()
                    # 连接正常，恢复原超时设置并直接加载
                    redis_client.connection_pool.connection_kwargs['socket_timeout'] = original_timeout
                    self._continue_load_key_details(key)
                except (redis.ConnectionError, redis.TimeoutError, socket.timeout, socket.error) as ping_error:
                    # 恢复原超时设置
                    redis_client.connection_pool.connection_kwargs['socket_timeout'] = original_timeout
                    raise ping_error
                
            except Exception as e:
                # 连接有问题，异步重连
                self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("🔄 Connection lost, attempting to reconnect..."))
                
                def on_reconnect_success(result):
                    if result:
                        # 重连成功，继续加载
                        self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("🔄 Reconnected, loading key..."))
                        self._continue_load_key_details(key)
                    else:
                        # 重连失败
                        self.main_window.root.after(0, lambda: messagebox.showerror("Connection Error", 
                            "Redis connection lost and failed to reconnect. Please check your connection."))
                        self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("❌ Connection failed"))
                
                def on_reconnect_error(error):
                    self.main_window.root.after(0, lambda: messagebox.showerror("Connection Error", 
                        f"Failed to reconnect: {error}"))
                    self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("❌ Reconnection failed"))
                
                self.main_window.redis_conn.check_and_reconnect_async(on_reconnect_success, on_reconnect_error)
        
        # 在后台线程中执行连接检查
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _continue_load_key_details(self, key):
        """继续加载键详情（在连接确认后）"""
        def load_thread():
            try:
                self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status(f"Loading key '{key}'..."))
                
                redis_client = self.main_window.get_redis_client()
                redis_ops = RedisOperations(redis_client)
                
                # 设置短超时进行操作，避免长时间阻塞
                original_timeout = redis_client.connection_pool.connection_kwargs.get('socket_timeout', 5)
                redis_client.connection_pool.connection_kwargs['socket_timeout'] = 5  # 5秒超时用于数据操作
                
                try:
                    # 获取键信息
                    key_info = redis_ops.get_key_info(key)
                    if not key_info:
                        self.main_window.root.after(0, lambda: messagebox.showerror("Error", f"Key '{key}' does not exist"))
                        self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("❌ Key not found"))
                        return
                    
                    # 获取值
                    value = redis_ops.get_key_value(key, key_info['type'])
                    
                    # 恢复原超时设置
                    redis_client.connection_pool.connection_kwargs['socket_timeout'] = original_timeout
                    
                    self.main_window.root.after(0, lambda: self._show_key_details(key, key_info, value))
                    self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status(f"✅ Loaded key '{key}'"))
                    
                except Exception as op_error:
                    # 恢复原超时设置
                    redis_client.connection_pool.connection_kwargs['socket_timeout'] = original_timeout
                    raise op_error
                
            except Exception as e:
                error_msg = f"Failed to load key '{key}': {str(e)}"
                # 检查是否是连接相关的错误
                if any(err_type in str(e).lower() for err_type in ["connection", "timeout", "broken pipe", "reset"]):
                    # 连接错误，再次尝试异步重连
                    def retry_on_success(result):
                        if result:
                            self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("🔄 Reconnected, retrying..."))
                            # 重试加载
                            self._continue_load_key_details(key)
                        else:
                            self.main_window.root.after(0, lambda: messagebox.showerror("Error", "Failed to reconnect and load key"))
                            self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("❌ Failed to load key"))
                    
                    def retry_on_error(error):
                        self.main_window.root.after(0, lambda: messagebox.showerror("Error", f"Reconnection failed: {error}"))
                        self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("❌ Reconnection failed"))
                    
                    self.main_window.redis_conn.check_and_reconnect_async(retry_on_success, retry_on_error)
                else:
                    self.main_window.root.after(0, lambda: messagebox.showerror("Error", error_msg))
                    self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("❌ Failed to load key"))
        
        # 在后台线程中执行实际的加载操作
        threading.Thread(target=load_thread, daemon=True).start()
    
    def _show_key_details(self, key, key_info, value):
        """显示键详情 - 使用section布局实现真正的自适应"""
        # 清空详情框架
        for widget in self.key_details_frame.winfo_children():
            widget.destroy()
        
        # 重新配置key_details_frame的grid权重 - 确保只有值区域可扩展
        for i in range(10):
            if i == 2:  # 值区域(第2行)可扩展
                self.key_details_frame.grid_rowconfigure(i, weight=1)
            else:
                self.key_details_frame.grid_rowconfigure(i, weight=0)
        self.key_details_frame.grid_columnconfigure(0, weight=1)
        
        key_type = key_info['type']
        ttl = key_info['ttl']
        
        # 固定区域：键信息 (第0行)
        info_section = self._create_fixed_section(0)
        info_frame = ttk.Frame(info_section)
        info_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 使用文本框显示完整键名
        ttk.Label(info_frame, text="Key:").pack(anchor=tk.W)
        key_text = tk.Text(info_frame, height=2, wrap=tk.WORD)
        key_text.pack(fill=tk.X, pady=(0, 5))
        key_text.insert(tk.END, key)
        key_text.config(state=tk.DISABLED)
        
        ttk.Label(info_frame, text=f"Type: {key_type}").pack(anchor=tk.W)
        
        # TTL 显示和编辑
        ttl_frame = ttk.Frame(info_frame)
        ttl_frame.pack(anchor=tk.W, fill=tk.X)
        
        ttl_text = ttl if ttl > 0 else 'Never expires'
        self.ttl_label = ttk.Label(ttl_frame, text=f"TTL: {ttl_text}")
        self.ttl_label.pack(side=tk.LEFT)
        
        # 存储当前key和ttl用于编辑
        self.current_key = key
        self.current_ttl = ttl
        
        ttk.Button(ttl_frame, text="✏️", width=3, 
                  command=lambda: self._edit_ttl(key, ttl)).pack(side=tk.LEFT, padx=(10, 0))
        
        # 固定区域：查询框架 (第1行) - 固定高度，不随窗口放大而增高
        query_section = self._create_fixed_section(1)
        query_frame = ttk.LabelFrame(query_section, text="Query & Edit")
        query_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # 查询输入 - 使用固定高度的布局
        query_input_frame = ttk.Frame(query_frame)
        query_input_frame.pack(fill=tk.X, padx=5, pady=8)  # 增加padding但保持固定高度
        
        ttk.Label(query_input_frame, text="Query:").pack(side=tk.LEFT)
        self.query_var = tk.StringVar(value=key)  # 设置默认值为当前键
        query_entry = ttk.Entry(query_input_frame, textvariable=self.query_var)
        query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        query_entry.bind('<Return>', lambda e: self._execute_key_query(key, key_type))
        
        ttk.Button(query_input_frame, text="Query", 
                  command=lambda: self._execute_key_query(key, key_type)).pack(side=tk.RIGHT)
        
        # 可扩展区域：值编辑区域 (第2行，可扩展)
        value_section = self._create_expandable_section(2)
        value_frame = ttk.LabelFrame(value_section, text="Value")
        value_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        value_frame.grid_rowconfigure(0, weight=1)
        value_frame.grid_columnconfigure(0, weight=1)
        
        # 根据数据类型选择显示方式
        if key_type in ['list', 'set', 'zset', 'hash']:
            self._show_structured_value(value_frame, key, key_type, value)
        else:
            self._show_text_value(value_frame, key, key_type, value)
        
        # 固定区域：操作按钮 (第3行)
        self._create_action_buttons(key, key_type)
    
    def _show_structured_value(self, parent, key, key_type, value):
        """显示结构化数据（表格形式） - 使用固定高度防止filter被挤压"""
        # 重新配置父容器的grid权重 - 确保只有表格区域可扩展
        parent.grid_rowconfigure(0, weight=0)  # 查询/过滤区域固定高度
        parent.grid_rowconfigure(1, weight=1)  # 表格区域可扩展
        parent.grid_rowconfigure(2, weight=0)  # 操作按钮区域固定高度
        parent.grid_columnconfigure(0, weight=1)
        
        # 清理之前的过滤状态标签
        if hasattr(self, 'filter_status_label'):
            self.filter_status_label.destroy()
            delattr(self, 'filter_status_label')
        
        # 先设置原始数据，确保总数统计正确
        if key_type == 'hash':
            self.original_hash_data = value if isinstance(value, dict) else {}
        elif key_type == 'list':
            self.original_list_data = value if isinstance(value, list) else []
        elif key_type == 'set':
            self.original_set_data = list(value) if isinstance(value, (list, set)) else []
        elif key_type == 'zset':
            self.original_zset_data = value if isinstance(value, list) else []
        
        # 固定区域：查询框架 (第0行) - 设置固定高度防止被挤压
        query_frame = ttk.Frame(parent, height=40)  # 设置固定高度40像素
        query_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        query_frame.pack_propagate(False)  # 防止子组件改变父容器大小
        
        # 根据类型创建过滤输入
        self._create_filter_input(query_frame, key, key_type)
        
        # 可扩展区域：表格显示 (第1行，可扩展)
        table_container = ttk.Frame(parent)
        table_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        self._create_data_table(table_container, key, key_type, value)
        
        # 固定区域：操作按钮 (第2行) - 设置固定高度
        btn_container = ttk.Frame(parent, height=40)  # 设置固定高度40像素
        btn_container.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        btn_container.pack_propagate(False)  # 防止子组件改变父容器大小
        self._create_table_buttons(btn_container, key, key_type)
    
    def _update_total_count_display(self, key_type):
        """更新总数显示"""
        # 查找并更新总数标签
        if hasattr(self, 'total_count_label'):
            if key_type == 'hash':
                total_count = len(self.original_hash_data) if hasattr(self, 'original_hash_data') else 0
                self.total_count_label.config(text=f"Total: {total_count} fields")
            elif key_type == 'list':
                total_count = len(self.original_list_data) if hasattr(self, 'original_list_data') else 0
                self.total_count_label.config(text=f"Total: {total_count} items")
            elif key_type == 'set':
                total_count = len(self.original_set_data) if hasattr(self, 'original_set_data') else 0
                self.total_count_label.config(text=f"Total: {total_count} members")
            elif key_type == 'zset':
                total_count = len(self.original_zset_data) if hasattr(self, 'original_zset_data') else 0
                self.total_count_label.config(text=f"Total: {total_count} members")
    
    def _create_filter_input(self, parent, key, key_type):
        """创建过滤输入"""
        if key_type == 'hash':
            ttk.Label(parent, text="Hash Key:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(parent, textvariable=self.struct_query_var, width=25)  # 设置固定宽度
            query_entry.pack(side=tk.LEFT, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self._filter_hash_data(key))
            ttk.Button(parent, text="Find", 
                      command=lambda: self._filter_hash_data(key)).pack(side=tk.LEFT, padx=(0, 10))
            
            # 添加总数统计标签
            total_count = len(self.original_hash_data) if hasattr(self, 'original_hash_data') else 0
            self.total_count_label = ttk.Label(parent, text=f"Total: {total_count} fields", 
                                              foreground='#666666')
            self.total_count_label.pack(side=tk.LEFT)
            
        elif key_type in ['list', 'zset']:
            ttk.Label(parent, text="Filter:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(parent, textvariable=self.struct_query_var, width=25)  # 设置固定宽度
            query_entry.pack(side=tk.LEFT, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self._filter_list_zset_data(key, key_type))
            ttk.Button(parent, text="Find", 
                      command=lambda: self._filter_list_zset_data(key, key_type)).pack(side=tk.LEFT, padx=(0, 10))
            
            # 添加总数统计标签
            if key_type == 'list':
                total_count = len(self.original_list_data) if hasattr(self, 'original_list_data') else 0
                self.total_count_label = ttk.Label(parent, text=f"Total: {total_count} items", 
                                                  foreground='#666666')
            elif key_type == 'zset':
                total_count = len(self.original_zset_data) if hasattr(self, 'original_zset_data') else 0
                self.total_count_label = ttk.Label(parent, text=f"Total: {total_count} members", 
                                                  foreground='#666666')
            self.total_count_label.pack(side=tk.LEFT)
            
        elif key_type == 'set':
            ttk.Label(parent, text="Filter:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(parent, textvariable=self.struct_query_var, width=25)  # 设置固定宽度
            query_entry.pack(side=tk.LEFT, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self._filter_set_data(key))
            ttk.Button(parent, text="Find", 
                      command=lambda: self._filter_set_data(key)).pack(side=tk.LEFT, padx=(0, 10))
            
            # 添加总数统计标签
            total_count = len(self.original_set_data) if hasattr(self, 'original_set_data') else 0
            self.total_count_label = ttk.Label(parent, text=f"Total: {total_count} members", 
                                              foreground='#666666')
            self.total_count_label.pack(side=tk.LEFT)
    
    def _create_data_table(self, parent, key, key_type, value):
        """创建数据表格 - 使用grid布局"""
        # 配置父容器的grid权重
        parent.grid_rowconfigure(0, weight=1)  # 表格区域可扩展
        parent.grid_rowconfigure(1, weight=0)  # 状态标签区域固定高度
        parent.grid_columnconfigure(0, weight=1)
        
        table_frame = ttk.Frame(parent)
        table_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置table_frame的grid权重
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # 配置Treeview样式
        style_name = self.main_window.style_manager.configure_treeview_style(key_type)
        
        # 根据类型创建表格
        if key_type == 'hash':
            columns = ('Field', 'Value')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name, selectmode='extended')
            self.data_tree.heading('Field', text='Field')
            self.data_tree.heading('Value', text='Value')
            # 自适应列宽：Field列占30%，Value列占70%
            self.data_tree.column('Field', width=200, minwidth=100, stretch=True)
            self.data_tree.column('Value', width=400, minwidth=200, stretch=True)
            
            # 加载数据到树形控件（原始数据已在_show_structured_value中设置）
            self._load_hash_data_to_tree(self.original_hash_data)
            
        elif key_type == 'list':
            columns = ('Index', 'Value')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name, selectmode='extended')
            self.data_tree.heading('Index', text='Index')
            self.data_tree.heading('Value', text='Value')
            # 自适应列宽：Index列固定宽度，Value列自适应
            self.data_tree.column('Index', width=80, minwidth=60, stretch=False)
            self.data_tree.column('Value', width=500, minwidth=200, stretch=True)
            
            # 加载数据到树形控件（原始数据已在_show_structured_value中设置）
            self._load_list_data_to_tree(self.original_list_data)
            
        elif key_type == 'set':
            columns = ('Value',)
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name, selectmode='extended')
            self.data_tree.heading('Value', text='Value')
            # 自适应列宽：Value列占满整个宽度
            self.data_tree.column('Value', width=600, minwidth=200, stretch=True)
            
            # 加载数据到树形控件（原始数据已在_show_structured_value中设置）
            self._load_set_data_to_tree(self.original_set_data)
            
        elif key_type == 'zset':
            columns = ('Score', 'Member')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name, selectmode='extended')
            self.data_tree.heading('Score', text='Score')
            self.data_tree.heading('Member', text='Member')
            # 自适应列宽：Score列固定宽度，Member列自适应
            self.data_tree.column('Score', width=100, minwidth=80, stretch=False)
            self.data_tree.column('Member', width=500, minwidth=200, stretch=True)
            
            # 加载数据到树形控件（原始数据已在_show_structured_value中设置）
            self._load_zset_data_to_tree(self.original_zset_data)
        
        self.data_tree.grid(row=0, column=0, sticky="nsew")
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.data_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 绑定双击事件和右键菜单
        self.data_tree.bind('<Double-1>', lambda e: self._edit_table_item(key, key_type))
        self.data_tree.bind('<Button-2>', lambda e: self._show_context_menu(e, key, key_type))  # 右键菜单
        self.data_tree.bind('<Control-Button-1>', lambda e: self._show_context_menu(e, key, key_type))  # macOS Ctrl+点击
    
    def _create_table_buttons(self, parent, key, key_type):
        """创建表格操作按钮"""
        # 直接在父容器中创建按钮，不再创建额外的frame
        ttk.Button(parent, text="Add Item", 
                  command=lambda: self._add_table_item(key, key_type)).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Button(parent, text="Delete Item", 
                  command=lambda: self._delete_table_item(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(parent, text="Update All", 
                  command=lambda: self._update_structured_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(parent, text="Refresh", 
                  command=lambda: self.load_key_details(key)).pack(side=tk.LEFT)
    
    def _show_text_value(self, parent, key, key_type, value):
        """显示文本数据 - 使用固定高度防止按钮被挤压"""
        # 重新配置父容器的grid权重 - 确保只有文本区域可扩展
        parent.grid_rowconfigure(0, weight=0)  # 格式化按钮区域固定高度
        parent.grid_rowconfigure(1, weight=1)  # 文本区域可扩展
        parent.grid_columnconfigure(0, weight=1)
        
        # 固定区域：格式化按钮 (第0行) - 设置固定高度防止被挤压
        format_frame = ttk.Frame(parent, height=40)  # 设置固定高度40像素
        format_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        format_frame.pack_propagate(False)  # 防止子组件改变父容器大小
        
        ttk.Button(format_frame, text="Format JSON", 
                  command=lambda: self._format_json_value()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(format_frame, text="Minify JSON", 
                  command=lambda: self._minify_json_value()).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(format_frame, text="Format PHP", 
                  command=lambda: self._format_php_value()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(format_frame, text="Minify PHP", 
                  command=lambda: self._minify_php_value()).pack(side=tk.LEFT)
        
        # 可扩展区域：文本编辑器 (第1行，可扩展)
        text_container = ttk.Frame(parent)
        text_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)  # 文本区域
        text_container.grid_rowconfigure(1, weight=0)  # 搜索按钮区域 - 固定高度
        text_container.grid_columnconfigure(0, weight=1)
        
        # 处理值的显示格式
        display_value = self._format_value_for_display(value)
        
        # 确保有内容显示
        if not display_value:
            display_value = "(empty or unable to display)"
        
        self.value_text, self.text_frame = self._create_auto_text(text_container, display_value)
        
        # 设置JSON文本组件配置和语法高亮
        setup_json_text_widget(self.value_text)
        apply_json_syntax_highlighting(self.value_text)
        
        # 确保文本框能接收焦点和键盘事件
        self.value_text.focus_set()
    
    def _format_value_for_display(self, value):
        """格式化值用于显示，处理二进制数据等特殊情况"""
        if value is None:
            return "(nil)"
        
        if isinstance(value, bytes):
            # 处理空 bytes
            if len(value) == 0:
                return "(empty)"
            
            # 检查是否全是 null 字节（常见于 bitmap）
            if all(b == 0 for b in value):
                return self._format_binary_value(value)
            
            # 尝试解码为 UTF-8
            try:
                decoded = value.decode('utf-8')
                # 检查是否包含不可打印字符（可能是二进制数据如 bitmap）
                # 包括 null 字符 \x00
                if any(ord(c) < 32 and c not in '\n\r\t' for c in decoded):
                    # 包含不可打印字符，显示为十六进制
                    return self._format_binary_value(value)
                # 检查解码后是否为空或只有空白
                if not decoded.strip():
                    return self._format_binary_value(value)
                return decoded
            except UnicodeDecodeError:
                # 解码失败，显示为十六进制
                return self._format_binary_value(value)
        
        # 处理空字符串
        if value == "" or value == b"":
            return "(empty)"
        
        return str(value)
    
    def _format_binary_value(self, value):
        """格式化二进制值（如 bitmap）为可读格式"""
        if not isinstance(value, bytes):
            return str(value)
        
        # 显示十六进制和二进制表示
        hex_str = value.hex()
        
        # 格式化为每字节一组
        hex_formatted = ' '.join(hex_str[i:i+2] for i in range(0, len(hex_str), 2))
        
        # 生成二进制位表示（用于 bitmap）
        binary_str = ''.join(format(byte, '08b') for byte in value)
        
        # 计算设置为 1 的位数
        bit_count = sum(bin(byte).count('1') for byte in value)
        
        result = f"[Binary Data - {len(value)} bytes, {bit_count} bits set]\n\n"
        result += f"Hex: {hex_formatted}\n\n"
        result += f"Binary: {binary_str}\n\n"
        result += f"Raw: {repr(value)}"
        
        return result
    
    
    def _create_action_buttons(self, key, key_type):
        """创建操作按钮"""
        btn_section = self._create_fixed_section(3)
        btn_frame = ttk.Frame(btn_section)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Update", 
                  command=lambda: self._update_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Delete", 
                  command=lambda: self._delete_key(key)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", 
                  command=lambda: self.load_key_details(key)).pack(side=tk.LEFT)
    
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
            # zrange with withscores=True 返回的是元组列表 [(member, score), ...]
            for item in zset_data:
                if isinstance(item, tuple) and len(item) == 2:
                    member, score = item
                    self.data_tree.insert('', tk.END, values=(score, member))
    
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
                    total_count = len(self.original_zset_data)
                    self._update_filter_status(total_count, total_count, filter_text)
                    return
                
                filtered_data = []
                filter_lower = filter_text.lower()
                
                # zset 数据是元组列表 [(member, score), ...]
                for item in self.original_zset_data:
                    if isinstance(item, tuple) and len(item) == 2:
                        member, score = item
                        
                        member_str = str(member).lower()
                        score_str = str(score).lower()
                        
                        if filter_lower in member_str or filter_lower in score_str:
                            filtered_data.append((member, score))
                
                self._load_zset_data_to_tree(filtered_data)
                filtered_count = len(filtered_data)
                total_count = len(self.original_zset_data)
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
        
        # 找到正确的父容器 - 应该是table_container (data_tree.master.master)
        table_frame = self.data_tree.master  # table_frame
        parent_frame = table_frame.master    # table_container
        self.filter_status_label = ttk.Label(parent_frame, 
                                            text=f"Showing {filtered_count} of {total_count} items" + 
                                                 (f" (filtered by: '{filter_text}')" if filter_text else ""),
                                            font=self.main_window.style_manager.get_font(FONT_SIZE_SMALL),
                                            foreground='#666666')
        # 使用grid布局，放在表格下方
        self.filter_status_label.grid(row=1, column=0, sticky="w", padx=5, pady=(5, 0))
    
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
        elif key_type == 'list':
            dialog = AddListDialog(self.main_window.root, key, self.main_window)
            result = dialog.show()
            if result:
                self._refresh_current_display(key, key_type)
        elif key_type == 'set':
            dialog = AddSetDialog(self.main_window.root, key, self.main_window)
            result = dialog.show()
            if result:
                self._refresh_current_display(key, key_type)
        elif key_type == 'zset':
            dialog = AddZSetDialog(self.main_window.root, key, self.main_window)
            result = dialog.show()
            if result:
                self._refresh_current_display(key, key_type)
        else:
            messagebox.showinfo("Info", f"Add item not supported for type '{key_type}'")
    
    def _delete_table_item(self, key, key_type):
        """删除表格项（支持批量删除）"""
        selections = self.data_tree.selection()
        if not selections:
            messagebox.showwarning("No Selection", "Please select one or more items to delete.")
            return
        
        # 获取所有选中项的信息
        items_to_delete = []
        for selection in selections:
            item = self.data_tree.item(selection)
            values = item['values']
            items_to_delete.append(values)
        
        # 根据数据类型确定删除的内容描述
        if len(items_to_delete) == 1:
            # 单个删除
            values = items_to_delete[0]
            if key_type == 'hash':
                field = values[0]
                confirm_msg = f"Are you sure you want to delete hash field '{field}' from key '{key}'?"
                delete_desc = f"hash field '{field}'"
            elif key_type == 'set':
                member = values[0]
                confirm_msg = f"Are you sure you want to delete member '{member}' from set '{key}'?"
                delete_desc = f"set member '{member}'"
            elif key_type == 'list':
                index, value = values[0], values[1]
                confirm_msg = f"Are you sure you want to delete list item at index {index} (value: '{value}') from key '{key}'?"
                delete_desc = f"list item at index {index}"
            elif key_type == 'zset':
                score, member = values[0], values[1]
                confirm_msg = f"Are you sure you want to delete member '{member}' (score: {score}) from sorted set '{key}'?"
                delete_desc = f"zset member '{member}'"
        else:
            # 批量删除
            count = len(items_to_delete)
            if key_type == 'hash':
                confirm_msg = f"Are you sure you want to delete {count} hash fields from key '{key}'?"
                delete_desc = f"{count} hash fields"
            elif key_type == 'set':
                confirm_msg = f"Are you sure you want to delete {count} members from set '{key}'?"
                delete_desc = f"{count} set members"
            elif key_type == 'list':
                confirm_msg = f"Are you sure you want to delete {count} items from list '{key}'?"
                delete_desc = f"{count} list items"
            elif key_type == 'zset':
                confirm_msg = f"Are you sure you want to delete {count} members from sorted set '{key}'?"
                delete_desc = f"{count} zset members"
        
        if key_type not in ['hash', 'set', 'list', 'zset']:
            messagebox.showerror("Error", f"Delete operation not supported for type '{key_type}'")
            return
        
        # 确认删除
        if not messagebox.askyesno("Confirm Delete", confirm_msg):
            return
        
        try:
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            success_count = 0
            failed_items = []
            
            # 执行删除操作
            if key_type == 'hash':
                for values in items_to_delete:
                    field = values[0]
                    result = redis_ops.hash_delete(key, field)
                    if result:
                        success_count += 1
                    else:
                        failed_items.append(field)
            
            elif key_type == 'set':
                # 批量删除set成员
                members = [values[0] for values in items_to_delete]
                result = redis_ops.set_remove(key, *members)
                success_count = result  # set_remove返回实际删除的数量
                if success_count < len(members):
                    failed_items = members[success_count:]
            
            elif key_type == 'list':
                # List批量删除需要按索引从大到小排序，避免索引变化影响
                indices = [(int(values[0]), values) for values in items_to_delete]
                indices.sort(reverse=True)  # 从大到小排序
                
                for index, values in indices:
                    result = redis_ops.list_remove_by_index(key, index)
                    if result:
                        success_count += 1
                    else:
                        failed_items.append(f"index {index}")
            
            elif key_type == 'zset':
                # 批量删除zset成员
                members = [values[1] for values in items_to_delete]  # member在第二列
                result = redis_ops.zset_remove(key, *members)
                success_count = result  # zset_remove返回实际删除的数量
                if success_count < len(members):
                    failed_items = members[success_count:]
            
            # 显示结果
            if success_count > 0:
                if failed_items:
                    messagebox.showwarning("Partial Success", 
                                         f"Successfully deleted {success_count} items.\n"
                                         f"Failed to delete: {', '.join(map(str, failed_items))}")
                else:
                    messagebox.showinfo("Success", f"Successfully deleted {delete_desc}")
            else:
                messagebox.showwarning("Warning", f"No items were deleted. They may not exist.")
            
            # 刷新显示
            self._refresh_current_display(key, key_type)
            
            # 刷新左侧键列表（以防键被完全删除）
            self.main_window.left_panel.search_keys()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete {delete_desc}: {str(e)}")
    
    def _show_context_menu(self, event, key, key_type):
        """显示右键菜单"""
        # 选中点击的项
        item = self.data_tree.identify_row(event.y)
        if item:
            # 如果点击的项没有被选中，则选中它
            if item not in self.data_tree.selection():
                self.data_tree.selection_set(item)
            
            # 创建右键菜单
            context_menu = tk.Menu(self.main_window.root, tearoff=0)
            
            # 获取选中项数量
            selection_count = len(self.data_tree.selection())
            
            # 根据数据类型和选中数量添加菜单项
            if selection_count == 1:
                # 单选菜单
                if key_type == 'hash':
                    context_menu.add_command(label="✏️ Edit Field", 
                                           command=lambda: self._edit_table_item(key, key_type))
                    context_menu.add_separator()
                    context_menu.add_command(label="🗑️ Delete Field", 
                                           command=lambda: self._delete_table_item(key, key_type))
                elif key_type == 'set':
                    context_menu.add_command(label="✏️ Edit Member", 
                                           command=lambda: self._edit_table_item(key, key_type))
                    context_menu.add_separator()
                    context_menu.add_command(label="🗑️ Delete Member", 
                                           command=lambda: self._delete_table_item(key, key_type))
                elif key_type == 'list':
                    context_menu.add_command(label="✏️ Edit Item", 
                                           command=lambda: self._edit_table_item(key, key_type))
                    context_menu.add_separator()
                    context_menu.add_command(label="🗑️ Delete Item", 
                                           command=lambda: self._delete_table_item(key, key_type))
                elif key_type == 'zset':
                    context_menu.add_command(label="✏️ Edit Member", 
                                           command=lambda: self._edit_table_item(key, key_type))
                    context_menu.add_separator()
                    context_menu.add_command(label="🗑️ Delete Member", 
                                           command=lambda: self._delete_table_item(key, key_type))
            else:
                # 多选菜单
                if key_type == 'hash':
                    context_menu.add_command(label=f"🗑️ Delete {selection_count} Fields", 
                                           command=lambda: self._delete_table_item(key, key_type))
                elif key_type == 'set':
                    context_menu.add_command(label=f"🗑️ Delete {selection_count} Members", 
                                           command=lambda: self._delete_table_item(key, key_type))
                elif key_type == 'list':
                    context_menu.add_command(label=f"🗑️ Delete {selection_count} Items", 
                                           command=lambda: self._delete_table_item(key, key_type))
                elif key_type == 'zset':
                    context_menu.add_command(label=f"🗑️ Delete {selection_count} Members", 
                                           command=lambda: self._delete_table_item(key, key_type))
            
            # 添加通用菜单项
            context_menu.add_separator()
            context_menu.add_command(label="🔄 Refresh", 
                                   command=lambda: self.load_key_details(key))
            
            # 添加选择相关菜单
            context_menu.add_separator()
            context_menu.add_command(label="📋 Select All", 
                                   command=lambda: self.data_tree.selection_set(self.data_tree.get_children()))
            if selection_count > 0:
                context_menu.add_command(label="❌ Clear Selection", 
                                       command=lambda: self.data_tree.selection_remove(self.data_tree.selection()))
            
            # 显示菜单
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
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
            
            # 更新总数显示
            self._update_total_count_display(key_type)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh display: {e}")
    
    def _update_key(self, key, key_type):
        """更新键"""
        try:
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            # 检查连接状态，如果断开则尝试重连
            if not self.main_window.redis_conn.check_and_reconnect():
                messagebox.showerror("Connection Error", "Redis connection lost and failed to reconnect")
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
            # 检查是否是连接相关的错误，如果是则尝试重连
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                try:
                    if self.main_window.redis_conn.check_and_reconnect():
                        # 重试更新操作
                        redis_ops = RedisOperations(self.main_window.get_redis_client())
                        if hasattr(self, 'value_text'):
                            new_value = self.value_text.get(1.0, tk.END).strip()
                            redis_ops.set_key_value(key, new_value, key_type)
                        messagebox.showinfo("Success", "Key updated successfully after reconnection!")
                        self.load_key_details(key)
                        return
                except Exception as retry_e:
                    messagebox.showerror("Error", f"Failed to update key after reconnection: {retry_e}")
                    return
            
            messagebox.showerror("Error", f"Failed to update key: {e}")
    
    def _update_structured_key(self, key, key_type):
        """更新结构化键"""
        # 这里实现复杂的结构化数据更新逻辑
        # 包括过滤状态的处理等
        pass
    
    def _edit_ttl(self, key, current_ttl):
        """编辑键的TTL"""
        from tkinter import simpledialog
        
        # 构建提示信息
        if current_ttl > 0:
            prompt = f"Current TTL: {current_ttl} seconds\n\nEnter new TTL in seconds:\n(Enter -1 to remove expiration, 0 to delete key immediately)"
            initial_value = str(current_ttl)
        else:
            prompt = "Key has no expiration.\n\nEnter TTL in seconds:\n(Enter -1 to keep no expiration)"
            initial_value = "-1"
        
        # 弹出输入对话框
        new_ttl_str = simpledialog.askstring(
            "Edit TTL",
            prompt,
            initialvalue=initial_value,
            parent=self.main_window.root
        )
        
        if new_ttl_str is None:
            return  # 用户取消
        
        try:
            new_ttl = int(new_ttl_str.strip())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer")
            return
        
        # 执行TTL更新
        def update_ttl_thread():
            try:
                redis_client = self.main_window.get_redis_client()
                if not redis_client:
                    self.main_window.root.after(0, lambda: messagebox.showerror("Error", "No Redis connection available"))
                    return
                
                if new_ttl == 0:
                    # TTL为0，删除键
                    redis_client.delete(key)
                    self.main_window.root.after(0, lambda: messagebox.showinfo("Success", f"Key '{key}' has been deleted"))
                    self.main_window.root.after(0, lambda: self.main_window.left_panel.search_keys())
                    self.main_window.root.after(0, self.clear_details)
                elif new_ttl < 0:
                    # 移除过期时间
                    redis_client.persist(key)
                    self.main_window.root.after(0, lambda: messagebox.showinfo("Success", "Expiration removed"))
                    self.main_window.root.after(0, lambda: self.load_key_details(key))
                else:
                    # 设置新的TTL
                    redis_client.expire(key, new_ttl)
                    self.main_window.root.after(0, lambda: messagebox.showinfo("Success", f"TTL set to {new_ttl} seconds"))
                    self.main_window.root.after(0, lambda: self.load_key_details(key))
                    
            except Exception as e:
                self.main_window.root.after(0, lambda: messagebox.showerror("Error", f"Failed to update TTL: {e}"))
        
        import threading
        threading.Thread(target=update_ttl_thread, daemon=True).start()
    
    def _delete_key(self, key):
        """删除键"""
        if messagebox.askyesno("Delete Key", f"Are you sure you want to delete '{key}'?"):
            def delete_thread():
                try:
                    redis_client = self.main_window.get_redis_client()
                    if not redis_client:
                        self.main_window.root.after(0, lambda: messagebox.showerror("Error", "No Redis connection available"))
                        return
                    
                    # 使用短超时进行快速ping测试
                    original_timeout = redis_client.connection_pool.connection_kwargs.get('socket_timeout', 5)
                    redis_client.connection_pool.connection_kwargs['socket_timeout'] = 2
                    redis_client.connection_pool.connection_kwargs['socket_connect_timeout'] = 2
                    
                    try:
                        # 快速ping测试
                        redis_client.ping()
                        # 恢复原超时设置并执行删除
                        redis_client.connection_pool.connection_kwargs['socket_timeout'] = original_timeout
                        self._continue_delete_key(key)
                    except (redis.ConnectionError, redis.TimeoutError, socket.timeout, socket.error) as ping_error:
                        # 恢复原超时设置
                        redis_client.connection_pool.connection_kwargs['socket_timeout'] = original_timeout
                        raise ping_error
                    
                except Exception as e:
                    # 连接有问题，异步重连
                    def on_reconnect_success(result):
                        if result:
                            # 重连成功，继续删除
                            self._continue_delete_key(key)
                        else:
                            # 重连失败
                            self.main_window.root.after(0, lambda: messagebox.showerror("Connection Error", "Redis connection lost and failed to reconnect"))
                    
                    def on_reconnect_error(error):
                        self.main_window.root.after(0, lambda: messagebox.showerror("Connection Error", f"Failed to reconnect: {error}"))
                    
                    self.main_window.redis_conn.check_and_reconnect_async(on_reconnect_success, on_reconnect_error)
            
            # 在后台线程中执行连接检查
            threading.Thread(target=delete_thread, daemon=True).start()
    
    def _continue_delete_key(self, key):
        """继续删除键（在连接确认后）"""
        def delete_thread():
            try:
                redis_client = self.main_window.get_redis_client()
                redis_ops = RedisOperations(redis_client)
                redis_ops.delete_key(key)
                
                self.main_window.root.after(0, lambda: messagebox.showinfo("Success", "Key deleted successfully!"))
                
                # 刷新键列表
                self.main_window.left_panel.search_keys()
                
                # 清空详情
                self.main_window.root.after(0, self.clear_details)
                
            except Exception as e:
                # 检查是否是连接相关的错误
                if "connection" in str(e).lower() or "timeout" in str(e).lower():
                    # 连接错误，再次尝试异步重连
                    def retry_on_success(result):
                        if result:
                            # 重试删除操作
                            self._continue_delete_key(key)
                        else:
                            self.main_window.root.after(0, lambda: messagebox.showerror("Error", "Failed to reconnect and delete key"))
                    
                    def retry_on_error(error):
                        self.main_window.root.after(0, lambda: messagebox.showerror("Error", f"Reconnection failed: {error}"))
                    
                    self.main_window.redis_conn.check_and_reconnect_async(retry_on_success, retry_on_error)
                else:
                    self.main_window.root.after(0, lambda: messagebox.showerror("Error", f"Failed to delete key: {e}"))
        
        # 在后台线程中执行删除操作
        threading.Thread(target=delete_thread, daemon=True).start()
    
    def _add_new_key(self):
        """添加新键"""
        dialog = AddNewKeyDialog(self.main_window.root, self.main_window)
        result = dialog.show()
        if result:
            # 刷新左侧键列表
            self.main_window.left_panel.search_keys()
    
    def _execute_key_query(self, key, key_type):
        """执行键查询"""
        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a query")
            return
        
        redis_client = self.main_window.get_redis_client()
        if not redis_client:
            messagebox.showerror("Error", "No Redis connection available")
            return
        
        try:
            # 检查连接状态
            if not self.main_window.redis_conn.check_and_reconnect():
                return
            
            # 如果查询的键名与当前键不同，加载新键
            if query != key:
                self.load_key_details(query)
                return
            
            # 如果是同一个键，刷新当前键的数据
            self.load_key_details(key)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to execute query: {e}")
    
    def _format_json_value(self):
        """格式化JSON值"""
        if not format_json_with_highlighting(self.value_text):
            messagebox.showerror("JSON Error", "Invalid JSON format")
    
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
    
    def _format_php_value(self):
        """格式化PHP序列化值"""
        try:
            from ..utils.helpers import format_php_serialize
            current_value = self.value_text.get(1.0, tk.END).strip()
            formatted = format_php_serialize(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, formatted)
            # 格式化后的是JSON，应用JSON语法高亮
            apply_json_syntax_highlighting(self.value_text)
        except ValueError as e:
            messagebox.showerror("PHP Serialize Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format PHP serialize: {e}")
    
    def _minify_php_value(self):
        """压缩PHP序列化值"""
        try:
            from ..utils.helpers import minify_php_serialize
            current_value = self.value_text.get(1.0, tk.END).strip()
            minified = minify_php_serialize(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, minified)
        except ValueError as e:
            messagebox.showerror("PHP Serialize Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify PHP serialize: {e}")
    
    def _show_search_dialog(self):
        """显示搜索对话框"""
        if not hasattr(self, 'value_text'):
            return
        
        # 创建搜索对话框
        search_dialog = tk.Toplevel(self.main_window.root)
        search_dialog.title("Search Text")
        search_dialog.geometry("400x120")
        search_dialog.transient(self.main_window.root)
        search_dialog.grab_set()
        
        # 居中显示
        search_dialog.update_idletasks()
        x = (search_dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (search_dialog.winfo_screenheight() // 2) - (120 // 2)
        search_dialog.geometry(f"400x120+{x}+{y}")
        
        # 搜索输入
        search_frame = ttk.Frame(search_dialog)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search for:").pack(anchor=tk.W)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(fill=tk.X, pady=(5, 0))
        
        # 按钮框架
        btn_frame = ttk.Frame(search_dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 搜索状态
        status_var = tk.StringVar()
        status_label = ttk.Label(btn_frame, textvariable=status_var, foreground='#666666')
        status_label.pack(side=tk.LEFT)
        
        # 按钮
        ttk.Button(btn_frame, text="Find Next", 
                  command=lambda: self._find_text(search_var.get(), status_var, True)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Find Previous", 
                  command=lambda: self._find_text(search_var.get(), status_var, False)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Close", 
                  command=search_dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 绑定回车键
        search_entry.bind('<Return>', lambda e: self._find_text(search_var.get(), status_var, True))
        search_entry.bind('<Shift-Return>', lambda e: self._find_text(search_var.get(), status_var, False))
        
        # 设置焦点
        search_entry.focus_set()
        
        # 存储搜索状态
        self.search_start_pos = "1.0"
    
    def _find_text(self, search_text, status_var, forward=True):
        """在文本中查找"""
        if not search_text or not hasattr(self, 'value_text'):
            status_var.set("Please enter search text")
            return
        
        # 清除之前的高亮
        self.value_text.tag_remove("search_highlight", "1.0", tk.END)
        
        # 获取当前光标位置
        current_pos = self.value_text.index(tk.INSERT)
        
        # 搜索文本
        pos = None
        if forward:
            # 向前搜索 - 从当前位置向文件末尾搜索
            pos = self.value_text.search(search_text, current_pos, tk.END, nocase=True)
            if not pos:
                # 从头开始搜索（循环到开头）
                pos = self.value_text.search(search_text, "1.0", current_pos, nocase=True)
                if pos:
                    status_var.set("Search wrapped to beginning")
                else:
                    status_var.set("Text not found")
                    return
        else:
            # 向后搜索 - 关键修复：确保搜索起始位置正确
            search_start = current_pos
            
            # 如果当前位置有选中的文本，从选中文本的开始位置搜索
            try:
                sel_start = self.value_text.index(tk.SEL_FIRST)
                sel_end = self.value_text.index(tk.SEL_LAST)
                # 如果光标在选中文本的末尾，从选中文本的开始位置搜索
                if current_pos == sel_end:
                    search_start = sel_start
            except tk.TclError:
                # 没有选中文本，使用当前光标位置
                pass
            
            # 向后搜索
            pos = self.value_text.search(search_text, search_start, "1.0", backwards=True, nocase=True)
            if not pos:
                # 从末尾开始搜索（循环到末尾）
                pos = self.value_text.search(search_text, tk.END, search_start, backwards=True, nocase=True)
                if pos:
                    status_var.set("Search wrapped to end")
                else:
                    status_var.set("Text not found")
                    return
        
        # 高亮找到的文本
        end_pos = f"{pos}+{len(search_text)}c"
        self.value_text.tag_add("search_highlight", pos, end_pos)
        self.value_text.tag_config("search_highlight", background="yellow", foreground="black")
        
        # 选中找到的文本（这样用户可以看到当前匹配）
        self.value_text.tag_remove(tk.SEL, "1.0", tk.END)
        self.value_text.tag_add(tk.SEL, pos, end_pos)
        
        # 根据搜索方向设置光标位置
        if forward:
            # 向前搜索：光标移到匹配文本后面，便于下次继续向前搜索
            self.value_text.mark_set(tk.INSERT, end_pos)
        else:
            # 向后搜索：光标移到匹配文本前面，便于下次继续向后搜索
            self.value_text.mark_set(tk.INSERT, pos)
        
        # 滚动到可见位置
        self.value_text.see(pos)
        
        # 更新状态
        status_var.set(f"Found at {pos}")
        
        # 确保文本框有焦点
        self.value_text.focus_set()