#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""UI样式配置"""

import tkinter as tk
from tkinter import ttk
from ..config import *


class StyleManager:
    """样式管理器"""
    
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self._setup_styles()
    
    def _setup_styles(self):
        """设置应用样式"""
        # 设置主题
        try:
            self.style.theme_use('aqua')  # macOS原生主题
        except:
            self.style.theme_use('clam')  # 备用主题
        
        # 自定义样式
        self.style.configure('Title.TLabel', 
                           font=(FONT_FAMILY, FONT_SIZE_TITLE, 'bold'))
        self.style.configure('Heading.TLabel', 
                           font=(FONT_FAMILY, FONT_SIZE_HEADING, 'bold'))
        self.style.configure('Connected.TLabel', 
                           foreground=SELECTED_COLOR, 
                           font=(FONT_FAMILY, FONT_SIZE_NORMAL, 'bold'))
        
        # 连接列表样式
        self.style.configure('Connected.TFrame', relief='solid', borderwidth=1)
        
        # 设置窗口背景色
        self.root.configure(bg=BACKGROUND_COLOR)
    
    def configure_treeview_style(self, key_type):
        """配置Treeview样式"""
        style_name = f"Structured.{key_type}.Treeview"
        
        # 配置行高（增加间距）
        self.style.configure(style_name, rowheight=TREE_ROW_HEIGHT)
        
        # 配置选中和悬停颜色
        self.style.map(style_name,
                      background=[('selected', SELECTED_COLOR),
                                ('active', HOVER_COLOR)],
                      foreground=[('selected', 'white'),
                                ('active', 'black')])
        
        return style_name
    
    def get_font(self, size=FONT_SIZE_NORMAL, weight='normal', family=FONT_FAMILY):
        """获取字体配置"""
        return (family, size, weight)
    
    def get_code_font(self, size=FONT_SIZE_SMALL):
        """获取代码字体配置"""
        return (FONT_FAMILY_CODE, size)