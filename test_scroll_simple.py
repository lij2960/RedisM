#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试窗口内滚动功能 - macOS优化版本"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dialogs.base_dialog import BaseDialog

class ScrollTestDialog(BaseDialog):
    """滚动测试对话框"""
    
    def __init__(self, parent):
        super().__init__(parent, "窗口内滚动测试 - macOS优化版", "600x500")
        self._setup_test_content()
    
    def _setup_test_content(self):
        """设置测试内容"""
        # 添加说明标题
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = ttk.Label(title_frame, text="鼠标滚轮测试", 
                               font=('Arial', 16, 'bold'), foreground='#2E86AB')
        title_label.pack(anchor=tk.W)
        
        instruction_label = ttk.Label(title_frame, 
                                    text="请将鼠标放在下面任何内容上（输入框、按钮、文字等），然后滚动鼠标轮", 
                                    font=('Arial', 11), foreground='#E63946', wraplength=550)
        instruction_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 添加分隔线
        separator = ttk.Separator(self.scrollable_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=10)
        
        # 创建各种类型的组件进行测试
        for i in range(40):
            content_frame = ttk.Frame(self.scrollable_frame)
            content_frame.pack(fill=tk.X, padx=20, pady=5)
            
            if i % 4 == 0:
                # 输入框测试
                label = ttk.Label(content_frame, text=f"输入框 {i+1}:", width=15)
                label.pack(side=tk.LEFT)
                entry = ttk.Entry(content_frame, width=40)
                entry.insert(0, f"在这个输入框上滚动鼠标轮试试 - 第{i+1}行")
                entry.pack(side=tk.LEFT, padx=(10, 0), fill=tk.X, expand=True)
                
            elif i % 4 == 1:
                # 按钮测试
                label = ttk.Label(content_frame, text=f"按钮 {i+1}:", width=15)
                label.pack(side=tk.LEFT)
                btn = ttk.Button(content_frame, text=f"鼠标在这个按钮上滚动 - 第{i+1}行")
                btn.pack(side=tk.LEFT, padx=(10, 0))
                
            elif i % 4 == 2:
                # 标签测试
                label = ttk.Label(content_frame, text=f"文字标签 {i+1}:", width=15)
                label.pack(side=tk.LEFT)
                text_label = ttk.Label(content_frame, 
                                     text=f"将鼠标放在这段文字上然后滚动 - 第{i+1}行。这是一段较长的文字用来测试滚动功能是否正常工作。",
                                     wraplength=400, foreground='#457B9D')
                text_label.pack(side=tk.LEFT, padx=(10, 0), anchor=tk.W)
                
            else:
                # 复选框和单选框测试
                label = ttk.Label(content_frame, text=f"选择框 {i+1}:", width=15)
                label.pack(side=tk.LEFT)
                
                check_var = tk.BooleanVar()
                checkbox = ttk.Checkbutton(content_frame, text="复选框 - 鼠标在这里滚动", variable=check_var)
                checkbox.pack(side=tk.LEFT, padx=(10, 0))
                
                radio_var = tk.StringVar()
                radio = ttk.Radiobutton(content_frame, text="单选框 - 鼠标在这里滚动", 
                                      variable=radio_var, value=f"option_{i}")
                radio.pack(side=tk.LEFT, padx=(20, 0))
        
        # 添加底部说明
        bottom_frame = ttk.Frame(self.scrollable_frame)
        bottom_frame.pack(fill=tk.X, padx=20, pady=(20, 30))
        
        separator2 = ttk.Separator(bottom_frame, orient='horizontal')
        separator2.pack(fill=tk.X, pady=(0, 10))
        
        status_label = ttk.Label(bottom_frame, 
                               text="✅ 如果滚动正常工作，你应该能在任何组件上滚动鼠标轮来上下移动内容", 
                               font=('Arial', 11, 'bold'), foreground='#2A9D8F', wraplength=550)
        status_label.pack(anchor=tk.W)
        
        error_label = ttk.Label(bottom_frame, 
                              text="❌ 如果只能在滚动条上滚动，说明还需要进一步修复", 
                              font=('Arial', 11), foreground='#E63946', wraplength=550)
        error_label.pack(anchor=tk.W, pady=(5, 0))

def main():
    """主函数"""
    root = tk.Tk()
    root.title("RedisM 滚动测试 - macOS优化版")
    root.geometry("400x300")
    root.configure(bg='#F8F9FA')
    
    # 创建主界面
    main_frame = ttk.Frame(root)
    main_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
    
    title = ttk.Label(main_frame, text="RedisM 对话框滚动测试", 
                     font=('Arial', 18, 'bold'), foreground='#2E86AB')
    title.pack(pady=(0, 20))
    
    description = ttk.Label(main_frame, 
                          text="这个测试用来验证连接编辑对话框的鼠标滚轮功能是否正常工作。\n\n"
                               "点击下面的按钮打开测试对话框，然后尝试在对话框内容区域的任何地方滚动鼠标轮。", 
                          font=('Arial', 12), wraplength=350, justify=tk.CENTER)
    description.pack(pady=(0, 30))
    
    def open_test():
        """打开测试对话框"""
        dialog = ScrollTestDialog(root)
        dialog.show()
    
    test_btn = ttk.Button(main_frame, text="🖱️ 打开滚动测试对话框", command=open_test)
    test_btn.pack(pady=(0, 20))
    
    platform_info = ttk.Label(main_frame, 
                             text=f"当前平台: {sys.platform}\n"
                                  f"Python版本: {sys.version.split()[0]}\n"
                                  f"Tkinter版本: {tk.TkVersion}", 
                             font=('Arial', 10), foreground='#6C757D', justify=tk.CENTER)
    platform_info.pack()
    
    # 设置窗口居中
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()