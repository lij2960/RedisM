#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""连接配置对话框"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

from .base_dialog import BaseDialog
from ..config import *
from ..redis.connection import RedisConnection


class ConnectionDialog(BaseDialog):
    """连接配置对话框"""
    
    def __init__(self, parent, connection=None):
        self.connection = connection
        self.fields = {}
        
        title = "Edit Connection" if connection else "Add Connection"
        super().__init__(parent, title, "650x700")
        
        self._setup_ui()
        
        if connection:
            self._populate_fields()
    
    def _setup_ui(self):
        """设置UI"""
        # 标题
        self._create_title()
        
        # Redis连接信息
        self._create_redis_section()
        
        # SSH隧道配置
        self._create_ssh_section()
        
        # 按钮
        self._create_buttons()
    
    def _create_title(self):
        """创建标题"""
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_text = "Add New Connection" if not self.connection else "Edit Connection"
        title_label = ttk.Label(title_frame, text=title_text, 
                               font=(FONT_FAMILY, FONT_SIZE_TITLE, 'bold'))
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, text="Configure your Redis connection settings", 
                                  font=(FONT_FAMILY, FONT_SIZE_NORMAL), foreground='#666666')
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))
    
    def _create_redis_section(self):
        """创建Redis连接配置区域"""
        redis_frame = ttk.LabelFrame(self.scrollable_frame, text="🔗 Redis Connection", padding=10)
        redis_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        redis_inner = ttk.Frame(redis_frame)
        redis_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # 连接名称
        ttk.Label(redis_inner, text="Connection Name:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.fields['name'] = ttk.Entry(redis_inner, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['name'].grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        # Redis主机和端口
        ttk.Label(redis_inner, text="Redis Host:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=1, column=0, sticky='w', pady=(0, 5))
        host_frame = ttk.Frame(redis_inner)
        host_frame.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        self.fields['host'] = ttk.Entry(host_frame, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['host'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(host_frame, text="Port:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack(side=tk.LEFT, padx=(10, 5))
        self.fields['port'] = ttk.Entry(host_frame, width=8, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['port'].pack(side=tk.RIGHT)
        
        # 认证信息
        ttk.Label(redis_inner, text="Username:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=2, column=0, sticky='w', pady=(0, 5))
        self.fields['username'] = ttk.Entry(redis_inner, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['username'].grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        ttk.Label(redis_inner, text="Password:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=3, column=0, sticky='w', pady=(0, 5))
        self.fields['password'] = ttk.Entry(redis_inner, show="*", font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['password'].grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        # 配置选项
        ttk.Label(redis_inner, text="Max Keys (0=unlimited):", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=4, column=0, sticky='w', pady=(0, 5))
        config_frame = ttk.Frame(redis_inner)
        config_frame.grid(row=4, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        self.fields['max_keys'] = ttk.Entry(config_frame, width=12, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['max_keys'].pack(side=tk.LEFT)
        
        ttk.Label(config_frame, text="Databases (1-128):", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack(side=tk.LEFT, padx=(15, 5))
        self.fields['db_count'] = ttk.Entry(config_frame, width=8, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['db_count'].pack(side=tk.LEFT)
        
        # 配置Grid权重
        redis_inner.columnconfigure(1, weight=1)
    
    def _create_ssh_section(self):
        """创建SSH隧道配置区域"""
        ssh_frame = ttk.LabelFrame(self.scrollable_frame, text="🔐 SSH Tunnel (Optional)", padding=10)
        ssh_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        ssh_inner = ttk.Frame(ssh_frame)
        ssh_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # SSH启用选项
        self.ssh_var = tk.BooleanVar()
        ssh_check = ttk.Checkbutton(ssh_inner, text="Enable SSH Tunnel", variable=self.ssh_var,
                                   command=self._toggle_ssh_section)
        ssh_check.pack(anchor=tk.W, pady=(0, 10))
        
        # SSH内容框架
        self.ssh_content_frame = ttk.Frame(ssh_inner)
        
        # SSH服务器信息
        self._create_ssh_server_section()
        
        # SSH认证方式
        self._create_ssh_auth_section()
    
    def _create_ssh_server_section(self):
        """创建SSH服务器配置"""
        ssh_server_frame = ttk.Frame(self.ssh_content_frame)
        ssh_server_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(ssh_server_frame, text="SSH Host:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        ssh_host_frame = ttk.Frame(ssh_server_frame)
        ssh_host_frame.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        self.fields['ssh_host'] = ttk.Entry(ssh_host_frame, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['ssh_host'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(ssh_host_frame, text="Port:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).pack(side=tk.LEFT, padx=(10, 5))
        self.fields['ssh_port'] = ttk.Entry(ssh_host_frame, width=8, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['ssh_port'].pack(side=tk.RIGHT)
        
        ttk.Label(ssh_server_frame, text="SSH Username:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=1, column=0, sticky='w', pady=(0, 5))
        self.fields['ssh_user'] = ttk.Entry(ssh_server_frame, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['ssh_user'].grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        ssh_server_frame.columnconfigure(1, weight=1)
    
    def _create_ssh_auth_section(self):
        """创建SSH认证配置"""
        auth_frame = ttk.LabelFrame(self.ssh_content_frame, text="Authentication Method", padding=10)
        auth_frame.pack(fill=tk.X, pady=(0, 10))
        
        auth_inner = ttk.Frame(auth_frame)
        auth_inner.pack(fill=tk.X, padx=10, pady=10)
        
        self.auth_method = tk.StringVar(value="password")
        
        # 认证方式选择按钮
        auth_buttons_frame = ttk.Frame(auth_inner)
        auth_buttons_frame.pack(fill=tk.X, pady=(0, 15))
        
        password_radio = ttk.Radiobutton(auth_buttons_frame, text="🔑 Password Authentication", 
                                       variable=self.auth_method, value="password",
                                       command=self._toggle_ssh_auth_fields)
        password_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        key_radio = ttk.Radiobutton(auth_buttons_frame, text="🔐 Private Key Authentication", 
                                  variable=self.auth_method, value="key",
                                  command=self._toggle_ssh_auth_fields)
        key_radio.pack(side=tk.LEFT)
        
        # 认证内容框架
        self.auth_content_frame = ttk.Frame(auth_inner)
        self.auth_content_frame.pack(fill=tk.X)
        
        # 密码认证框架
        self.password_frame = ttk.Frame(self.auth_content_frame)
        password_inner = ttk.Frame(self.password_frame)
        password_inner.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(password_inner, text="SSH Password:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        self.fields['ssh_password'] = ttk.Entry(password_inner, show="*", font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['ssh_password'].grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        password_inner.columnconfigure(1, weight=1)
        
        # 私钥认证框架
        self.key_frame = ttk.Frame(self.auth_content_frame)
        key_inner = ttk.Frame(self.key_frame)
        key_inner.pack(fill=tk.X, padx=10, pady=10)
        
        # 私钥文件选择
        ttk.Label(key_inner, text="Private Key File:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=0, column=0, sticky='w', pady=(0, 5))
        key_file_frame = ttk.Frame(key_inner)
        key_file_frame.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
        
        self.fields['ssh_key'] = ttk.Entry(key_file_frame, font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['ssh_key'].pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(key_file_frame, text="Browse...", command=self._browse_key)
        browse_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 私钥内容输入
        ttk.Label(key_inner, text="Or paste private key content:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=1, column=0, sticky='nw', pady=(15, 5))
        key_content_frame = ttk.Frame(key_inner)
        key_content_frame.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=(15, 5))
        
        # 固定Text组件的大小，不让它影响整体布局
        self.fields['ssh_key_content'] = tk.Text(key_content_frame, height=3, width=40, wrap=tk.WORD,
                                               font=(FONT_FAMILY_CODE, FONT_SIZE_SMALL), 
                                               bg='white', relief='solid', borderwidth=1)
        self.fields['ssh_key_content'].pack(side=tk.LEFT)
        
        key_content_scroll = ttk.Scrollbar(key_content_frame, orient=tk.VERTICAL, 
                                         command=self.fields['ssh_key_content'].yview)
        key_content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.fields['ssh_key_content'].configure(yscrollcommand=key_content_scroll.set)
        
        # 密钥密码
        ttk.Label(key_inner, text="Key Passphrase:", 
                 font=(FONT_FAMILY, FONT_SIZE_NORMAL)).grid(row=2, column=0, sticky='w', pady=(15, 5))
        self.fields['ssh_key_passphrase'] = ttk.Entry(key_inner, show="*", font=(FONT_FAMILY, FONT_SIZE_NORMAL))
        self.fields['ssh_key_passphrase'].grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=(15, 5))
        
        key_inner.columnconfigure(1, weight=1)
        
        # 初始显示密码认证
        self.password_frame.pack(fill=tk.X)
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=(10, 20))
        
        # 分隔线
        separator = ttk.Separator(btn_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 15))
        
        # 按钮容器
        button_container = ttk.Frame(btn_frame)
        button_container.pack(fill=tk.X)
        
        # 左侧按钮
        self.test_btn = ttk.Button(button_container, text="Test Connection", command=self._test_connection)
        self.test_btn.pack(side=tk.LEFT)
        
        # 右侧按钮
        cancel_btn = ttk.Button(button_container, text="Cancel", command=lambda: self.close())
        cancel_btn.pack(side=tk.RIGHT)
        
        save_btn = ttk.Button(button_container, text="Save Connection", command=self._save_connection)
        save_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    def _populate_fields(self):
        """填充字段数据"""
        if not self.connection:
            # 新建连接 - 设置默认值
            self.fields['host'].insert(0, 'localhost')
            self.fields['port'].insert(0, str(DEFAULT_REDIS_PORT))
            self.fields['max_keys'].insert(0, str(DEFAULT_MAX_KEYS))
            self.fields['db_count'].insert(0, str(DEFAULT_DB_COUNT))
            self.fields['ssh_port'].insert(0, str(DEFAULT_SSH_PORT))
            return
        
        # 编辑现有连接
        conn = self.connection
        self.fields['name'].insert(0, conn.get('name', ''))
        self.fields['host'].insert(0, conn.get('host', 'localhost'))
        self.fields['port'].insert(0, str(conn.get('port', DEFAULT_REDIS_PORT)))
        self.fields['username'].insert(0, conn.get('username', ''))
        self.fields['password'].insert(0, conn.get('password', ''))
        self.fields['max_keys'].insert(0, str(conn.get('max_keys', DEFAULT_MAX_KEYS)))
        self.fields['db_count'].insert(0, str(conn.get('db_count', DEFAULT_DB_COUNT)))
        
        use_ssh = conn.get('use_ssh', False)
        self.ssh_var.set(use_ssh)
        if use_ssh:
            self.ssh_content_frame.pack(fill=tk.X)
        
        self.fields['ssh_host'].insert(0, conn.get('ssh_host', ''))
        self.fields['ssh_port'].insert(0, str(conn.get('ssh_port', DEFAULT_SSH_PORT)))
        self.fields['ssh_user'].insert(0, conn.get('ssh_user', ''))
        self.fields['ssh_password'].insert(0, conn.get('ssh_password', ''))
        self.fields['ssh_key'].insert(0, conn.get('ssh_key', ''))
        self.fields['ssh_key_content'].insert(tk.END, conn.get('ssh_key_content', ''))
        self.fields['ssh_key_passphrase'].insert(0, conn.get('ssh_key_passphrase', ''))
        
        # 设置认证方式
        auth_method_val = "key" if conn.get('ssh_key') or conn.get('ssh_key_content') else "password"
        self.auth_method.set(auth_method_val)
        self._toggle_ssh_auth_fields()
    
    def _toggle_ssh_section(self):
        """切换SSH配置区域的显示/隐藏"""
        if self.ssh_var.get():
            self.ssh_content_frame.pack(fill=tk.X)
        else:
            self.ssh_content_frame.pack_forget()
    
    def _toggle_ssh_auth_fields(self):
        """切换SSH认证方式显示"""
        # 隐藏所有认证框架
        self.password_frame.pack_forget()
        self.key_frame.pack_forget()
        
        # 显示对应的认证框架，使用相同的pack配置
        if self.auth_method.get() == "password":
            self.password_frame.pack(fill=tk.X)
        else:
            self.key_frame.pack(fill=tk.X)
    
    def _browse_key(self):
        """浏览私钥文件"""
        filename = filedialog.askopenfilename(title="Select SSH Private Key")
        if filename:
            self.fields['ssh_key'].delete(0, tk.END)
            self.fields['ssh_key'].insert(0, filename)
    
    def _test_connection(self):
        """测试连接"""
        try:
            # 验证必填字段
            if not self.fields['name'].get().strip():
                messagebox.showerror("Test Failed", "Connection name is required")
                return
            
            if not self.fields['host'].get().strip():
                messagebox.showerror("Test Failed", "Redis host is required")
                return
            
            # SSH验证（如果启用）
            if self.ssh_var.get():
                if not self.fields['ssh_host'].get().strip():
                    messagebox.showerror("Test Failed", "SSH host is required when SSH tunnel is enabled")
                    return
                if not self.fields['ssh_user'].get().strip():
                    messagebox.showerror("Test Failed", "SSH username is required when SSH tunnel is enabled")
                    return
                
                auth_method_val = self.auth_method.get()
                if auth_method_val == "password":
                    if not self.fields['ssh_password'].get():
                        messagebox.showerror("Test Failed", "SSH password is required for password authentication")
                        return
                elif auth_method_val == "key":
                    ssh_key_file = self.fields['ssh_key'].get().strip()
                    ssh_key_content = self.fields['ssh_key_content'].get(1.0, tk.END).strip()
                    
                    if not ssh_key_file and not ssh_key_content:
                        messagebox.showerror("Test Failed", "Private key file or content is required for key authentication")
                        return
                    
                    # 验证私钥内容格式（如果提供了内容）
                    if ssh_key_content:
                        if not ("BEGIN" in ssh_key_content and "PRIVATE KEY" in ssh_key_content and "END" in ssh_key_content):
                            messagebox.showerror("Test Failed", "Invalid private key format. Please ensure the key includes BEGIN and END markers.")
                            return
            
            # 构建测试连接配置
            test_config = self._build_connection_config()
            
            # 显示测试进度
            self.test_btn.config(text="Testing...", state="disabled")
            self.dialog.update()
            
            def test_thread():
                try:
                    redis_conn = RedisConnection()
                    result = redis_conn.test_connection(test_config)
                    self.dialog.after(0, lambda: self._on_test_complete(result, None))
                except Exception as e:
                    self.dialog.after(0, lambda: self._on_test_complete(None, str(e)))
            
            threading.Thread(target=test_thread, daemon=True).start()
            
        except Exception as e:
            self.test_btn.config(text="Test Connection", state="normal")
            messagebox.showerror("Test Failed", f"Connection test failed: {e}")
    
    def _on_test_complete(self, result, error):
        """测试完成回调"""
        self.test_btn.config(text="Test Connection", state="normal")
        if error:
            messagebox.showerror("Test Failed", f"Connection test failed:\n{error}")
        else:
            messagebox.showinfo("Test Successful", 
                              f"✅ Connection test successful!\n\n"
                              f"Redis Version: {result.get('version', 'Unknown')}\n"
                              f"Connected to: {self.fields['host'].get()}:{self.fields['port'].get()}\n"
                              f"SSH Tunnel: {'Yes' if self.ssh_var.get() else 'No'}")
    
    def _save_connection(self):
        """保存连接"""
        try:
            # 验证必填字段
            if not self.fields['name'].get().strip():
                messagebox.showerror("Validation Error", "Connection name is required")
                return
            
            if not self.fields['host'].get().strip():
                messagebox.showerror("Validation Error", "Redis host is required")
                return
            
            # 验证数据库数量
            db_count = int(self.fields['db_count'].get() or DEFAULT_DB_COUNT)
            if db_count < 1 or db_count > 128:
                messagebox.showerror("Validation Error", "Database count must be between 1 and 128")
                return
            
            # SSH验证
            if self.ssh_var.get():
                if not self.fields['ssh_host'].get().strip():
                    messagebox.showerror("Validation Error", "SSH host is required when SSH tunnel is enabled")
                    return
                if not self.fields['ssh_user'].get().strip():
                    messagebox.showerror("Validation Error", "SSH username is required when SSH tunnel is enabled")
                    return
                
                auth_method_val = self.auth_method.get()
                if auth_method_val == "password" and not self.fields['ssh_password'].get():
                    messagebox.showerror("Validation Error", "SSH password is required for password authentication")
                    return
                elif auth_method_val == "key" and not self.fields['ssh_key'].get() and not self.fields['ssh_key_content'].get(1.0, tk.END).strip():
                    messagebox.showerror("Validation Error", "Private key file or content is required for key authentication")
                    return
            
            # 构建连接配置
            new_conn = self._build_connection_config()
            
            # 显示成功消息
            action = "updated" if self.connection else "created"
            messagebox.showinfo("Success", f"Connection '{new_conn['name']}' {action} successfully!")
            
            self.close(new_conn)
            
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save connection: {e}")
    
    def _build_connection_config(self):
        """构建连接配置"""
        return {
            'name': self.fields['name'].get().strip(),
            'host': self.fields['host'].get().strip(),
            'port': int(self.fields['port'].get() or DEFAULT_REDIS_PORT),
            'username': self.fields['username'].get().strip(),
            'password': self.fields['password'].get(),
            'max_keys': int(self.fields['max_keys'].get() or DEFAULT_MAX_KEYS),
            'db_count': int(self.fields['db_count'].get() or DEFAULT_DB_COUNT),
            'use_ssh': self.ssh_var.get(),
            'ssh_host': self.fields['ssh_host'].get().strip(),
            'ssh_port': int(self.fields['ssh_port'].get() or DEFAULT_SSH_PORT),
            'ssh_user': self.fields['ssh_user'].get().strip(),
            'ssh_password': self.fields['ssh_password'].get(),
            'ssh_key': self.fields['ssh_key'].get().strip(),
            'ssh_key_content': self.fields['ssh_key_content'].get(1.0, tk.END).strip(),
            'ssh_key_passphrase': self.fields['ssh_key_passphrase'].get(),
        }