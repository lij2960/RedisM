#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""基础对话框类"""

import tkinter as tk
from tkinter import ttk


class BaseDialog:
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
        
        # 设置最小尺寸
        self.dialog.minsize(width, height)
        
        # 允许调整大小
        self.dialog.resizable(True, True)
    
    def _create_scrollable_frame(self):
        """创建可滚动框架 - 使用简单可靠的方法"""
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
        
        # 最关键的部分：直接绑定鼠标滚轮到Canvas
        self._setup_mousewheel()
    
    def _setup_mousewheel(self):
        """设置鼠标滚轮 - macOS优化版本，确保在窗口内任何地方都能滚动"""
        
        def _on_mousewheel(event):
            """处理鼠标滚轮事件"""
            try:
                # macOS和Windows的滚轮事件处理
                if hasattr(event, 'delta') and event.delta:
                    # macOS/Windows: delta值通常是120的倍数
                    delta = int(-1 * (event.delta / 120))
                else:
                    # Linux: 使用Button-4和Button-5
                    if event.num == 4:
                        delta = -1
                    elif event.num == 5:
                        delta = 1
                    else:
                        return "break"
                
                # 执行滚动
                self.canvas.yview_scroll(delta, "units")
                return "break"  # 阻止事件继续传播
                
            except Exception:
                return "break"
        
        # macOS特殊处理：使用bind_all来捕获全局鼠标滚轮事件
        def _global_mousewheel(event):
            """全局鼠标滚轮处理器 - 只在对话框区域内生效"""
            try:
                # 检查鼠标是否在对话框窗口内
                x, y = self.dialog.winfo_pointerxy()
                dialog_x = self.dialog.winfo_rootx()
                dialog_y = self.dialog.winfo_rooty()
                dialog_width = self.dialog.winfo_width()
                dialog_height = self.dialog.winfo_height()
                
                # 判断鼠标是否在对话框范围内
                if (dialog_x <= x <= dialog_x + dialog_width and 
                    dialog_y <= y <= dialog_y + dialog_height):
                    
                    # 在对话框内，执行滚动
                    return _on_mousewheel(event)
                    
            except Exception:
                pass
            
            return None  # 让其他组件处理事件
        
        # 绑定策略：多层绑定确保兼容性
        
        # 1. 绑定到对话框本身（最高优先级）
        self.dialog.bind("<MouseWheel>", _on_mousewheel)
        self.dialog.bind("<Button-4>", _on_mousewheel)  
        self.dialog.bind("<Button-5>", _on_mousewheel)
        
        # 2. 绑定到Canvas（直接滚动区域）
        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.canvas.bind("<Button-4>", _on_mousewheel)
        self.canvas.bind("<Button-5>", _on_mousewheel)
        
        # 3. 绑定到内容框架
        self.scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        self.scrollable_frame.bind("<Button-4>", _on_mousewheel)
        self.scrollable_frame.bind("<Button-5>", _on_mousewheel)
        
        # 4. 全局绑定（macOS关键）- 使用root窗口的bind_all
        try:
            root = self.dialog.winfo_toplevel()
            while root.master:
                root = root.master
            root.bind_all("<MouseWheel>", _global_mousewheel, add=True)
            root.bind_all("<Button-4>", _global_mousewheel, add=True)
            root.bind_all("<Button-5>", _global_mousewheel, add=True)
        except Exception:
            pass
        
        # 5. 递归绑定到所有子组件（延迟执行）
        def bind_to_children():
            """递归绑定所有子组件"""
            def recursive_bind(widget):
                try:
                    # 绑定到当前组件
                    widget.bind("<MouseWheel>", _on_mousewheel, add=True)
                    widget.bind("<Button-4>", _on_mousewheel, add=True)
                    widget.bind("<Button-5>", _on_mousewheel, add=True)
                    
                    # 递归处理子组件
                    for child in widget.winfo_children():
                        recursive_bind(child)
                except Exception:
                    pass
            
            # 绑定scrollable_frame及其所有子组件
            recursive_bind(self.scrollable_frame)
        
        # 延迟绑定，确保所有UI组件都已创建
        self.dialog.after(100, bind_to_children)
        
        # 6. 焦点管理
        self.dialog.focus_force()
        
        # 7. 动态重新绑定（当有新组件添加时）
        def on_focus_in(event):
            """当对话框获得焦点时重新绑定"""
            self.dialog.after(50, bind_to_children)
        
        self.dialog.bind("<FocusIn>", on_focus_in, add=True)
        
        # 8. 鼠标进入事件重新绑定
        def on_enter(event):
            """鼠标进入对话框时重新绑定"""
            self.dialog.after(50, bind_to_children)
        
        self.dialog.bind("<Enter>", on_enter, add=True)
    
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