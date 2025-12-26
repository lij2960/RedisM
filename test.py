#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""RedisM 功能测试"""

import tkinter as tk
import sys
import os

def main():
    """主函数"""
    root = tk.Tk()
    root.title("RedisM 功能测试")
    root.geometry("500x400")
    root.configure(bg='#F8F9FA')
    
    # 创建主界面
    main_frame = tk.Frame(root, bg='#F8F9FA')
    main_frame.pack(expand=True, fill=tk.BOTH, padx=30, pady=30)
    
    title = tk.Label(main_frame, text="RedisM 功能测试", 
                    font=('Arial', 18, 'bold'), fg='#2E86AB', bg='#F8F9FA')
    title.pack(pady=(0, 20))
    
    description = tk.Label(main_frame, 
                          text="测试 RedisM 的各项功能：\n\n"
                               "✅ Redis 连接管理\n"
                               "✅ SSH 隧道支持\n"
                               "✅ 数据类型操作\n"
                               "✅ 过滤和搜索\n"
                               "✅ 对话框滚动\n"
                               "✅ 键盘快捷键\n\n"
                               "点击下面的按钮启动 RedisM 进行测试。", 
                          font=('Arial', 12), bg='#F8F9FA', justify=tk.LEFT)
    description.pack(pady=(0, 30))
    
    def run_main_app():
        """运行主应用"""
        import subprocess
        subprocess.Popen([sys.executable, "main.py"])
    
    test_btn = tk.Button(main_frame, text="🚀 启动 RedisM", 
                        command=run_main_app,
                        font=('Arial', 14), bg='#2A9D8F', fg='white',
                        relief='flat', padx=20, pady=10)
    test_btn.pack(pady=(0, 20))
    
    instruction = tk.Label(main_frame, 
                          text="测试要点：\n\n"
                               "• 创建和编辑连接\n"
                               "• 测试 SSH 隧道连接\n"
                               "• 浏览和编辑 Redis 数据\n"
                               "• 使用过滤功能\n"
                               "• 测试对话框滚动（键盘 ↑↓ 或右侧按钮）", 
                          font=('Arial', 10), fg='#6C757D', bg='#F8F9FA', justify=tk.LEFT)
    instruction.pack()
    
    # 设置窗口居中
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()