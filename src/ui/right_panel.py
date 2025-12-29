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
        
        # 标签页
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 键管理标签页 - 添加滚动功能
        key_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(key_tab_frame, text="🔑 Key Manager")
        
        # 创建滚动框架
        self.key_canvas = tk.Canvas(key_tab_frame, highlightthickness=0)
        self.key_scrollbar = ttk.Scrollbar(key_tab_frame, orient="vertical", command=self.key_canvas.yview)
        self.key_scrollable_frame = ttk.Frame(self.key_canvas, padding="15")
        
        # 配置滚动
        self.key_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.key_canvas.configure(scrollregion=self.key_canvas.bbox("all"))
        )
        
        # 绑定Canvas大小变化事件，确保内容框架宽度与Canvas一致
        def _configure_canvas(event):
            canvas_width = event.width
            self.key_canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.key_canvas.bind('<Configure>', _configure_canvas)
        
        self.canvas_window = self.key_canvas.create_window((0, 0), window=self.key_scrollable_frame, anchor="nw")
        self.key_canvas.configure(yscrollcommand=self.key_scrollbar.set)
        
        # 布局滚动组件 - 使用grid布局确保完全填充
        key_tab_frame.grid_rowconfigure(0, weight=1)
        key_tab_frame.grid_columnconfigure(0, weight=1)
        
        self.key_canvas.grid(row=0, column=0, sticky="nsew")
        self.key_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # 绑定鼠标滚轮事件
        self._bind_key_manager_mousewheel()
        
        # 创建KeyManager实例，使用可滚动框架
        self.key_manager = KeyManager(self.key_scrollable_frame, self.main_window)
        
        # 命令行标签页
        cli_frame = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(cli_frame, text="💻 Command Line")
        self.cli_interface = CLIInterface(cli_frame, self.main_window)
    
    def _bind_key_manager_mousewheel(self):
        """绑定Key Manager的鼠标滚轮事件"""
        def _on_mousewheel(event):
            self.key_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.key_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.key_canvas.unbind_all("<MouseWheel>")
        
        # 绑定鼠标进入和离开事件
        self.key_canvas.bind('<Enter>', _bind_to_mousewheel)
        self.key_canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def update_status(self, text):
        """更新状态文本"""
        self.status_label.config(text=text)
    
    def load_key_details(self, key):
        """加载键详情"""
        self.key_manager.load_key_details(key)
    
    def clear_key_details(self):
        """清空键详情"""
        # 重置滚动位置
        self.key_canvas.yview_moveto(0)
        self.key_manager.clear_details()