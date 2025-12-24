#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time

class KeyManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    def load_key_details(self, key):
        """加载键详情"""
        if not self.redis_client.exists(key):
            raise Exception(f"Key '{key}' does not exist")
        
        key_type = self.redis_client.type(key)
        ttl = self.redis_client.ttl(key)
        
        value = None
        try:
            if key_type == 'string':
                value = self.redis_client.get(key)
            elif key_type == 'list':
                value = self.redis_client.lrange(key, 0, -1)
            elif key_type == 'set':
                value = list(self.redis_client.smembers(key))
            elif key_type == 'hash':
                hash_len = self.redis_client.hlen(key)
                if hash_len > 1000:
                    value = {}
                    cursor = 0
                    while True:
                        cursor, fields = self.redis_client.hscan(key, cursor, count=100)
                        value.update(fields)
                        if cursor == 0:
                            break
                else:
                    value = self.redis_client.hgetall(key)
            elif key_type == 'zset':
                value = self.redis_client.zrange(key, 0, -1, withscores=True)
            else:
                value = str(self.redis_client.dump(key))
        except Exception as e:
            value = f"Error reading value: {str(e)}"
        
        return key_type, ttl, value
    
    def search_keys(self, pattern="*", max_keys=0):
        """搜索键"""
        if max_keys == 0:
            return self.load_keys_streaming(pattern)
        else:
            keys = []
            for key in self.redis_client.scan_iter(match=pattern, count=1000):
                keys.append(key)
                if len(keys) >= max_keys:
                    break
            return keys
    
    def load_keys_streaming(self, pattern):
        """流式加载键"""
        keys = []
        count = 0
        max_keys = 100000
        
        for key in self.redis_client.scan_iter(match=pattern, count=1000):
            keys.append(key)
            count += 1
            if count >= max_keys:
                break
        
        return keys
    
    def build_tree_structure(self, keys, separator=":"):
        """构建树结构"""
        tree_structure = {}
        
        for key in keys:
            if separator in key:
                parts = key.split(separator)
                current_level = tree_structure
                
                for i, part in enumerate(parts[:-1]):
                    if part not in current_level:
                        current_level[part] = {'_children': {}, '_keys': []}
                    current_level = current_level[part]['_children']
                
                if len(parts) > 1:
                    final_part = parts[-1]
                    if final_part not in current_level:
                        current_level[final_part] = {'_children': {}, '_keys': []}
                    current_level[final_part]['_keys'].append(key)
                else:
                    if '_keys' not in tree_structure:
                        tree_structure['_keys'] = []
                    tree_structure['_keys'].append(key)
            else:
                if '_ungrouped' not in tree_structure:
                    tree_structure['_ungrouped'] = {'_children': {}, '_keys': []}
                tree_structure['_ungrouped']['_keys'].append(key)
        
        return tree_structure
    
    def count_keys_in_structure(self, structure):
        """递归计算结构中的键总数"""
        count = 0
        if '_keys' in structure:
            count += len(structure['_keys'])
        if '_children' in structure:
            for child in structure['_children'].values():
                count += self.count_keys_in_structure(child)
        return count