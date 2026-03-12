#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试搜索功能修复的脚本
"""

import tkinter as tk
from tkinter import ttk

class SearchTestApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Search Function Test")
        self.root.geometry("600x400")
        
        # 创建文本框
        self.text_widget = tk.Text(self.root, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 插入测试文本
        test_text = """This is a test document.
We will test the search functionality here.
The word 'test' appears multiple times in this test.
Let's test both forward and backward search.
Another test line with the word test.
Final test to make sure everything works."""
        
        self.text_widget.insert(tk.END, test_text)
        
        # 创建搜索控制面板
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar(value="test")
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=(5, 10), fill=tk.X, expand=True)
        
        ttk.Button(control_frame, text="Find Next", 
                  command=lambda: self.find_text(True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Find Previous", 
                  command=lambda: self.find_text(False)).pack(side=tk.LEFT, padx=2)
        
        # 状态标签
        self.status_var = tk.StringVar()
        status_label = ttk.Label(self.root, textvariable=self.status_var, foreground='blue')
        status_label.pack(pady=5)
        
        # 绑定快捷键
        search_entry.bind('<Return>', lambda e: self.find_text(True))
        search_entry.bind('<Shift-Return>', lambda e: self.find_text(False))
        
        # 设置初始光标位置
        self.text_widget.mark_set(tk.INSERT, "1.0")
        self.text_widget.focus_set()
    
    def find_text(self, forward=True):
        """搜索文本"""
        search_text = self.search_var.get()
        if not search_text:
            self.status_var.set("Please enter search text")
            return
        
        # 清除之前的高亮
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        
        # 获取当前光标位置
        current_pos = self.text_widget.index(tk.INSERT)
        
        # 搜索文本
        pos = None
        if forward:
            # 向前搜索
            pos = self.text_widget.search(search_text, current_pos, tk.END, nocase=True)
            if not pos:
                # 从头开始搜索
                pos = self.text_widget.search(search_text, "1.0", current_pos, nocase=True)
                if pos:
                    self.status_var.set("Search wrapped to beginning")
                else:
                    self.status_var.set("Text not found")
                    return
        else:
            # 向后搜索 - 修复版本
            search_start = current_pos
            
            # 如果当前位置有选中的文本，从选中文本的开始位置搜索
            try:
                sel_start = self.text_widget.index(tk.SEL_FIRST)
                sel_end = self.text_widget.index(tk.SEL_LAST)
                # 如果光标在选中文本的末尾，从选中文本的开始位置搜索
                if current_pos == sel_end:
                    search_start = sel_start
            except tk.TclError:
                # 没有选中文本，使用当前光标位置
                pass
            
            # 向后搜索
            pos = self.text_widget.search(search_text, search_start, "1.0", backwards=True, nocase=True)
            if not pos:
                # 从末尾开始搜索
                pos = self.text_widget.search(search_text, tk.END, search_start, backwards=True, nocase=True)
                if pos:
                    self.status_var.set("Search wrapped to end")
                else:
                    self.status_var.set("Text not found")
                    return
        
        # 高亮找到的文本
        end_pos = f"{pos}+{len(search_text)}c"
        self.text_widget.tag_add("search_highlight", pos, end_pos)
        self.text_widget.tag_config("search_highlight", background="yellow", foreground="black")
        
        # 选中找到的文本
        self.text_widget.tag_remove(tk.SEL, "1.0", tk.END)
        self.text_widget.tag_add(tk.SEL, pos, end_pos)
        
        # 根据搜索方向设置光标位置
        if forward:
            # 向前搜索：光标移到匹配文本后面
            self.text_widget.mark_set(tk.INSERT, end_pos)
        else:
            # 向后搜索：光标移到匹配文本前面
            self.text_widget.mark_set(tk.INSERT, pos)
        
        # 滚动到可见位置
        self.text_widget.see(pos)
        
        # 更新状态
        self.status_var.set(f"Found '{search_text}' at {pos}")
        
        # 确保文本框有焦点
        self.text_widget.focus_set()
    
    def run(self):
        print("Search Test Application")
        print("======================")
        print("Instructions:")
        print("1. The word 'test' is pre-filled in the search box")
        print("2. Click 'Find Next' to search forward")
        print("3. Click 'Find Previous' to search backward")
        print("4. Use Enter for Find Next, Shift+Enter for Find Previous")
        print("5. Watch the status message and highlighted text")
        print("")
        print("Expected behavior:")
        print("- Find Next should move forward through matches")
        print("- Find Previous should move backward through matches")
        print("- Both should wrap around when reaching the end/beginning")
        print("")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = SearchTestApp()
    app.run()