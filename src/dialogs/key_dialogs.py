#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""键编辑对话框"""

import tkinter as tk
from tkinter import ttk, messagebox

from .base_dialog import BaseDialog
from .simple_dialog import SimpleDialog
from ..config import *
from ..utils.helpers import format_json, minify_json, apply_json_syntax_highlighting, setup_json_text_widget, format_json_with_highlighting
from ..redis.operations import RedisOperations


class HashEditDialog(SimpleDialog):
    """Hash字段编辑对话框 - 使用SimpleDialog实现真正的自适应"""
    
    def __init__(self, parent, key, field, value, main_window):
        self.key = key
        self.field = field
        self.value = value
        self.main_window = main_window
        
        super().__init__(parent, "Edit Hash Field", "900x700")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 固定区域：Field编辑
        field_section = self.create_fixed_section(0)
        field_frame = ttk.LabelFrame(field_section, text="Field (Key)")
        field_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        field_frame.grid_columnconfigure(0, weight=1)
        
        self.field_var = tk.StringVar(value=self.field)
        field_entry = ttk.Entry(field_frame, textvariable=self.field_var)
        field_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # 可扩展区域：Value编辑
        value_section = self.create_expandable_section(1)
        value_frame = ttk.LabelFrame(value_section, text="Value")
        value_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        value_frame.grid_rowconfigure(1, weight=1)  # 文本区域可扩展
        value_frame.grid_columnconfigure(0, weight=1)
        
        # JSON格式化按钮 - 固定高度
        json_btn_frame = ttk.Frame(value_frame)
        json_btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(json_btn_frame, text="Format JSON", 
                  command=self._format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", 
                  command=self._minify_json).pack(side=tk.LEFT)
        
        # 文本编辑器 - 自适应高度
        text_container = ttk.Frame(value_frame)
        text_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)  # 文本区域
        text_container.grid_rowconfigure(1, weight=0)  # 搜索按钮区域
        text_container.grid_columnconfigure(0, weight=1)
        
        self.value_text, self.text_frame = self.create_auto_text(text_container, str(self.value))
        
        # 固定区域：按钮
        button_section = self.create_fixed_section(2)
        btn_frame = ttk.Frame(button_section)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        ttk.Button(btn_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
        
        # 设置焦点
        field_entry.focus_set()
        field_entry.select_range(0, tk.END)
    
    def _format_json(self):
        """格式化JSON"""
        if not format_json_with_highlighting(self.value_text):
            messagebox.showerror("JSON Error", "Invalid JSON format")
    
    def _minify_json(self):
        """压缩JSON"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            minified = minify_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, minified)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify JSON: {e}")
    
    def _save_changes(self):
        """保存更改"""
        new_field = self.field_var.get().strip()
        new_value = self.value_text.get(1.0, tk.END).strip()
        
        if not new_field:
            messagebox.showwarning("Warning", "Field name cannot be empty")
            return
        
        try:
            # 获取Redis客户端
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            # 如果字段名改变了，删除旧字段
            if new_field != self.field:
                redis_ops.hash_delete(self.key, self.field)
            
            # 设置新的字段值
            redis_ops.hash_set(self.key, new_field, new_value)
            
            messagebox.showinfo("Success", "Hash field updated successfully!")
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update hash field: {e}")


class SetEditDialog(SimpleDialog):
    """Set成员编辑对话框 - 使用SimpleDialog实现真正的自适应"""
    
    def __init__(self, parent, key, old_value, main_window):
        self.key = key
        self.old_value = old_value
        self.main_window = main_window
        
        super().__init__(parent, "Edit Set Value", "800x500")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 固定区域：标题信息
        header_section = self.create_fixed_section(0)
        header_frame = ttk.Frame(header_section)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        ttk.Label(header_frame, text=f"Editing Set Member: {self.key}", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, padx=5, pady=5)
        
        # 可扩展区域：Value编辑
        value_section = self.create_expandable_section(1)  # 使用row 1作为可扩展区域
        value_frame = ttk.LabelFrame(value_section, text="Value")
        value_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        value_frame.grid_rowconfigure(1, weight=1)  # 文本区域可扩展
        value_frame.grid_columnconfigure(0, weight=1)
        
        # JSON格式化按钮 - 固定高度
        json_btn_frame = ttk.Frame(value_frame)
        json_btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(json_btn_frame, text="Format JSON", 
                  command=self._format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", 
                  command=self._minify_json).pack(side=tk.LEFT)
        
        # 文本编辑器 - 自适应高度
        text_container = ttk.Frame(value_frame)
        text_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)  # 文本区域
        text_container.grid_rowconfigure(1, weight=0)  # 搜索按钮区域
        text_container.grid_columnconfigure(0, weight=1)
        
        self.value_text, self.text_frame = self.create_auto_text(text_container, str(self.old_value))
        
        # 固定区域：按钮
        button_section = self.create_fixed_section(2)  # 使用row 2作为底部按钮
        btn_frame = ttk.Frame(button_section)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        ttk.Button(btn_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
        
        # 设置焦点
        self.value_text.focus_set()
    
    def _format_json(self):
        """格式化JSON"""
        if not format_json_with_highlighting(self.value_text):
            messagebox.showerror("JSON Error", "Invalid JSON format")
    
    def _minify_json(self):
        """压缩JSON"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            minified = minify_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, minified)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify JSON: {e}")
    
    def _save_changes(self):
        """保存更改"""
        new_value = self.value_text.get(1.0, tk.END).strip()
        
        try:
            # 获取Redis客户端
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            # 删除旧值，添加新值
            redis_ops.set_remove(self.key, self.old_value)
            redis_ops.set_add(self.key, new_value)
            
            messagebox.showinfo("Success", "Set value updated successfully!")
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update set value: {e}")
    
    def _get_main_window(self):
        """获取主窗口实例"""
        # 通过父窗口层级找到主窗口
        parent = self.parent
        while parent and not hasattr(parent, 'get_redis_client'):
            parent = parent.master if hasattr(parent, 'master') else None
        return parent


class ListEditDialog(SimpleDialog):
    """List元素编辑对话框 - 使用SimpleDialog实现真正的自适应"""
    
    def __init__(self, parent, key, index, value, main_window):
        self.key = key
        self.index = index
        self.value = value
        self.main_window = main_window
        
        super().__init__(parent, "Edit List Item", "800x500")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 固定区域：Index显示
        index_section = self.create_fixed_section(0)
        index_frame = ttk.LabelFrame(index_section, text="Index")
        index_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        ttk.Label(index_frame, text=f"Index: {self.index}").pack(anchor=tk.W, padx=5, pady=5)
        
        # 可扩展区域：Value编辑
        value_section = self.create_expandable_section(1)
        value_frame = ttk.LabelFrame(value_section, text="Value")
        value_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        value_frame.grid_rowconfigure(1, weight=1)  # 文本区域可扩展
        value_frame.grid_columnconfigure(0, weight=1)
        
        # JSON格式化按钮 - 固定高度
        json_btn_frame = ttk.Frame(value_frame)
        json_btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(json_btn_frame, text="Format JSON", 
                  command=self._format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", 
                  command=self._minify_json).pack(side=tk.LEFT)
        
        # 文本编辑器 - 自适应高度
        text_container = ttk.Frame(value_frame)
        text_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)  # 文本区域
        text_container.grid_rowconfigure(1, weight=0)  # 搜索按钮区域
        text_container.grid_columnconfigure(0, weight=1)
        
        self.value_text, self.text_frame = self.create_auto_text(text_container, str(self.value))
        
        # 固定区域：按钮
        button_section = self.create_fixed_section(2)
        btn_frame = ttk.Frame(button_section)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        ttk.Button(btn_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
        
        # 设置焦点
        self.value_text.focus_set()
    
    def _format_json(self):
        """格式化JSON"""
        if not format_json_with_highlighting(self.value_text):
            messagebox.showerror("JSON Error", "Invalid JSON format")
    
    def _minify_json(self):
        """压缩JSON"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            minified = minify_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, minified)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify JSON: {e}")
    
    def _save_changes(self):
        """保存更改"""
        new_value = self.value_text.get(1.0, tk.END).strip()
        
        try:
            # 获取Redis客户端
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            # 设置列表指定位置的值
            redis_ops.list_set(self.key, self.index, new_value)
            
            messagebox.showinfo("Success", "List item updated successfully!")
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update list item: {e}")
    
    def _get_main_window(self):
        """获取主窗口实例"""
        # 通过父窗口层级找到主窗口
        parent = self.parent
        while parent and not hasattr(parent, 'get_redis_client'):
            parent = parent.master if hasattr(parent, 'master') else None
        return parent


class ZSetEditDialog(SimpleDialog):
    """ZSet成员编辑对话框 - 使用SimpleDialog实现真正的自适应"""
    
    def __init__(self, parent, key, member, score, main_window):
        self.key = key
        self.member = member
        self.score = score
        self.main_window = main_window
        
        super().__init__(parent, "Edit ZSet Member", "800x500")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 固定区域：Score编辑
        score_section = self.create_fixed_section(0)
        score_frame = ttk.LabelFrame(score_section, text="Score")
        score_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        score_frame.grid_columnconfigure(0, weight=1)
        
        self.score_var = tk.StringVar(value=str(self.score))
        score_entry = ttk.Entry(score_frame, textvariable=self.score_var)
        score_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # 可扩展区域：Member编辑
        member_section = self.create_expandable_section(1)
        member_frame = ttk.LabelFrame(member_section, text="Member")
        member_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        member_frame.grid_rowconfigure(1, weight=1)  # 文本区域可扩展
        member_frame.grid_columnconfigure(0, weight=1)
        
        # JSON格式化按钮 - 固定高度
        json_btn_frame = ttk.Frame(member_frame)
        json_btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(json_btn_frame, text="Format JSON", 
                  command=self._format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", 
                  command=self._minify_json).pack(side=tk.LEFT)
        
        # 文本编辑器 - 自适应高度
        text_container = ttk.Frame(member_frame)
        text_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)  # 文本区域
        text_container.grid_rowconfigure(1, weight=0)  # 搜索按钮区域
        text_container.grid_columnconfigure(0, weight=1)
        
        self.member_text, self.text_frame = self.create_auto_text(text_container, str(self.member))
        
        # 固定区域：按钮
        button_section = self.create_fixed_section(2)
        btn_frame = ttk.Frame(button_section)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        ttk.Button(btn_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
        
        # 设置焦点
        score_entry.focus_set()
        score_entry.select_range(0, tk.END)
    
    def _format_json(self):
        """格式化JSON"""
        if not format_json_with_highlighting(self.member_text):
            messagebox.showerror("JSON Error", "Invalid JSON format")
    
    def _minify_json(self):
        """压缩JSON"""
        try:
            current_value = self.member_text.get(1.0, tk.END).strip()
            minified = minify_json(current_value)
            self.member_text.delete(1.0, tk.END)
            self.member_text.insert(1.0, minified)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify JSON: {e}")
    
    def _save_changes(self):
        """保存更改"""
        try:
            new_score = float(self.score_var.get().strip())
            new_member = self.member_text.get(1.0, tk.END).strip()
            
            # 获取Redis客户端
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            # 删除旧成员，添加新成员
            redis_ops.zset_remove(self.key, self.member)
            redis_ops.zset_add(self.key, {new_member: new_score})
            
            messagebox.showinfo("Success", "ZSet member updated successfully!")
            self.close(True)
            
        except ValueError:
            messagebox.showerror("Error", "Score must be a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update ZSet member: {e}")
    
    def _get_main_window(self):
        """获取主窗口实例"""
        # 通过父窗口层级找到主窗口
        parent = self.parent
        while parent and not hasattr(parent, 'get_redis_client'):
            parent = parent.master if hasattr(parent, 'master') else None
        return parent


class AddHashDialog(BaseDialog):
    """添加Hash字段对话框"""
    
    def __init__(self, parent, key, main_window):
        self.key = key
        self.main_window = main_window
        
        super().__init__(parent, "Add Hash Field", "900x700")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # Field编辑 - 固定高度
        field_frame = ttk.LabelFrame(self.scrollable_frame, text="Field (Key)")
        field_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.field_var = tk.StringVar()
        field_entry = ttk.Entry(field_frame, textvariable=self.field_var)
        field_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Value编辑 - 让文本区域占用剩余空间
        value_frame = ttk.LabelFrame(self.scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # JSON格式化按钮 - 固定高度
        self._create_json_buttons(value_frame)
        
        # 文本编辑器 - 自适应高度
        self._create_text_editor(value_frame)
        
        # 按钮 - 固定高度
        self._create_buttons()
        
        # 设置焦点
        field_entry.focus_set()
    
    def _create_json_buttons(self, parent):
        """创建JSON格式化按钮"""
        json_btn_frame = ttk.Frame(parent)
        json_btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(json_btn_frame, text="Format JSON", 
                  command=self._format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", 
                  command=self._minify_json).pack(side=tk.LEFT)
    
    def _create_text_editor(self, parent):
        """创建文本编辑器"""
        self.value_text, self.text_frame = self.create_auto_resize_text(parent, "", min_height=6, max_height=15)
        
        # 存储文本组件引用以便在resize时使用
        self._text_widgets = [self.value_text]
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self._add_field).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _format_json(self):
        """格式化JSON"""
        if not format_json_with_highlighting(self.value_text):
            messagebox.showerror("JSON Error", "Invalid JSON format")
    
    def _minify_json(self):
        """压缩JSON"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            minified = minify_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, minified)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to minify JSON: {e}")
    
    def _add_field(self):
        """添加字段"""
        new_field = self.field_var.get().strip()
        new_value = self.value_text.get(1.0, tk.END).strip()
        
        if not new_field:
            messagebox.showerror("Error", "Field name cannot be empty")
            return
        
        try:
            # 获取Redis客户端
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            # 添加字段
            redis_ops.hash_set(self.key, new_field, new_value)
            
            messagebox.showinfo("Success", "Hash field added successfully!")
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add hash field: {e}")


class AddListDialog(BaseDialog):
    """添加List元素对话框"""
    
    def __init__(self, parent, key, main_window):
        self.key = key
        self.main_window = main_window
        
        super().__init__(parent, "Add List Item", "600x400")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 说明 - 固定高度
        info_frame = ttk.Frame(self.scrollable_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(info_frame, text=f"Add new item to list: {self.key}", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # 位置选择 - 固定高度
        position_frame = ttk.LabelFrame(self.scrollable_frame, text="Position")
        position_frame.pack(fill=tk.X, padx=10, pady=(5, 5))
        
        self.position_var = tk.StringVar(value="end")
        ttk.Radiobutton(position_frame, text="Add to end (RPUSH)", 
                       variable=self.position_var, value="end").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(position_frame, text="Add to beginning (LPUSH)", 
                       variable=self.position_var, value="start").pack(anchor=tk.W, padx=5, pady=2)
        
        # Value编辑 - 让文本区域占用剩余空间
        value_frame = ttk.LabelFrame(self.scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 文本编辑器 - 自适应高度
        self.value_text, self.text_frame = self.create_auto_resize_text(value_frame, "", min_height=5, max_height=10)
        
        # 存储文本组件引用以便在resize时使用
        self._text_widgets = [self.value_text]
        
        # 按钮 - 固定高度
        self._create_buttons()
        
        # 设置焦点
        self.value_text.focus_set()
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self._add_item).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _add_item(self):
        """添加列表项"""
        try:
            value = self.value_text.get(1.0, tk.END).strip()
            if not value:
                messagebox.showwarning("Warning", "Value cannot be empty")
                return
            
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            # 根据位置选择添加到开头或结尾
            if self.position_var.get() == "start":
                redis_ops.list_push(self.key, value, left=True)  # LPUSH
            else:
                redis_ops.list_push(self.key, value, left=False)  # RPUSH
            
            messagebox.showinfo("Success", "List item added successfully!")
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add list item: {e}")


class AddSetDialog(BaseDialog):
    """添加Set成员对话框"""
    
    def __init__(self, parent, key, main_window):
        self.key = key
        self.main_window = main_window
        
        super().__init__(parent, "Add Set Member", "600x400")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 说明 - 固定高度
        info_frame = ttk.Frame(self.scrollable_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(info_frame, text=f"Add new member to set: {self.key}", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(info_frame, text="Note: Duplicate members will be ignored", 
                 font=('Arial', 10), foreground='#666666').pack(anchor=tk.W, pady=(2, 0))
        
        # Value编辑 - 让文本区域占用大部分空间
        value_frame = ttk.LabelFrame(self.scrollable_frame, text="Member Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 文本编辑器 - 自适应高度
        self.value_text, self.text_frame = self.create_auto_resize_text(value_frame, "", min_height=5, max_height=10)
        
        # 存储文本组件引用以便在resize时使用
        self._text_widgets = [self.value_text]
        
        # 批量添加选项 - 固定高度
        batch_frame = ttk.LabelFrame(self.scrollable_frame, text="Batch Add Options")
        batch_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.batch_var = tk.BooleanVar()
        ttk.Checkbutton(batch_frame, text="Add multiple members (one per line)", 
                       variable=self.batch_var).pack(anchor=tk.W, padx=5, pady=5)
        
        # 按钮 - 固定高度
        self._create_buttons()
        
        # 设置焦点
        self.value_text.focus_set()
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self._add_member).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _add_member(self):
        """添加集合成员"""
        try:
            value = self.value_text.get(1.0, tk.END).strip()
            if not value:
                messagebox.showwarning("Warning", "Value cannot be empty")
                return
            
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            if self.batch_var.get():
                # 批量添加，按行分割
                members = [line.strip() for line in value.split('\n') if line.strip()]
                if not members:
                    messagebox.showwarning("Warning", "No valid members to add")
                    return
                
                result = redis_ops.set_add(self.key, *members)
                messagebox.showinfo("Success", f"Added {result} new members to set (duplicates ignored)")
            else:
                # 单个添加
                result = redis_ops.set_add(self.key, value)
                if result:
                    messagebox.showinfo("Success", "Set member added successfully!")
                else:
                    messagebox.showinfo("Info", "Member already exists in set")
            
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add set member: {e}")


class AddZSetDialog(BaseDialog):
    """添加ZSet成员对话框"""
    
    def __init__(self, parent, key, main_window):
        self.key = key
        self.main_window = main_window
        
        super().__init__(parent, "Add ZSet Member", "600x500")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 说明 - 固定高度
        info_frame = ttk.Frame(self.scrollable_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(info_frame, text=f"Add new member to sorted set: {self.key}", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Score编辑 - 固定高度
        score_frame = ttk.LabelFrame(self.scrollable_frame, text="Score")
        score_frame.pack(fill=tk.X, padx=10, pady=(5, 5))
        
        self.score_var = tk.StringVar(value="0")
        score_entry = ttk.Entry(score_frame, textvariable=self.score_var)
        score_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Member编辑 - 让文本区域占用剩余空间
        member_frame = ttk.LabelFrame(self.scrollable_frame, text="Member")
        member_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 文本编辑器 - 自适应高度
        self.member_text, self.text_frame = self.create_auto_resize_text(member_frame, "", min_height=4, max_height=8)
        
        # 存储文本组件引用以便在resize时使用
        self._text_widgets = [self.member_text]
        
        # 按钮 - 固定高度
        self._create_buttons()
        
        # 设置焦点
        score_entry.focus_set()
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self._add_member).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _add_member(self):
        """添加有序集合成员"""
        try:
            score_str = self.score_var.get().strip()
            member = self.member_text.get(1.0, tk.END).strip()
            
            if not score_str:
                messagebox.showwarning("Warning", "Score cannot be empty")
                return
            
            if not member:
                messagebox.showwarning("Warning", "Member cannot be empty")
                return
            
            try:
                score = float(score_str)
            except ValueError:
                messagebox.showerror("Error", "Score must be a valid number")
                return
            
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            # 添加成员
            result = redis_ops.zset_add(self.key, {member: score})
            if result:
                messagebox.showinfo("Success", "ZSet member added successfully!")
            else:
                messagebox.showinfo("Info", "Member score updated (member already existed)")
            
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add zset member: {e}")


class AddNewKeyDialog(SimpleDialog):
    """添加新键对话框 - 使用SimpleDialog实现真正的自适应"""
    
    def __init__(self, parent, main_window):
        self.main_window = main_window
        self._text_widgets = []  # 初始化文本组件列表
        
        super().__init__(parent, "Add New Key", "700x650")  # 增加默认高度
        self._setup_ui()
        
        # 设置更大的最小尺寸以确保data type区域可见
        self.dialog.minsize(600, 500)
    
    def _setup_ui(self):
        """设置UI"""
        # 重新配置grid权重 - 只有值输入区域(row 3)可扩展
        for i in range(10):
            if i == 3:  # 值输入区域可扩展
                self.main_container.grid_rowconfigure(i, weight=1)
            else:
                self.main_container.grid_rowconfigure(i, weight=0)
        
        # 固定区域：键名输入
        key_section = self.create_fixed_section(0)
        key_frame = ttk.LabelFrame(key_section, text="Key Name")
        key_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        key_frame.grid_columnconfigure(0, weight=1)
        
        self.key_var = tk.StringVar()
        key_entry = ttk.Entry(key_frame, textvariable=self.key_var, font=('Arial', 11))
        key_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # 固定区域：数据类型选择 - 设置固定高度防止被挤压
        type_section = self.create_fixed_section(1)
        type_frame = ttk.LabelFrame(type_section, text="Data Type")
        type_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # 设置固定高度的内容区域 - 单行布局
        self.type_var = tk.StringVar(value="string")
        type_inner = ttk.Frame(type_frame, height=40)  # 减少高度到40像素，适合单行
        type_inner.pack(fill=tk.X, padx=5, pady=8)
        type_inner.pack_propagate(False)  # 防止子组件改变父容器大小
        
        # 数据类型单选按钮 - 单行布局
        ttk.Radiobutton(type_inner, text="String", variable=self.type_var, 
                       value="string", command=self._on_type_change).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_inner, text="Hash", variable=self.type_var, 
                       value="hash", command=self._on_type_change).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_inner, text="List", variable=self.type_var, 
                       value="list", command=self._on_type_change).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_inner, text="Set", variable=self.type_var, 
                       value="set", command=self._on_type_change).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(type_inner, text="ZSet", variable=self.type_var, 
                       value="zset", command=self._on_type_change).pack(side=tk.LEFT)
        
        # 固定区域：TTL设置
        ttl_section = self.create_fixed_section(2)
        ttl_frame = ttk.LabelFrame(ttl_section, text="TTL (Time To Live)")
        ttl_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        ttl_inner = ttk.Frame(ttl_frame)
        ttl_inner.pack(fill=tk.X, padx=5, pady=5)
        
        self.ttl_enabled = tk.BooleanVar()
        ttk.Checkbutton(ttl_inner, text="Set TTL", variable=self.ttl_enabled).pack(side=tk.LEFT)
        
        self.ttl_var = tk.StringVar(value="3600")
        ttl_entry = ttk.Entry(ttl_inner, textvariable=self.ttl_var, width=10)
        ttl_entry.pack(side=tk.LEFT, padx=(10, 5))
        ttk.Label(ttl_inner, text="seconds").pack(side=tk.LEFT)
        
        # 可扩展区域：值输入区域
        value_section = self.create_expandable_section(3)
        self.value_frame = ttk.LabelFrame(value_section, text="Value")
        self.value_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.value_frame.grid_rowconfigure(0, weight=1)
        self.value_frame.grid_columnconfigure(0, weight=1)
        
        # 初始化为String类型的输入
        self._setup_string_input()
        
        # 固定区域：按钮
        self._create_buttons()
        
        # 设置焦点
        key_entry.focus_set()
    
    def _on_type_change(self):
        """数据类型改变事件"""
        # 清空当前值输入区域
        for widget in self.value_frame.winfo_children():
            widget.destroy()
        
        # 清空文本组件引用
        self._text_widgets = []
        
        # 根据选择的类型设置相应的输入界面
        data_type = self.type_var.get()
        if data_type == "string":
            self._setup_string_input()
        elif data_type == "hash":
            self._setup_hash_input()
        elif data_type == "list":
            self._setup_list_input()
        elif data_type == "set":
            self._setup_set_input()
        elif data_type == "zset":
            self._setup_zset_input()
    
    def _setup_string_input(self):
        """设置String类型输入"""
        # 清空当前内容
        for widget in self.value_frame.winfo_children():
            widget.destroy()
        
        # 配置value_frame的grid权重
        self.value_frame.grid_rowconfigure(1, weight=1)  # 文本区域可扩展
        self.value_frame.grid_columnconfigure(0, weight=1)
        
        # JSON格式化按钮
        json_btn_frame = ttk.Frame(self.value_frame)
        json_btn_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        ttk.Button(json_btn_frame, text="Format JSON", 
                  command=self._format_json).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(json_btn_frame, text="Minify JSON", 
                  command=self._minify_json).pack(side=tk.LEFT)
        
        # 文本输入 - 使用自适应高度
        text_container = ttk.Frame(self.value_frame)
        text_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        
        self.string_text, self.string_text_frame = self.create_auto_text(text_container, "")
        
        # 存储文本组件引用
        self._text_widgets = [self.string_text]
    
    def _setup_hash_input(self):
        """设置Hash类型输入"""
        # 清空当前内容
        for widget in self.value_frame.winfo_children():
            widget.destroy()
        
        # 配置value_frame的grid权重
        self.value_frame.grid_rowconfigure(2, weight=1)  # 文本区域可扩展
        self.value_frame.grid_columnconfigure(0, weight=1)
        
        # 说明
        ttk.Label(self.value_frame, text="Enter hash fields (one per line): field=value", 
                 font=('Arial', 10), foreground='#666666').grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        # 示例
        example_frame = ttk.Frame(self.value_frame)
        example_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        ttk.Label(example_frame, text="Example:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Label(example_frame, text="name=John Doe", font=('Arial', 9), foreground='#0066CC').pack(side=tk.LEFT, padx=(5, 0))
        
        # 文本输入 - 使用自适应高度
        text_container = ttk.Frame(self.value_frame)
        text_container.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        
        self.hash_text, self.hash_text_frame = self.create_auto_text(text_container, "name=\nage=\nemail=")
        
        # 存储文本组件引用
        self._text_widgets = [self.hash_text]
    
    def _setup_list_input(self):
        """设置List类型输入"""
        # 清空当前内容
        for widget in self.value_frame.winfo_children():
            widget.destroy()
        
        # 配置value_frame的grid权重
        self.value_frame.grid_rowconfigure(1, weight=1)  # 文本区域可扩展
        self.value_frame.grid_columnconfigure(0, weight=1)
        
        # 说明
        ttk.Label(self.value_frame, text="Enter list items (one per line):", 
                 font=('Arial', 10), foreground='#666666').grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        # 文本输入 - 使用自适应高度
        text_container = ttk.Frame(self.value_frame)
        text_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        
        self.list_text, self.list_text_frame = self.create_auto_text(text_container, "item1\nitem2\nitem3")
        
        # 存储文本组件引用
        self._text_widgets = [self.list_text]
    
    def _setup_set_input(self):
        """设置Set类型输入"""
        # 清空当前内容
        for widget in self.value_frame.winfo_children():
            widget.destroy()
        
        # 配置value_frame的grid权重
        self.value_frame.grid_rowconfigure(1, weight=1)  # 文本区域可扩展
        self.value_frame.grid_columnconfigure(0, weight=1)
        
        # 说明
        ttk.Label(self.value_frame, text="Enter set members (one per line, duplicates will be ignored):", 
                 font=('Arial', 10), foreground='#666666').grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        # 文本输入 - 使用自适应高度
        text_container = ttk.Frame(self.value_frame)
        text_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        
        self.set_text, self.set_text_frame = self.create_auto_text(text_container, "member1\nmember2\nmember3")
        
        # 存储文本组件引用
        self._text_widgets = [self.set_text]
    
    def _setup_zset_input(self):
        """设置ZSet类型输入"""
        # 清空当前内容
        for widget in self.value_frame.winfo_children():
            widget.destroy()
        
        # 配置value_frame的grid权重
        self.value_frame.grid_rowconfigure(2, weight=1)  # 文本区域可扩展
        self.value_frame.grid_columnconfigure(0, weight=1)
        
        # 说明
        ttl_label = ttk.Label(self.value_frame, text="Enter sorted set members (one per line): score member", 
                             font=('Arial', 10), foreground='#666666')
        ttl_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        # 示例
        example_frame = ttk.Frame(self.value_frame)
        example_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        ttk.Label(example_frame, text="Example:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        ttk.Label(example_frame, text="100 player1", font=('Arial', 9), foreground='#0066CC').pack(side=tk.LEFT, padx=(5, 0))
        
        # 文本输入 - 使用自适应高度
        text_container = ttk.Frame(self.value_frame)
        text_container.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        
        self.zset_text, self.zset_text_frame = self.create_auto_text(text_container, "100 player1\n90 player2\n80 player3")
        
        # 存储文本组件引用
        self._text_widgets = [self.zset_text]
    
    def _create_buttons(self):
        """创建按钮"""
        btn_section = self.create_fixed_section(4)
        btn_frame = ttk.Frame(btn_section)
        btn_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Create Key", command=self._create_key).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _format_json(self):
        """格式化JSON"""
        if hasattr(self, 'string_text'):
            if not format_json_with_highlighting(self.string_text):
                messagebox.showerror("JSON Error", "Invalid JSON format")
    
    def _minify_json(self):
        """压缩JSON"""
        if hasattr(self, 'string_text'):
            try:
                from ..utils.helpers import minify_json
                current_value = self.string_text.get(1.0, tk.END).strip()
                minified = minify_json(current_value)
                self.string_text.delete(1.0, tk.END)
                self.string_text.insert(1.0, minified)
            except Exception as e:
                messagebox.showerror("JSON Error", f"Failed to minify JSON: {e}")
    
    def _create_key(self):
        """创建键"""
        try:
            key_name = self.key_var.get().strip()
            if not key_name:
                messagebox.showwarning("Warning", "Key name cannot be empty")
                return
            
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            # 检查键是否已存在
            if redis_client.exists(key_name):
                if not messagebox.askyesno("Key Exists", f"Key '{key_name}' already exists. Overwrite?"):
                    return
            
            redis_ops = RedisOperations(redis_client)
            data_type = self.type_var.get()
            
            # 根据数据类型创建键
            if data_type == "string":
                value = self.string_text.get(1.0, tk.END).strip()
                redis_client.set(key_name, value)
                
            elif data_type == "hash":
                hash_data = self._parse_hash_input()
                if hash_data:
                    redis_client.hset(key_name, mapping=hash_data)
                else:
                    messagebox.showwarning("Warning", "No valid hash fields provided")
                    return
                    
            elif data_type == "list":
                list_items = self._parse_list_input()
                if list_items:
                    redis_client.rpush(key_name, *list_items)
                else:
                    messagebox.showwarning("Warning", "No valid list items provided")
                    return
                    
            elif data_type == "set":
                set_members = self._parse_set_input()
                if set_members:
                    redis_client.sadd(key_name, *set_members)
                else:
                    messagebox.showwarning("Warning", "No valid set members provided")
                    return
                    
            elif data_type == "zset":
                zset_data = self._parse_zset_input()
                if zset_data:
                    redis_client.zadd(key_name, zset_data)
                else:
                    messagebox.showwarning("Warning", "No valid zset members provided")
                    return
            
            # 设置TTL
            if self.ttl_enabled.get():
                try:
                    ttl_seconds = int(self.ttl_var.get())
                    if ttl_seconds > 0:
                        redis_client.expire(key_name, ttl_seconds)
                except ValueError:
                    messagebox.showwarning("Warning", "Invalid TTL value, key created without TTL")
            
            messagebox.showinfo("Success", f"Key '{key_name}' created successfully!")
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create key: {e}")
    
    def _parse_hash_input(self):
        """解析Hash输入"""
        try:
            text = self.hash_text.get(1.0, tk.END).strip()
            hash_data = {}
            
            for line in text.split('\n'):
                line = line.strip()
                if line and '=' in line:
                    field, value = line.split('=', 1)
                    field = field.strip()
                    value = value.strip()
                    if field:  # 允许空值
                        hash_data[field] = value
            
            return hash_data
        except Exception:
            return {}
    
    def _parse_list_input(self):
        """解析List输入"""
        try:
            text = self.list_text.get(1.0, tk.END).strip()
            items = []
            
            for line in text.split('\n'):
                line = line.strip()
                if line:  # 忽略空行
                    items.append(line)
            
            return items
        except Exception:
            return []
    
    def _parse_set_input(self):
        """解析Set输入"""
        try:
            text = self.set_text.get(1.0, tk.END).strip()
            members = []
            
            for line in text.split('\n'):
                line = line.strip()
                if line:  # 忽略空行
                    members.append(line)
            
            return members
        except Exception:
            return []
    
    def _parse_zset_input(self):
        """解析ZSet输入"""
        try:
            text = self.zset_text.get(1.0, tk.END).strip()
            zset_data = {}
            
            for line in text.split('\n'):
                line = line.strip()
                if line:
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        try:
                            score = float(parts[0])
                            member = parts[1].strip()
                            if member:
                                zset_data[member] = score
                        except ValueError:
                            continue  # 忽略无效的分数
            
            return zset_data
        except Exception:
            return {}
    
    def _get_main_window(self):
        """获取主窗口实例"""
        # 通过父窗口层级找到主窗口
        parent = self.parent
        while parent and not hasattr(parent, 'get_redis_client'):
            parent = parent.master if hasattr(parent, 'master') else None
        return parent