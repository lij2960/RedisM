#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""左侧面板UI"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from ..config import *
from ..redis.operations import RedisOperations
from ..utils.helpers import count_keys_in_structure
from ..dialogs.connection_dialog import ConnectionDialog


class LeftPanel:
    """左侧面板类"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        
        # 键管理相关
        self.keys_data = {}
        self.group_data = {}
        self.selected_line = None
        self.expanded_groups = set()
        self.tree_structure = {}
        self.current_keys = []
        self.total_keys_estimate = None
        
        # 鼠标悬停相关
        self.current_hover_line = None
        self.mouse_in_widget = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 连接管理
        self._setup_connection_section()
        
        # 数据库选择
        self._setup_database_section()
        
        # 键搜索
        self._setup_keys_section()
    
    def _setup_connection_section(self):
        """设置连接管理区域"""
        conn_frame = ttk.LabelFrame(self.parent, text="🔗 Connections", padding="10")
        conn_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 连接列表框架
        list_frame = ttk.Frame(conn_frame)
        list_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 连接列表
        self.conn_listbox = tk.Listbox(list_frame, height=6, 
                                      font=self.main_window.style_manager.get_font(),
                                      selectbackground=SELECTED_COLOR, 
                                      selectforeground='white',
                                      relief='flat', borderwidth=0, 
                                      highlightthickness=1,
                                      highlightcolor=SELECTED_COLOR)
        self.conn_listbox.pack(fill=tk.X)
        self.conn_listbox.bind('<<ListboxSelect>>', self._on_connection_select)
        self.conn_listbox.bind('<Double-1>', self._on_connection_double_click)
        
        # 连接按钮
        self._setup_connection_buttons(conn_frame)
    
    def _setup_connection_buttons(self, parent):
        """设置连接按钮"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X)
        
        # 第一行按钮
        btn_row1 = ttk.Frame(btn_frame)
        btn_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(btn_row1, text="➕ Add", command=self._add_connection, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row1, text="✏️ Edit", command=self._edit_connection, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_row1, text="🗑️ Delete", command=self._delete_connection, width=8).pack(side=tk.LEFT)
        
        # 第二行按钮
        btn_row2 = ttk.Frame(btn_frame)
        btn_row2.pack(fill=tk.X)
        
        self.connect_btn = ttk.Button(btn_row2, text="🔌 Connect", command=self._connect_redis)
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(btn_row2, text="🔌 Disconnect", 
                                        command=self._disconnect_redis, state="disabled")
        self.disconnect_btn.pack(side=tk.RIGHT)
    
    def _setup_database_section(self):
        """设置数据库选择区域"""
        db_frame = ttk.LabelFrame(self.parent, text="🗄️ Database", padding="10")
        db_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.db_var = tk.StringVar()
        self.db_combo = ttk.Combobox(db_frame, textvariable=self.db_var, state="readonly",
                                    font=self.main_window.style_manager.get_font())
        self.db_combo['values'] = [f"DB {i}" for i in range(16)]
        self.db_combo.pack(fill=tk.X)
        self.db_combo.bind('<<ComboboxSelected>>', self._on_db_change)
    
    def _setup_keys_section(self):
        """设置键搜索区域"""
        search_frame = ttk.LabelFrame(self.parent, text="🔍 Keys", padding="10")
        search_frame.pack(fill=tk.BOTH, expand=True)
        
        # 分隔符设置和添加键按钮
        sep_frame = ttk.Frame(search_frame)
        sep_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(sep_frame, text="Separator:", 
                 font=self.main_window.style_manager.get_font()).pack(side=tk.LEFT)
        self.separator_var = tk.StringVar(value=":")
        sep_entry = ttk.Entry(sep_frame, textvariable=self.separator_var, width=5,
                             font=self.main_window.style_manager.get_font())
        sep_entry.pack(side=tk.LEFT, padx=(5, 10))
        sep_entry.bind('<KeyRelease>', self._on_separator_change)
        
        # Add New Key按钮
        ttk.Button(sep_frame, text="➕ Add New Key", 
                  command=self._add_new_key).pack(side=tk.LEFT)
        
        # 搜索框
        search_input_frame = ttk.Frame(search_frame)
        search_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_input_frame, textvariable=self.search_var,
                                font=self.main_window.style_manager.get_font())
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<Return>', lambda e: self.search_keys())
        
        ttk.Button(search_input_frame, text="🔍", command=self.search_keys, width=4).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 键树形列表
        self._setup_keys_tree(search_frame)
    
    def _setup_keys_tree(self, parent):
        """设置键树形列表"""
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # 配置grid权重
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # 使用Text widget显示键列表
        self.keys_text = tk.Text(tree_frame, wrap=tk.NONE, 
                                font=self.main_window.style_manager.get_font())
        self.keys_text.grid(row=0, column=0, sticky='nsew')
        self.keys_text.bind('<Button-1>', self._on_text_click)
        self.keys_text.bind('<Double-Button-1>', self._on_text_double_click)
        
        # 垂直滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.keys_text.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.keys_text.configure(yscrollcommand=v_scrollbar.set)
        
        # 水平滚动条
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.keys_text.xview)
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        self.keys_text.configure(xscrollcommand=h_scrollbar.set)
        
        # 配置文本标签样式
        self._setup_text_tags()
        
        # 绑定鼠标事件
        self._bind_mouse_events()
    
    def _setup_text_tags(self):
        """设置文本标签样式"""
        self.keys_text.tag_configure('selected', background=SELECTED_COLOR, foreground='white')
        self.keys_text.tag_configure('group', foreground='#666666', 
                                    font=self.main_window.style_manager.get_font(weight='bold'))
        self.keys_text.tag_configure('key', foreground='#333333')
        self.keys_text.tag_configure('hover', background=HOVER_COLOR)
    
    def _bind_mouse_events(self):
        """绑定鼠标事件"""
        self.keys_text.bind('<Motion>', self._on_mouse_motion)
        self.keys_text.bind('<Leave>', self._on_mouse_leave)
        self.keys_text.bind('<Enter>', self._on_mouse_enter)
    
    # 连接管理方法
    def _add_connection(self):
        """添加连接"""
        dialog = ConnectionDialog(self.main_window.root)
        result = dialog.show()
        if result:
            self.main_window.connections.append(result)
            self.refresh_connection_list()
            self.main_window.save_connections()
    
    def _edit_connection(self):
        """编辑连接"""
        selection = self.conn_listbox.curselection()
        if selection:
            conn = self.main_window.connections[selection[0]]
            dialog = ConnectionDialog(self.main_window.root, conn)
            result = dialog.show()
            if result:
                self.main_window.connections[selection[0]] = result
                self.refresh_connection_list()
                self.main_window.save_connections()
    
    def _delete_connection(self):
        """删除连接"""
        selection = self.conn_listbox.curselection()
        if selection:
            if messagebox.askyesno("Delete Connection", "Are you sure?"):
                del self.main_window.connections[selection[0]]
                self.refresh_connection_list()
                self.main_window.save_connections()
    
    def _on_connection_select(self, event):
        """连接选择事件"""
        selection = self.conn_listbox.curselection()
        if selection:
            self.main_window.current_conn = self.main_window.connections[selection[0]]
    
    def _on_connection_double_click(self, event):
        """连接双击事件"""
        self._connect_redis()
    
    def _connect_redis(self):
        """连接Redis"""
        if not self.main_window.current_conn:
            messagebox.showwarning("Warning", "Please select a connection")
            return
        
        # 如果已经连接到同一个连接，不需要重新连接
        selection = self.conn_listbox.curselection()
        if selection and selection[0] == self.main_window.current_conn_index:
            return
        
        def connect_thread():
            try:
                self.main_window.right_panel.update_status("Connecting...")
                
                # 连接Redis
                self.main_window.redis_conn.connect(self.main_window.current_conn)
                
                self.main_window.root.after(0, self._on_connect_success)
                
            except Exception as e:
                error_msg = str(e)
                self.main_window.root.after(0, lambda msg=error_msg: self._on_connect_error(msg))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _disconnect_redis(self):
        """断开Redis连接"""
        try:
            self.main_window.redis_conn.disconnect()
            
            # 重置连接索引
            self.main_window.current_conn_index = -1
            
            # 更新UI状态
            self.main_window.right_panel.update_status("🔌 Disconnected")
            self.connect_btn.config(text="🔌 Connect", state="normal")
            self.disconnect_btn.config(state="disabled")
            
            # 更新连接列表显示
            self.refresh_connection_list()
            
            # 清空键列表和详情
            self._clear_keys_display()
            self.main_window.right_panel.clear_key_details()
            
        except Exception as e:
            messagebox.showerror("Disconnect Error", f"Error while disconnecting: {e}")
    
    def _on_connect_success(self):
        """连接成功回调"""
        # 更新当前连接索引
        selection = self.conn_listbox.curselection()
        if selection:
            self.main_window.current_conn_index = selection[0]
        
        self.main_window.right_panel.update_status(f"✅ Connected to {self.main_window.current_conn['name']}")
        self.connect_btn.config(text="✅ Connected", state="disabled")
        self.disconnect_btn.config(state="normal")
        
        # 更新连接列表显示
        self.refresh_connection_list()
        
        self._update_db_list()
        self.search_keys()
        
        # 刷新key manager显示Redis服务器信息
        self.main_window.right_panel.key_manager.clear_details()
        self.main_window.right_panel.key_manager._show_welcome()
    
    def _on_connect_error(self, error):
        """连接错误回调"""
        self.main_window.right_panel.update_status(f"❌ Connection failed: {error}")
        self.connect_btn.config(text="🔌 Connect", state="normal")
        self.disconnect_btn.config(state="disabled")
        messagebox.showerror("Connection Error", error)
    
    def _update_db_list(self):
        """更新数据库列表"""
        db_count = self.main_window.current_conn.get('db_count', DEFAULT_DB_COUNT)
        self.db_combo['values'] = [f"DB {i}" for i in range(db_count)]
        self.db_var.set("DB 0")
    
    def _on_db_change(self, event):
        """数据库切换事件"""
        redis_client = self.main_window.get_redis_client()
        if redis_client:
            # 重置总键数估计
            self.total_keys_estimate = None
            db_num = int(self.db_var.get().split()[1])
            redis_client.execute_command('SELECT', db_num)
            self.search_keys()
            
            # 刷新key manager显示以更新当前数据库信息
            self.main_window.right_panel.key_manager.clear_details()
            self.main_window.right_panel.key_manager._show_welcome()
    
    def refresh_connection_list(self):
        """刷新连接列表"""
        self.conn_listbox.delete(0, tk.END)
        for i, conn in enumerate(self.main_window.connections):
            # 标记当前连接
            if i == self.main_window.current_conn_index and self.main_window.get_redis_client():
                display_name = f"✅ {conn['name']} (Connected)"
            else:
                display_name = conn['name']
            self.conn_listbox.insert(tk.END, display_name)
    
    # 键搜索和显示方法
    def search_keys(self):
        """搜索键"""
        redis_client = self.main_window.get_redis_client()
        if not redis_client:
            return
        
        # 检查连接状态，如果断开则尝试重连
        if not self.main_window.redis_conn.check_and_reconnect():
            return
        
        # 重置总键数估计
        self.total_keys_estimate = None
        
        def progress_callback(current_count, total_count):
            """进度回调函数"""
            if total_count:
                progress_text = f"Loading keys... {current_count}/{total_count} ({current_count/total_count*100:.1f}%)"
            else:
                progress_text = f"Loading keys... {current_count}"
            
            self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status(progress_text))
        
        def search_thread():
            try:
                pattern = self.search_var.get() or "*"
                max_keys = self.main_window.current_conn.get('max_keys', DEFAULT_MAX_KEYS)
                
                self.main_window.root.after(0, lambda: self.main_window.right_panel.update_status("Initializing key loading..."))
                
                redis_ops = RedisOperations(redis_client)
                keys, total_keys = redis_ops.get_keys(pattern, max_keys, progress_callback)
                
                self.current_keys = keys
                self.total_keys_estimate = total_keys
                self.main_window.root.after(0, lambda: self._update_keys_tree(keys))
                
            except Exception as e:
                error_msg = str(e)
                self.main_window.root.after(0, lambda msg=error_msg: 
                    self.main_window.right_panel.update_status(f"Failed to get keys: {msg}"))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def _update_keys_tree(self, keys):
        """更新键树显示"""
        # 清空文本
        self.keys_text.config(state='normal')
        self.keys_text.delete('1.0', tk.END)
        
        if not keys:
            self.main_window.right_panel.update_status("No keys found")
            self.keys_text.config(state='disabled')
            return
        
        # 首先对键进行排序
        sorted_keys = sorted(keys)
        
        # 按分隔符分组 - 支持多级结构
        separator = self.separator_var.get()
        self.tree_structure = {}
        
        for key in sorted_keys:
            if separator in key:
                parts = key.split(separator)
                current_level = self.tree_structure
                
                # 构建多级树结构
                for i, part in enumerate(parts[:-1]):
                    if part not in current_level:
                        current_level[part] = {'_children': {}, '_keys': []}
                    current_level = current_level[part]['_children']
                
                # 添加最终的键
                if len(parts) > 1:
                    final_part = parts[-1]
                    if final_part not in current_level:
                        current_level[final_part] = {'_children': {}, '_keys': []}
                    current_level[final_part]['_keys'].append(key)
                else:
                    # 只有一个部分，直接作为键
                    if '_keys' not in self.tree_structure:
                        self.tree_structure['_keys'] = []
                    self.tree_structure['_keys'].append(key)
            else:
                if '_ungrouped' not in self.tree_structure:
                    self.tree_structure['_ungrouped'] = {'_children': {}, '_keys': []}
                self.tree_structure['_ungrouped']['_keys'].append(key)
        
        # 对树结构进行排序
        self._sort_tree_structure(self.tree_structure)
        
        # 渲染树结构
        self._render_tree_structure()
        
        # 更新状态
        status_text = f"Found {len(keys)} keys"
        if self.total_keys_estimate and self.total_keys_estimate > len(keys):
            status_text += f" (showing {len(keys)} of ~{self.total_keys_estimate} total)"
        elif self.total_keys_estimate and self.total_keys_estimate == len(keys):
            status_text += f" (total: {self.total_keys_estimate})"
        self.main_window.right_panel.update_status(status_text)
    
    def _sort_tree_structure(self, structure):
        """递归排序树结构"""
        if isinstance(structure, dict):
            # 排序键列表
            if '_keys' in structure and structure['_keys']:
                structure['_keys'].sort()
            
            # 递归排序子结构
            if '_children' in structure and structure['_children']:
                for child_name, child_structure in structure['_children'].items():
                    self._sort_tree_structure(child_structure)
    
    def _render_tree_structure(self):
        """渲染树结构显示"""
        self.keys_text.config(state='normal')
        self.keys_text.delete('1.0', tk.END)
        
        lines = []
        self.keys_data = {}
        self.group_data = {}
        
        def add_tree_items(structure, level=0, path_prefix=""):
            # 对分组名称进行排序
            sorted_names = sorted([name for name in structure.keys() if not name.startswith('_')])
            
            for name in sorted_names:
                data = structure[name]
                
                # 计算该分组的总键数
                total_keys = count_keys_in_structure(data)
                group_path = f"{path_prefix}/{name}" if path_prefix else name
                
                # 如果分组只有一个键且没有子分组，直接显示键
                if total_keys == 1 and not data.get('_children') and data.get('_keys'):
                    key = data['_keys'][0]
                    indent = "    " * level
                    key_line = f"{indent}🔑 {key}"
                    lines.append(key_line)
                    self.keys_data[len(lines)] = key
                    continue
                
                # 显示分组
                indent = "    " * level
                is_expanded = group_path in self.expanded_groups
                expand_icon = "▼" if is_expanded else "▶"
                display_name = f"{indent}{expand_icon} 📁 {name} ({total_keys})"
                lines.append(display_name)
                
                line_index = len(lines)
                self.group_data[line_index] = group_path
                
                # 如果展开，显示子内容
                if is_expanded:
                    if '_children' in data and data['_children']:
                        add_tree_items(data['_children'], level + 1, group_path)
                    
                    if '_keys' in data and data['_keys']:
                        # 键已经在_sort_tree_structure中排序过了
                        for i, key in enumerate(data['_keys']):
                            key_indent = "    " * (level + 1) + "  "
                            is_last = i == len(data['_keys']) - 1 and not data.get('_children')
                            connector = "└─" if is_last else "├─"
                            key_line = f"{key_indent}{connector} 🔑 {key}"
                            lines.append(key_line)
                            self.keys_data[len(lines)] = key
        
        # 处理未分组的键
        if '_ungrouped' in self.tree_structure:
            ungrouped_keys = self.tree_structure['_ungrouped']['_keys']
            if ungrouped_keys:
                if len(ungrouped_keys) == 1:
                    key = ungrouped_keys[0]
                    key_line = f"🔑 {key}"
                    lines.append(key_line)
                    self.keys_data[len(lines)] = key
                else:
                    group_path = "_ungrouped"
                    is_expanded = group_path in self.expanded_groups
                    expand_icon = "▼" if is_expanded else "▶"
                    display_name = f"{expand_icon} 📁 ungrouped ({len(ungrouped_keys)})"
                    lines.append(display_name)
                    line_index = len(lines)
                    self.group_data[line_index] = group_path
                    
                    if is_expanded:
                        for i, key in enumerate(sorted(ungrouped_keys)):
                            is_last = i == len(ungrouped_keys) - 1
                            connector = "└─" if is_last else "├─"
                            key_line = f"      {connector} 🔑 {key}"
                            lines.append(key_line)
                            self.keys_data[len(lines)] = key
        
        # 添加分组的键
        add_tree_items(self.tree_structure)
        
        # 显示文本并应用样式
        self.keys_text.insert('1.0', '\n'.join(lines))
        
        # 为不同类型的行应用样式
        for line_num in range(1, len(lines) + 1):
            if line_num in self.group_data:
                self.keys_text.tag_add('group', f"{line_num}.0", f"{line_num}.end")
            elif line_num in self.keys_data:
                self.keys_text.tag_add('key', f"{line_num}.0", f"{line_num}.end")
        
        self.keys_text.config(state='disabled')
    
    def _clear_keys_display(self):
        """清空键显示"""
        self.keys_text.config(state='normal')
        self.keys_text.delete('1.0', tk.END)
        self.keys_text.config(state='disabled')
        
        # 重置数据
        self.keys_data = {}
        self.group_data = {}
        self.selected_line = None
        self.expanded_groups = set()
        self.tree_structure = {}
        self.current_keys = []
    
    def _on_separator_change(self, event):
        """分隔符改变事件"""
        if self.main_window.get_redis_client() and hasattr(self, 'current_keys'):
            self._update_keys_tree(self.current_keys)
    
    def _add_new_key(self):
        """添加新键"""
        # 调用key_manager的添加新键功能
        if hasattr(self.main_window, 'right_panel') and hasattr(self.main_window.right_panel, 'key_manager'):
            self.main_window.right_panel.key_manager._add_new_key()
        else:
            # 备用方案：显示简单的输入对话框
            from tkinter import simpledialog, messagebox
            key_name = simpledialog.askstring("Add New Key", "Enter key name:")
            if key_name:
                key_value = simpledialog.askstring("Add New Key", "Enter key value:")
                if key_value is not None:  # 允许空值
                    try:
                        redis_client = self.main_window.get_redis_client()
                        if redis_client:
                            redis_client.set(key_name, key_value)
                            messagebox.showinfo("Success", f"Key '{key_name}' added successfully!")
                            self.search_keys()  # 刷新键列表
                        else:
                            messagebox.showerror("Error", "No Redis connection available")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to add key: {e}")
    
    # 鼠标事件处理
    def _on_mouse_motion(self, event):
        """处理鼠标移动事件"""
        try:
            line_num = int(self.keys_text.index(f"@{event.x},{event.y}").split('.')[0])
            
            # 如果鼠标还在同一行，不做任何处理
            if line_num == self.current_hover_line:
                return
            
            # 清除之前的悬停效果
            if self.current_hover_line and self.current_hover_line != self.selected_line:
                self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
            
            # 检查是否是可点击的行（分组或键）
            if line_num in self.group_data or line_num in self.keys_data:
                self.keys_text.config(cursor="hand2")
                if line_num != self.selected_line:
                    self.keys_text.tag_add('hover', f"{line_num}.0", f"{line_num}.end")
                self.current_hover_line = line_num
            else:
                self.keys_text.config(cursor="")
                self.current_hover_line = None
        except (ValueError, tk.TclError):
            self.keys_text.config(cursor="")
            self.current_hover_line = None
    
    def _on_mouse_enter(self, event):
        """处理鼠标进入事件"""
        self.mouse_in_widget = True
    
    def _on_mouse_leave(self, event):
        """处理鼠标离开事件"""
        self.mouse_in_widget = False
        self.keys_text.config(cursor="")
        if self.current_hover_line and self.current_hover_line != self.selected_line:
            self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
        self.current_hover_line = None
    
    def _on_text_click(self, event):
        """处理文本点击事件"""
        # 确保鼠标在widget内才处理点击
        if not getattr(self, 'mouse_in_widget', True):
            return
        
        try:
            line_num = int(self.keys_text.index(tk.CURRENT).split('.')[0])
        except (ValueError, tk.TclError):
            return
        
        # 检查是否点击了分组
        if line_num in self.group_data:
            group_path = self.group_data[line_num]
            current_view = self.keys_text.yview()
            
            if group_path in self.expanded_groups:
                # 收起时，同时收起所有子目录
                self.expanded_groups.remove(group_path)
                to_remove = [path for path in self.expanded_groups if path.startswith(group_path + '/')]
                for path in to_remove:
                    self.expanded_groups.remove(path)
            else:
                self.expanded_groups.add(group_path)
            
            self._render_tree_structure()
            self.keys_text.yview_moveto(current_view[0])
            
        elif line_num in self.keys_data:
            if self.selected_line:
                self.keys_text.tag_remove('selected', f"{self.selected_line}.0", f"{self.selected_line}.end")
            
            self.selected_line = line_num
            self.keys_text.tag_add('selected', f"{line_num}.0", f"{line_num}.end")
            
            key = self.keys_data[line_num]
            self.main_window.right_panel.load_key_details(key)
        
        # 清除悬停效果
        if self.current_hover_line:
            self.keys_text.tag_remove('hover', f"{self.current_hover_line}.0", f"{self.current_hover_line}.end")
            self.current_hover_line = None
    
    def _on_text_double_click(self, event):
        """处理文本双击事件"""
        self._on_text_click(event)