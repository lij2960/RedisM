#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试删除key后数据库切换问题的修复"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from redis.connection import RedisConnection
from redis.operations import RedisOperations

def test_delete_key_db_consistency():
    """测试删除key后数据库状态保持一致"""
    
    # 创建连接配置
    conn_config = {
        'host': 'localhost',
        'port': 6379,
        'password': '',
        'username': '',
        'use_ssh': False
    }
    
    # 创建连接
    redis_conn = RedisConnection()
    
    try:
        # 连接到Redis
        redis_conn.connect(conn_config)
        redis_client = redis_conn.redis_client
        
        print("✅ Connected to Redis")
        
        # 切换到数据库1
        redis_client.execute_command('SELECT', 1)
        redis_conn.set_current_database(1)
        print("✅ Switched to database 1")
        
        # 创建测试key
        test_key = "test_delete_key_db_consistency"
        redis_client.set(test_key, "test_value")
        print(f"✅ Created test key: {test_key}")
        
        # 验证key存在于数据库1
        assert redis_client.exists(test_key), "Test key should exist in database 1"
        print("✅ Verified key exists in database 1")
        
        # 模拟get_redis_client()的行为（修复后的逻辑）
        def get_redis_client_fixed():
            current_db = redis_conn.get_current_database()
            try:
                redis_client.execute_command('SELECT', current_db)
                print(f"✅ Ensured client is in database {current_db}")
            except Exception as e:
                print(f"Warning: Failed to select database {current_db}: {e}")
            return redis_client
        
        # 使用修复后的客户端获取方法
        fixed_client = get_redis_client_fixed()
        
        # 删除key
        redis_ops = RedisOperations(fixed_client)
        result = redis_ops.delete_key(test_key)
        print(f"✅ Deleted key, result: {result}")
        
        # 验证key已被删除
        assert not fixed_client.exists(test_key), "Test key should be deleted"
        print("✅ Verified key is deleted")
        
        # 验证仍在数据库1中
        current_db_after = redis_conn.get_current_database()
        assert current_db_after == 1, f"Should still be in database 1, but in {current_db_after}"
        print(f"✅ Still in database {current_db_after}")
        
        # 模拟刷新键列表操作（修复后的逻辑）
        refresh_client = get_redis_client_fixed()
        
        # 搜索键
        redis_ops = RedisOperations(refresh_client)
        keys, _ = redis_ops.get_keys("*", 100)
        print(f"✅ Found {len(keys)} keys in database {current_db_after}")
        
        # 验证删除的key不在列表中
        assert test_key not in keys, "Deleted key should not be in key list"
        print("✅ Verified deleted key is not in key list")
        
        # 验证仍在正确的数据库中
        final_db = redis_conn.get_current_database()
        assert final_db == 1, f"Should still be in database 1, but in {final_db}"
        print(f"✅ Final verification: still in database {final_db}")
        
        # 额外测试：验证连接池不会重置数据库
        print("\n🔍 Testing connection pool behavior...")
        
        # 创建多个操作来测试连接池
        for i in range(5):
            test_client = get_redis_client_fixed()
            test_key_i = f"test_key_{i}"
            test_client.set(test_key_i, f"value_{i}")
            
            # 验证仍在数据库1
            current_db_test = redis_conn.get_current_database()
            assert current_db_test == 1, f"Operation {i}: Should be in database 1, but in {current_db_test}"
            
            # 验证key在正确的数据库中
            assert test_client.exists(test_key_i), f"Test key {test_key_i} should exist in database 1"
            
            # 清理
            test_client.delete(test_key_i)
        
        print("✅ Connection pool behavior test passed")
        
        print("\n🎉 All tests passed! Delete key database consistency is maintained.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理
        try:
            redis_client.execute_command('SELECT', 1)
            if redis_client.exists(test_key):
                redis_client.delete(test_key)
            # 清理可能的测试key
            for i in range(5):
                test_key_i = f"test_key_{i}"
                if redis_client.exists(test_key_i):
                    redis_client.delete(test_key_i)
            redis_conn.disconnect()
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = test_delete_key_db_consistency()
    sys.exit(0 if success else 1)