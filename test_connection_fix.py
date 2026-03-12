#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试连接修复效果的脚本
"""

import sys
import os
import time
import threading

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redis.connection import RedisConnection

def test_connection_timeout():
    """测试连接超时处理"""
    print("Testing connection timeout handling...")
    
    # 创建连接管理器
    conn = RedisConnection()
    
    # 测试配置（使用一个不存在的Redis服务器来模拟超时）
    test_config = {
        'host': '192.168.1.999',  # 不存在的IP
        'port': 6379,
        'password': None,
        'username': None,
        'use_ssh': False
    }
    
    print("Attempting to connect to non-existent Redis server...")
    start_time = time.time()
    
    try:
        conn.connect(test_config)
        print("❌ Connection should have failed")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✅ Connection failed as expected after {elapsed:.2f} seconds")
        print(f"   Error: {e}")
        
        if elapsed < 10:  # 应该在10秒内快速失败
            print("✅ Timeout handling is working correctly")
        else:
            print("❌ Timeout took too long")

def test_async_reconnect():
    """测试异步重连机制"""
    print("\nTesting async reconnect mechanism...")
    
    conn = RedisConnection()
    
    # 模拟连接丢失后的重连
    success_called = threading.Event()
    error_called = threading.Event()
    
    def on_success(result):
        print(f"✅ Async reconnect callback: success={result}")
        success_called.set()
    
    def on_error(error):
        print(f"✅ Async reconnect callback: error={error}")
        error_called.set()
    
    print("Testing async reconnect with invalid config...")
    start_time = time.time()
    
    # 设置无效配置来测试错误处理
    conn.current_conn = {
        'host': '192.168.1.999',
        'port': 6379,
        'password': None,
        'username': None,
        'use_ssh': False
    }
    
    conn.check_and_reconnect_async(on_success, on_error)
    
    # 等待回调（最多40秒）
    if error_called.wait(timeout=40):
        elapsed = time.time() - start_time
        print(f"✅ Async error callback triggered after {elapsed:.2f} seconds")
        if elapsed < 35:
            print("✅ Async timeout handling is working correctly")
        else:
            print("❌ Async timeout took too long")
    else:
        print("❌ Async callback was not triggered within timeout")

if __name__ == "__main__":
    print("Redis Connection Fix Test")
    print("=" * 50)
    
    test_connection_timeout()
    test_async_reconnect()
    
    print("\n" + "=" * 50)
    print("Test completed. The fixes should prevent UI freezing by:")
    print("1. Using short timeouts (2-3 seconds) for connection tests")
    print("2. Running all connection operations in background threads")
    print("3. Providing proper timeout monitoring for async operations")
    print("4. Gracefully handling connection errors without blocking UI")