#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""右侧面板UI"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from ..config import *
from .key_manager import KeyManager
from .cli_interface import CLIInterface


class RightPanel:
    """右侧面板类"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 状态标签
        status_frame = ttk.Frame(self.parent)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_label = ttk.Label(status_frame, text="🔌 Select a connection to get started", 
                                     style='Title.TLabel')
        self.status_label.pack(anchor=tk.W)
        
        # 标签页 - 禁用滚轮切换
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 彻底禁用标签页滚轮切换
        def block_notebook_scroll(event):
            return "break"
        
        # 使用bind_all全局拦截滚轮事件
        self.parent.bind_all("<MouseWheel>", block_notebook_scroll)
        self.parent.bind_all("<Button-4>", block_notebook_scroll)
        self.parent.bind_all("<Button-5>", block_notebook_scroll)
        
        # 键管理标签页 - 移除滚动功能
        key_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(key_tab_frame, text="🔑 Key Manager")
        
        # 直接创建KeyManager实例，不使用滚动框架
        self.key_manager = KeyManager(key_tab_frame, self.main_window)
        
        # 命令行标签页
        cli_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(cli_frame, text="💻 Command Line")
        self.cli_interface = CLIInterface(cli_frame, self.main_window)
    
    def _bind_key_manager_mousewheel(self):
        """禁用Key Manager的鼠标滚轮事件"""
        # 完全移除滚轮绑定，不再提供滚动功能
        pass
    
    def update_status(self, text):
        """更新状态文本"""
        self.status_label.config(text=text)
    
    def load_key_details(self, key):
        """加载键详情"""
        self.key_manager.load_key_details(key)
    
    def clear_key_details(self):
        """清空键详情"""
        self.key_manager.clear_details()