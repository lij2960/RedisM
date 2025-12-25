#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "1.0.0"
__app_name__ = "RedisM"

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import redis
import json
import os
from pathlib import Path
import threading
import time
import paramiko
import socket
from contextlib import contextmanager

class RedisManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{__app_name__} v{__version__}")
        self.root.geometry("1600x1000")
        
        # 设置应用图标和样式
        self.setup_styles()
        
        self.connections = []
        self.current_conn = None
        self.current_conn_index = -1  # 跟踪当前连接的索引
        self.redis_client = None
        self.ssh_client = None
        self.ssh_tunnel = None
        self.keepalive_thread = None
        self.keepalive_running = False
        
        self.setup_ui()
        self.load_connections()
        
    def setup_styles(self):
        """设置应用样式"""
        style = ttk.Style()
        
        # 设置主题
        try:
            style.theme_use('aqua')  # macOS原生主题
        except:
            style.theme_use('clam')  # 备用主题
        
        # 自定义样式
        style.configure('Title.TLabel', font=('SF Pro Display', 14, 'bold'))
        style.configure('Heading.TLabel', font=('SF Pro Display', 12, 'bold'))
        style.configure('Connected.TLabel', foreground='#007AFF', font=('SF Pro Display', 10, 'bold'))
        
        # 连接列表样式
        style.configure('Connected.TFrame', relief='solid', borderwidth=1)
        
        # 设置窗口背景色
        self.root.configure(bg='#F2F2F7')
        
    def setup_ui(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板
        left_frame = ttk.Frame(main_frame, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_frame.pack_propagate(False)
        
        # 右侧面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
    def setup_left_panel(self, parent):
        # 连接管理
        conn_frame = ttk.LabelFrame(parent, text="🔗 Connections", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 连接列表框架
        list_frame = ttk.Frame(conn_frame)
        list_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 连接列表
        self.conn_listbox = tk.Listbox(list_frame, height=6, font=('SF Pro Display', 11),
                                      selectbackground='#007AFF', selectforeground='white',
                                      relief='flat', borderwidth=0, highlightthickness=1,
                                      highlightcolor='#007AFF')
        self.conn_listbox.pack(fill=tk.X)
        self.conn_listbox.bind('<<ListboxSelect>>', self.on_connection_select)
        self.conn_listbox.bind('<Double-1>', self.on_connection_double_click)
        
        # 连接按钮
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(fill=tk.X)
        
        # 第一行按钮
        btn_row1 = ttk.Frame(btn_frame)
        btn_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(btn_row1, text="➕ Add", command=self.add_connection, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row1, text="✏️ Edit", command=self.edit_connection, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row1, text="🗑️ Delete", command=self.delete_connection, width=8).pack(side=tk.LEFT)
        
        # 第二行按钮
        btn_row2 = ttk.Frame(btn_frame)
        btn_row2.pack(fill=tk.X)
        
        self.connect_btn = ttk.Button(btn_row2, text="🔌 Connect", command=self.connect_redis)
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(btn_row2, text="🔌 Disconnect", command=self.disconnect_redis, state="disabled")
        self.disconnect_btn.pack(side=tk.RIGHT)
        
        # 数据库选择
        db_frame = ttk.LabelFrame(parent, text="🗄️ Database", padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.db_var = tk.StringVar()
        self.db_combo = ttk.Combobox(db_frame, textvariable=self.db_var, state="readonly",
                                    font=('SF Pro Display', 11))
        self.db_combo['values'] = [f"DB {i}" for i in range(16)]
        self.db_combo.pack(fill=tk.X)
        self.db_combo.bind('<<ComboboxSelected>>', self.on_db_change)
        
        # 键搜索
        search_frame = ttk.LabelFrame(parent, text="🔍 Keys", padding="10")
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        # 分隔符设置
        sep_frame = ttk.Frame(search_frame)
        sep_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(sep_frame, text="Separator:", font=('SF Pro Display', 10)).pack(side=tk.LEFT)
        self.separator_var = tk.StringVar(value=":")
        sep_entry = ttk.Entry(sep_frame, textvariable=self.separator_var, width=5,
                             font=('SF Pro Display', 10))
        sep_entry.pack(side=tk.LEFT, padx=(5, 0))
        sep_entry.bind('<KeyRelease>', self.on_separator_change)
        
        # 搜索框
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_input_frame, textvariable=self.search_var,
                                font=('SF Pro Display', 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<Return>', lambda e: self.search_keys())
        
        ttk.Button(search_input_frame, text="🔍", command=self.search_keys, width=4).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 键树形列表 - 使用Text widget替代Treeview以支持水平滚动
        tree_frame = ttk.Frame(search_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置grid权重
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 使用Text widget显示键列表
        self.keys_text = tk.Text(tree_frame, wrap=tk.NONE, font=('SF Pro Display', 11))
        self.keys_text.grid(row=0, column=0, sticky='nsew')
        self.keys_text.bind('<Button-1>', self.on_text_click)
        self.keys_text.bind('<Double-Button-1>', self.on_text_double_click)
        
        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.keys_text.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.keys_text.configure(yscrollcommand=v_scrollbar.set)
        
        # 水平滚动条
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.keys_text.xview)
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.keys_text.configure(xscrollcommand=h_scrollbar.set)
        
        # 存储键数据和选中状态
        self.keys_data = {}
        self.group_data = {}  # 存储分组信息
        self.expanded_groups = set()  # 跟踪展开的分组
        self.selected_line = None
        self.tree_structure = {}  # 存储完整的树结构
        
        # 配置文本标签样式
        self.keys_text.tag_configure('selected', background='#007AFF', foreground='white')
        self.keys_text.tag_configure('group', foreground='#666666', font=('SF Pro Display', 11, 'bold'))
        self.keys_text.tag_configure('key', foreground='#333333')
        self.keys_text.tag_configure('hover', background='#F0F0F0')
        
        # 绑定鼠标事件
        self.keys_text.bind('<Motion>', self.on_mouse_motion)
        self.keys_text.bind('<Leave>', self.on_mouse_leave)
        self.keys_text.bind('<Enter>', self.on_mouse_enter)
        self.current_hover_line = None
        self.mouse_in_widget = False
        
    def setup_right_panel(self, parent):
        # 状态标签
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(status_frame, text="🔌 Select a connection to get started", 
                                     style='Title.TLabel')
        self.status_label.pack(anchor=tk.W)
        
        # 标签页
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 键管理标签页
        key_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(key_frame, text="🔑 Key Manager")
        self.setup_key_manager(key_frame)
        
        # 命令行标签页
        cli_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(cli_frame, text="💻 Command Line")
        self.setup_cli(cli_frame)
        
    def on_mouse_motion(self, event):
        """处理鼠标移动事件"""
        # 获取鼠标位置的行号
        try:
            line_num = int(self.keys_text.index(f"@{event.x},{event.y}").split('.')[0])
            
            # 清除之前的悬停效果
            if self.current_hover_line and self.current_hover_line != self.selected_line:
                self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
            
            # 检查是否是可点击的行（分组或键）
            if line_num in self.group_data or line_num in self.keys_data:
                self.keys_text.config(cursor="hand2")
                # 添加悬停效果（但不覆盖选中效果）
                if line_num != self.selected_line:
                    self.keys_text.tag_add('hover', f"{line_num}.0", f"{line_num}.end")
                self.current_hover_line = line_num
            else:
                self.keys_text.config(cursor="")
                self.current_hover_line = None
        except:
            self.keys_text.config(cursor="")
            self.current_hover_line = None
    
    def on_mouse_leave(self, event):
        """处理鼠标离开事件"""
        self.keys_text.config(cursor="")
        if self.current_hover_line and self.current_hover_line != self.selected_line:
            self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
        self.current_hover_line = None
        
    def on_text_click(self, event):
        """处理文本点击事件"""
        # 获取点击的行号
        line_num = int(self.keys_text.index(tk.CURRENT).split('.')[0])
        
        # 检查是否点击了分组
        if line_num in self.group_data:
            group_path = self.group_data[line_num]
            
            # 保存当前滚动位置
            current_view = self.keys_text.yview()
            
            if group_path in self.expanded_groups:
                # 收起时，同时收起所有子目录
                self.expanded_groups.remove(group_path)
                # 移除所有以该路径开头的子目录
                to_remove = [path for path in self.expanded_groups if path.startswith(group_path + '/')]
                for path in to_remove:
                    self.expanded_groups.remove(path)
            else:
                self.expanded_groups.add(group_path)
            
            # 重新渲染树结构
            self.render_tree_structure()
            
            # 恢复滚动位置以减少跳动
            self.keys_text.yview_moveto(current_view[0])
            
        elif line_num in self.keys_data:
            # 清除之前的选中效果
            if self.selected_line:
                self.keys_text.tag_remove('selected', f"{self.selected_line}.0", f"{self.selected_line}.end")
            
            # 选中当前行
            self.selected_line = line_num
            self.keys_text.tag_add('selected', f"{line_num}.0", f"{line_num}.end")
            
            # 加载键详情
            key = self.keys_data[line_num]
            self.load_key_details(key)
        
        # 清除悬停效果
        if self.current_hover_line:
            self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
            self.current_hover_line = None
        
    def on_text_double_click(self, event):
        """处理文本双击事件"""
        self.on_text_click(event)
        
    def setup_key_manager(self, parent):
        self.key_details_frame = ttk.Frame(parent)
        self.key_details_frame.pack(fill=tk.BOTH, expand=True)
        
        # 初始提示
        welcome_frame = ttk.Frame(self.key_details_frame)
        welcome_frame.pack(expand=True)
        
        ttk.Label(welcome_frame, text="🔑", font=('SF Pro Display', 48)).pack(pady=(0, 10))
        ttk.Label(welcome_frame, text="Select a key to view details", 
                 style='Title.TLabel').pack()
        
    def setup_cli(self, parent):
        # Redis命令列表
        self.redis_commands = [
            'GET', 'SET', 'DEL', 'EXISTS', 'KEYS', 'TYPE', 'TTL', 'EXPIRE',
            'HGET', 'HSET', 'HDEL', 'HKEYS', 'HVALS', 'HGETALL', 'HEXISTS',
            'LLEN', 'LPUSH', 'RPUSH', 'LPOP', 'RPOP', 'LRANGE', 'LINDEX',
            'SADD', 'SREM', 'SMEMBERS', 'SCARD', 'SISMEMBER',
            'ZADD', 'ZREM', 'ZRANGE', 'ZCARD', 'ZSCORE',
            'PING', 'INFO', 'SELECT', 'FLUSHDB', 'FLUSHALL', 'DBSIZE',
            'INCR', 'DECR', 'INCRBY', 'DECRBY', 'APPEND', 'STRLEN'
        ]
        
        # 命令输入
        cmd_input_frame = ttk.LabelFrame(parent, text="⌨️ Command Input", padding="10")
        cmd_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        input_frame = ttk.Frame(cmd_input_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="redis>", font=('SF Pro Display', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        self.cmd_var = tk.StringVar()
        self.cmd_entry = ttk.Entry(input_frame, textvariable=self.cmd_var, font=('Menlo', 11))
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.cmd_entry.bind('<Return>', lambda e: self.execute_command())
        self.cmd_entry.bind('<KeyRelease>', self.on_cmd_key_release)
        self.cmd_entry.bind('<Tab>', self.on_cmd_tab)
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="▶️ Execute", command=self.execute_command).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ Clear", command=self.clear_output).pack(side=tk.LEFT)
        
        # 命令提示框架
        self.suggestion_frame = ttk.Frame(cmd_input_frame)
        self.suggestion_listbox = tk.Listbox(self.suggestion_frame, height=5, font=('Menlo', 9))
        self.suggestion_listbox.bind('<Double-Button-1>', self.on_suggestion_select)
        self.suggestion_listbox.bind('<Return>', self.on_suggestion_select)
        
        # 输出区域
        output_frame = ttk.LabelFrame(parent, text="📊 Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文本框和滚动条
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(text_frame, state=tk.DISABLED, wrap=tk.WORD,
                                  font=('Menlo', 10), bg='#1E1E1E', fg='#FFFFFF',
                                  insertbackground='#FFFFFF', selectbackground='#007AFF')
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        output_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.configure(yscrollcommand=output_scroll.set)
        
    def show_about(self):
        """显示关于对话框"""
        about_text = f"""{__app_name__} v{__version__}

一个现代化的Redis管理工具

功能特性：
• 支持多个Redis连接配置
• 支持SSH隧道连接
• 支持所有Redis数据类型
• JSON格式化和编辑
• 内置Redis命令行

Python {'.'.join(map(str, __import__('sys').version_info[:2]))}
tkinter GUI框架

© 2024 RedisManager"""
        
        messagebox.showinfo("About", about_text)
        
    def add_connection(self):
        self.show_connection_dialog()
        
    def edit_connection(self):
        selection = self.conn_listbox.curselection()
        if selection:
            conn = self.connections[selection[0]]
            self.show_connection_dialog(conn)
            
    def delete_connection(self):
        selection = self.conn_listbox.curselection()
        if selection:
            if messagebox.askyesno("Delete Connection", "Are you sure?"):
                del self.connections[selection[0]]
                self.refresh_connection_list()
                self.save_connections()
                
    def show_connection_dialog(self, conn=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Connection" if conn is None else "Edit Connection")
        dialog.geometry("600x800")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 设置对话框样式 - 使用内联样式避免兼容性问题
        # 不使用自定义样式，直接在组件中设置属性
        
        # 创建滚动框架
        canvas = tk.Canvas(dialog, bg='#F5F5F5')
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind('<Enter>', _bind_to_mousewheel)
        canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 表单字段
        fields = {}
        
        # 标题
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_text = "Add New Connection" if conn is None else "Edit Connection"
        title_label = ttk.Label(title_frame, text=title_text, font=('SF Pro Display', 16, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Configure your Redis connection settings", 
                                  font=('SF Pro Display', 10), foreground='#666666')
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Redis连接信息
        redis_frame = ttk.LabelFrame(scrollable_frame, text="🔗 Redis Connection", padding=10)
        redis_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # 使用Grid布局来美化表单
        redis_inner = ttk.Frame(redis_frame)
        redis_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # 连接名称
        ttk.Label(redis_inner, text="Connection Name:", font=('SF Pro Display', 10)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        fields['name'] = ttk.Entry(redis_inner, font=('SF Pro Display', 10))
        fields['name'].grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        # Redis主机和端口
        ttk.Label(redis_inner, text="Redis Host:", font=('SF Pro Display', 10)).grid(row=1, column=0, sticky='w', pady=(0, 5))
        host_frame = ttk.Frame(redis_inner)
        host_frame.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        fields['host'] = ttk.Entry(host_frame, font=('SF Pro Display', 10))
        fields['host'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(host_frame, text="Port:", font=('SF Pro Display', 10)).pack(side=tk.LEFT, padx=(10, 5))
        fields['port'] = ttk.Entry(host_frame, width=8, font=('SF Pro Display', 10))
        fields['port'].pack(side=tk.RIGHT)
        # 默认值将在后面根据是否为新连接来设置
        
        # 认证信息
        ttk.Label(redis_inner, text="Username:", font=('SF Pro Display', 10)).grid(row=2, column=0, sticky='w', pady=(0, 5))
        fields['username'] = ttk.Entry(redis_inner, font=('SF Pro Display', 10))
        fields['username'].grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        ttk.Label(redis_inner, text="Password:", font=('SF Pro Display', 10)).grid(row=3, column=0, sticky='w', pady=(0, 5))
        fields['password'] = ttk.Entry(redis_inner, show="*", font=('SF Pro Display', 10))
        fields['password'].grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        # 配置选项
        ttk.Label(redis_inner, text="Max Keys (0=unlimited):", font=('SF Pro Display', 10)).grid(row=4, column=0, sticky='w', pady=(0, 5))
        config_frame = ttk.Frame(redis_inner)
        config_frame.grid(row=4, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        fields['max_keys'] = ttk.Entry(config_frame, width=12, font=('SF Pro Display', 10))
        fields['max_keys'].pack(side=tk.LEFT)
        # 默认值将在后面根据是否为新连接来设置
        
        ttk.Label(config_frame, text="Databases (1-128):", font=('SF Pro Display', 10)).pack(side=tk.LEFT, padx=(15, 5))
        fields['db_count'] = ttk.Entry(config_frame, width=8, font=('SF Pro Display', 10))
        fields['db_count'].pack(side=tk.LEFT)
        # 默认值将在后面根据是否为新连接来设置
        
        # 配置Grid权重
        redis_inner.columnconfigure(1, weight=1)
        
        # SSH隧道配置
        ssh_frame = ttk.LabelFrame(scrollable_frame, text="🔐 SSH Tunnel (Optional)", padding=10)
        ssh_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        ssh_inner = ttk.Frame(ssh_frame)
        ssh_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # SSH启用选项
        ssh_var = tk.BooleanVar()
        ssh_check = ttk.Checkbutton(ssh_inner, text="Enable SSH Tunnel", variable=ssh_var,
                                   command=lambda: self.toggle_ssh_section(ssh_var.get(), ssh_content_frame))
        ssh_check.pack(anchor=tk.W, pady=(0, 10))
        
        # SSH内容框架
        ssh_content_frame = ttk.Frame(ssh_inner)
        ssh_content_frame.pack(fill=tk.X)
        
        # SSH服务器信息
        ssh_server_frame = ttk.Frame(ssh_content_frame)
        ssh_server_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(ssh_server_frame, text="SSH Host:", font=('SF Pro Display', 10)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        ssh_host_frame = ttk.Frame(ssh_server_frame)
        ssh_host_frame.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        fields['ssh_host'] = ttk.Entry(ssh_host_frame, font=('SF Pro Display', 10))
        fields['ssh_host'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(ssh_host_frame, text="Port:", font=('SF Pro Display', 10)).pack(side=tk.LEFT, padx=(10, 5))
        fields['ssh_port'] = ttk.Entry(ssh_host_frame, width=8, font=('SF Pro Display', 10))
        fields['ssh_port'].pack(side=tk.RIGHT)
        # 默认值将在后面根据是否为新连接来设置
        
        ttk.Label(ssh_server_frame, text="SSH Username:", font=('SF Pro Display', 10)).grid(row=1, column=0, sticky='w', pady=(0, 5))
        fields['ssh_user'] = ttk.Entry(ssh_server_frame, font=('SF Pro Display', 10))
        fields['ssh_user'].grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        ssh_server_frame.columnconfigure(1, weight=1)
        
        # SSH认证方式
        auth_frame = ttk.LabelFrame(ssh_content_frame, text="Authentication Method", padding=10)
        auth_frame.pack(fill=tk.X, pady=(0, 10))
        
        auth_inner = ttk.Frame(auth_frame)
        auth_inner.pack(fill=tk.X, padx=10, pady=10)
        
        auth_method = tk.StringVar(value="password")
        
        # 认证方式选择按钮 - 使用更美观的布局
        auth_buttons_frame = ttk.Frame(auth_inner)
        auth_buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        password_radio = ttk.Radiobutton(auth_buttons_frame, text="🔑 Password Authentication", 
                                       variable=auth_method, value="password",
                                       command=lambda: self.toggle_ssh_auth_fields(auth_method.get(), fields))
        password_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        key_radio = ttk.Radiobutton(auth_buttons_frame, text="🔐 Private Key Authentication", 
                                  variable=auth_method, value="key",
                                  command=lambda: self.toggle_ssh_auth_fields(auth_method.get(), fields))
        key_radio.pack(side=tk.LEFT)
        
        # 统一的认证内容框架 - 设置固定尺寸以保持一致性
        auth_content_frame = ttk.Frame(auth_inner)
        auth_content_frame.pack(fill=tk.X, pady=(0, 0))  # 移除expand=True
        auth_content_frame.configure(height=200)  # 设置固定高度
        auth_content_frame.pack_propagate(False)  # 防止子组件改变框架大小
        
        # 密码认证框架
        password_frame = ttk.Frame(auth_content_frame)
        
        password_inner = ttk.Frame(password_frame)
        password_inner.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(password_inner, text="SSH Password:", font=('SF Pro Display', 10)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        fields['ssh_password'] = ttk.Entry(password_inner, show="*", font=('SF Pro Display', 10))
        fields['ssh_password'].grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        password_inner.columnconfigure(1, weight=1)
        
        # 私钥认证框架
        key_frame = ttk.Frame(auth_content_frame)
        
        key_inner = ttk.Frame(key_frame)
        key_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # 私钥文件选择
        ttk.Label(key_inner, text="Private Key File:", font=('SF Pro Display', 10)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        key_file_frame = ttk.Frame(key_inner)
        key_file_frame.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        fields['ssh_key'] = ttk.Entry(key_file_frame, font=('SF Pro Display', 10))
        fields['ssh_key'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_key():
            filename = filedialog.askopenfilename(
                title="Select SSH Private Key",
                filetypes=[("Private Key Files", "*.pem *.key *.rsa"), ("All Files", "*.*")]
            )
            if filename:
                fields['ssh_key'].delete(0, tk.END)
                fields['ssh_key'].insert(0, filename)
        
        browse_btn = ttk.Button(key_file_frame, text="Browse...", command=browse_key)
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 私钥内容输入
        ttk.Label(key_inner, text="Or paste private key content:", font=('SF Pro Display', 10)).grid(row=1, column=0, sticky='nw', pady=(15, 5))
        key_content_frame = ttk.Frame(key_inner)
        key_content_frame.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=(15, 5))
        
        # 设置固定宽度的文本框，防止影响整体布局
        fields['ssh_key_content'] = tk.Text(key_content_frame, height=3, width=40, wrap=tk.WORD,  # 设置固定宽度和高度
                                          font=('Menlo', 9), bg='white', relief='solid', borderwidth=1)
        fields['ssh_key_content'].pack(side=tk.LEFT)  # 不使用expand和fill
        
        key_content_scroll = ttk.Scrollbar(key_content_frame, orient=tk.VERTICAL, command=fields['ssh_key_content'].yview)
        key_content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        fields['ssh_key_content'].configure(yscrollcommand=key_content_scroll.set)
        
        # 密钥密码
        ttk.Label(key_inner, text="Key Passphrase:", font=('SF Pro Display', 10)).grid(row=2, column=0, sticky='w', pady=(15, 5))
        fields['ssh_key_passphrase'] = ttk.Entry(key_inner, show="*", font=('SF Pro Display', 10))
        fields['ssh_key_passphrase'].grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=(15, 5))
        
        key_inner.columnconfigure(1, weight=1)
        # 移除行权重设置以保持一致的高度
        # key_inner.rowconfigure(1, weight=1)
        
        # 保存框架引用
        fields['_auth_method'] = auth_method
        fields['_password_frame'] = password_frame
        fields['_key_frame'] = key_frame
        fields['_auth_content_frame'] = auth_content_frame
        fields['_ssh_content_frame'] = ssh_content_frame
        
        # 初始化显示状态 - 两个框架都使用相同的pack参数
        password_frame.pack(fill=tk.X, expand=False)  # 确保不会expand
        ssh_content_frame.pack_forget()  # 默认隐藏SSH配置
        
        # 填充现有数据
        if conn:
            # 编辑现有连接 - 填充现有值
            fields['name'].insert(0, conn.get('name', ''))
            fields['host'].insert(0, conn.get('host', 'localhost'))
            fields['port'].insert(0, str(conn.get('port', 6379)))
            fields['username'].insert(0, conn.get('username', ''))
            fields['password'].insert(0, conn.get('password', ''))
            fields['max_keys'].insert(0, str(conn.get('max_keys', 0)))
            fields['db_count'].insert(0, str(conn.get('db_count', 16)))
            
            use_ssh = conn.get('use_ssh', False)
            ssh_var.set(use_ssh)
            if use_ssh:
                ssh_content_frame.pack(fill=tk.X)
                
            fields['ssh_host'].insert(0, conn.get('ssh_host', ''))
            fields['ssh_port'].insert(0, str(conn.get('ssh_port', 22)))
            fields['ssh_user'].insert(0, conn.get('ssh_user', ''))
            fields['ssh_password'].insert(0, conn.get('ssh_password', ''))
            fields['ssh_key'].insert(0, conn.get('ssh_key', ''))
            fields['ssh_key_content'].insert(tk.END, conn.get('ssh_key_content', ''))
            fields['ssh_key_passphrase'].insert(0, conn.get('ssh_key_passphrase', ''))
            
            # 设置认证方式
            auth_method_val = "key" if conn.get('ssh_key') or conn.get('ssh_key_content') else "password"
            fields['_auth_method'].set(auth_method_val)
            self.toggle_ssh_auth_fields(auth_method_val, fields)
        else:
            # 新建连接 - 设置默认值
            fields['host'].insert(0, 'localhost')
            fields['port'].insert(0, '6379')
            fields['max_keys'].insert(0, '0')
            fields['db_count'].insert(0, '16')
            fields['ssh_port'].insert(0, '22')
        
        # 按钮区域
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # 分隔线
        separator = ttk.Separator(btn_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        def save_connection():
            try:
                # 验证必填字段
                if not fields['name'].get().strip():
                    messagebox.showerror("Validation Error", "Connection name is required")
                    return
                    
                if not fields['host'].get().strip():
                    messagebox.showerror("Validation Error", "Redis host is required")
                    return
                
                db_count = int(fields['db_count'].get() or 16)
                if db_count < 1 or db_count > 128:
                    messagebox.showerror("Validation Error", "Database count must be between 1 and 128")
                    return
                
                # SSH验证
                if ssh_var.get():
                    if not fields['ssh_host'].get().strip():
                        messagebox.showerror("Validation Error", "SSH host is required when SSH tunnel is enabled")
                        return
                    if not fields['ssh_user'].get().strip():
                        messagebox.showerror("Validation Error", "SSH username is required when SSH tunnel is enabled")
                        return
                    
                    auth_method_val = fields['_auth_method'].get()
                    if auth_method_val == "password" and not fields['ssh_password'].get():
                        messagebox.showerror("Validation Error", "SSH password is required for password authentication")
                        return
                    elif auth_method_val == "key" and not fields['ssh_key'].get() and not fields['ssh_key_content'].get(1.0, tk.END).strip():
                        messagebox.showerror("Validation Error", "Private key file or content is required for key authentication")
                        return
                    
                new_conn = {
                    'name': fields['name'].get().strip(),
                    'host': fields['host'].get().strip(),
                    'port': int(fields['port'].get() or 6379),
                    'username': fields['username'].get().strip(),
                    'password': fields['password'].get(),
                    'max_keys': int(fields['max_keys'].get() or 0),
                    'db_count': db_count,
                    'use_ssh': ssh_var.get(),
                    'ssh_host': fields['ssh_host'].get().strip(),
                    'ssh_port': int(fields['ssh_port'].get() or 22),
                    'ssh_user': fields['ssh_user'].get().strip(),
                    'ssh_password': fields['ssh_password'].get(),
                    'ssh_key': fields['ssh_key'].get().strip(),
                    'ssh_key_content': fields['ssh_key_content'].get(1.0, tk.END).strip(),
                    'ssh_key_passphrase': fields['ssh_key_passphrase'].get(),
                }
                
                if conn:
                    # 编辑现有连接
                    idx = self.connections.index(conn)
                    self.connections[idx] = new_conn
                else:
                    # 添加新连接
                    self.connections.append(new_conn)
                
                self.refresh_connection_list()
                self.save_connections()
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()
                
                # 显示成功消息
                action = "updated" if conn else "created"
                messagebox.showinfo("Success", f"Connection '{new_conn['name']}' {action} successfully!")
                
            except ValueError as e:
                messagebox.showerror("Validation Error", f"Invalid input: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save connection: {e}")
        
        def test_connection():
            """测试连接功能"""
            try:
                # 这里可以添加连接测试逻辑
                messagebox.showinfo("Test Connection", "Connection test feature will be implemented in future version")
            except Exception as e:
                messagebox.showerror("Test Failed", f"Connection test failed: {e}")
        
        # 按钮布局
        button_container = ttk.Frame(btn_frame)
        button_container.pack(fill=tk.X)
        
        # 左侧按钮
        test_btn = ttk.Button(button_container, text="Test Connection", command=test_connection)
        test_btn.pack(side=tk.LEFT)
        
        # 右侧按钮
        cancel_btn = ttk.Button(button_container, text="Cancel", command=lambda: [canvas.unbind_all("<MouseWheel>"), dialog.destroy()])
        cancel_btn.pack(side=tk.RIGHT)
        
        save_btn = ttk.Button(button_container, text="Save Connection", command=save_connection)
        save_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # 设置焦点
        fields['name'].focus_set()
    
    def toggle_ssh_section(self, enabled, ssh_content_frame):
        """切换SSH配置区域的显示/隐藏"""
        if enabled:
            ssh_content_frame.pack(fill=tk.X)
        else:
            ssh_content_frame.pack_forget()
    
    def toggle_ssh_auth_fields(self, auth_method, fields):
        """切换SSH认证方式显示 - 统一布局，防止宽度变化"""
        # 隐藏所有认证框架
        fields['_password_frame'].pack_forget()
        fields['_key_frame'].pack_forget()
        
        # 显示对应的认证框架 - 使用相同的pack参数
        if auth_method == "password":
            fields['_password_frame'].pack(fill=tk.X, expand=False)
        else:  # key
            fields['_key_frame'].pack(fill=tk.X, expand=False)
        
    def on_connection_select(self, event):
        selection = self.conn_listbox.curselection()
        if selection:
            self.current_conn = self.connections[selection[0]]
            # 不更新current_conn_index，只有在成功连接后才更新
            
    def on_connection_double_click(self, event):
        self.connect_redis()
        
    def connect_redis(self):
        if not self.current_conn:
            messagebox.showwarning("Warning", "Please select a connection")
            return
            
        def connect_thread():
            try:
                self.status_label.config(text="Connecting...")
                self.root.update()
                
                if self.current_conn.get('use_ssh'):
                    # SSH隧道连接 - 通过SSH服务器连接内网Redis
                    self.setup_ssh_tunnel()
                    redis_host = '127.0.0.1'
                    redis_port = self.ssh_tunnel.getsockname()[1]
                else:
                    # 直接连接
                    redis_host = self.current_conn['host']
                    redis_port = self.current_conn['port']
                
                # 连接Redis
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=self.current_conn.get('password') or None,
                    username=self.current_conn.get('username') or None,
                    db=0,
                    decode_responses=True
                )
                
                # 测试连接
                self.redis_client.ping()
                
                self.root.after(0, self.on_connect_success)
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self.on_connect_error(msg))
        
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def disconnect_redis(self):
        """断开Redis连接"""
        try:
            self.stop_keepalive()
            
            if self.redis_client:
                self.redis_client.close()
                self.redis_client = None
            
            if self.ssh_tunnel:
                self.ssh_tunnel.close()
                self.ssh_tunnel = None
                
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
            
            # 重置UI状态
            self.current_conn_index = -1
            self.status_label.config(text="🔌 Disconnected")
            self.connect_btn.config(text="🔌 Connect", state="normal")
            self.disconnect_btn.config(state="disabled")
            
            # 清空键列表
            self.keys_text.config(state='normal')
            self.keys_text.delete('1.0', tk.END)
            self.keys_text.config(state='disabled')
            self.keys_data = {}
            self.selected_line = None
            
            # 清空键详情
            for widget in self.key_details_frame.winfo_children():
                widget.destroy()
            
            welcome_frame = ttk.Frame(self.key_details_frame)
            welcome_frame.pack(expand=True)
            ttk.Label(welcome_frame, text="🔑", font=('SF Pro Display', 48)).pack(pady=(0, 10))
            ttk.Label(welcome_frame, text="Select a key to view details", style='Title.TLabel').pack()
            
            # 更新连接列表显示
            self.refresh_connection_list()
            
        except Exception as e:
            messagebox.showerror("Disconnect Error", f"Error while disconnecting: {e}")
        
    def setup_ssh_tunnel(self):
        ssh_config = self.current_conn
        
        # 创建SSH客户端
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # SSH认证 - 优先使用私钥
        key_path = ssh_config.get('ssh_key', '').strip()
        key_content = ssh_config.get('ssh_key_content', '').strip()
        
        try:
            if key_path or key_content:
                # 私钥认证
                passphrase = ssh_config.get('ssh_key_passphrase') or None
                
                if key_content:
                    # 使用私钥内容
                    import io
                    from paramiko import RSAKey, DSSKey, ECDSAKey, Ed25519Key
                    
                    key_file = io.StringIO(key_content)
                    key = None
                    
                    for key_class in [RSAKey, DSSKey, ECDSAKey, Ed25519Key]:
                        try:
                            key_file.seek(0)
                            key = key_class.from_private_key(key_file, password=passphrase)
                            break
                        except:
                            continue
                    
                    if not key:
                        raise Exception("Invalid private key content")
                        
                elif key_path:
                    # 使用私钥文件
                    if not os.path.exists(key_path):
                        raise Exception(f"Private key file not found: {key_path}")
                    
                    # 尝试直接使用paramiko的connect方法加载密钥
                    self.ssh_client.connect(
                        hostname=ssh_config['ssh_host'],
                        port=ssh_config['ssh_port'],
                        username=ssh_config['ssh_user'],
                        key_filename=key_path,
                        passphrase=passphrase,
                        timeout=30
                    )
                else:
                    raise Exception("No private key provided")
                
                # 如果使用key_content，需要手动连接
                if key_content:
                    self.ssh_client.connect(
                        hostname=ssh_config['ssh_host'],
                        port=ssh_config['ssh_port'],
                        username=ssh_config['ssh_user'],
                        pkey=key,
                        timeout=30
                    )
            else:
                # 密码认证
                self.ssh_client.connect(
                    hostname=ssh_config['ssh_host'],
                    port=ssh_config['ssh_port'],
                    username=ssh_config['ssh_user'],
                    password=ssh_config['ssh_password'],
                    timeout=30
                )
        except Exception as e:
            if self.ssh_client:
                self.ssh_client.close()
            raise Exception(f"SSH connection failed: {str(e)}")
        
        # 创建隧道 - 连接内网Redis地址
        local_port = self.find_free_port()
        self.ssh_tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssh_tunnel.bind(('127.0.0.1', local_port))
        self.ssh_tunnel.listen(1)
        
        def tunnel_handler():
            while True:
                try:
                    client_socket, addr = self.ssh_tunnel.accept()
                    transport = self.ssh_client.get_transport()
                    # 连接到内网Redis地址
                    dest_addr = (ssh_config['host'], ssh_config['port'])
                    channel = transport.open_channel('direct-tcpip', dest_addr, addr)
                    
                    def forward_data(src, dst):
                        try:
                            while True:
                                data = src.recv(1024)
                                if not data:
                                    break
                                dst.send(data)
                        except:
                            pass
                        finally:
                            src.close()
                            dst.close()
                    
                    threading.Thread(target=forward_data, args=(client_socket, channel), daemon=True).start()
                    threading.Thread(target=forward_data, args=(channel, client_socket), daemon=True).start()
                    
                except:
                    break
        
        threading.Thread(target=tunnel_handler, daemon=True).start()
        time.sleep(0.5)  # 等待隧道建立
        
    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
            
    def on_connect_success(self):
        # 更新当前连接索引
        selection = self.conn_listbox.curselection()
        if selection:
            self.current_conn_index = selection[0]
        
        self.status_label.config(text=f"✅ Connected to {self.current_conn['name']}")
        self.connect_btn.config(text="✅ Connected", state="disabled")
        self.disconnect_btn.config(state="normal")
        
        # 更新连接列表显示
        self.refresh_connection_list()
        
        self.update_db_list()
        self.search_keys()
        self.start_keepalive()
        
    def on_connect_error(self, error):
        self.status_label.config(text=f"❌ Connection failed: {error}")
        self.connect_btn.config(text="🔌 Connect", state="normal")
        self.disconnect_btn.config(state="disabled")
        messagebox.showerror("Connection Error", error)
        
    def update_db_list(self):
        db_count = self.current_conn.get('db_count', 16)
        self.db_combo['values'] = [f"DB {i}" for i in range(db_count)]
        self.db_var.set("DB 0")
        
    def on_db_change(self, event):
        if self.redis_client:
            # 重置总键数估计
            self.total_keys_estimate = None
            db_num = int(self.db_var.get().split()[1])
            self.redis_client.execute_command('SELECT', db_num)
            self.search_keys()
            
    def search_keys(self):
        if not self.redis_client:
            return
            
        # 重置总键数估计
        self.total_keys_estimate = None
            
        def search_thread():
            try:
                pattern = self.search_var.get() or "*"
                max_keys = self.current_conn.get('max_keys', 0)
                
                self.root.after(0, lambda: self.status_label.config(text="Loading keys..."))
                
                if max_keys == 0:
                    # 无限制模式 - 使用流式加载
                    self.load_keys_streaming(pattern)
                else:
                    # 限制模式 - 快速加载指定数量
                    keys = []
                    for key in self.redis_client.scan_iter(match=pattern, count=1000):
                        keys.append(key)
                        if len(keys) >= max_keys:
                            break
                    
                    self.current_keys = keys
                    self.root.after(0, lambda: self.update_keys_tree(keys))
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self.status_label.config(text=f"Failed to get keys: {msg}"))
        
        threading.Thread(target=search_thread, daemon=True).start()
        
    def load_keys_streaming(self, pattern):
        """流式加载键，最大100000个"""
        try:
            keys = []
            count = 0
            max_keys = 100000
            
            # 先获取当前数据库的总键数
            try:
                info = self.redis_client.info('keyspace')
                current_db = int(self.db_var.get().split()[1]) if hasattr(self, 'db_var') and self.db_var.get() else 0
                db_key = f'db{current_db}'
                total_keys = info.get(db_key, {}).get('keys', None) if db_key in info else None
            except:
                total_keys = None
            
            for key in self.redis_client.scan_iter(match=pattern, count=1000):
                keys.append(key)
                count += 1
                
                # 更新状态
                if count % 2000 == 0:
                    if total_keys:
                        status_text = f"Loading keys... ({count} loaded, total ~{total_keys})"
                    else:
                        status_text = f"Loading keys... ({count} loaded)"
                    self.root.after(0, lambda t=status_text: self.status_label.config(text=t))
                    time.sleep(0.1)
                
                # 超过100000个键时停止加载
                if count >= max_keys:
                    break
            
            # 所有键加载完成后一次性更新树结构
            self.current_keys = keys
            self.total_keys_estimate = total_keys
            self.root.after(0, lambda: self.update_keys_tree(self.current_keys))
            
            # 显示最终状态
            if total_keys and count >= max_keys:
                final_status = f"Loaded {count} keys (showing {count} of ~{total_keys} total)"
            elif total_keys:
                final_status = f"Loaded {count} keys (all of ~{total_keys} total)"
            else:
                final_status = f"Loaded {count} keys (all)"
            
            self.root.after(0, lambda t=final_status: self.status_label.config(text=t))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.status_label.config(text=f"Failed to load keys: {error_msg}"))
        
    def update_keys_tree(self, keys):
        # 清空文本
        self.keys_text.config(state='normal')
        self.keys_text.delete('1.0', tk.END)
            
        if not keys:
            self.status_label.config(text="No keys found")
            self.keys_text.config(state='disabled')
            return
            
        # 按分隔符分组 - 支持多级结构
        separator = self.separator_var.get()
        self.tree_structure = {}
        
        for key in keys:
            if separator in key:
                parts = key.split(separator)
                current_level = self.tree_structure
                
                # 构建多级树结构
                for i, part in enumerate(parts[:-1]):
                    if part not in current_level:
                        current_level[part] = {'_children': {}, '_keys': []}
                    current_level = current_level[part]['_children']
                
                # 添加最终的键
                if len(parts) > 1:
                    final_part = parts[-1]
                    if final_part not in current_level:
                        current_level[final_part] = {'_children': {}, '_keys': []}
                    current_level[final_part]['_keys'].append(key)
                else:
                    # 只有一个部分，直接作为键
                    if '_keys' not in self.tree_structure:
                        self.tree_structure['_keys'] = []
                    self.tree_structure['_keys'].append(key)
            else:
                if '_ungrouped' not in self.tree_structure:
                    self.tree_structure['_ungrouped'] = {'_children': {}, '_keys': []}
                self.tree_structure['_ungrouped']['_keys'].append(key)
        
        # 渲染树结构
        self.render_tree_structure()
        
        self.status_label.config(text=f"Found {len(keys)} keys" + 
                                (f" (showing {len(keys)} of ~{self.total_keys_estimate} total)" 
                                 if hasattr(self, 'total_keys_estimate') and self.total_keys_estimate and self.total_keys_estimate > len(keys) 
                                 else ""))
        
    def render_tree_structure(self):
        """渲染树结构显示"""
        self.keys_text.config(state='normal')
        self.keys_text.delete('1.0', tk.END)
        
        lines = []
        self.keys_data = {}
        self.group_data = {}
        
        def add_tree_items(structure, level=0, path_prefix=""):
            for name, data in structure.items():
                if name.startswith('_'):
                    continue
                    
                # 计算该分组的总键数
                total_keys = self.count_keys_in_structure(data)
                group_path = f"{path_prefix}/{name}" if path_prefix else name
                
                # 如果分组只有一个键且没有子分组，直接显示键
                if total_keys == 1 and not data.get('_children') and data.get('_keys'):
                    key = data['_keys'][0]
                    indent = "    " * level
                    key_line = f"{indent}🔑 {key}"
                    lines.append(key_line)
                    self.keys_data[len(lines)] = key
                    continue
                
                # 显示分组
                indent = "    " * level
                is_expanded = group_path in self.expanded_groups
                expand_icon = "▼" if is_expanded else "▶"
                display_name = f"{indent}{expand_icon} 📁 {name} ({total_keys})"
                lines.append(display_name)
                
                line_index = len(lines)
                self.group_data[line_index] = group_path
                
                # 如果展开，显示子内容
                if is_expanded:
                    if '_children' in data and data['_children']:
                        add_tree_items(data['_children'], level + 1, group_path)
                    
                    if '_keys' in data and data['_keys']:
                        for i, key in enumerate(sorted(data['_keys'])):
                            key_indent = "    " * (level + 1) + "  "
                            is_last = i == len(data['_keys']) - 1 and not data.get('_children')
                            connector = "└─" if is_last else "├─"
                            key_line = f"{key_indent}{connector} 🔑 {key}"
                            lines.append(key_line)
                            self.keys_data[len(lines)] = key
        
        # 处理未分组的键
        if '_ungrouped' in self.tree_structure:
            ungrouped_keys = self.tree_structure['_ungrouped']['_keys']
            if ungrouped_keys:
                # 如果只有一个未分组的键，直接显示
                if len(ungrouped_keys) == 1:
                    key = ungrouped_keys[0]
                    key_line = f"🔑 {key}"
                    lines.append(key_line)
                    self.keys_data[len(lines)] = key
                else:
                    group_path = "_ungrouped"
                    is_expanded = group_path in self.expanded_groups
                    expand_icon = "▼" if is_expanded else "▶"
                    display_name = f"{expand_icon} 📁 ungrouped ({len(ungrouped_keys)})"
                    lines.append(display_name)
                    line_index = len(lines)
                    self.group_data[line_index] = group_path
                    
                    if is_expanded:
                        for i, key in enumerate(sorted(ungrouped_keys)):
                            is_last = i == len(ungrouped_keys) - 1
                            connector = "└─" if is_last else "├─"
                            key_line = f"      {connector} 🔑 {key}"
                            lines.append(key_line)
                            self.keys_data[len(lines)] = key
        
        # 添加分组的键
        add_tree_items(self.tree_structure)
        
        # 显示文本并应用样式
        self.keys_text.insert('1.0', '\n'.join(lines))
        
        # 为不同类型的行应用样式
        for line_num in range(1, len(lines) + 1):
            if line_num in self.group_data:
                self.keys_text.tag_add('group', f"{line_num}.0", f"{line_num}.end")
            elif line_num in self.keys_data:
                self.keys_text.tag_add('key', f"{line_num}.0", f"{line_num}.end")
        
        self.keys_text.config(state='disabled')
        
    def get_group_data_by_path(self, group_path):
        """根据路径获取分组数据"""
        if group_path == "_ungrouped":
            return self.tree_structure.get('_ungrouped')
        
        parts = group_path.split('/')
        current = self.tree_structure
        
        for part in parts:
            if part in current:
                current = current[part]
            else:
                return None
        
        return current
        
    def count_keys_in_structure(self, structure):
        """递归计算结构中的键总数"""
        count = 0
        if '_keys' in structure:
            count += len(structure['_keys'])
        if '_children' in structure:
            for child in structure['_children'].values():
                count += self.count_keys_in_structure(child)
        return count
        
    def on_mouse_motion(self, event):
        """处理鼠标移动事件"""
        try:
            line_num = int(self.keys_text.index(f"@{event.x},{event.y}").split('.')[0])
            
            # 如果鼠标还在同一行，不做任何处理
            if line_num == self.current_hover_line:
                return
            
            # 清除之前的悬停效果
            if self.current_hover_line and self.current_hover_line != self.selected_line:
                self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
            
            # 检查是否是可点击的行（分组或键）
            if line_num in self.group_data or line_num in self.keys_data:
                self.keys_text.config(cursor="hand2")
                if line_num != self.selected_line:
                    self.keys_text.tag_add('hover', f"{line_num}.0", f"{line_num}.end")
                self.current_hover_line = line_num
            else:
                self.keys_text.config(cursor="")
                self.current_hover_line = None
        except (ValueError, tk.TclError):
            self.keys_text.config(cursor="")
            self.current_hover_line = None
    
    def on_mouse_enter(self, event):
        """处理鼠标进入事件"""
        self.mouse_in_widget = True
    
    def on_mouse_leave(self, event):
        """处理鼠标离开事件"""
        self.mouse_in_widget = False
        self.keys_text.config(cursor="")
        if self.current_hover_line and self.current_hover_line != self.selected_line:
            self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
        self.current_hover_line = None
        
    def on_text_click(self, event):
        """处理文本点击事件"""
        # 确保鼠标在widget内才处理点击
        if not getattr(self, 'mouse_in_widget', True):
            return
            
        try:
            line_num = int(self.keys_text.index(tk.CURRENT).split('.')[0])
        except (ValueError, tk.TclError):
            return
        
        # 检查是否点击了分组
        if line_num in self.group_data:
            group_path = self.group_data[line_num]
            current_view = self.keys_text.yview()
            
            # 检查是否为只有一个key的最后一层分组
            if group_path in self.expanded_groups:
                # 收起时，同时收起所有子目录
                self.expanded_groups.remove(group_path)
                to_remove = [path for path in self.expanded_groups if path.startswith(group_path + '/')]
                for path in to_remove:
                    self.expanded_groups.remove(path)
            else:
                self.expanded_groups.add(group_path)
                # 检查是否为只有一个key的分组，如果是则直接选中该key
                group_data = self.get_group_data_by_path(group_path)
                if group_data and len(group_data.get('_keys', [])) == 1 and not group_data.get('_children'):
                    key = group_data['_keys'][0]
                    # 重新渲染后查找该key的行号
                    self.render_tree_structure()
                    for line, k in self.keys_data.items():
                        if k == key:
                            if self.selected_line:
                                self.keys_text.tag_remove('selected', f"{self.selected_line}.0", f"{self.selected_line}.end")
                            self.selected_line = line
                            self.keys_text.tag_add('selected', f"{line}.0", f"{line}.end")
                            self.load_key_details(key)
                            break
                    self.keys_text.yview_moveto(current_view[0])
                    return
            
            self.render_tree_structure()
            self.keys_text.yview_moveto(current_view[0])
            
        elif line_num in self.keys_data:
            if self.selected_line:
                self.keys_text.tag_remove('selected', f"{self.selected_line}.0", f"{self.selected_line}.end")
            
            self.selected_line = line_num
            self.keys_text.tag_add('selected', f"{line_num}.0", f"{line_num}.end")
            
            key = self.keys_data[line_num]
            self.load_key_details(key)
        
        # 清除悬停效果
        if self.current_hover_line:
            self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
            self.current_hover_line = None
        
    def on_text_double_click(self, event):
        """处理文本双击事件"""
        self.on_text_click(event)
        
    def on_key_select(self, event):
        selection = self.keys_tree.selection()
        if selection:
            item = self.keys_tree.item(selection[0])
            if item['values']:  # 这是一个键，不是分组
                key = item['values'][0]
                self.load_key_details(key)
                
    def load_key_details(self, key):
        if not self.redis_client:
            return
            
        def load_thread():
            try:
                # 检查键是否存在
                if not self.redis_client.exists(key):
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Key '{key}' does not exist"))
                    return
                
                # 获取键信息
                key_type = self.redis_client.type(key)
                ttl = self.redis_client.ttl(key)
                
                # 获取值
                value = None
                try:
                    if key_type == 'string':
                        value = self.redis_client.get(key)
                    elif key_type == 'list':
                        value = self.redis_client.lrange(key, 0, -1)
                    elif key_type == 'set':
                        value = list(self.redis_client.smembers(key))
                    elif key_type == 'hash':
                        # 对hash类型使用更安全的读取方式
                        hash_len = self.redis_client.hlen(key)
                        if hash_len > 1000:  # 大hash分批读取
                            value = {}
                            cursor = 0
                            while True:
                                cursor, fields = self.redis_client.hscan(key, cursor, count=100)
                                value.update(fields)
                                if cursor == 0:
                                    break
                        else:
                            value = self.redis_client.hgetall(key)
                    elif key_type == 'zset':
                        value = self.redis_client.zrange(key, 0, -1, withscores=True)
                    else:
                        value = str(self.redis_client.dump(key))
                except Exception as e:
                    # 如果读取失败，尝试获取基本信息
                    value = f"Error reading value: {str(e)}"
                
                self.root.after(0, lambda: self.show_key_details(key, key_type, ttl, value))
                
            except Exception as e:
                error_msg = f"Failed to load key '{key}': {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        threading.Thread(target=load_thread, daemon=True).start()
        
    def show_key_details(self, key, key_type, ttl, value):
        # 清空详情框架
        for widget in self.key_details_frame.winfo_children():
            widget.destroy()
            
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
        ttk.Label(info_frame, text=f"TTL: {ttl if ttl > 0 else 'Never expires'}").pack(anchor=tk.W)
        
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
        query_entry.bind('<Return>', lambda e: self.execute_key_query(key, key_type))
        
        ttk.Button(query_input_frame, text="Query", command=lambda: self.execute_key_query(key, key_type)).pack(side=tk.RIGHT)
        
        # 值编辑区域
        value_frame = ttk.LabelFrame(self.key_details_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 根据数据类型选择显示方式
        if key_type in ['list', 'set', 'zset', 'hash']:
            self.show_structured_value(value_frame, key, key_type, value)
        else:
            self.show_text_value(value_frame, key, key_type, value)
        
        # 操作按钮
        btn_frame = ttk.Frame(self.key_details_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def update_key():
            try:
                new_value = self.value_text.get(1.0, tk.END).strip()
                
                # 尝试压缩JSON格式
                try:
                    import json
                    parsed = json.loads(new_value)
                    new_value = json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
                except json.JSONDecodeError:
                    pass  # 不是JSON格式，保持原样
                
                if key_type == 'string':
                    self.redis_client.set(key, new_value)
                elif key_type == 'hash':
                    # 尝试解析JSON格式的hash数据
                    try:
                        import json
                        hash_data = json.loads(new_value)
                        if isinstance(hash_data, dict):
                            self.redis_client.delete(key)
                            self.redis_client.hset(key, mapping=hash_data)
                        else:
                            self.redis_client.set(key, new_value)
                    except json.JSONDecodeError:
                        self.redis_client.set(key, new_value)
                else:
                    self.redis_client.set(key, new_value)
                messagebox.showinfo("Success", "Key updated successfully!")
                self.load_key_details(key)  # 重新加载显示
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update key: {e}")
        
        def delete_key():
            if messagebox.askyesno("Delete Key", f"Are you sure you want to delete '{key}'?"):
                try:
                    self.redis_client.delete(key)
                    messagebox.showinfo("Success", "Key deleted successfully!")
                    self.search_keys()
                    # 清空详情
                    for widget in self.key_details_frame.winfo_children():
                        widget.destroy()
                    ttk.Label(self.key_details_frame, text="Select a key to view details").pack(pady=20)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete key: {e}")
        
        ttk.Button(btn_frame, text="Update", command=update_key).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Delete", command=delete_key).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=lambda: self.load_key_details(key)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Add New Key", command=self.add_new_key).pack(side=tk.LEFT)
        
    def show_structured_value(self, parent, key, key_type, value):
        """显示结构化数据（表格形式）"""
        # 清理之前的过滤状态标签
        if hasattr(self, 'filter_status_label'):
            self.filter_status_label.destroy()
            delattr(self, 'filter_status_label')
        
        # 查询框架
        query_frame = ttk.Frame(parent)
        query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if key_type == 'hash':
            ttk.Label(query_frame, text="Hash Key:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(query_frame, textvariable=self.struct_query_var)
            query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self.filter_hash_data(key))
            ttk.Button(query_frame, text="Find", 
                      command=lambda: self.filter_hash_data(key)).pack(side=tk.RIGHT)
        elif key_type in ['list', 'zset']:
            ttk.Label(query_frame, text="Filter:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(query_frame, textvariable=self.struct_query_var)
            query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self.filter_list_zset_data(key, key_type))
            ttk.Button(query_frame, text="Find", 
                      command=lambda: self.filter_list_zset_data(key, key_type)).pack(side=tk.RIGHT)
        elif key_type == 'set':
            ttk.Label(query_frame, text="Filter:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(query_frame, textvariable=self.struct_query_var)
            query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            query_entry.bind('<Return>', lambda e: self.filter_set_data(key))
            ttk.Button(query_frame, text="Find", 
                      command=lambda: self.filter_set_data(key)).pack(side=tk.RIGHT)
        
        # 表格显示
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置Treeview样式，增加行间距和悬停效果
        style = ttk.Style()
        
        # 为不同数据类型创建不同的样式
        style_name = f"Structured.{key_type}.Treeview"
        
        # 配置行高（增加间距）
        style.configure(style_name, rowheight=28)  # 默认是20，增加到28
        
        # 配置选中和悬停颜色
        style.map(style_name,
                 background=[('selected', '#007AFF'),
                           ('active', '#E8F4FD')],  # 悬停时的浅蓝色背景
                 foreground=[('selected', 'white'),
                           ('active', 'black')])
        
        if key_type == 'hash':
            columns = ('Field', 'Value')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name)
            self.data_tree.heading('Field', text='Field')
            self.data_tree.heading('Value', text='Value')
            
            # 设置列宽
            self.data_tree.column('Field', width=150, minwidth=100)
            self.data_tree.column('Value', width=300, minwidth=200)
            
            # 存储原始hash数据以便过滤
            self.original_hash_data = value if isinstance(value, dict) else {}
            
            # 加载hash数据
            self.load_hash_data_to_tree(self.original_hash_data)
        elif key_type == 'list':
            columns = ('Index', 'Value')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name)
            self.data_tree.heading('Index', text='Index')
            self.data_tree.heading('Value', text='Value')
            
            # 设置列宽
            self.data_tree.column('Index', width=80, minwidth=60)
            self.data_tree.column('Value', width=400, minwidth=200)
            
            # 存储原始list数据以便过滤
            self.original_list_data = value if isinstance(value, list) else []
            
            # 加载list数据
            self.load_list_data_to_tree(self.original_list_data)
        elif key_type == 'set':
            columns = ('Value',)
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name)
            self.data_tree.heading('Value', text='Value')
            
            # 设置列宽
            self.data_tree.column('Value', width=400, minwidth=200)
            
            # 存储原始set数据以便过滤
            self.original_set_data = list(value) if isinstance(value, (list, set)) else []
            
            # 加载set数据
            self.load_set_data_to_tree(self.original_set_data)
        elif key_type == 'zset':
            columns = ('Score', 'Member')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings', style=style_name)
            self.data_tree.heading('Score', text='Score')
            self.data_tree.heading('Member', text='Member')
            
            # 设置列宽
            self.data_tree.column('Score', width=100, minwidth=80)
            self.data_tree.column('Member', width=300, minwidth=200)
            
            # 存储原始zset数据以便过滤
            self.original_zset_data = value if isinstance(value, list) else []
            
            # 加载zset数据
            self.load_zset_data_to_tree(self.original_zset_data)
        
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 绑定鼠标事件以实现悬停效果
        self.data_tree.bind('<Motion>', self.on_treeview_motion)
        self.data_tree.bind('<Leave>', self.on_treeview_leave)
        self.data_tree.bind('<Double-1>', lambda e: self.edit_table_item(key, key_type))
        
        # 操作按钮
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add Item", command=lambda: self.add_table_item(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Update All", command=lambda: self.update_structured_key(key, key_type)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Refresh", command=lambda: self.load_key_details(key)).pack(side=tk.LEFT)
        
    def show_text_value(self, parent, key, key_type, value):
        """显示文本数据"""
        # JSON格式化按钮
        format_frame = ttk.Frame(parent)
        format_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(format_frame, text="Format JSON", command=lambda: self.format_json_value()).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(format_frame, text="Minify JSON", command=lambda: self.minify_json_value()).pack(side=tk.LEFT)
        
        # 文本编辑器
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.value_text = tk.Text(text_frame, wrap=tk.WORD)
        self.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.value_text.insert(tk.END, str(value))
        
        value_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.value_text.yview)
        value_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.value_text.configure(yscrollcommand=value_scroll.set)
        
    def query_hash_field(self, key):
        """查询hash字段"""
        field = self.struct_query_var.get().strip()
        if not field:
            return
        try:
            result = self.redis_client.hget(key, field)
            if result is not None:
                # 使用与双击一致的编辑对话框
                self.show_hash_field_dialog(key, field, result)
            else:
                messagebox.showinfo("Query Result", f"Field '{field}' not found in hash '{key}'")
        except Exception as e:
            messagebox.showerror("Query Error", f"Failed to get hash field: {e}")
    
    def show_hash_field_dialog(self, key, field, value):
        """显示hash字段查看/编辑对话框，与双击行为一致"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Hash Field: {field}")
        dialog.geometry("900x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 创建滚动框架
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Field显示（只读）
        field_frame = ttk.LabelFrame(scrollable_frame, text="Field (Key)")
        field_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        field_label = ttk.Label(field_frame, text=field, font=('SF Pro Display', 11, 'bold'))
        field_label.pack(fill=tk.X, padx=5, pady=5)
        
        # Value编辑
        value_frame = ttk.LabelFrame(scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # JSON格式化按钮
        json_btn_frame = ttk.Frame(value_frame)
        json_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def format_json():
            try:
                import json
                current_value = value_text.get(1.0, tk.END).strip()
                parsed = json.loads(current_value)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                value_text.delete(1.0, tk.END)
                value_text.insert(1.0, formatted)
            except json.JSONDecodeError:
                messagebox.showerror("JSON Error", "Invalid JSON format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to format JSON: {e}")
        
        def minify_json():
            try:
                import json
                current_value = value_text.get(1.0, tk.END).strip()
                parsed = json.loads(current_value)
                minified = json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
                value_text.delete(1.0, tk.END)
                value_text.insert(1.0, minified)
            except json.JSONDecodeError:
                messagebox.showerror("JSON Error", "Invalid JSON format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to minify JSON: {e}")
        
        ttk.Button(json_btn_frame, text="Format JSON", command=format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", command=minify_json).pack(side=tk.LEFT)
        
        # 文本编辑器
        text_frame = ttk.Frame(value_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        value_text = tk.Text(text_frame, wrap=tk.WORD, height=20, width=80)
        value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        value_text.insert(tk.END, str(value))
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        value_text.configure(yscrollcommand=text_scroll.set)
        
        # 按钮
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_changes():
            new_value = value_text.get(1.0, tk.END).strip()
            try:
                # 更新Redis中的值
                self.redis_client.hset(key, field, new_value)
                messagebox.showinfo("Success", f"Hash field '{field}' updated successfully!")
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()
                # 刷新key详情显示
                self.load_key_details(key)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update hash field: {e}")
        
        def cancel_dialog():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Save", command=save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=cancel_dialog).pack(side=tk.RIGHT)
        
        # 设置焦点到value文本框
        value_text.focus_set()
            
    def query_list_range(self, key, key_type):
        """查询list/zset范围"""
        range_str = self.struct_query_var.get().strip()
        try:
            parts = range_str.split()
            start = int(parts[0]) if len(parts) > 0 else 0
            end = int(parts[1]) if len(parts) > 1 else -1
            
            if key_type == 'list':
                result = self.redis_client.lrange(key, start, end)
            elif key_type == 'zset':
                result = self.redis_client.zrange(key, start, end, withscores=True)
            
            self.show_query_result(result)
        except Exception as e:
            messagebox.showerror("Query Error", f"Failed to get range: {e}")
            
    def load_hash_data_to_tree(self, hash_data):
        """将hash数据加载到树形控件"""
        # 清空现有数据
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # 加载数据
        if isinstance(hash_data, dict):
            for field, val in hash_data.items():
                self.data_tree.insert('', tk.END, values=(field, val))
    
    def filter_hash_data(self, key):
        """过滤hash数据"""
        filter_text = self.struct_query_var.get().strip()
        
        if not filter_text:
            # 如果过滤文本为空，显示所有数据
            self.load_hash_data_to_tree(self.original_hash_data)
            self._update_filter_status(len(self.original_hash_data), len(self.original_hash_data), filter_text)
            return
        
        try:
            # 过滤数据 - 支持字段名和值的模糊匹配
            filtered_data = {}
            filter_lower = filter_text.lower()
            
            for field, value in self.original_hash_data.items():
                field_str = str(field).lower()
                value_str = str(value).lower()
                
                # 如果字段名或值包含过滤文本，则包含该项
                if filter_lower in field_str or filter_lower in value_str:
                    filtered_data[field] = value
            
            # 更新显示
            self.load_hash_data_to_tree(filtered_data)
            self._update_filter_status(len(filtered_data), len(self.original_hash_data), filter_text)
            
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to filter hash data: {e}")
    
    def load_list_data_to_tree(self, list_data):
        """将list数据加载到树形控件"""
        # 清空现有数据
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # 加载数据
        if isinstance(list_data, list):
            for i, val in enumerate(list_data):
                self.data_tree.insert('', tk.END, values=(i, val))
    
    def load_set_data_to_tree(self, set_data):
        """将set数据加载到树形控件"""
        # 清空现有数据
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # 加载数据
        if isinstance(set_data, list):
            for val in sorted(set_data):  # 排序显示，便于查看
                self.data_tree.insert('', tk.END, values=(val,))
    
    def load_zset_data_to_tree(self, zset_data):
        """将zset数据加载到树形控件"""
        # 清空现有数据
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # 加载数据
        if isinstance(zset_data, list):
            for i in range(0, len(zset_data), 2):
                if i + 1 < len(zset_data):
                    self.data_tree.insert('', tk.END, values=(zset_data[i+1], zset_data[i]))
    
    def filter_list_zset_data(self, key, key_type):
        """过滤list和zset数据"""
        filter_text = self.struct_query_var.get().strip()
        
        try:
            if key_type == 'list':
                if not filter_text:
                    # 如果过滤文本为空，显示所有数据
                    self.load_list_data_to_tree(self.original_list_data)
                    self._update_filter_status(len(self.original_list_data), len(self.original_list_data), filter_text)
                    return
                
                # 过滤数据 - 支持值的模糊匹配
                filtered_data = []
                filter_lower = filter_text.lower()
                
                for val in self.original_list_data:
                    value_str = str(val).lower()
                    if filter_lower in value_str:
                        filtered_data.append(val)
                
                # 更新显示
                self.load_list_data_to_tree(filtered_data)
                self._update_filter_status(len(filtered_data), len(self.original_list_data), filter_text)
                
            elif key_type == 'zset':
                if not filter_text:
                    # 如果过滤文本为空，显示所有数据
                    self.load_zset_data_to_tree(self.original_zset_data)
                    total_count = len(self.original_zset_data) // 2
                    self._update_filter_status(total_count, total_count, filter_text)
                    return
                
                # 过滤数据 - 支持成员名和分数的模糊匹配
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
                
                # 更新显示
                self.load_zset_data_to_tree(filtered_data)
                filtered_count = len(filtered_data) // 2
                total_count = len(self.original_zset_data) // 2
                self._update_filter_status(filtered_count, total_count, filter_text)
                
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to filter {key_type} data: {e}")
    
    def filter_set_data(self, key):
        """过滤set数据"""
        filter_text = self.struct_query_var.get().strip()
        
        if not filter_text:
            # 如果过滤文本为空，显示所有数据
            self.load_set_data_to_tree(self.original_set_data)
            self._update_filter_status(len(self.original_set_data), len(self.original_set_data), filter_text)
            return
        
        try:
            # 过滤数据 - 支持值的模糊匹配
            filtered_data = []
            filter_lower = filter_text.lower()
            
            for val in self.original_set_data:
                value_str = str(val).lower()
                if filter_lower in value_str:
                    filtered_data.append(val)
            
            # 更新显示
            self.load_set_data_to_tree(filtered_data)
            self._update_filter_status(len(filtered_data), len(self.original_set_data), filter_text)
            
        except Exception as e:
            messagebox.showerror("Filter Error", f"Failed to filter set data: {e}")
    
    def _update_filter_status(self, filtered_count, total_count, filter_text):
        """更新过滤状态显示"""
        # 清理之前的状态标签
        if hasattr(self, 'filter_status_label'):
            self.filter_status_label.destroy()
        
        # 在表格下方显示过滤状态
        parent_frame = self.data_tree.master.master  # 获取包含表格的父框架
        self.filter_status_label = ttk.Label(parent_frame, 
                                            text=f"Showing {filtered_count} of {total_count} items" + 
                                                 (f" (filtered by: '{filter_text}')" if filter_text else ""),
                                            font=('SF Pro Display', 9),
                                            foreground='#666666')
        self.filter_status_label.pack(pady=(5, 0))
    
    def on_treeview_motion(self, event):
        """处理Treeview鼠标移动事件，实现悬停效果"""
        try:
            # 获取鼠标位置的item
            item = self.data_tree.identify_row(event.y)
            
            # 如果有之前悬停的item且不是当前选中的，清除悬停状态
            if hasattr(self, '_hover_item') and self._hover_item != item:
                if self._hover_item and self._hover_item not in self.data_tree.selection():
                    # 清除之前的悬停状态
                    pass
            
            # 设置当前悬停的item
            if item:
                self._hover_item = item
                # 如果不是选中状态，设置悬停状态
                if item not in self.data_tree.selection():
                    self.data_tree.set(item, '#0', '')  # 触发重绘
            else:
                self._hover_item = None
                
        except Exception:
            pass
    
    def on_treeview_leave(self, event):
        """处理Treeview鼠标离开事件"""
        try:
            # 清除悬停状态
            if hasattr(self, '_hover_item'):
                self._hover_item = None
        except Exception:
            pass
    
    def edit_table_item(self, key, key_type):
        """编辑表格项"""
        selection = self.data_tree.selection()
        if not selection:
            return
            
        item = self.data_tree.item(selection[0])
        values = item['values']
        
        if key_type == 'hash':
            field, value = values[0], values[1]
            self.show_hash_edit_dialog(key, field, value, selection[0])
        elif key_type == 'list':
            index, value = int(values[0]), values[1]
            new_value = simpledialog.askstring("Edit List Value", f"Index: {index}\nEnter new value:", initialvalue=value)
            if new_value is not None:
                try:
                    # 直接更新Redis
                    self.redis_client.lset(key, index, new_value)
                    # 更新原始数据
                    if hasattr(self, 'original_list_data') and 0 <= index < len(self.original_list_data):
                        self.original_list_data[index] = new_value
                    # 更新UI
                    self.data_tree.item(selection[0], values=(index, new_value))
                    messagebox.showinfo("Success", "List item updated successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update list item: {e}")
        elif key_type == 'set':
            old_value = values[0]
            self.show_set_edit_dialog(key, old_value, selection[0])
        elif key_type == 'zset':
            score, member = float(values[0]), values[1]
            new_member = simpledialog.askstring("Edit ZSet Member", f"Score: {score}\nEnter new member:", initialvalue=member)
            if new_member is not None:
                new_score_str = simpledialog.askstring("Edit ZSet Score", f"Member: {new_member}\nEnter new score:", initialvalue=str(score))
                if new_score_str is not None:
                    try:
                        new_score = float(new_score_str)
                        
                        # 如果成员名改变了，删除旧成员
                        if member != new_member:
                            self.redis_client.zrem(key, member)
                        
                        # 添加/更新新成员
                        self.redis_client.zadd(key, {new_member: new_score})
                        
                        # 更新原始数据
                        if hasattr(self, 'original_zset_data'):
                            # 找到并更新原始数据中的项目
                            for i in range(0, len(self.original_zset_data), 2):
                                if i < len(self.original_zset_data) and self.original_zset_data[i] == member:
                                    self.original_zset_data[i] = new_member
                                    self.original_zset_data[i + 1] = new_score
                                    break
                        
                        # 更新UI
                        self.data_tree.item(selection[0], values=(new_score, new_member))
                        
                        messagebox.showinfo("Success", "ZSet member updated successfully!")
                    except ValueError:
                        messagebox.showerror("Error", "Score must be a valid number")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to update zset member: {e}")
    def start_keepalive(self):
        """启动Redis连接保活"""
        self.keepalive_running = True
        
        def keepalive_worker():
            while self.keepalive_running and self.redis_client:
                try:
                    time.sleep(30)  # 每30秒ping一次
                    if self.redis_client and self.keepalive_running:
                        self.redis_client.ping()
                except Exception:
                    break
        
        self.keepalive_thread = threading.Thread(target=keepalive_worker, daemon=True)
        self.keepalive_thread.start()
        
    def stop_keepalive(self):
        """停止Redis连接保活"""
        self.keepalive_running = False
        
    def show_hash_edit_dialog(self, key, field, value, tree_item):
        """显示hash编辑对话框，支持同时编辑key和value，并支持JSON格式化"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Hash Field")
        dialog.geometry("900x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 创建滚动框架
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Field编辑
        field_frame = ttk.LabelFrame(scrollable_frame, text="Field (Key)")
        field_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        field_var = tk.StringVar(value=field)
        field_entry = ttk.Entry(field_frame, textvariable=field_var)
        field_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Value编辑
        value_frame = ttk.LabelFrame(scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # JSON格式化按钮
        json_btn_frame = ttk.Frame(value_frame)
        json_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def format_json():
            try:
                import json
                current_value = value_text.get(1.0, tk.END).strip()
                parsed = json.loads(current_value)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                value_text.delete(1.0, tk.END)
                value_text.insert(1.0, formatted)
            except json.JSONDecodeError:
                messagebox.showerror("JSON Error", "Invalid JSON format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to format JSON: {e}")
        
        def minify_json():
            try:
                import json
                current_value = value_text.get(1.0, tk.END).strip()
                parsed = json.loads(current_value)
                minified = json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
                value_text.delete(1.0, tk.END)
                value_text.insert(1.0, minified)
            except json.JSONDecodeError:
                messagebox.showerror("JSON Error", "Invalid JSON format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to minify JSON: {e}")
        
        ttk.Button(json_btn_frame, text="Format JSON", command=format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", command=minify_json).pack(side=tk.LEFT)
        
        # 文本编辑器
        text_frame = ttk.Frame(value_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        value_text = tk.Text(text_frame, wrap=tk.WORD, height=20, width=80)
        value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        value_text.insert(tk.END, str(value))
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        value_text.configure(yscrollcommand=text_scroll.set)
        
        # 按钮
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_changes():
            new_field = field_var.get().strip()
            new_value = value_text.get(1.0, tk.END).strip()
            
            if not new_field:
                messagebox.showerror("Error", "Field name cannot be empty")
                return
            
            try:
                # 如果字段名改变了，需要删除旧字段
                if field and field != new_field:
                    self.redis_client.hdel(key, field)
                
                # 设置新字段值
                self.redis_client.hset(key, new_field, new_value)
                
                # 更新原始数据
                if hasattr(self, 'original_hash_data'):
                    if field and field != new_field and field in self.original_hash_data:
                        del self.original_hash_data[field]
                    self.original_hash_data[new_field] = new_value
                
                # 更新UI
                self.data_tree.item(tree_item, values=(new_field, new_value))
                
                messagebox.showinfo("Success", "Hash field updated successfully!")
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update hash field: {e}")
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        def cancel_dialog():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Save", command=save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=cancel_dialog).pack(side=tk.RIGHT)
        
        # 设置焦点到field输入框
        field_entry.focus_set()
        field_entry.select_range(0, tk.END)
        
    def show_set_edit_dialog(self, key, old_value, tree_item):
        """显示set编辑对话框，支持JSON格式化"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Set Value")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Value编辑
        value_frame = ttk.LabelFrame(dialog, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # JSON格式化按钮
        json_btn_frame = ttk.Frame(value_frame)
        json_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def format_json():
            try:
                import json
                current_value = value_text.get(1.0, tk.END).strip()
                parsed = json.loads(current_value)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                value_text.delete(1.0, tk.END)
                value_text.insert(1.0, formatted)
            except json.JSONDecodeError:
                messagebox.showerror("JSON Error", "Invalid JSON format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to format JSON: {e}")
        
        def minify_json():
            try:
                import json
                current_value = value_text.get(1.0, tk.END).strip()
                parsed = json.loads(current_value)
                minified = json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
                value_text.delete(1.0, tk.END)
                value_text.insert(1.0, minified)
            except json.JSONDecodeError:
                messagebox.showerror("JSON Error", "Invalid JSON format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to minify JSON: {e}")
        
        ttk.Button(json_btn_frame, text="Format JSON", command=format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", command=minify_json).pack(side=tk.LEFT)
        
        # 文本编辑器
        text_frame = ttk.Frame(value_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        value_text = tk.Text(text_frame, wrap=tk.WORD, height=15)
        value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        value_text.insert(tk.END, str(old_value))
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        value_text.configure(yscrollcommand=text_scroll.set)
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_changes():
            new_value = value_text.get(1.0, tk.END).strip()
            if new_value != old_value:
                try:
                    # 删除旧值，添加新值
                    self.redis_client.srem(key, old_value)
                    result = self.redis_client.sadd(key, new_value)
                    
                    # 更新原始数据
                    if hasattr(self, 'original_set_data'):
                        if old_value in self.original_set_data:
                            self.original_set_data.remove(old_value)
                        if new_value not in self.original_set_data:
                            self.original_set_data.append(new_value)
                    
                    # 更新UI
                    self.data_tree.item(tree_item, values=(new_value,))
                    
                    messagebox.showinfo("Success", "Set member updated successfully!")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update set member: {e}")
            else:
                dialog.destroy()
        
        ttk.Button(btn_frame, text="Save", command=save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
        value_text.focus_set()
        
    def add_table_item(self, key, key_type):
        """添加表格项 - 直接添加到Redis"""
        if key_type == 'hash':
            # 使用对话框添加hash字段
            self.show_add_hash_dialog(key)
        elif key_type == 'list':
            value = simpledialog.askstring("Add List Item", "Enter value:")
            if value is not None:
                try:
                    # 直接添加到Redis
                    self.redis_client.rpush(key, value)
                    # 更新原始数据
                    if hasattr(self, 'original_list_data'):
                        self.original_list_data.append(value)
                    # 刷新显示
                    self.refresh_current_display(key, key_type)
                    messagebox.showinfo("Success", "List item added successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add list item: {e}")
        elif key_type == 'set':
            value = simpledialog.askstring("Add Set Member", "Enter member:")
            if value is not None:
                try:
                    # 直接添加到Redis
                    result = self.redis_client.sadd(key, value)
                    if result > 0:
                        # 更新原始数据
                        if hasattr(self, 'original_set_data'):
                            if value not in self.original_set_data:
                                self.original_set_data.append(value)
                        # 刷新显示
                        self.refresh_current_display(key, key_type)
                        messagebox.showinfo("Success", "Set member added successfully!")
                    else:
                        messagebox.showinfo("Info", "Member already exists in set")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to add set member: {e}")
        elif key_type == 'zset':
            member = simpledialog.askstring("Add ZSet Member", "Enter member:")
            if member:
                score = simpledialog.askstring("Add ZSet Score", f"Member: {member}\nEnter score:")
                if score is not None:
                    try:
                        score_float = float(score)
                        # 直接添加到Redis
                        self.redis_client.zadd(key, {member: score_float})
                        # 更新原始数据
                        if hasattr(self, 'original_zset_data'):
                            # 检查是否已存在该成员
                            found = False
                            for i in range(0, len(self.original_zset_data), 2):
                                if i < len(self.original_zset_data) and self.original_zset_data[i] == member:
                                    self.original_zset_data[i + 1] = score_float  # 更新分数
                                    found = True
                                    break
                            if not found:
                                self.original_zset_data.extend([member, score_float])
                        # 刷新显示
                        self.refresh_current_display(key, key_type)
                        messagebox.showinfo("Success", "ZSet member added successfully!")
                    except ValueError:
                        messagebox.showerror("Error", "Score must be a valid number")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to add zset member: {e}")
    
    def show_add_hash_dialog(self, key):
        """显示添加hash字段的对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Hash Field")
        dialog.geometry("900x700")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 创建滚动框架
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Field编辑
        field_frame = ttk.LabelFrame(scrollable_frame, text="Field (Key)")
        field_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        field_var = tk.StringVar()
        field_entry = ttk.Entry(field_frame, textvariable=field_var)
        field_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Value编辑
        value_frame = ttk.LabelFrame(scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # JSON格式化按钮
        json_btn_frame = ttk.Frame(value_frame)
        json_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        def format_json():
            try:
                import json
                current_value = value_text.get(1.0, tk.END).strip()
                parsed = json.loads(current_value)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
                value_text.delete(1.0, tk.END)
                value_text.insert(1.0, formatted)
            except json.JSONDecodeError:
                messagebox.showerror("JSON Error", "Invalid JSON format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to format JSON: {e}")
        
        def minify_json():
            try:
                import json
                current_value = value_text.get(1.0, tk.END).strip()
                parsed = json.loads(current_value)
                minified = json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
                value_text.delete(1.0, tk.END)
                value_text.insert(1.0, minified)
            except json.JSONDecodeError:
                messagebox.showerror("JSON Error", "Invalid JSON format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to minify JSON: {e}")
        
        ttk.Button(json_btn_frame, text="Format JSON", command=format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", command=minify_json).pack(side=tk.LEFT)
        
        # 文本编辑器
        text_frame = ttk.Frame(value_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        value_text = tk.Text(text_frame, wrap=tk.WORD, height=20, width=80)
        value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        value_text.configure(yscrollcommand=text_scroll.set)
        
        # 按钮
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_new_field():
            new_field = field_var.get().strip()
            new_value = value_text.get(1.0, tk.END).strip()
            
            if not new_field:
                messagebox.showerror("Error", "Field name cannot be empty")
                return
            
            try:
                # 直接添加到Redis
                self.redis_client.hset(key, new_field, new_value)
                # 更新原始数据
                if hasattr(self, 'original_hash_data'):
                    self.original_hash_data[new_field] = new_value
                # 刷新显示
                self.refresh_current_display(key, 'hash')
                messagebox.showinfo("Success", "Hash field added successfully!")
                canvas.unbind_all("<MouseWheel>")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add hash field: {e}")
        
        def cancel_dialog():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Add", command=save_new_field).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=cancel_dialog).pack(side=tk.RIGHT)
        
        # 设置焦点到field输入框
        field_entry.focus_set()
    
    def refresh_current_display(self, key, key_type):
        """刷新当前显示，保持过滤状态"""
        try:
            # 重新从Redis加载数据
            if key_type == 'hash':
                new_data = self.redis_client.hgetall(key)
                self.original_hash_data = new_data
                # 如果有过滤状态，重新应用过滤
                if hasattr(self, 'struct_query_var') and self.struct_query_var.get().strip():
                    self.filter_hash_data(key)
                else:
                    self.load_hash_data_to_tree(new_data)
            elif key_type == 'list':
                new_data = self.redis_client.lrange(key, 0, -1)
                self.original_list_data = new_data
                if hasattr(self, 'struct_query_var') and self.struct_query_var.get().strip():
                    self.filter_list_zset_data(key, key_type)
                else:
                    self.load_list_data_to_tree(new_data)
            elif key_type == 'set':
                new_data = list(self.redis_client.smembers(key))
                self.original_set_data = new_data
                if hasattr(self, 'struct_query_var') and self.struct_query_var.get().strip():
                    self.filter_set_data(key)
                else:
                    self.load_set_data_to_tree(new_data)
            elif key_type == 'zset':
                new_data = self.redis_client.zrange(key, 0, -1, withscores=True)
                self.original_zset_data = new_data
                if hasattr(self, 'struct_query_var') and self.struct_query_var.get().strip():
                    self.filter_list_zset_data(key, key_type)
                else:
                    self.load_zset_data_to_tree(new_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh display: {e}")
                    
    def update_structured_key(self, key, key_type):
        """更新结构化键"""
        try:
            # 收集当前显示的数据（可能被修改过）
            displayed_data = {}
            displayed_list = []
            displayed_set = []
            displayed_zset = []
            
            for item in self.data_tree.get_children():
                values = self.data_tree.item(item)['values']
                
                if key_type == 'hash':
                    field, value = values[0], values[1]
                    displayed_data[field] = value
                elif key_type == 'list':
                    index, value = int(values[0]), values[1]
                    displayed_list.append((index, value))
                elif key_type == 'set':
                    value = values[0]
                    displayed_set.append(value)
                elif key_type == 'zset':
                    score, member = float(values[0]), values[1]
                    displayed_zset.append((member, score))
            
            # 检查是否有过滤状态
            is_filtered = hasattr(self, 'filter_status_label') and self.filter_status_label.winfo_exists()
            
            if is_filtered:
                # 如果有过滤，需要合并显示的数据和隐藏的数据
                if key_type == 'hash':
                    # 合并hash数据：用显示的数据更新原始数据
                    merged_data = self.original_hash_data.copy()
                    merged_data.update(displayed_data)
                    final_data = merged_data
                elif key_type == 'list':
                    # 对于list，需要按索引更新
                    merged_data = self.original_list_data.copy()
                    for index, value in displayed_list:
                        if 0 <= index < len(merged_data):
                            merged_data[index] = value
                    final_data = merged_data
                elif key_type == 'set':
                    # 对于set，需要找出原始数据中对应的项并更新
                    # 这里比较复杂，因为set的显示是排序后的
                    # 简化处理：如果有过滤，建议用户先清除过滤再更新
                    if len(displayed_set) < len(self.original_set_data):
                        response = messagebox.askyesno(
                            "Filtered Update Warning", 
                            "You are updating filtered data. This will only update the visible items.\n\n"
                            "Do you want to:\n"
                            "• Yes: Update only visible items (hidden items will be preserved)\n"
                            "• No: Cancel and clear filter first"
                        )
                        if not response:
                            return
                    
                    # 保留原始数据，只更新显示的部分
                    # 由于set的复杂性，这里采用保守策略
                    final_data = displayed_set
                elif key_type == 'zset':
                    # 对于zset，合并数据
                    # 将原始数据转换为字典格式便于处理
                    original_dict = {}
                    for i in range(0, len(self.original_zset_data), 2):
                        if i + 1 < len(self.original_zset_data):
                            member = self.original_zset_data[i]
                            score = self.original_zset_data[i + 1]
                            original_dict[member] = score
                    
                    # 更新显示的数据
                    for member, score in displayed_zset:
                        original_dict[member] = score
                    
                    final_data = original_dict
            else:
                # 没有过滤，直接使用显示的数据
                if key_type == 'hash':
                    final_data = displayed_data
                elif key_type == 'list':
                    final_data = [value for index, value in sorted(displayed_list)]
                elif key_type == 'set':
                    final_data = displayed_set
                elif key_type == 'zset':
                    final_data = {member: score for member, score in displayed_zset}
            
            # 先删除原键
            self.redis_client.delete(key)
            
            # 根据类型重新创建
            if key_type == 'hash':
                if final_data:
                    self.redis_client.hset(key, mapping=final_data)
            elif key_type == 'list':
                if final_data:
                    for value in final_data:
                        self.redis_client.rpush(key, value)
            elif key_type == 'set':
                if final_data:
                    self.redis_client.sadd(key, *final_data)
            elif key_type == 'zset':
                if final_data:
                    self.redis_client.zadd(key, final_data)
                    
            messagebox.showinfo("Success", "Key updated successfully!")
            
            # 重新加载数据并清除过滤状态
            if hasattr(self, 'struct_query_var'):
                self.struct_query_var.set("")  # 清除过滤输入
            self.load_key_details(key)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update key: {e}")
            
    def add_new_key(self):
        """添加新键"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Key")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 键名
        ttk.Label(dialog, text="Key Name:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        key_entry = ttk.Entry(dialog)
        key_entry.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 数据类型
        ttk.Label(dialog, text="Data Type:").pack(anchor=tk.W, padx=10)
        type_var = tk.StringVar(value="string")
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=["string", "list", "set", "hash", "zset"], state="readonly")
        type_combo.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 值输入区域
        value_frame = ttk.LabelFrame(dialog, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # string/list/set 的值输入
        ttk.Label(value_frame, text="Value:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        value_entry = ttk.Entry(value_frame)
        value_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # hash/zset 的键值对输入
        hash_frame = ttk.Frame(value_frame)
        ttk.Label(hash_frame, text="Field/Member:").pack(anchor=tk.W, padx=5)
        field_entry = ttk.Entry(hash_frame)
        field_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(hash_frame, text="Value/Score:").pack(anchor=tk.W, padx=5)
        field_value_entry = ttk.Entry(hash_frame)
        field_value_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        def toggle_input_fields():
            if type_var.get() in ['hash', 'zset']:
                value_entry.pack_forget()
                hash_frame.pack(fill=tk.X, padx=5, pady=5)
            else:
                hash_frame.pack_forget()
                value_entry.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        type_combo.bind('<<ComboboxSelected>>', lambda e: toggle_input_fields())
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def create_key():
            try:
                key_name = key_entry.get().strip()
                if not key_name:
                    messagebox.showerror("Error", "Key name is required")
                    return
                    
                data_type = type_var.get()
                
                if data_type == 'string':
                    value = value_entry.get()
                    self.redis_client.set(key_name, value)
                elif data_type == 'list':
                    value = value_entry.get()
                    if value:
                        self.redis_client.rpush(key_name, value)
                elif data_type == 'set':
                    value = value_entry.get()
                    if value:
                        self.redis_client.sadd(key_name, value)
                elif data_type == 'hash':
                    field = field_entry.get().strip()
                    value = field_value_entry.get()
                    if field:
                        self.redis_client.hset(key_name, field, value)
                elif data_type == 'zset':
                    member = field_entry.get().strip()
                    score = field_value_entry.get().strip()
                    if member and score:
                        self.redis_client.zadd(key_name, {member: float(score)})
                
                messagebox.showinfo("Success", "Key created successfully!")
                dialog.destroy()
                self.search_keys()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create key: {e}")
        
        ttk.Button(btn_frame, text="Create", command=create_key).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
    def execute_key_query(self, key, key_type):
        """执行键查询"""
        query = self.query_var.get().strip()
        if not query:
            return
            
        try:
            # 如果查询内容就是key本身，直接重新加载key详情
            if query == key:
                self.load_key_details(key)
                return
            
            # 解析查询命令
            parts = query.split()
            if not parts:
                return
                
            cmd = parts[0].upper()
            
            if key_type == 'hash':
                if cmd == 'HGET' and len(parts) >= 2:
                    # HGET field 或 HGET key field
                    if len(parts) == 2:
                        # 只有field，使用当前key
                        field = parts[1]
                        result = self.redis_client.hget(key, field)
                    else:
                        # 完整的HGET key field命令
                        field = parts[2]
                        result = self.redis_client.hget(parts[1], field)
                    self.show_query_result({field: result})
                elif cmd == 'HKEYS':
                    result = self.redis_client.hkeys(key)
                    self.show_query_result(result)
                elif cmd == 'HVALS':
                    result = self.redis_client.hvals(key)
                    self.show_query_result(result)
                elif cmd == 'HGETALL':
                    result = self.redis_client.hgetall(key)
                    self.show_query_result(result)
                else:
                    # 直接执行命令，如果没有指定key则使用当前key
                    if len(parts) == 1 and cmd in ['HKEYS', 'HVALS', 'HGETALL', 'HLEN']:
                        result = self.redis_client.execute_command(cmd, key)
                    else:
                        result = self.redis_client.execute_command(cmd, *parts[1:])
                    self.show_query_result(result)
            elif key_type == 'list':
                if cmd == 'LRANGE' and len(parts) >= 3:
                    start = int(parts[1])
                    end = int(parts[2])
                    result = self.redis_client.lrange(key, start, end)
                    self.show_query_result(result)
                elif cmd == 'LLEN':
                    result = self.redis_client.llen(key)
                    self.show_query_result(result)
                elif cmd == 'LINDEX' and len(parts) >= 2:
                    index = int(parts[1])
                    result = self.redis_client.lindex(key, index)
                    self.show_query_result(result)
                else:
                    # 直接执行命令
                    if len(parts) == 1 and cmd in ['LLEN']:
                        result = self.redis_client.execute_command(cmd, key)
                    else:
                        args = [key] + parts[1:]
                        result = self.redis_client.execute_command(cmd, *args)
                    self.show_query_result(result)
            elif key_type == 'set':
                if cmd == 'SMEMBERS':
                    result = self.redis_client.smembers(key)
                    self.show_query_result(list(result))
                elif cmd == 'SCARD':
                    result = self.redis_client.scard(key)
                    self.show_query_result(result)
                elif cmd == 'SISMEMBER' and len(parts) >= 2:
                    member = parts[1]
                    result = self.redis_client.sismember(key, member)
                    self.show_query_result(result)
                else:
                    if len(parts) == 1 and cmd in ['SMEMBERS', 'SCARD']:
                        result = self.redis_client.execute_command(cmd, key)
                    else:
                        args = [key] + parts[1:]
                        result = self.redis_client.execute_command(cmd, *args)
                    self.show_query_result(result)
            elif key_type == 'zset':
                if cmd == 'ZRANGE' and len(parts) >= 3:
                    start = int(parts[1])
                    end = int(parts[2])
                    withscores = len(parts) > 3 and parts[3].upper() == 'WITHSCORES'
                    result = self.redis_client.zrange(key, start, end, withscores=withscores)
                    self.show_query_result(result)
                elif cmd == 'ZCARD':
                    result = self.redis_client.zcard(key)
                    self.show_query_result(result)
                elif cmd == 'ZSCORE' and len(parts) >= 2:
                    member = parts[1]
                    result = self.redis_client.zscore(key, member)
                    self.show_query_result(result)
                else:
                    if len(parts) == 1 and cmd in ['ZCARD']:
                        result = self.redis_client.execute_command(cmd, key)
                    else:
                        args = [key] + parts[1:]
                        result = self.redis_client.execute_command(cmd, *args)
                    self.show_query_result(result)
            else:
                # 其他类型的通用查询
                if cmd in ['GET', 'TYPE', 'TTL', 'EXISTS']:
                    result = self.redis_client.execute_command(cmd, key)
                else:
                    args = [key] + parts[1:]
                    result = self.redis_client.execute_command(cmd, *args)
                self.show_query_result(result)
                    
        except Exception as e:
            messagebox.showerror("Query Error", f"Failed to execute query: {e}")
            
    def show_query_result(self, result):
        """显示查询结果"""
        result_window = tk.Toplevel(self.root)
        result_window.title("Query Result")
        result_window.geometry("800x600")
        result_window.transient(self.root)
        
        # 结果显示区域
        text_frame = ttk.Frame(result_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        result_text = tk.Text(text_frame, wrap=tk.WORD)
        result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        result_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=result_text.yview)
        result_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        result_text.configure(yscrollcommand=result_scroll.set)
        
        # 格式化结果
        try:
            import json
            if isinstance(result, (dict, list)):
                formatted_result = json.dumps(result, indent=2, ensure_ascii=False)
            else:
                formatted_result = str(result)
        except:
            formatted_result = str(result)
            
        result_text.insert(tk.END, formatted_result)
        result_text.config(state=tk.DISABLED)
        
        # 关闭按钮
        ttk.Button(result_window, text="Close", command=result_window.destroy).pack(pady=5)
        
    def format_json_value(self):
        """格式化JSON值"""
        try:
            import json
            current_value = self.value_text.get(1.0, tk.END).strip()
            parsed = json.loads(current_value)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, formatted)
        except json.JSONDecodeError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format JSON: {e}")
            
    def minify_json_value(self):
        """压缩JSON值"""
        try:
            import json
            current_value = self.value_text.get(1.0, tk.END).strip()
            parsed = json.loads(current_value)
            minified = json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
            
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, minified)
        except json.JSONDecodeError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify JSON: {e}")
        
    def execute_command(self):
        if not self.redis_client:
            self.append_output("No active connection")
            return
            
        command = self.cmd_var.get().strip()
        if not command:
            return
            
        def execute_thread():
            try:
                self.root.after(0, lambda: self.append_output(f"> {command}"))
                
                # 解析命令
                parts = command.split()
                cmd = parts[0].upper()
                args = parts[1:] if len(parts) > 1 else []
                
                # 执行命令
                if cmd == 'SELECT' and args:
                    result = self.redis_client.execute_command('SELECT', int(args[0]))
                    self.db_var.set(f"DB {args[0]}")
                    self.search_keys()
                else:
                    result = self.redis_client.execute_command(cmd, *args)
                
                # 格式化输出
                if isinstance(result, list):
                    if not result:
                        output = "(empty list or set)"
                    else:
                        output = '\n'.join([f"{i+1}) {item}" for i, item in enumerate(result)])
                elif isinstance(result, dict):
                    output = '\n'.join([f"{k}: {v}" for k, v in result.items()])
                elif result is None:
                    output = "(nil)"
                else:
                    output = str(result)
                
                self.root.after(0, lambda: self.append_output(output))
                self.root.after(0, lambda: self.cmd_var.set(""))
                self.root.after(0, self.hide_suggestions)
                
            except Exception as e:
                self.root.after(0, lambda: self.append_output(f"Error: {e}"))
        
        threading.Thread(target=execute_thread, daemon=True).start()
        
    def on_cmd_key_release(self, event):
        """处理命令输入的键盘事件"""
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Return', 'Tab']:
            return
            
        current_text = self.cmd_var.get().upper()
        if not current_text:
            self.hide_suggestions()
            return
            
        # 查找匹配的命令
        matches = [cmd for cmd in self.redis_commands if cmd.startswith(current_text)]
        
        if matches:
            self.show_suggestions(matches)
        else:
            self.hide_suggestions()
            
    def on_cmd_tab(self, event):
        """处理Tab键自动完成"""
        current_text = self.cmd_var.get().upper()
        if not current_text:
            return 'break'
            
        matches = [cmd for cmd in self.redis_commands if cmd.startswith(current_text)]
        if matches:
            # 如果只有一个匹配，直接完成
            if len(matches) == 1:
                self.cmd_var.set(matches[0] + ' ')
                self.cmd_entry.icursor(tk.END)
                self.hide_suggestions()
            else:
                # 多个匹配，显示提示列表
                self.show_suggestions(matches)
                
        return 'break'  # 阻止默认Tab行为
        
    def show_suggestions(self, suggestions):
        """显示命令提示列表"""
        self.suggestion_listbox.delete(0, tk.END)
        for suggestion in suggestions[:10]:  # 最多显示10个
            self.suggestion_listbox.insert(tk.END, suggestion)
            
        if not self.suggestion_frame.winfo_viewable():
            self.suggestion_frame.pack(fill=tk.X, pady=(5, 0))
            self.suggestion_listbox.pack(fill=tk.X)
            
    def hide_suggestions(self):
        """隐藏命令提示列表"""
        if self.suggestion_frame.winfo_viewable():
            self.suggestion_frame.pack_forget()
            
    def on_suggestion_select(self, event=None):
        """选择提示命令"""
        selection = self.suggestion_listbox.curselection()
        if selection:
            selected_cmd = self.suggestion_listbox.get(selection[0])
            self.cmd_var.set(selected_cmd + ' ')
            self.cmd_entry.icursor(tk.END)
            self.cmd_entry.focus_set()
            self.hide_suggestions()
        
    def append_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def clear_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
    def on_separator_change(self, event):
        if self.redis_client and hasattr(self, 'current_keys'):
            self.update_keys_tree(self.current_keys)
            
    def refresh_connection_list(self):
        self.conn_listbox.delete(0, tk.END)
        for i, conn in enumerate(self.connections):
            # 标记当前连接
            if i == self.current_conn_index and self.redis_client:
                display_name = f"✅ {conn['name']} (Connected)"
            else:
                display_name = conn['name']
            self.conn_listbox.insert(tk.END, display_name)
            
    def save_connections(self):
        config_path = Path.home() / ".redis_manager_config.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(self.connections, f, indent=2)
        except Exception as e:
            print(f"Failed to save connections: {e}")
            
    def load_connections(self):
        config_path = Path.home() / ".redis_manager_config.json"
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.connections = json.load(f)
                self.refresh_connection_list()
        except Exception as e:
            print(f"Failed to load connections: {e}")
            
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        self.save_connections()
        self.stop_keepalive()
        
        # 重置连接状态
        self.current_conn_index = -1
        
        if self.ssh_tunnel:
            self.ssh_tunnel.close()
        if self.ssh_client:
            self.ssh_client.close()
        self.root.destroy()

if __name__ == "__main__":
    app = RedisManager()
    app.run()