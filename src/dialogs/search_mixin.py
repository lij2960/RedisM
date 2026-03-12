#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""搜索功能混入类"""

import tkinter as tk
from tkinter import ttk


class SearchMixin:
    """搜索功能混入类，为文本组件添加⌘F搜索功能"""
    
    def add_search_to_text_widget(self, text_widget, parent_frame=None):
        """为文本组件添加搜索功能"""
        # 绑定⌘F快捷键
        text_widget.bind('<Command-f>', lambda e: self._show_text_search_dialog(text_widget))
        text_widget.bind('<Command-F>', lambda e: self._show_text_search_dialog(text_widget))
        
        # 如果提供了父框架，添加搜索按钮
        if parent_frame:
            search_btn_frame = ttk.Frame(parent_frame)
            search_btn_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
            
            ttk.Button(search_btn_frame, text="🔍 Search (⌘F)", 
                      command=lambda: self._show_text_search_dialog(text_widget)).pack(side=tk.RIGHT)
    
    def _show_text_search_dialog(self, text_widget):
        """显示文本搜索对话框"""
        # 创建搜索对话框
        search_dialog = tk.Toplevel(self.dialog if hasattr(self, 'dialog') else self.parent)
        search_dialog.title("Search Text")
        search_dialog.geometry("400x120")
        search_dialog.transient(self.dialog if hasattr(self, 'dialog') else self.parent)
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
                  command=lambda: self._find_in_text_widget(text_widget, search_var.get(), status_var, True)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Find Previous", 
                  command=lambda: self._find_in_text_widget(text_widget, search_var.get(), status_var, False)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Close", 
                  command=search_dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 绑定回车键
        search_entry.bind('<Return>', lambda e: self._find_in_text_widget(text_widget, search_var.get(), status_var, True))
        search_entry.bind('<Shift-Return>', lambda e: self._find_in_text_widget(text_widget, search_var.get(), status_var, False))
        
        # 设置焦点
        search_entry.focus_set()
    
    def _find_in_text_widget(self, text_widget, search_text, status_var, forward=True):
        """在文本组件中查找"""
        if not search_text:
            status_var.set("Please enter search text")
            return
        
        # 清除之前的高亮
        text_widget.tag_remove("search_highlight", "1.0", tk.END)
        
        # 获取当前光标位置
        current_pos = text_widget.index(tk.INSERT)
        
        # 搜索文本
        if forward:
            # 向前搜索
            pos = text_widget.search(search_text, current_pos, tk.END, nocase=True)
            if not pos:
                # 从头开始搜索
                pos = text_widget.search(search_text, "1.0", current_pos, nocase=True)
                if pos:
                    status_var.set("Search wrapped to beginning")
                else:
                    status_var.set("Text not found")
                    return
        else:
            # 向后搜索 - 使用更可靠的方法
            # 先尝试从当前位置向前搜索
            pos = text_widget.search(search_text, current_pos, "1.0", backwards=True, nocase=True)
            if not pos:
                # 如果没找到，从文件末尾向当前位置搜索
                pos = text_widget.search(search_text, tk.END, current_pos, backwards=True, nocase=True)
                if pos:
                    status_var.set("Search wrapped to end")
                else:
                    status_var.set("Text not found")
                    return
        
        # 高亮找到的文本
        end_pos = f"{pos}+{len(search_text)}c"
        text_widget.tag_add("search_highlight", pos, end_pos)
        text_widget.tag_config("search_highlight", background="yellow", foreground="black")
        
        # 选中找到的文本
        text_widget.tag_remove(tk.SEL, "1.0", tk.END)
        text_widget.tag_add(tk.SEL, pos, end_pos)
        
        # 根据搜索方向设置光标位置
        if forward:
            # 向前搜索：光标移到匹配文本后面，便于下次继续向前搜索
            text_widget.mark_set(tk.INSERT, end_pos)
        else:
            # 向后搜索：光标移到匹配文本前面，便于下次继续向后搜索
            text_widget.mark_set(tk.INSERT, pos)
        
        # 滚动到可见位置
        text_widget.see(pos)
        
        # 更新状态
        status_var.set(f"Found at {pos}")
        
        # 确保文本框有焦点
        text_widget.focus_set()