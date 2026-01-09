#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""工具函数"""

import json
import socket
import re
import tkinter as tk
from pathlib import Path


def format_json(text, indent=2):
    """格式化JSON文本"""
    try:
        parsed = json.loads(text)
        return json.dumps(parsed, indent=indent, ensure_ascii=False)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")


def minify_json(text):
    """压缩JSON文本"""
    try:
        parsed = json.loads(text)
        return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")


def apply_json_syntax_highlighting(text_widget):
    """为Text组件应用JSON语法高亮"""
    
    # 定义颜色配置
    colors = {
        'string': '#22863a',      # 绿色 - 字符串
        'number': '#005cc5',      # 蓝色 - 数字
        'boolean': '#d73a49',     # 红色 - 布尔值
        'null': '#6f42c1',        # 紫色 - null
        'key': '#032f62',         # 深蓝色 - 键名
        'brace': '#24292e',       # 深灰色 - 大括号
        'bracket': '#24292e',     # 深灰色 - 方括号
        'comma': '#24292e',       # 深灰色 - 逗号
        'colon': '#24292e',       # 深灰色 - 冒号
    }
    
    # 配置标签样式
    for tag, color in colors.items():
        text_widget.tag_configure(tag, foreground=color)
    
    # 获取文本内容
    content = text_widget.get(1.0, tk.END)
    
    # 清除之前的标签
    for tag in colors.keys():
        text_widget.tag_remove(tag, 1.0, tk.END)
    
    # 检查是否是有效的JSON
    try:
        json.loads(content.strip())
    except (json.JSONDecodeError, ValueError):
        # 如果不是有效JSON，不应用高亮
        return
    
    # 应用语法高亮
    _highlight_json_content(text_widget, content, colors)


def _highlight_json_content(text_widget, content, colors):
    """应用JSON内容高亮"""
    
    # 正则表达式模式
    patterns = [
        # 字符串 (包括键名)
        (r'"[^"\\]*(?:\\.[^"\\]*)*"', 'string'),
        # 数字
        (r'-?\d+\.?\d*(?:[eE][+-]?\d+)?', 'number'),
        # 布尔值
        (r'\b(true|false)\b', 'boolean'),
        # null
        (r'\bnull\b', 'null'),
        # 大括号
        (r'[{}]', 'brace'),
        # 方括号
        (r'[\[\]]', 'bracket'),
        # 逗号
        (r',', 'comma'),
        # 冒号
        (r':', 'colon'),
    ]
    
    # 分行处理
    lines = content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        line_start = f"{line_num}.0"
        
        # 检查是否在字符串内部
        in_string = False
        string_start = 0
        
        for match in re.finditer(r'"[^"\\]*(?:\\.[^"\\]*)*"', line):
            start_pos = f"{line_num}.{match.start()}"
            end_pos = f"{line_num}.{match.end()}"
            
            # 检查是否是键名（后面跟着冒号）
            remaining_line = line[match.end():].strip()
            if remaining_line.startswith(':'):
                text_widget.tag_add('key', start_pos, end_pos)
            else:
                text_widget.tag_add('string', start_pos, end_pos)
        
        # 应用其他模式（除了字符串）
        for pattern, tag in patterns[1:]:  # 跳过字符串模式
            for match in re.finditer(pattern, line):
                # 检查是否在字符串内部
                if not _is_inside_string(line, match.start()):
                    start_pos = f"{line_num}.{match.start()}"
                    end_pos = f"{line_num}.{match.end()}"
                    text_widget.tag_add(tag, start_pos, end_pos)


def _is_inside_string(line, position):
    """检查位置是否在字符串内部"""
    in_string = False
    escaped = False
    
    for i, char in enumerate(line[:position]):
        if char == '"' and not escaped:
            in_string = not in_string
        escaped = (char == '\\' and not escaped)
    
    return in_string


def format_json_with_highlighting(text_widget):
    """格式化JSON并应用语法高亮"""
    try:
        current_value = text_widget.get(1.0, tk.END).strip()
        formatted = format_json(current_value)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(1.0, formatted)
        # 应用JSON语法高亮
        apply_json_syntax_highlighting(text_widget)
        return True
    except ValueError:
        return False
    except Exception:
        return False


def setup_json_text_widget(text_widget):
    """设置JSON文本组件的基本配置"""
    # 设置字体
    text_widget.configure(
        font=('Monaco', 11) if tk.TkVersion >= 8.5 else ('Courier', 11),
        wrap=tk.WORD,
        undo=True,
        maxundo=20
    )
    
    # 绑定内容变化事件，实时高亮
    def on_content_change(event=None):
        # 延迟执行高亮，避免频繁更新
        text_widget.after_idle(lambda: apply_json_syntax_highlighting(text_widget))
    
    # 绑定各种可能改变内容的事件
    text_widget.bind('<KeyRelease>', on_content_change)
    text_widget.bind('<Button-1>', lambda e: text_widget.after(10, on_content_change))
    text_widget.bind('<<Paste>>', lambda e: text_widget.after(10, on_content_change))


def find_free_port():
    """查找可用端口"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def get_config_path():
    """获取配置文件路径"""
    return Path.home() / ".redis_manager_config.json"


def save_connections(connections):
    """保存连接配置"""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(connections, f, indent=2)
    except Exception as e:
        print(f"Failed to save connections: {e}")


def load_connections():
    """加载连接配置"""
    config_path = get_config_path()
    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Failed to load connections: {e}")
    return []


def count_keys_in_structure(structure):
    """递归计算结构中的键总数"""
    count = 0
    if '_keys' in structure:
        count += len(structure['_keys'])
    if '_children' in structure:
        for child in structure['_children'].values():
            count += count_keys_in_structure(child)
    return count