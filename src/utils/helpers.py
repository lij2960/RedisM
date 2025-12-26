#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""工具函数"""

import json
import socket
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