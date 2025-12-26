#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""键编辑对话框"""

import tkinter as tk
from tkinter import ttk, messagebox

from .base_dialog import BaseDialog
from ..config import *
from ..utils.helpers import format_json, minify_json
from ..redis.operations import RedisOperations


class HashEditDialog(BaseDialog):
    """Hash字段编辑对话框"""
    
    def __init__(self, parent, key, field, value, main_window):
        self.key = key
        self.field = field
        self.value = value
        self.main_window = main_window
        
        super().__init__(parent, "Edit Hash Field", "900x700")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # Field编辑
        field_frame = ttk.LabelFrame(self.scrollable_frame, text="Field (Key)")
        field_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.field_var = tk.StringVar(value=self.field)
        field_entry = ttk.Entry(field_frame, textvariable=self.field_var)
        field_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Value编辑
        value_frame = ttk.LabelFrame(self.scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # JSON格式化按钮
        self._create_json_buttons(value_frame)
        
        # 文本编辑器
        self._create_text_editor(value_frame)
        
        # 按钮
        self._create_buttons()
        
        # 设置焦点
        field_entry.focus_set()
        field_entry.select_range(0, tk.END)
    
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
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.value_text = tk.Text(text_frame, wrap=tk.WORD, height=20)
        self.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.value_text.insert(tk.END, str(self.value))
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.value_text.configure(yscrollcommand=text_scroll.set)
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _format_json(self):
        """格式化JSON"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            formatted = format_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, formatted)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format JSON: {e}")
    
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
            messagebox.showerror("Error", "Field name cannot be empty")
            return
        
        try:
            # 获取Redis客户端
            redis_client = self.main_window.get_redis_client()
            if not redis_client:
                messagebox.showerror("Error", "No Redis connection available")
                return
            
            redis_ops = RedisOperations(redis_client)
            
            # 如果字段名改变了，先删除旧字段
            if new_field != self.field:
                redis_ops.hash_delete(self.key, self.field)
            
            # 设置新值
            redis_ops.hash_set(self.key, new_field, new_value)
            
            messagebox.showinfo("Success", "Hash field updated successfully!")
            self.close(True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update hash field: {e}")
    
    def _get_main_window(self):
        """获取主窗口实例"""
        # 通过父窗口层级找到主窗口
        parent = self.parent
        while parent and not hasattr(parent, 'get_redis_client'):
            parent = parent.master if hasattr(parent, 'master') else None
        return parent


class SetEditDialog(BaseDialog):
    """Set成员编辑对话框"""
    
    def __init__(self, parent, key, old_value, main_window):
        self.key = key
        self.old_value = old_value
        self.main_window = main_window
        
        super().__init__(parent, "Edit Set Value", "600x400")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # Value编辑
        value_frame = ttk.LabelFrame(self.scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # JSON格式化按钮
        self._create_json_buttons(value_frame)
        
        # 文本编辑器
        self._create_text_editor(value_frame)
        
        # 按钮
        self._create_buttons()
        
        self.value_text.focus_set()
    
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
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.value_text = tk.Text(text_frame, wrap=tk.WORD, height=12)
        self.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.value_text.insert(tk.END, str(self.old_value))
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.value_text.configure(yscrollcommand=text_scroll.set)
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _format_json(self):
        """格式化JSON"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            formatted = format_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, formatted)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format JSON: {e}")
    
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


class ListEditDialog(BaseDialog):
    """List元素编辑对话框"""
    
    def __init__(self, parent, key, index, value, main_window):
        self.key = key
        self.index = index
        self.value = value
        self.main_window = main_window
        
        super().__init__(parent, "Edit List Item", "600x400")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # Index显示
        index_frame = ttk.LabelFrame(self.scrollable_frame, text="Index")
        index_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(index_frame, text=f"Index: {self.index}").pack(anchor=tk.W, padx=5, pady=5)
        
        # Value编辑
        value_frame = ttk.LabelFrame(self.scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # JSON格式化按钮
        self._create_json_buttons(value_frame)
        
        # 文本编辑器
        self._create_text_editor(value_frame)
        
        # 按钮
        self._create_buttons()
        
        self.value_text.focus_set()
    
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
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.value_text = tk.Text(text_frame, wrap=tk.WORD, height=12)
        self.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.value_text.insert(tk.END, str(self.value))
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.value_text.configure(yscrollcommand=text_scroll.set)
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _format_json(self):
        """格式化JSON"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            formatted = format_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, formatted)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format JSON: {e}")
    
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


class ZSetEditDialog(BaseDialog):
    """ZSet成员编辑对话框"""
    
    def __init__(self, parent, key, member, score, main_window):
        self.key = key
        self.member = member
        self.score = score
        self.main_window = main_window
        
        super().__init__(parent, "Edit ZSet Member", "600x500")
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # Score编辑
        score_frame = ttk.LabelFrame(self.scrollable_frame, text="Score")
        score_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.score_var = tk.StringVar(value=str(self.score))
        score_entry = ttk.Entry(score_frame, textvariable=self.score_var)
        score_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Member编辑
        member_frame = ttk.LabelFrame(self.scrollable_frame, text="Member")
        member_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # JSON格式化按钮
        self._create_json_buttons(member_frame)
        
        # 文本编辑器
        self._create_text_editor(member_frame)
        
        # 按钮
        self._create_buttons()
        
        score_entry.focus_set()
        score_entry.select_range(0, tk.END)
    
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
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.member_text = tk.Text(text_frame, wrap=tk.WORD, height=10)
        self.member_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.member_text.insert(tk.END, str(self.member))
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.member_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.member_text.configure(yscrollcommand=text_scroll.set)
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=self._save_changes).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _format_json(self):
        """格式化JSON"""
        try:
            current_value = self.member_text.get(1.0, tk.END).strip()
            formatted = format_json(current_value)
            self.member_text.delete(1.0, tk.END)
            self.member_text.insert(1.0, formatted)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format JSON: {e}")
    
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
        # Field编辑
        field_frame = ttk.LabelFrame(self.scrollable_frame, text="Field (Key)")
        field_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.field_var = tk.StringVar()
        field_entry = ttk.Entry(field_frame, textvariable=self.field_var)
        field_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Value编辑
        value_frame = ttk.LabelFrame(self.scrollable_frame, text="Value")
        value_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # JSON格式化按钮
        self._create_json_buttons(value_frame)
        
        # 文本编辑器
        self._create_text_editor(value_frame)
        
        # 按钮
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
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.value_text = tk.Text(text_frame, wrap=tk.WORD, height=20)
        self.value_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        text_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.value_text.yview)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.value_text.configure(yscrollcommand=text_scroll.set)
    
    def _create_buttons(self):
        """创建按钮"""
        btn_frame = ttk.Frame(self.scrollable_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Add", command=self._add_field).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Cancel", command=lambda: self.close()).pack(side=tk.RIGHT)
    
    def _format_json(self):
        """格式化JSON"""
        try:
            current_value = self.value_text.get(1.0, tk.END).strip()
            formatted = format_json(current_value)
            self.value_text.delete(1.0, tk.END)
            self.value_text.insert(1.0, formatted)
        except ValueError:
            messagebox.showerror("JSON Error", "Invalid JSON format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to format JSON: {e}")
    
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
    
    def _get_main_window(self):
        """获取主窗口实例"""
        # 通过父窗口层级找到主窗口
        parent = self.parent
        while parent and not hasattr(parent, 'get_redis_client'):
            parent = parent.master if hasattr(parent, 'master') else None
        return parent