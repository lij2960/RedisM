#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__version__ = "1.0.1"
__app_name__ = "RedisM"

# Redis命令列表
REDIS_COMMANDS = [
    'GET', 'SET', 'DEL', 'EXISTS', 'KEYS', 'TYPE', 'TTL', 'EXPIRE',
    'HGET', 'HSET', 'HDEL', 'HKEYS', 'HVALS', 'HGETALL', 'HEXISTS',
    'LLEN', 'LPUSH', 'RPUSH', 'LPOP', 'RPOP', 'LRANGE', 'LINDEX',
    'SADD', 'SREM', 'SMEMBERS', 'SCARD', 'SISMEMBER',
    'ZADD', 'ZREM', 'ZRANGE', 'ZCARD', 'ZSCORE',
    'PING', 'INFO', 'SELECT', 'FLUSHDB', 'FLUSHALL', 'DBSIZE',
    'INCR', 'DECR', 'INCRBY', 'DECRBY', 'APPEND', 'STRLEN'
]

# 样式配置
STYLES = {
    'title_font': ('SF Pro Display', 14, 'bold'),
    'heading_font': ('SF Pro Display', 12, 'bold'),
    'normal_font': ('SF Pro Display', 11),
    'mono_font': ('Menlo', 11),
    'connected_color': '#007AFF',
    'bg_color': '#F2F2F7'
}