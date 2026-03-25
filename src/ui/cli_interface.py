#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CLI界面"""

import tkinter as tk
from tkinter import ttk
import threading

from ..config import *


class CLIInterface:
    """CLI界面类"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # Redis命令列表
        self.redis_commands = [
            'GET', 'SET', 'DEL', 'EXISTS', 'KEYS', 'TYPE', 'TTL', 'EXPIRE',
            'HGET', 'HSET', 'HDEL', 'HKEYS', 'HVALS', 'HGETALL', 'HEXISTS',
            'LLEN', 'LPUSH', 'RPUSH', 'LPOP', 'RPOP', 'LRANGE', 'LINDEX',
            'SADD', 'SREM', 'SMEMBERS', 'SCARD', 'SISMEMBER',
            'ZADD', 'ZREM', 'ZRANGE', 'ZCARD', 'ZSCORE',
            'PING', 'INFO', 'SELECT', 'FLUSHDB', 'FLUSHALL', 'DBSIZE',
            'INCR', 'DECR', 'INCRBY', 'DECRBY', 'APPEND', 'STRLEN'
        ]
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 命令输入
        self._setup_command_input()
        
        # 输出区域
        self._setup_output_area()
    
    def _setup_command_input(self):
        """设置命令输入区域"""
        cmd_input_frame = ttk.LabelFrame(self.parent, text="⌨️ Command Input", padding="10")
        cmd_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        input_frame = ttk.Frame(cmd_input_frame)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="redis>", 
                 font=self.main_window.style_manager.get_font(weight='bold')).pack(side=tk.LEFT, padx=(0, 5))
        
        self.cmd_var = tk.StringVar()
        self.cmd_entry = ttk.Entry(input_frame, textvariable=self.cmd_var, 
                                  font=self.main_window.style_manager.get_code_font())
        self.cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.cmd_entry.bind('<Return>', lambda e: self._execute_command())
        self.cmd_entry.bind('<KeyRelease>', self._on_cmd_key_release)
        self.cmd_entry.bind('<Tab>', self._on_cmd_tab)
        
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="▶️ Execute", command=self._execute_command).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ Clear", command=self._clear_output).pack(side=tk.LEFT)
        
        # 命令提示框架
        self.suggestion_frame = ttk.Frame(cmd_input_frame)
        self.suggestion_listbox = tk.Listbox(self.suggestion_frame, height=5, 
                                           font=self.main_window.style_manager.get_code_font())
        self.suggestion_listbox.bind('<Double-Button-1>', self._on_suggestion_select)
        self.suggestion_listbox.bind('<Return>', self._on_suggestion_select)
    
    def _setup_output_area(self):
        """设置输出区域"""
        output_frame = ttk.LabelFrame(self.parent, text="📊 Output", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文本框和滚动条
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(text_frame, state=tk.DISABLED, wrap=tk.WORD,
                                  font=self.main_window.style_manager.get_code_font(), 
                                  bg='#1E1E1E', fg='#FFFFFF',
                                  insertbackground='#FFFFFF', selectbackground=SELECTED_COLOR)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        output_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        output_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.configure(yscrollcommand=output_scroll.set)
    
    def _execute_command(self):
        """执行Redis命令"""
        redis_client = self.main_window.get_redis_client()
        if not redis_client:
            self._append_output("Error: Not connected to Redis")
            return
        
        command = self.cmd_var.get().strip()
        if not command:
            return
        
        def execute_thread():
            try:
                # 先尝试快速检查连接
                redis_client = self.main_window.get_redis_client()
                if not redis_client:
                    self.main_window.root.after(0, lambda: self._append_output("Error: No Redis connection available"))
                    return
                
                # 快速ping测试
                redis_client.ping()
                # 连接正常，执行命令
                self._continue_execute_command(command)
                
            except Exception as e:
                # 连接有问题，异步重连
                def on_reconnect_success(result):
                    if result:
                        # 重连成功，继续执行命令
                        self._continue_execute_command(command)
                    else:
                        # 重连失败
                        self.main_window.root.after(0, lambda: self._append_output("Error: Connection lost and reconnection failed"))
                
                def on_reconnect_error(error):
                    self.main_window.root.after(0, lambda: self._append_output(f"Error: Reconnection failed: {error}"))
                
                self.main_window.root.after(0, lambda: self._append_output("Connection lost, attempting to reconnect..."))
                self.main_window.redis_conn.check_and_reconnect_async(on_reconnect_success, on_reconnect_error)
        
        threading.Thread(target=execute_thread, daemon=True).start()
    
    def _continue_execute_command(self, command):
        """继续执行命令（在连接确认后）"""
        def execute_thread():
            try:
                redis_client = self.main_window.get_redis_client()
                
                # 解析命令
                parts = command.split()
                if not parts:
                    return
                
                # 执行命令
                result = redis_client.execute_command(*parts)
                
                # 格式化结果 - 在后台线程中完成，避免大数据集阻塞UI
                if isinstance(result, (list, tuple)):
                    if len(result) == 0:
                        formatted_result = "(empty list or set)"
                    else:
                        lines = [f"{i+1}) {item}" for i, item in enumerate(result)]
                        formatted_result = "\n".join(lines)
                elif isinstance(result, set):
                    # 修复：SMEMBERS 返回 set 类型
                    if len(result) == 0:
                        formatted_result = "(empty set)"
                    else:
                        lines = [f"{i+1}) {item}" for i, item in enumerate(sorted(result))]
                        formatted_result = "\n".join(lines)
                elif isinstance(result, dict):
                    formatted_result = "\n".join([f"{k}: {v}" for k, v in result.items()])
                elif result is None:
                    formatted_result = "(nil)"
                else:
                    formatted_result = str(result)
                
                # 显示结果（在主线程中更新UI）
                output = f"redis> {command}\n{formatted_result}\n"
                self.main_window.root.after(0, lambda: self._append_output_bulk(output))
                
            except Exception as e:
                error_msg = f"redis> {command}\nError: {str(e)}\n"
                self.main_window.root.after(0, lambda: self._append_output_bulk(error_msg))
        
        threading.Thread(target=execute_thread, daemon=True).start()
        
        # 清空输入（在主线程中执行）
        self.main_window.root.after(0, lambda: self.cmd_var.set(""))
        self.main_window.root.after(0, self._hide_suggestions)
    
    def _on_cmd_key_release(self, event):
        """命令输入键释放事件"""
        if event.keysym in ['Up', 'Down', 'Left', 'Right', 'Return', 'Tab']:
            return
        
        current_text = self.cmd_var.get().upper()
        if len(current_text) < 2:
            self._hide_suggestions()
            return
        
        # 查找匹配的命令
        matches = [cmd for cmd in self.redis_commands if cmd.startswith(current_text)]
        
        if matches:
            self._show_suggestions(matches)
        else:
            self._hide_suggestions()
    
    def _on_cmd_tab(self, event):
        """Tab键自动完成"""
        current_text = self.cmd_var.get().upper()
        matches = [cmd for cmd in self.redis_commands if cmd.startswith(current_text)]
        
        if len(matches) == 1:
            self.cmd_var.set(matches[0] + " ")
            self.cmd_entry.icursor(tk.END)
        elif len(matches) > 1:
            # 找到最长公共前缀
            common_prefix = matches[0]
            for match in matches[1:]:
                while not match.startswith(common_prefix):
                    common_prefix = common_prefix[:-1]
            
            if len(common_prefix) > len(current_text):
                self.cmd_var.set(common_prefix)
                self.cmd_entry.icursor(tk.END)
        
        return "break"  # 阻止默认Tab行为
    
    def _show_suggestions(self, suggestions):
        """显示命令建议"""
        self.suggestion_frame.pack(fill=tk.X, pady=(5, 0))
        self.suggestion_listbox.pack(fill=tk.X)
        
        self.suggestion_listbox.delete(0, tk.END)
        for suggestion in suggestions[:5]:  # 最多显示5个建议
            self.suggestion_listbox.insert(tk.END, suggestion)
    
    def _hide_suggestions(self):
        """隐藏命令建议"""
        self.suggestion_frame.pack_forget()
    
    def _on_suggestion_select(self, event):
        """选择建议"""
        selection = self.suggestion_listbox.curselection()
        if selection:
            selected_cmd = self.suggestion_listbox.get(selection[0])
            self.cmd_var.set(selected_cmd + " ")
            self.cmd_entry.focus_set()
            self.cmd_entry.icursor(tk.END)
            self._hide_suggestions()
    
    def _append_output(self, text):
        """追加输出文本"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def _append_output_bulk(self, text):
        """一次性追加大量输出文本，避免多次 UI 更新导致卡顿"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def _clear_output(self):
        """清空输出"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)