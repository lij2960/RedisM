#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试连接编辑对话框的美化效果
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_connection_dialog():
    """测试连接编辑对话框"""
    root = tk.Tk()
    root.title("RedisM Connection Dialog Test")
    root.geometry("400x300")
    
    # 模拟RedisManager类的部分功能
    class MockRedisManager:
        def __init__(self):
            self.connections = []
            self.root = root
        
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
        
        def show_connection_dialog(self, conn=None):
            """显示连接编辑对话框"""
            dialog = tk.Toplevel(self.root)
            dialog.title("Add Connection" if conn is None else "Edit Connection")
            dialog.geometry("600x800")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # 设置对话框样式
            style = ttk.Style()
            # 移除自定义样式以避免错误
            # style.configure('Dialog.TLabelFrame', padding=10)
            # style.configure('Dialog.TLabel', font=('SF Pro Display', 10))
            # style.configure('Dialog.TEntry', fieldbackground='white')
            
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
            key_inner.pack(fill=tk.X, padx=10, pady=10)  # 改为fill=tk.X，与密码认证保持一致
            
            # 私钥文件选择
            ttk.Label(key_inner, text="Private Key File:", font=('SF Pro Display', 10)).grid(row=0, column=0, sticky='w', pady=(0, 5))
            key_file_frame = ttk.Frame(key_inner)
            key_file_frame.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=(0, 5))
            
            fields['ssh_key'] = ttk.Entry(key_file_frame, font=('SF Pro Display', 10))
            fields['ssh_key'].pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            def browse_key():
                from tkinter import filedialog
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
            
            # 保存框架引用
            fields['_auth_method'] = auth_method
            fields['_password_frame'] = password_frame
            fields['_key_frame'] = key_frame
            fields['_auth_content_frame'] = auth_content_frame
            fields['_ssh_content_frame'] = ssh_content_frame
            
            # 初始化其他字段
            fields['ssh_host'] = fields.get('ssh_host', ttk.Entry(ssh_server_frame))
            fields['ssh_port'] = fields.get('ssh_port', ttk.Entry(ssh_server_frame))
            fields['ssh_user'] = fields.get('ssh_user', ttk.Entry(ssh_server_frame))
            fields['max_keys'] = fields.get('max_keys', ttk.Entry(config_frame))
            fields['db_count'] = fields.get('db_count', ttk.Entry(config_frame))
            fields['host'] = fields.get('host', ttk.Entry(host_frame))
            fields['port'] = fields.get('port', ttk.Entry(host_frame))
            fields['username'] = fields.get('username', ttk.Entry(redis_inner))
            fields['password'] = fields.get('password', ttk.Entry(redis_inner))
            
            # 初始化显示状态 - 两个框架都使用相同的pack参数
            password_frame.pack(fill=tk.X, expand=False)  # 确保不会expand
            ssh_content_frame.pack_forget()  # 默认隐藏SSH配置
            
            # 为新建连接设置默认值（测试文件中总是新建）
            if not conn:
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
            
            # 按钮布局
            button_container = ttk.Frame(btn_frame)
            button_container.pack(fill=tk.X)
            
            # 左侧按钮
            test_btn = ttk.Button(button_container, text="Test Connection")
            test_btn.pack(side=tk.LEFT)
            
            # 右侧按钮
            cancel_btn = ttk.Button(button_container, text="Cancel", command=dialog.destroy)
            cancel_btn.pack(side=tk.RIGHT)
            
            save_btn = ttk.Button(button_container, text="Save Connection")
            save_btn.pack(side=tk.RIGHT, padx=(0, 10))
            
            # 设置焦点
            fields['name'].focus_set()
    
    # 创建模拟管理器并显示对话框
    manager = MockRedisManager()
    
    # 创建测试按钮
    test_frame = ttk.Frame(root)
    test_frame.pack(expand=True)
    
    ttk.Label(test_frame, text="RedisM Connection Dialog Test", 
             font=('SF Pro Display', 14, 'bold')).pack(pady=(0, 20))
    
    ttk.Button(test_frame, text="Open Add Connection Dialog", 
              command=lambda: manager.show_connection_dialog()).pack(pady=5)
    
    # 创建一个测试连接数据
    test_conn = {
        'name': 'Test Connection', 
        'host': 'localhost',
        'port': 6379,
        'username': 'testuser',
        'password': 'testpass',
        'max_keys': 1000,
        'db_count': 16,
        'use_ssh': True,
        'ssh_host': 'ssh.example.com',
        'ssh_port': 22,
        'ssh_user': 'sshuser',
        'ssh_password': 'sshpass',
        'ssh_key': '/path/to/key.pem',
        'ssh_key_content': '-----BEGIN RSA PRIVATE KEY-----\ntest content\n-----END RSA PRIVATE KEY-----',
        'ssh_key_passphrase': 'keypass'
    }
    
    ttk.Button(test_frame, text="Open Edit Connection Dialog", 
              command=lambda: manager.show_connection_dialog(test_conn)).pack(pady=5)
    
    ttk.Button(test_frame, text="Exit", command=root.quit).pack(pady=(20, 0))
    
    root.mainloop()

if __name__ == "__main__":
    test_connection_dialog()