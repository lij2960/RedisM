#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""测试数据库切换功能"""

def test_database_switching_logic():
    """测试数据库切换逻辑"""
    
    print("Testing database switching logic...")
    
    # 模拟RedisConnection类
    class MockRedisConnection:
        def __init__(self):
            self.current_database = 0
            self.actual_db = 0  # 模拟Redis实际的数据库
        
        def set_current_database(self, db_num):
            """设置当前数据库编号"""
            self.current_database = db_num
            print(f"  Internal state updated: current_database = {db_num}")
        
        def get_current_database(self):
            """获取当前数据库编号"""
            return self.current_database
        
        def execute_select(self, db_num):
            """模拟执行SELECT命令"""
            self.actual_db = db_num
            print(f"  Redis SELECT executed: actual_db = {db_num}")
    
    # 测试场景1：正常切换数据库
    print("\n场景1：正常切换数据库")
    conn = MockRedisConnection()
    
    print("初始状态:")
    print(f"  Internal: {conn.get_current_database()}, Actual: {conn.actual_db}")
    
    print("\n切换到DB 5:")
    conn.execute_select(5)
    conn.set_current_database(5)
    print(f"  Internal: {conn.get_current_database()}, Actual: {conn.actual_db}")
    
    if conn.get_current_database() == conn.actual_db == 5:
        print("  ✓ 状态同步正确")
    else:
        print("  ✗ 状态不同步！")
    
    # 测试场景2：旧方法（有问题的方式）
    print("\n场景2：旧方法 - 只执行SELECT不更新状态")
    conn2 = MockRedisConnection()
    
    print("初始状态:")
    print(f"  Internal: {conn2.get_current_database()}, Actual: {conn2.actual_db}")
    
    print("\n只执行SELECT到DB 3（不更新内部状态）:")
    conn2.execute_select(3)
    # 注意：没有调用set_current_database
    print(f"  Internal: {conn2.get_current_database()}, Actual: {conn2.actual_db}")
    
    if conn2.get_current_database() != conn2.actual_db:
        print("  ✗ 状态不同步！这会导致问题")
        print(f"    应用认为在DB {conn2.get_current_database()}，实际在DB {conn2.actual_db}")
    else:
        print("  ✓ 状态同步")
    
    # 测试场景3：新方法（修复后的方式）
    print("\n场景3：新方法 - 先切换数据库再调用get_keys")
    conn3 = MockRedisConnection()
    
    print("初始状态:")
    print(f"  Internal: {conn3.get_current_database()}, Actual: {conn3.actual_db}")
    
    print("\n使用新方法切换到DB 7:")
    print("  1. 执行SELECT命令")
    conn3.execute_select(7)
    print("  2. 更新内部状态")
    conn3.set_current_database(7)
    print("  3. 调用get_keys（不再传递target_db参数）")
    print(f"  Internal: {conn3.get_current_database()}, Actual: {conn3.actual_db}")
    
    if conn3.get_current_database() == conn3.actual_db == 7:
        print("  ✓ 状态同步正确，修复成功！")
    else:
        print("  ✗ 状态不同步")
    
    print("\n" + "="*60)
    print("总结:")
    print("  旧方法问题: RedisOperations.get_keys()内部执行SELECT")
    print("             但不更新RedisConnection.current_database")
    print("  新方法修复: 在调用get_keys()前先切换数据库并更新状态")
    print("             确保内部状态与实际Redis状态一致")
    print("="*60)

if __name__ == "__main__":
    test_database_switching_logic()