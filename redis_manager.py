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
        
        self.connections = []
        self.current_conn = None
        self.redis_client = None
        self.ssh_client = None
        self.ssh_tunnel = None
        self.keepalive_thread = None
        self.keepalive_running = False
        
        self.setup_ui()
        self.load_connections()
        
    def setup_ui(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧面板
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # 右侧面板
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
        
    def setup_left_panel(self, parent):
        # 连接管理
        conn_frame = ttk.LabelFrame(parent, text="Connections")
        conn_frame.pack(fill=tk.BOTH, pady=(0, 10))
        
        # 连接列表
        self.conn_listbox = tk.Listbox(conn_frame, height=6)
        self.conn_listbox.pack(fill=tk.BOTH, padx=5, pady=5)
        self.conn_listbox.bind('<<ListboxSelect>>', self.on_connection_select)
        self.conn_listbox.bind('<Double-1>', self.on_connection_double_click)
        
        # 连接按钮
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add", command=self.add_connection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Edit", command=self.edit_connection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Delete", command=self.delete_connection).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Connect", command=self.connect_redis).pack(side=tk.LEFT, padx=(0, 5))
        
        # 数据库选择
        db_frame = ttk.LabelFrame(parent, text="Database")
        db_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.db_var = tk.StringVar()
        self.db_combo = ttk.Combobox(db_frame, textvariable=self.db_var, state="readonly")
        self.db_combo['values'] = [f"DB {i}" for i in range(16)]
        self.db_combo.pack(fill=tk.X, padx=5, pady=5)
        self.db_combo.bind('<<ComboboxSelected>>', self.on_db_change)
        
        # 键搜索
        search_frame = ttk.LabelFrame(parent, text="Keys")
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        # 分隔符设置
        sep_frame = ttk.Frame(search_frame)
        sep_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(sep_frame, text="Separator:").pack(side=tk.LEFT)
        self.separator_var = tk.StringVar(value=":")
        sep_entry = ttk.Entry(sep_frame, textvariable=self.separator_var, width=5)
        sep_entry.pack(side=tk.LEFT, padx=(5, 0))
        sep_entry.bind('<KeyRelease>', self.on_separator_change)
        
        # 搜索框
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_input_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<Return>', lambda e: self.search_keys())
        
        ttk.Button(search_input_frame, text="Search", command=self.search_keys).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 键树形列表
        tree_frame = ttk.Frame(search_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.keys_tree = ttk.Treeview(tree_frame)
        self.keys_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.keys_tree.bind('<<TreeviewSelect>>', self.on_key_select)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.keys_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.keys_tree.configure(yscrollcommand=tree_scroll.set)
        
    def setup_right_panel(self, parent):
        # 状态标签
        self.status_label = ttk.Label(parent, text="Select a connection")
        self.status_label.pack(fill=tk.X, pady=(0, 10))
        
        # 标签页
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 键管理标签页
        key_frame = ttk.Frame(self.notebook)
        self.notebook.add(key_frame, text="Key Manager")
        self.setup_key_manager(key_frame)
        
        # 命令行标签页
        cli_frame = ttk.Frame(self.notebook)
        self.notebook.add(cli_frame, text="Command Line")
        self.setup_cli(cli_frame)
        
    def setup_key_manager(self, parent):
        self.key_details_frame = ttk.Frame(parent)
        self.key_details_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(self.key_details_frame, text="Select a key to view details").pack(pady=20)
        
    def setup_cli(self, parent):
        # 命令输入
        cmd_input_frame = ttk.Frame(parent)
        cmd_input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(cmd_input_frame, text="Command:").pack(side=tk.LEFT)
        self.cmd_var = tk.StringVar()
        cmd_entry = ttk.Entry(cmd_input_frame, textvariable=self.cmd_var)
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        cmd_entry.bind('<Return>', lambda e: self.execute_command())
        
        ttk.Button(cmd_input_frame, text="Execute", command=self.execute_command).pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Button(cmd_input_frame, text="Clear", command=self.clear_output).pack(side=tk.RIGHT)
        
        # 输出区域 - 占据剩余所有空间
        output_frame = ttk.Frame(parent)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Label(output_frame, text="Output:").pack(anchor=tk.W)
        
        # 文本框和滚动条
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(text_frame, state=tk.DISABLED, wrap=tk.WORD)
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
        dialog.geometry("500x700")
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
        
        # 基本信息
        ttk.Label(scrollable_frame, text="Connection Name:").pack(anchor=tk.W, padx=10, pady=(10, 0))
        fields['name'] = ttk.Entry(scrollable_frame)
        fields['name'].pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(scrollable_frame, text="Redis Host:").pack(anchor=tk.W, padx=10)
        fields['host'] = ttk.Entry(scrollable_frame)
        fields['host'].pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(scrollable_frame, text="Redis Port:").pack(anchor=tk.W, padx=10)
        fields['port'] = ttk.Entry(scrollable_frame)
        fields['port'].pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(scrollable_frame, text="Username (optional):").pack(anchor=tk.W, padx=10)
        fields['username'] = ttk.Entry(scrollable_frame)
        fields['username'].pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Label(scrollable_frame, text="Password:").pack(anchor=tk.W, padx=10)
        fields['password'] = ttk.Entry(scrollable_frame, show="*")
        fields['password'].pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 键数量限制
        ttk.Label(scrollable_frame, text="Max Keys to Display (0 = unlimited):").pack(anchor=tk.W, padx=10)
        fields['max_keys'] = ttk.Entry(scrollable_frame)
        fields['max_keys'].pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # SSH选项
        ssh_var = tk.BooleanVar()
        ssh_check = ttk.Checkbutton(scrollable_frame, text="Use SSH Tunnel", variable=ssh_var)
        ssh_check.pack(anchor=tk.W, padx=10, pady=10)
        
        # SSH字段
        ssh_frame = ttk.LabelFrame(scrollable_frame, text="SSH Configuration")
        ssh_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(ssh_frame, text="SSH Host:").pack(anchor=tk.W, padx=5, pady=(5, 0))
        fields['ssh_host'] = ttk.Entry(ssh_frame)
        fields['ssh_host'].pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(ssh_frame, text="SSH Port:").pack(anchor=tk.W, padx=5)
        fields['ssh_port'] = ttk.Entry(ssh_frame)
        fields['ssh_port'].pack(fill=tk.X, padx=5, pady=(0, 5))
        
        ttk.Label(ssh_frame, text="SSH Username:").pack(anchor=tk.W, padx=5)
        fields['ssh_user'] = ttk.Entry(ssh_frame)
        fields['ssh_user'].pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # SSH认证方式选择
        auth_frame = ttk.LabelFrame(ssh_frame, text="Authentication Method")
        auth_frame.pack(fill=tk.X, padx=5, pady=5)
        
        auth_method = tk.StringVar(value="password")
        
        # 创建认证方式选择按钮
        ttk.Radiobutton(auth_frame, text="Password", variable=auth_method, value="password", 
                       command=lambda: self.toggle_ssh_auth_fields(auth_method.get(), fields)).pack(anchor=tk.W, padx=5)
        ttk.Radiobutton(auth_frame, text="Private Key", variable=auth_method, value="key",
                       command=lambda: self.toggle_ssh_auth_fields(auth_method.get(), fields)).pack(anchor=tk.W, padx=5)
        
        # SSH密码字段框架
        password_frame = ttk.Frame(ssh_frame)
        ttk.Label(password_frame, text="SSH Password:").pack(anchor=tk.W)
        fields['ssh_password'] = ttk.Entry(password_frame, show="*")
        fields['ssh_password'].pack(fill=tk.X, pady=(0, 5))
        
        # SSH私钥字段框架
        key_frame = ttk.Frame(ssh_frame)
        
        # 私钥文件选择
        ttk.Label(key_frame, text="Private Key File:").pack(anchor=tk.W)
        key_input_frame = ttk.Frame(key_frame)
        key_input_frame.pack(fill=tk.X, pady=(0, 5))
        
        fields['ssh_key'] = ttk.Entry(key_input_frame)
        fields['ssh_key'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_key():
            filename = filedialog.askopenfilename(
                title="Select SSH Private Key"
            )
            if filename:
                fields['ssh_key'].delete(0, tk.END)
                fields['ssh_key'].insert(0, filename)
        
        ttk.Button(key_input_frame, text="Browse", command=browse_key).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 私钥内容输入
        ttk.Label(key_frame, text="Or paste private key content:").pack(anchor=tk.W, pady=(10, 0))
        key_content_frame = ttk.Frame(key_frame)
        key_content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        fields['ssh_key_content'] = tk.Text(key_content_frame, height=8, wrap=tk.WORD)
        fields['ssh_key_content'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        key_content_scroll = ttk.Scrollbar(key_content_frame, orient=tk.VERTICAL, command=fields['ssh_key_content'].yview)
        key_content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        fields['ssh_key_content'].configure(yscrollcommand=key_content_scroll.set)
        
        # 密钥密码字段（用于加密的私钥）
        ttk.Label(key_frame, text="Key Passphrase (if encrypted):").pack(anchor=tk.W)
        fields['ssh_key_passphrase'] = ttk.Entry(key_frame, show="*")
        fields['ssh_key_passphrase'].pack(fill=tk.X, pady=(0, 5))
        
        # 保存框架引用
        fields['_auth_method'] = auth_method
        fields['_password_frame'] = password_frame
        fields['_key_frame'] = key_frame
        
        # 初始化显示状态 - 默认显示密码认证
        password_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 填充现有数据
        if conn:
            fields['name'].insert(0, conn.get('name', ''))
            fields['host'].insert(0, conn.get('host', 'localhost'))
            fields['port'].insert(0, str(conn.get('port', 6379)))
            fields['username'].insert(0, conn.get('username', ''))
            fields['password'].insert(0, conn.get('password', ''))
            fields['max_keys'].insert(0, str(conn.get('max_keys', 0)))
            ssh_var.set(conn.get('use_ssh', False))
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
            fields['host'].insert(0, 'localhost')
            fields['port'].insert(0, '6379')
            fields['max_keys'].insert(0, '0')
            fields['ssh_port'].insert(0, '22')
        
        # 按钮
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_connection():
            try:
                new_conn = {
                    'name': fields['name'].get(),
                    'host': fields['host'].get(),
                    'port': int(fields['port'].get() or 6379),
                    'username': fields['username'].get(),
                    'password': fields['password'].get(),
                    'max_keys': int(fields['max_keys'].get() or 0),
                    'use_ssh': ssh_var.get(),
                    'ssh_host': fields['ssh_host'].get(),
                    'ssh_port': int(fields['ssh_port'].get() or 22),
                    'ssh_user': fields['ssh_user'].get(),
                    'ssh_password': fields['ssh_password'].get(),
                    'ssh_key': fields['ssh_key'].get(),
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
                dialog.destroy()
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {e}")
        
        ttk.Button(btn_frame, text="Save", command=save_connection).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
    def toggle_ssh_auth_fields(self, auth_method, fields):
        """切换SSH认证方式显示"""
        # 隐藏所有框架
        fields['_password_frame'].pack_forget()
        fields['_key_frame'].pack_forget()
        
        # 显示对应框架
        if auth_method == "password":
            fields['_password_frame'].pack(fill=tk.X, padx=5, pady=5)
        else:  # key
            fields['_key_frame'].pack(fill=tk.X, padx=5, pady=5)
        
    def on_connection_select(self, event):
        selection = self.conn_listbox.curselection()
        if selection:
            self.current_conn = self.connections[selection[0]]
            
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
                self.root.after(0, lambda: self.on_connect_error(str(e)))
        
        threading.Thread(target=connect_thread, daemon=True).start()
        
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
        self.status_label.config(text=f"Connected to {self.current_conn['name']}")
        self.update_db_list()
        self.search_keys()
        self.start_keepalive()
        
    def on_connect_error(self, error):
        self.status_label.config(text=f"Connection failed: {error}")
        messagebox.showerror("Connection Error", error)
        
    def update_db_list(self):
        self.db_combo['values'] = [f"DB {i}" for i in range(16)]
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
        # 清空树
        for item in self.keys_tree.get_children():
            self.keys_tree.delete(item)
            
        if not keys:
            self.status_label.config(text="No keys found")
            return
            
        # 按分隔符分组 - 支持多级结构
        separator = self.separator_var.get()
        tree_structure = {}
        
        for key in keys:
            if separator in key:
                parts = key.split(separator)
                current_level = tree_structure
                
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
                    if '_keys' not in tree_structure:
                        tree_structure['_keys'] = []
                    tree_structure['_keys'].append(key)
            else:
                if '_ungrouped' not in tree_structure:
                    tree_structure['_ungrouped'] = {'_children': {}, '_keys': []}
                tree_structure['_ungrouped']['_keys'].append(key)
        
        # 递归添加到树中 - 默认收起状态
        def add_tree_items(parent_id, structure, level=0):
            for name, data in structure.items():
                if name.startswith('_'):
                    continue
                    
                # 计算该分组的总键数
                total_keys = self.count_keys_in_structure(data)
                display_name = f"{name} ({total_keys})"
                
                # 添加分组节点，默认收起 (open=False)
                group_id = self.keys_tree.insert(parent_id, tk.END, text=display_name, open=False)
                
                # 递归添加子分组
                if '_children' in data and data['_children']:
                    add_tree_items(group_id, data['_children'], level + 1)
                
                # 添加该分组的键
                if '_keys' in data and data['_keys']:
                    for key in sorted(data['_keys']):
                        self.keys_tree.insert(group_id, tk.END, text=key, values=(key,))
        
        # 处理未分组的键
        if '_ungrouped' in tree_structure:
            ungrouped_keys = tree_structure['_ungrouped']['_keys']
            if ungrouped_keys:
                group_id = self.keys_tree.insert("", tk.END, text=f"ungrouped ({len(ungrouped_keys)})", open=False)
                for key in sorted(ungrouped_keys):
                    self.keys_tree.insert(group_id, tk.END, text=key, values=(key,))
        
        # 添加分组的键
        add_tree_items("", tree_structure)
        
        self.status_label.config(text=f"Found {len(keys)} keys" + 
                                (f" (showing {len(keys)} of ~{self.total_keys_estimate} total)" 
                                 if hasattr(self, 'total_keys_estimate') and self.total_keys_estimate and self.total_keys_estimate > len(keys) 
                                 else ""))
        
    def count_keys_in_structure(self, structure):
        """递归计算结构中的键总数"""
        count = 0
        if '_keys' in structure:
            count += len(structure['_keys'])
        if '_children' in structure:
            for child in structure['_children'].values():
                count += self.count_keys_in_structure(child)
        return count
        
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
                # 获取键信息
                key_type = self.redis_client.type(key)
                ttl = self.redis_client.ttl(key)
                
                # 获取值
                if key_type == 'string':
                    value = self.redis_client.get(key)
                elif key_type == 'list':
                    value = self.redis_client.lrange(key, 0, -1)
                elif key_type == 'set':
                    value = list(self.redis_client.smembers(key))
                elif key_type == 'hash':
                    value = self.redis_client.hgetall(key)
                elif key_type == 'zset':
                    value = self.redis_client.zrange(key, 0, -1, withscores=True)
                else:
                    value = str(self.redis_client.dump(key))
                
                self.root.after(0, lambda: self.show_key_details(key, key_type, ttl, value))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load key: {e}"))
        
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
        # 查询框架
        query_frame = ttk.Frame(parent)
        query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        if key_type == 'hash':
            ttk.Label(query_frame, text="Hash Key:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar()
            query_entry = ttk.Entry(query_frame, textvariable=self.struct_query_var)
            query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            ttk.Button(query_frame, text="Get Value", 
                      command=lambda: self.query_hash_field(key)).pack(side=tk.RIGHT)
        elif key_type in ['list', 'zset']:
            ttk.Label(query_frame, text="Index/Range:").pack(side=tk.LEFT)
            self.struct_query_var = tk.StringVar(value="0 -1")
            query_entry = ttk.Entry(query_frame, textvariable=self.struct_query_var)
            query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
            ttk.Button(query_frame, text="Get Range", 
                      command=lambda: self.query_list_range(key, key_type)).pack(side=tk.RIGHT)
        
        # 表格显示
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if key_type == 'hash':
            columns = ('Field', 'Value')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
            self.data_tree.heading('Field', text='Field')
            self.data_tree.heading('Value', text='Value')
            
            # 加载hash数据
            if isinstance(value, dict):
                for field, val in value.items():
                    self.data_tree.insert('', tk.END, values=(field, val))
        elif key_type == 'list':
            columns = ('Index', 'Value')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
            self.data_tree.heading('Index', text='Index')
            self.data_tree.heading('Value', text='Value')
            
            # 加载list数据
            if isinstance(value, list):
                for i, val in enumerate(value):
                    self.data_tree.insert('', tk.END, values=(i, val))
        elif key_type == 'set':
            columns = ('Value',)
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
            self.data_tree.heading('Value', text='Value')
            
            # 加载set数据
            if isinstance(value, (list, set)):
                for val in value:
                    self.data_tree.insert('', tk.END, values=(val,))
        elif key_type == 'zset':
            columns = ('Score', 'Member')
            self.data_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
            self.data_tree.heading('Score', text='Score')
            self.data_tree.heading('Member', text='Member')
            
            # 加载zset数据
            if isinstance(value, list):
                for i in range(0, len(value), 2):
                    if i + 1 < len(value):
                        self.data_tree.insert('', tk.END, values=(value[i+1], value[i]))
        
        self.data_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.data_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.data_tree.configure(yscrollcommand=tree_scroll.set)
        
        # 绑定双击编辑事件
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
            self.show_query_result({field: result})
        except Exception as e:
            messagebox.showerror("Query Error", f"Failed to get hash field: {e}")
            
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
            
    def edit_table_item(self, key, key_type):
        """编辑表格项"""
        selection = self.data_tree.selection()
        if not selection:
            return
            
        item = self.data_tree.item(selection[0])
        values = item['values']
        
        if key_type == 'hash':
            field, value = values[0], values[1]
            self.show_hash_edit_dialog(field, value, selection[0])
        elif key_type == 'list':
            index, value = values[0], values[1]
            new_value = simpledialog.askstring("Edit List Value", f"Index: {index}\nEnter new value:", initialvalue=value)
            if new_value is not None:
                self.data_tree.item(selection[0], values=(index, new_value))
        elif key_type == 'set':
            old_value = values[0]
            self.show_set_edit_dialog(old_value, selection[0])
        elif key_type == 'zset':
            score, member = values[0], values[1]
            new_member = simpledialog.askstring("Edit ZSet Member", f"Score: {score}\nEnter new member:", initialvalue=member)
            if new_member is not None:
                new_score = simpledialog.askstring("Edit ZSet Score", f"Member: {new_member}\nEnter new score:", initialvalue=str(score))
                if new_score is not None:
                    self.data_tree.item(selection[0], values=(new_score, new_member))
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
        
    def show_hash_edit_dialog(self, field, value, tree_item):
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
            
            # 更新树表项
            self.data_tree.item(tree_item, values=(new_field, new_value))
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
        
    def show_set_edit_dialog(self, value, tree_item):
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
        value_text.insert(tk.END, str(value))
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        value_text.configure(yscrollcommand=text_scroll.set)
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_changes():
            new_value = value_text.get(1.0, tk.END).strip()
            self.data_tree.item(tree_item, values=(new_value,))
            dialog.destroy()
        
        ttk.Button(btn_frame, text="Save", command=save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        
        value_text.focus_set()
        
    def add_table_item(self, key, key_type):
        """添加表格项"""
        if key_type == 'hash':
            # 使用同样的编辑对话框
            new_item = self.data_tree.insert('', tk.END, values=("", ""))
            self.show_hash_edit_dialog("", "", new_item)
        elif key_type == 'list':
            value = simpledialog.askstring("Add List Item", "Enter value:")
            if value is not None:
                index = len(self.data_tree.get_children())
                self.data_tree.insert('', tk.END, values=(index, value))
        elif key_type == 'set':
            value = simpledialog.askstring("Add Set Member", "Enter member:")
            if value is not None:
                self.data_tree.insert('', tk.END, values=(value,))
        elif key_type == 'zset':
            member = simpledialog.askstring("Add ZSet Member", "Enter member:")
            if member:
                score = simpledialog.askstring("Add ZSet Score", f"Member: {member}\nEnter score:")
                if score is not None:
                    self.data_tree.insert('', tk.END, values=(score, member))
                    
    def update_structured_key(self, key, key_type):
        """更新结构化键"""
        try:
            # 先删除原键
            self.redis_client.delete(key)
            
            # 根据类型重新创建
            for item in self.data_tree.get_children():
                values = self.data_tree.item(item)['values']
                
                if key_type == 'hash':
                    field, value = values[0], values[1]
                    self.redis_client.hset(key, field, value)
                elif key_type == 'list':
                    value = values[1]
                    self.redis_client.rpush(key, value)
                elif key_type == 'set':
                    value = values[0]
                    self.redis_client.sadd(key, value)
                elif key_type == 'zset':
                    score, member = float(values[0]), values[1]
                    self.redis_client.zadd(key, {member: score})
                    
            messagebox.showinfo("Success", "Key updated successfully!")
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
            if key_type == 'hash':
                if query.startswith('HGET'):
                    # HGET key field
                    parts = query.split()
                    if len(parts) >= 3:
                        field = parts[2]
                        result = self.redis_client.hget(key, field)
                        self.show_query_result(result)
                elif query.startswith('HKEYS'):
                    result = self.redis_client.hkeys(key)
                    self.show_query_result(result)
                elif query.startswith('HVALS'):
                    result = self.redis_client.hvals(key)
                    self.show_query_result(result)
                else:
                    # 直接执行命令
                    parts = query.split()
                    if len(parts) > 0:
                        cmd = parts[0].upper()
                        args = [key] + parts[1:]
                        result = self.redis_client.execute_command(cmd, *args)
                        self.show_query_result(result)
            elif key_type == 'list':
                if query.startswith('LRANGE'):
                    parts = query.split()
                    start = int(parts[1]) if len(parts) > 1 else 0
                    end = int(parts[2]) if len(parts) > 2 else -1
                    result = self.redis_client.lrange(key, start, end)
                    self.show_query_result(result)
                else:
                    parts = query.split()
                    if len(parts) > 0:
                        cmd = parts[0].upper()
                        args = [key] + parts[1:]
                        result = self.redis_client.execute_command(cmd, *args)
                        self.show_query_result(result)
            else:
                # 其他类型的通用查询
                parts = query.split()
                if len(parts) > 0:
                    cmd = parts[0].upper()
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
                
            except Exception as e:
                self.root.after(0, lambda: self.append_output(f"Error: {e}"))
        
        threading.Thread(target=execute_thread, daemon=True).start()
        
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
        for conn in self.connections:
            self.conn_listbox.insert(tk.END, conn['name'])
            
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
        if self.ssh_tunnel:
            self.ssh_tunnel.close()
        if self.ssh_client:
            self.ssh_client.close()
        self.root.destroy()

if __name__ == "__main__":
    app = RedisManager()
    app.run()