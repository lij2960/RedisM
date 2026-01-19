#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""主窗口UI"""

import tkinter as tk
from tkinter import ttk, messagebox

from ..config import *
from .styles import StyleManager
from .left_panel import LeftPanel
from .right_panel import RightPanel
from ..redis.connection import RedisConnection
from ..utils.helpers import load_connections, save_connections


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        # 初始化组件
        self.style_manager = StyleManager(self.root)
        self.redis_conn = RedisConnection()
        
        # 连接管理
        self.connections = []
        self.current_conn = None
        self.current_conn_index = -1
        
        # 初始化UI
        self._setup_ui()
        self._load_connections()
        
    def _setup_ui(self):
        """设置UI"""
        # 创建菜单栏
        self._create_menu()
        
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
        
        # 创建面板
        self.left_panel = LeftPanel(left_frame, self)
        self.right_panel = RightPanel(right_frame, self)
        
    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _show_about(self):
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
    
    def _load_connections(self):
        """加载连接配置"""
        self.connections = load_connections()
        self.left_panel.refresh_connection_list()
    
    def save_connections(self):
        """保存连接配置"""
        save_connections(self.connections)
    
    def get_redis_client(self):
        """获取Redis客户端，确保在正确的数据库中"""
        if not self.redis_conn.redis_client:
            return None
        
        # 确保客户端在正确的数据库中
        current_db = self.redis_conn.get_current_database()
        try:
            # 每次都执行SELECT命令确保在正确的数据库中
            self.redis_conn.redis_client.execute_command('SELECT', current_db)
        except Exception as e:
            print(f"Warning: Failed to select database {current_db}: {e}")
        
        return self.redis_conn.redis_client
    
    def get_redis_connection(self):
        """获取Redis连接管理器"""
        return self.redis_conn
    
    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """关闭应用"""
        self.save_connections()
        self.redis_conn.disconnect()
        self.root.destroy()