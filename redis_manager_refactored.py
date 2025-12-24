#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import threading
from pathlib import Path

from config import __version__, __app_name__, REDIS_COMMANDS, STYLES
from connection_manager import ConnectionManager
from key_manager import KeyManager

class RedisManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{__app_name__} v{__version__}")
        self.root.geometry("1600x1000")
        
        self.setup_styles()
        
        self.connections = []
        self.current_conn = None
        self.current_conn_index = -1
        self.conn_manager = ConnectionManager()
        self.key_manager = None
        
        # UI状态
        self.keys_data = {}
        self.group_data = {}
        self.expanded_groups = set()
        self.selected_line = None
        self.tree_structure = {}
        self.current_hover_line = None
        self.mouse_in_widget = False
        
        self.setup_ui()
        self.load_connections()
        
    def setup_styles(self):
        """设置应用样式"""
        style = ttk.Style()
        try:
            style.theme_use('aqua')
        except:
            style.theme_use('clam')
        
        style.configure('Title.TLabel', font=STYLES['title_font'])
        style.configure('Heading.TLabel', font=STYLES['heading_font'])
        style.configure('Connected.TLabel', foreground=STYLES['connected_color'], font=STYLES['normal_font'])
        style.configure('Connected.TFrame', relief='solid', borderwidth=1)
        
        self.root.configure(bg=STYLES['bg_color'])
        
    def setup_ui(self):
        """设置UI"""
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左右面板
        left_frame = ttk.Frame(main_frame, width=350)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_frame.pack_propagate(False)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
    
    def connect_redis(self):
        """连接Redis"""
        if not self.current_conn:
            messagebox.showwarning("Warning", "Please select a connection")
            return
            
        def connect_thread():
            try:
                self.status_label.config(text="Connecting...")
                self.root.update()
                
                self.conn_manager.connect_redis(self.current_conn)
                self.key_manager = KeyManager(self.conn_manager.redis_client)
                
                self.root.after(0, self.on_connect_success)
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self.on_connect_error(msg))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def disconnect_redis(self):
        """断开Redis连接"""
        try:
            self.conn_manager.disconnect()
            self.key_manager = None
            
            # 重置UI状态
            self.current_conn_index = -1
            self.status_label.config(text="🔌 Disconnected")
            self.connect_btn.config(text="🔌 Connect", state="normal")
            self.disconnect_btn.config(state="disabled")
            
            # 清空键列表
            self.keys_text.config(state='normal')
            self.keys_text.delete('1.0', tk.END)
            self.keys_text.config(state='disabled')
            self.keys_data = {}
            self.selected_line = None
            
            # 清空键详情
            for widget in self.key_details_frame.winfo_children():
                widget.destroy()
            
            welcome_frame = ttk.Frame(self.key_details_frame)
            welcome_frame.pack(expand=True)
            ttk.Label(welcome_frame, text="🔑", font=('SF Pro Display', 48)).pack(pady=(0, 10))
            ttk.Label(welcome_frame, text="Select a key to view details", style='Title.TLabel').pack()
            
            self.refresh_connection_list()
            
        except Exception as e:
            messagebox.showerror("Disconnect Error", f"Error while disconnecting: {e}")
    
    def search_keys(self):
        """搜索键"""
        if not self.key_manager:
            return
            
        def search_thread():
            try:
                pattern = self.search_var.get() or "*"
                max_keys = self.current_conn.get('max_keys', 0)
                
                self.root.after(0, lambda: self.status_label.config(text="Loading keys..."))
                
                keys = self.key_manager.search_keys(pattern, max_keys)
                self.current_keys = keys
                self.root.after(0, lambda: self.update_keys_tree(keys))
                
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda msg=error_msg: self.status_label.config(text=f"Failed to get keys: {msg}"))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def update_keys_tree(self, keys):
        """更新键树"""
        self.keys_text.config(state='normal')
        self.keys_text.delete('1.0', tk.END)
            
        if not keys:
            self.status_label.config(text="No keys found")
            self.keys_text.config(state='disabled')
            return
        
        separator = self.separator_var.get()
        self.tree_structure = self.key_manager.build_tree_structure(keys, separator)
        self.render_tree_structure()
        
        self.status_label.config(text=f"Found {len(keys)} keys")
    
    def load_key_details(self, key):
        """加载键详情"""
        if not self.key_manager:
            return
            
        def load_thread():
            try:
                key_type, ttl, value = self.key_manager.load_key_details(key)
                self.root.after(0, lambda: self.show_key_details(key, key_type, ttl, value))
            except Exception as e:
                error_msg = f"Failed to load key '{key}': {str(e)}"
                self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def save_connections(self):
        """保存连接配置"""
        config_path = Path.home() / ".redis_manager_config.json"
        try:
            with open(config_path, 'w') as f:
                json.dump(self.connections, f, indent=2)
        except Exception as e:
            print(f"Failed to save connections: {e}")
            
    def load_connections(self):
        """加载连接配置"""
        config_path = Path.home() / ".redis_manager_config.json"
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.connections = json.load(f)
                self.refresh_connection_list()
        except Exception as e:
            print(f"Failed to load connections: {e}")
    
    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """关闭应用"""
        self.save_connections()
        self.conn_manager.disconnect()
        self.current_conn_index = -1
        self.root.destroy()

if __name__ == "__main__":
    app = RedisManager()
    app.run()