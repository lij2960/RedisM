#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试连接对话框滚动功能"""

import tkinter as tk
import sys
import os

def main():
    """主函数"""
    root = tk.Tk()
    root.title("连接对话框滚动测试")
    root.geometry("400x300")
    root.configure(bg='#F8F9FA')
    
    # 创建主界面
    main_frame = tk.Frame(root, bg='#F8F9FA')
    main_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
    
    title = tk.Label(main_frame, text="连接对话框滚动测试", 
                    font=('Arial', 18, 'bold'), fg='#2E86AB', bg='#F8F9FA')
    title.pack(pady=(0, 20))
    
    description = tk.Label(main_frame, 
                          text="请运行以下命令来测试连接对话框的滚动功能：\n\npython src/main.py\n\n然后点击'Add Connection'按钮", 
                          font=('Arial', 12), bg='#F8F9FA', justify=tk.CENTER)
    description.pack(pady=(0, 30))
    
    def run_main_app():
        """运行主应用"""
        import subprocess
        subprocess.Popen([sys.executable, "src/main.py"])
    
    test_btn = tk.Button(main_frame, text="🚀 启动 RedisM 主程序", 
                        command=run_main_app,
                        font=('Arial', 14), bg='#2A9D8F', fg='white',
                        relief='flat', padx=20, pady=10)
    test_btn.pack(pady=(0, 20))
    
    instruction = tk.Label(main_frame, 
                          text="在主程序中点击'Add Connection'，\n然后测试对话框中的鼠标滚轮功能。", 
                          font=('Arial', 10), fg='#6C757D', bg='#F8F9FA', justify=tk.CENTER)
    instruction.pack()
    
    # 设置窗口居中
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()