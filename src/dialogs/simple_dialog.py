#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""简化的对话框基类 - 专门用于编辑对话框，支持真正的自适应布局"""

import tkinter as tk
from tkinter import ttk, messagebox
from .search_mixin import SearchMixin


class SimpleDialog(SearchMixin):
    """简化的对话框基类 - 不使用Canvas滚动，直接使用grid布局"""
    
    def __init__(self, parent, title="Dialog", size="600x400"):
        self.parent = parent
        self.result = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 先隐藏对话框，避免闪烁
        self.dialog.withdraw()
        
        # 设置尺寸和位置
        self._setup_geometry(size)
        
        # 创建简单布局
        self._create_simple_layout()
        
        # 确保对话框可以接收键盘和鼠标事件
        self.dialog.focus_force()
        
        # 显示对话框
        self.dialog.deiconify()
    
    def _format_php(self):
        """格式化PHP序列化值（通用方法）"""
        if not hasattr(self, 'value_text') and not hasattr(self, 'member_text'):
            return
        
        text_widget = getattr(self, 'value_text', None) or getattr(self, 'member_text', None)
        if not text_widget:
            return
        
        try:
            from ..utils.helpers import format_php_serialize, apply_json_syntax_highlighting
            current_value = text_widget.get(1.0, tk.END).strip()
            formatted = format_php_serialize(current_value)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, formatted)
            # 格式化后的是JSON，应用JSON语法高亮
            apply_json_syntax_highlighting(text_widget)
        except ValueError as e:
            messagebox.showerror("PHP Serialize Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format PHP serialize: {e}")
    
    def _minify_php(self):
        """压缩PHP序列化值（通用方法）"""
        if not hasattr(self, 'value_text') and not hasattr(self, 'member_text'):
            return
        
        text_widget = getattr(self, 'value_text', None) or getattr(self, 'member_text', None)
        if not text_widget:
            return
        
        try:
            from ..utils.helpers import minify_php_serialize
            current_value = text_widget.get(1.0, tk.END).strip()
            minified = minify_php_serialize(current_value)
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, minified)
        except ValueError as e:
            messagebox.showerror("PHP Serialize Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify PHP serialize: {e}")
    
    def _setup_geometry(self, size):
        """设置对话框几何属性"""
        # 解析尺寸
        if 'x' in size:
            width, height = map(int, size.split('x'))
        else:
            width, height = 600, 400
        
        # 获取父窗口位置和尺寸
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # 计算居中位置
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        # 设置几何属性
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # 设置最小尺寸
        min_width = max(400, width // 2)
        min_height = max(300, height // 2)
        self.dialog.minsize(min_width, min_height)
        
        # 允许调整大小
        self.dialog.resizable(True, True)
    
    def _create_simple_layout(self):
        """创建简单的布局结构"""
        # 创建主容器
        self.main_container = ttk.Frame(self.dialog)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置grid权重 - 支持灵活的section配置
        # 默认配置3个section，但可以根据需要使用任意数量
        for i in range(10):  # 支持最多10个section
            if i == 1:  # 通常第1个section是可扩展的
                self.main_container.grid_rowconfigure(i, weight=1)
            else:
                self.main_container.grid_rowconfigure(i, weight=0)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # 创建内容区域
        self.content_frame = self.main_container
    
    def create_fixed_section(self, row):
        """创建固定高度的区域"""
        section = ttk.Frame(self.content_frame)
        section.grid(row=row, column=0, sticky="ew", pady=5)
        section.grid_columnconfigure(0, weight=1)
        return section
    
    def create_expandable_section(self, row):
        """创建可扩展的区域"""
        section = ttk.Frame(self.content_frame)
        section.grid(row=row, column=0, sticky="nsew", pady=5)
        section.grid_rowconfigure(0, weight=1)
        section.grid_columnconfigure(0, weight=1)
        return section
    
    def create_auto_text(self, parent, initial_text="", **kwargs):
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
        
        # 添加搜索功能 - 添加搜索按钮到父容器
        search_frame = ttk.Frame(parent)
        search_frame.grid(row=1, column=0, sticky="ew")
        
        ttk.Button(search_frame, text="🔍 Search (⌘F)", 
                  command=lambda: self._show_text_search_dialog(text_widget)).pack(side=tk.RIGHT)
        
        # 绑定⌘F快捷键
        text_widget.bind('<Command-f>', lambda e: self._show_text_search_dialog(text_widget))
        text_widget.bind('<Command-F>', lambda e: self._show_text_search_dialog(text_widget))
        
        return text_widget, text_frame
    
    def show(self):
        """显示对话框并返回结果"""
        # 等待对话框关闭
        self.dialog.wait_window()
        return self.result
    
    def close(self, result=None):
        """关闭对话框"""
        self.result = result
        self.dialog.destroy()