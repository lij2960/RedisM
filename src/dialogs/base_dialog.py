#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""基础对话框类"""

import tkinter as tk
from tkinter import ttk
from .search_mixin import SearchMixin


class BaseDialog(SearchMixin):
    """基础对话框类"""
    
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
        
        # 创建滚动框架
        self._create_scrollable_frame()
        
        # 确保对话框可以接收键盘和鼠标事件
        self.dialog.focus_force()
        
        # 显示对话框
        self.dialog.deiconify()
    
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
        
        # 设置最小尺寸 - 确保有足够空间显示内容
        min_width = max(400, width // 2)
        min_height = max(300, height // 2)
        self.dialog.minsize(min_width, min_height)
        
        # 允许调整大小
        self.dialog.resizable(True, True)
        
        # 绑定窗口大小变化事件，用于自动调整内容
        self.dialog.bind('<Configure>', self._on_dialog_resize)
    
    def _create_scrollable_frame(self):
        """创建可滚动框架 - macOS优化版本"""
        # 创建主容器
        container = ttk.Frame(self.dialog)
        container.pack(fill=tk.BOTH, expand=True)
        
        # 创建Canvas和滚动条
        self.canvas = tk.Canvas(container, bg='#F5F5F5', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # 配置滚动
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # 绑定Canvas大小变化
        def _on_canvas_configure(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.canvas.bind('<Configure>', _on_canvas_configure)
        
        # 布局
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 设置滚轮 - 使用更激进的方法
        self._setup_mousewheel_aggressive()
    
    def _setup_mousewheel_aggressive(self):
        """最后的解决方案 - 使用键盘绑定和鼠标位置检测"""
        
        def scroll_function(delta):
            """执行滚动"""
            try:
                self.canvas.yview_scroll(int(delta), "units")
            except Exception:
                pass
        
    def _setup_mousewheel_aggressive(self):
        """实用的滚动解决方案 - 针对macOS tkinter鼠标滚轮兼容性问题"""
        
        def scroll_function(delta):
            """执行滚动"""
            try:
                self.canvas.yview_scroll(int(delta), "units")
            except Exception:
                pass
        
        # 键盘滚动 - 主要滚动方式
        def on_key_up(event):
            scroll_function(-3)
            return "break"
        
        def on_key_down(event):
            scroll_function(3)
            return "break"
        
        def on_page_up(event):
            scroll_function(-10)
            return "break"
        
        def on_page_down(event):
            scroll_function(10)
            return "break"
        
        def on_home(event):
            try:
                self.canvas.yview_moveto(0)
            except:
                pass
            return "break"
        
        def on_end(event):
            try:
                self.canvas.yview_moveto(1)
            except:
                pass
            return "break"
        
        # 绑定键盘快捷键 - 确保对话框有焦点时能响应
        self.dialog.bind("<Up>", on_key_up)
        self.dialog.bind("<Down>", on_key_down)
        self.dialog.bind("<Prior>", on_page_up)  # Page Up
        self.dialog.bind("<Next>", on_page_down)   # Page Down
        self.dialog.bind("<Home>", on_home)
        self.dialog.bind("<End>", on_end)
        
        # 数字键盘支持
        self.dialog.bind("<KP_Up>", on_key_up)
        self.dialog.bind("<KP_Down>", on_key_down)
        self.dialog.bind("<KP_Prior>", on_page_up)
        self.dialog.bind("<KP_Next>", on_page_down)
        self.dialog.bind("<KP_Home>", on_home)
        self.dialog.bind("<KP_End>", on_end)
        
        # 添加滚动按钮
        self._add_scroll_buttons()
        
        # 确保对话框能接收键盘事件
        self.dialog.focus_force()
        
        # 添加用户说明
        self._add_scroll_instructions()
        
        # 注意：由于macOS tkinter的限制，鼠标滚轮功能暂时无法实现
        # 但提供了多种替代方案确保良好的用户体验
    
    def _add_scroll_buttons(self):
        """添加滚动按钮 - 小尺寸，放在最右侧"""
        try:
            # 创建滚动按钮框架，放在最右侧
            scroll_frame = ttk.Frame(self.dialog)
            scroll_frame.place(relx=1.0, rely=0.1, anchor='ne', x=-5, y=10)
            
            # 向上按钮 - 缩小尺寸
            up_btn = ttk.Button(scroll_frame, text="▲", width=2,
                               command=lambda: self.canvas.yview_scroll(-3, "units"))
            up_btn.pack(pady=1)
            
            # 向下按钮 - 缩小尺寸
            down_btn = ttk.Button(scroll_frame, text="▼", width=2,
                                 command=lambda: self.canvas.yview_scroll(3, "units"))
            down_btn.pack(pady=1)
            
            # 添加简单的工具提示
            self._add_tooltip(up_btn, "向上滚动 (↑)")
            self._add_tooltip(down_btn, "向下滚动 (↓)")
            
        except Exception:
            pass
    
    def _add_tooltip(self, widget, text):
        """添加工具提示"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _add_scroll_instructions(self):
        """添加滚动说明 - 去掉红色警告文字"""
        try:
            # 在对话框底部添加说明
            info_frame = ttk.Frame(self.dialog)
            info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
            
            info_label = ttk.Label(info_frame, 
                                  text="💡 滚动方式: 键盘 ↑↓ 箭头键 | Page Up/Down | 右侧 ▲▼ 按钮 | 拖拽滚动条", 
                                  font=('Arial', 9), foreground='#666666')
            info_label.pack()
            
        except Exception:
            pass
    
    def _bind_mousewheel(self):
        """绑定鼠标滚轮事件 - Text组件自带滚轮支持"""
        pass  # Text组件天然支持滚轮，不需要手动绑定
    
    def _unbind_mousewheel(self):
        """解绑鼠标滚轮事件"""
        try:
            # 解绑对话框事件
            self.dialog.unbind("<MouseWheel>")
            self.dialog.unbind("<Button-4>")
            self.dialog.unbind("<Button-5>")
            
            # 解绑Canvas事件
            if hasattr(self, 'canvas'):
                self.canvas.unbind("<MouseWheel>")
                self.canvas.unbind("<Button-4>")
                self.canvas.unbind("<Button-5>")
            
            # 解绑全局事件（如果可能的话）
            try:
                root = self.dialog.winfo_toplevel()
                while root.master:
                    root = root.master
                # 注意：tkinter的unbind_all可能不完全可靠，但尝试清理
                root.unbind_all("<MouseWheel>")
                root.unbind_all("<Button-4>")
                root.unbind_all("<Button-5>")
            except Exception:
                pass
                
        except Exception:
            pass
    
    def show(self):
        """显示对话框并返回结果"""
        # 等待对话框关闭
        self.dialog.wait_window()
        return self.result
    
    def close(self, result=None):
        """关闭对话框"""
        self.result = result
        self._unbind_mousewheel()
        self.dialog.destroy()
    
    def _on_dialog_resize(self, event):
        """对话框大小变化事件处理"""
        # 只处理对话框本身的resize事件，忽略子组件的
        if event.widget == self.dialog:
            # 更新Canvas滚动区域
            if hasattr(self, 'canvas'):
                self.dialog.after_idle(self._update_scroll_region)
            
            # 通知子类处理resize事件
            if hasattr(self, '_handle_dialog_resize'):
                self._handle_dialog_resize(event)
    
    def _update_scroll_region(self):
        """更新滚动区域"""
        try:
            if hasattr(self, 'canvas') and hasattr(self, 'scrollable_frame'):
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception:
            pass
    
    def create_simple_dialog_layout(self):
        """创建简单的对话框布局 - 不使用Canvas滚动，专门用于编辑对话框"""
        # 创建主容器，直接使用Frame而不是Canvas
        self.main_container = ttk.Frame(self.dialog)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 配置grid权重，让内容可以扩展
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # 创建内容框架
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # 配置内容框架的grid权重
        self.content_frame.grid_rowconfigure(1, weight=1)  # 让第二行（文本区域）可扩展
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        return self.content_frame
    
    def create_auto_resize_text(self, parent, initial_text="", min_height=6, max_height=15, **kwargs):
        """创建自动调整大小的文本组件 - 恢复原有功能"""
        # 创建文本框架
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建文本组件 - 使用最小高度作为初始值
        text_widget = tk.Text(text_frame, wrap=tk.WORD, height=min_height, **kwargs)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 插入初始文本
        if initial_text:
            text_widget.insert(tk.END, initial_text)
        
        # 创建滚动条
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=text_scroll.set)
        
        # 添加搜索功能
        self.add_search_to_text_widget(text_widget, parent)
        
        return text_widget, text_frame
    
    def create_auto_resize_text_simple(self, parent, initial_text="", **kwargs):
        """创建真正自适应的文本组件 - 使用grid布局"""
        # 创建文本框架
        text_frame = ttk.Frame(parent)
        
        # 配置grid权重
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # 创建文本组件 - 不设置固定高度，让grid管理
        text_widget = tk.Text(text_frame, wrap=tk.WORD, **kwargs)
        text_widget.grid(row=0, column=0, sticky="nsew")
        
        # 插入初始文本
        if initial_text:
            text_widget.insert(tk.END, initial_text)
        
        # 创建滚动条
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_scroll.grid(row=0, column=1, sticky="ns")
        text_widget.configure(yscrollcommand=text_scroll.set)
        
        # 添加搜索功能
        self.add_search_to_text_widget(text_widget, parent)
        
        return text_widget, text_frame