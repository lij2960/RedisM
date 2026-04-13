#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Redis操作类"""

import time
from ..config import MAX_KEYS_STREAMING


class RedisOperations:
    """Redis数据操作"""
    
    def __init__(self, redis_client):
        self.redis_client = redis_client
    
    def get_keys(self, pattern="*", max_keys=0, progress_callback=None):
        """获取键列表
        
        注意：调用此方法前应确保已切换到正确的数据库
        """
        if max_keys == 0:
            # 无限制模式 - 使用流式加载
            return self._load_keys_streaming(pattern, progress_callback)
        else:
            # 限制模式 - 快速加载指定数量
            keys = []
            for key in self.redis_client.scan_iter(match=pattern, count=1000):
                keys.append(key)
                if progress_callback:
                    progress_callback(len(keys), max_keys)
                if len(keys) >= max_keys:
                    break
            return keys, None
    
    def _load_keys_streaming(self, pattern, progress_callback=None):
        """流式加载键"""
        keys = []
        count = 0
        batch_size = 1000  # 每批处理的键数量
        
        # 获取当前数据库的总键数
        try:
            # 使用DBSIZE命令获取当前数据库的键总数，这比INFO keyspace更准确
            total_keys = self.redis_client.dbsize()
            
            # 如果DBSIZE失败，尝试使用INFO keyspace作为备选方案
            if total_keys is None:
                info = self.redis_client.info('keyspace')
                current_db = self.redis_client.connection_pool.connection_kwargs.get('db', 0)
                db_key = f'db{current_db}'
                total_keys = info.get(db_key, {}).get('keys', None) if db_key in info else None
        except Exception as e:
            print(f"Warning: Failed to get total keys count: {e}")
            total_keys = None
        
        for key in self.redis_client.scan_iter(match=pattern, count=1000):
            keys.append(key)
            count += 1
            
            # 每批次更新进度
            if progress_callback and count % batch_size == 0:
                progress_callback(count, total_keys)
            
            # 超过最大键数时停止加载
            if count >= MAX_KEYS_STREAMING:
                break
        
        # 最终进度更新
        if progress_callback:
            progress_callback(count, total_keys)
        
        return keys, total_keys
    
    def get_server_info(self, current_db=None):
        """获取Redis服务器信息"""
        try:
            info = self.redis_client.info()
            
            # 提取关键信息
            server_info = {
                'redis_version': info.get('redis_version', 'Unknown'),
                'redis_mode': info.get('redis_mode', 'standalone'),
                'os': info.get('os', 'Unknown'),
                'arch_bits': info.get('arch_bits', 'Unknown'),
                'process_id': info.get('process_id', 'Unknown'),
                'tcp_port': info.get('tcp_port', 'Unknown'),
                'uptime_in_seconds': info.get('uptime_in_seconds', 0),
                'uptime_in_days': info.get('uptime_in_days', 0),
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', 'Unknown'),
                'used_memory_peak_human': info.get('used_memory_peak_human', 'Unknown'),
                'total_system_memory_human': info.get('total_system_memory_human', 'Unknown'),
                'maxmemory_human': info.get('maxmemory_human', 'Unknown'),
                'total_commands_processed': info.get('total_commands_processed', 0),
                'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'expired_keys': info.get('expired_keys', 0),
                'evicted_keys': info.get('evicted_keys', 0),
            }
            
            # 计算命中率
            hits = server_info['keyspace_hits']
            misses = server_info['keyspace_misses']
            if hits + misses > 0:
                server_info['hit_rate'] = round((hits / (hits + misses)) * 100, 2)
            else:
                server_info['hit_rate'] = 0
            
            # 获取数据库信息
            keyspace_info = info.get('keyspace', {})
            databases = {}
            for db_key, db_info in keyspace_info.items():
                if db_key.startswith('db'):
                    db_num = db_key[2:]  # 去掉'db'前缀
                    databases[db_num] = {
                        'keys': db_info.get('keys', 0),
                        'expires': db_info.get('expires', 0),
                        'avg_ttl': db_info.get('avg_ttl', 0)
                    }
            
            server_info['databases'] = databases
            
            # 获取当前数据库编号
            if current_db is not None:
                server_info['current_db'] = current_db
            else:
                # 使用连接池的默认值作为后备
                server_info['current_db'] = self.redis_client.connection_pool.connection_kwargs.get('db', 0)
            
            return server_info
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_key_info(self, key):
        """获取键信息"""
        if not self.redis_client.exists(key):
            return None
        
        key_type = self.redis_client.type(key)
        ttl = self.redis_client.ttl(key)
        
        return {
            'type': key_type,
            'ttl': ttl
        }
    
    def get_key_value(self, key, key_type=None):
        """获取键值"""
        if key_type is None:
            key_type = self.redis_client.type(key)
        
        try:
            if key_type == 'string':
                return self.redis_client.get(key)
            elif key_type == 'list':
                return self.redis_client.lrange(key, 0, -1)
            elif key_type == 'set':
                return list(self.redis_client.smembers(key))
            elif key_type == 'hash':
                # 对hash类型使用更安全的读取方式
                hash_len = self.redis_client.hlen(key)
                if hash_len > 1000:  # 大hash分批读取
                    value = {}
                    cursor = 0
                    while True:
                        cursor, fields = self.redis_client.hscan(key, cursor, count=100)
                        value.update(fields)
                        if cursor == 0:
                            break
                    return value
                else:
                    return self.redis_client.hgetall(key)
            elif key_type == 'zset':
                return self.redis_client.zrange(key, 0, -1, withscores=True)
            else:
                return str(self.redis_client.dump(key))
        except Exception as e:
            return f"Error reading value: {str(e)}"
    
    def set_key_value(self, key, value, key_type, preserve_ttl=True):
        """设置键值
        
        Args:
            key: 键名
            value: 值
            key_type: 键类型
            preserve_ttl: 是否保留原有的TTL，默认为True
        """
        # 先获取原有的TTL
        original_ttl = None
        if preserve_ttl:
            original_ttl = self.redis_client.ttl(key)
            # TTL返回-1表示永不过期，-2表示键不存在
            if original_ttl is not None and original_ttl < 0:
                original_ttl = None
        
        if key_type == 'string':
            self.redis_client.set(key, value)
        elif key_type == 'hash':
            # 尝试解析JSON格式的hash数据
            try:
                import json
                hash_data = json.loads(value)
                if isinstance(hash_data, dict):
                    self.redis_client.delete(key)
                    self.redis_client.hset(key, mapping=hash_data)
                else:
                    self.redis_client.set(key, value)
            except json.JSONDecodeError:
                self.redis_client.set(key, value)
        else:
            self.redis_client.set(key, value)
        
        # 恢复原有的TTL
        if original_ttl is not None and original_ttl > 0:
            self.redis_client.expire(key, original_ttl)
    
    def delete_key(self, key):
        """删除键"""
        return self.redis_client.delete(key)
    
    def execute_command(self, command, *args):
        """执行Redis命令"""
        return self.redis_client.execute_command(command, *args)
    
    # Hash操作
    def hash_get(self, key, field):
        """获取hash字段"""
        return self.redis_client.hget(key, field)
    
    def hash_set(self, key, field, value):
        """设置hash字段"""
        return self.redis_client.hset(key, field, value)
    
    def hash_delete(self, key, field):
        """删除hash字段"""
        return self.redis_client.hdel(key, field)
    
    def hash_keys(self, key):
        """获取hash所有字段"""
        return self.redis_client.hkeys(key)
    
    def hash_values(self, key):
        """获取hash所有值"""
        return self.redis_client.hvals(key)
    
    def hash_getall(self, key):
        """获取hash所有字段和值"""
        return self.redis_client.hgetall(key)
    
    # List操作
    def list_push(self, key, value, left=False):
        """向列表添加元素"""
        if left:
            return self.redis_client.lpush(key, value)
        else:
            return self.redis_client.rpush(key, value)
    
    def list_set(self, key, index, value):
        """设置列表指定位置的值"""
        return self.redis_client.lset(key, index, value)
    
    def list_range(self, key, start=0, end=-1):
        """获取列表范围"""
        return self.redis_client.lrange(key, start, end)
    
    def list_length(self, key):
        """获取列表长度"""
        return self.redis_client.llen(key)
    
    def list_remove_by_value(self, key, value, count=1):
        """从列表中删除指定值的元素"""
        return self.redis_client.lrem(key, count, value)
    
    def list_remove_by_index(self, key, index):
        """从列表中删除指定索引的元素"""
        try:
            # 先获取原有的TTL
            original_ttl = self.redis_client.ttl(key)
            if original_ttl is not None and original_ttl < 0:
                original_ttl = None
            
            # 获取当前列表
            current_list = self.redis_client.lrange(key, 0, -1)
            if 0 <= index < len(current_list):
                # 删除指定索引的元素
                current_list.pop(index)
                
                # 重新设置整个列表
                pipe = self.redis_client.pipeline()
                pipe.delete(key)
                if current_list:  # 如果列表不为空，重新添加所有元素
                    pipe.rpush(key, *current_list)
                    # 恢复原有的TTL
                    if original_ttl is not None and original_ttl > 0:
                        pipe.expire(key, original_ttl)
                pipe.execute()
                return True
            return False
        except Exception:
            return False
    
    # Set操作
    def set_add(self, key, *values):
        """向集合添加成员"""
        return self.redis_client.sadd(key, *values)
    
    def set_remove(self, key, *values):
        """从集合删除成员"""
        return self.redis_client.srem(key, *values)
    
    def set_members(self, key):
        """获取集合所有成员"""
        return self.redis_client.smembers(key)
    
    def set_card(self, key):
        """获取集合成员数量"""
        return self.redis_client.scard(key)
    
    # ZSet操作
    def zset_add(self, key, mapping):
        """向有序集合添加成员"""
        return self.redis_client.zadd(key, mapping)
    
    def zset_remove(self, key, *members):
        """从有序集合删除成员"""
        return self.redis_client.zrem(key, *members)
    
    def zset_range(self, key, start=0, end=-1, withscores=False):
        """获取有序集合范围"""
        return self.redis_client.zrange(key, start, end, withscores=withscores)
    
    def zset_card(self, key):
        """获取有序集合成员数量"""
        return self.redis_client.zcard(key)
    
    def zset_score(self, key, member):
        """获取有序集合成员分数"""
        return self.redis_client.zscore(key, member)