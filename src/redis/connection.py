#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Redis连接管理"""

import redis
import paramiko
import socket
import threading
import time
import io
import select
from paramiko import RSAKey, ECDSAKey, Ed25519Key

# 注意：DSSKey在新版本paramiko中已被移除，因为DSS算法已被弃用

from ..utils.helpers import find_free_port


class RedisConnection:
    """Redis连接管理器"""
    
    def __init__(self):
        self.redis_client = None
        self.ssh_client = None
        self.ssh_tunnel = None
        self.keepalive_thread = None
        self.keepalive_running = False
        self.current_conn = None
        
    def connect(self, conn_config):
        """连接到Redis"""
        self.current_conn = conn_config
        
        # 先断开现有连接
        self.disconnect()
        
        if conn_config.get('use_ssh'):
            # SSH隧道连接
            self._setup_ssh_tunnel(conn_config)
            redis_host = '127.0.0.1'
            redis_port = self.ssh_tunnel.getsockname()[1]
        else:
            # 直接连接
            redis_host = conn_config['host']
            redis_port = conn_config['port']
        
        # 连接Redis
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=conn_config.get('password') or None,
            username=conn_config.get('username') or None,
            db=0,
            decode_responses=True
        )
        
        # 测试连接
        self.redis_client.ping()
        
        # 启动保活
        self._start_keepalive()
        
        return True
    
    def disconnect(self):
        """断开连接"""
        # 停止保活线程
        self._stop_keepalive()
        
        # 关闭Redis连接
        if self.redis_client:
            try:
                self.redis_client.close()
            except:
                pass
            self.redis_client = None
        
        # 关闭SSH隧道
        if self.ssh_tunnel:
            try:
                self.ssh_tunnel.close()
            except:
                pass
            self.ssh_tunnel = None
            
        # 关闭SSH客户端
        if self.ssh_client:
            try:
                self.ssh_client.close()
            except:
                pass
            self.ssh_client = None
    
    def is_connected(self):
        """检查是否已连接"""
        return self.redis_client is not None
    
    def check_and_reconnect(self):
        """检查连接状态，如果断开则尝试自动重连"""
        try:
            if not self.redis_client:
                return False
            
            # 尝试ping测试连接
            self.redis_client.ping()
            return True
            
        except Exception as ping_error:
            print(f"Connection lost: {ping_error}")
            # 连接断开，尝试重连
            if self.current_conn:
                try:
                    print("Attempting to reconnect...")
                    self.connect(self.current_conn)
                    print("Reconnection successful")
                    return True
                except Exception as reconnect_error:
                    print(f"Reconnection failed: {reconnect_error}")
                    return False
            return False
    
    def test_connection(self, conn_config):
        """测试连接配置"""
        test_ssh_client = None
        test_redis_client = None
        
        try:
            if conn_config.get('use_ssh'):
                # 测试SSH连接
                test_ssh_client = paramiko.SSHClient()
                test_ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                try:
                    # SSH认证测试
                    self._ssh_authenticate(test_ssh_client, conn_config)
                    
                    # 简单测试SSH连接是否成功
                    transport = test_ssh_client.get_transport()
                    if not transport or not transport.is_active():
                        raise Exception("SSH connection failed")
                    
                    # 测试端口转发能力
                    try:
                        # 尝试创建一个简单的端口转发测试
                        channel = transport.open_channel(
                            'direct-tcpip',
                            (conn_config['host'], conn_config['port']),
                            ('127.0.0.1', 0)
                        )
                        
                        if channel:
                            channel.close()
                            return {
                                'success': True,
                                'version': 'SSH Connection Successful',
                                'info': {'redis_version': 'SSH Tunnel Test Passed'}
                            }
                        else:
                            raise Exception("Cannot create SSH tunnel to Redis server")
                            
                    except Exception as tunnel_error:
                        raise Exception(f"SSH tunnel test failed: {str(tunnel_error)}")
                        
                except Exception as ssh_error:
                    error_msg = str(ssh_error).lower()
                    if "authentication" in error_msg or "auth" in error_msg:
                        raise Exception("SSH authentication failed. Please check your username, password, or private key.")
                    elif "connection" in error_msg or "refused" in error_msg:
                        raise Exception("Cannot connect to SSH server. Please check the SSH host and port.")
                    elif "key" in error_msg or "invalid" in error_msg:
                        raise Exception("Invalid private key or passphrase. Please check your key format.")
                    elif "timeout" in error_msg:
                        raise Exception("SSH connection timeout. Please check network connectivity.")
                    else:
                        raise Exception(f"SSH connection failed: {str(ssh_error)}")
                
            else:
                # 直接连接测试
                redis_host = conn_config['host']
                redis_port = conn_config['port']
                
                # 测试Redis连接
                test_redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=conn_config.get('password') or None,
                    username=conn_config.get('username') or None,
                    db=0,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                
                # 执行PING测试
                test_redis_client.ping()
                
                # 获取Redis信息
                info = test_redis_client.info()
                redis_version = info.get('redis_version', 'Unknown')
                
                return {
                    'success': True,
                    'version': redis_version,
                    'info': info
                }
            
        except Exception as e:
            # 重新抛出异常，保持原始错误信息
            raise e
            
        finally:
            # 清理测试资源
            if test_redis_client:
                try:
                    test_redis_client.close()
                except:
                    pass
                    
            if test_ssh_client:
                try:
                    test_ssh_client.close()
                except:
                    pass
    
    def _setup_ssh_tunnel(self, ssh_config):
        """设置SSH隧道"""
        # 创建SSH客户端
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # SSH认证
        self._ssh_authenticate(self.ssh_client, ssh_config)
        
        # 创建隧道
        local_port = find_free_port()
        self.ssh_tunnel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssh_tunnel.bind(('127.0.0.1', local_port))
        self.ssh_tunnel.listen(1)
        
        def tunnel_handler():
            while True:
                try:
                    client_socket, addr = self.ssh_tunnel.accept()
                    transport = self.ssh_client.get_transport()
                    dest_addr = (ssh_config['host'], ssh_config['port'])
                    channel = transport.open_channel('direct-tcpip', dest_addr, addr)
                    
                    def forward_data(src, dst):
                        try:
                            while True:
                                data = src.recv(1024)
                                if not data:
                                    break
                                dst.send(data)
                        except:
                            pass
                        finally:
                            src.close()
                            dst.close()
                    
                    threading.Thread(target=forward_data, args=(client_socket, channel), daemon=True).start()
                    threading.Thread(target=forward_data, args=(channel, client_socket), daemon=True).start()
                    
                except:
                    break
        
        threading.Thread(target=tunnel_handler, daemon=True).start()
        time.sleep(0.5)  # 等待隧道建立
    
    def _ssh_authenticate(self, ssh_client, ssh_config):
        """SSH认证"""
        key_path = ssh_config.get('ssh_key', '').strip()
        key_content = ssh_config.get('ssh_key_content', '').strip()
        
        try:
            if key_path or key_content:
                # 私钥认证
                passphrase = ssh_config.get('ssh_key_passphrase') or None
                
                if key_content:
                    # 使用私钥内容
                    key_file = io.StringIO(key_content)
                    key = None
                    
                    # 尝试不同的私钥格式
                    for key_class in [RSAKey, ECDSAKey, Ed25519Key]:
                        try:
                            key_file.seek(0)
                            key = key_class.from_private_key(key_file, password=passphrase)
                            break
                        except Exception as key_error:
                            # 记录但继续尝试其他格式
                            continue
                    
                    if not key:
                        raise Exception("Invalid private key content or unsupported key format")
                    
                    # 连接SSH服务器
                    ssh_client.connect(
                        hostname=ssh_config['ssh_host'],
                        port=ssh_config['ssh_port'],
                        username=ssh_config['ssh_user'],
                        pkey=key,
                        timeout=10,
                        allow_agent=False,
                        look_for_keys=False
                    )
                    
                elif key_path:
                    # 使用私钥文件
                    ssh_client.connect(
                        hostname=ssh_config['ssh_host'],
                        port=ssh_config['ssh_port'],
                        username=ssh_config['ssh_user'],
                        key_filename=key_path,
                        passphrase=passphrase,
                        timeout=10,
                        allow_agent=False,
                        look_for_keys=False
                    )
            else:
                # 密码认证
                ssh_client.connect(
                    hostname=ssh_config['ssh_host'],
                    port=ssh_config['ssh_port'],
                    username=ssh_config['ssh_user'],
                    password=ssh_config['ssh_password'],
                    timeout=10,
                    allow_agent=False,
                    look_for_keys=False
                )
                
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg:
                raise Exception("SSH authentication failed")
            elif "connection" in error_msg or "refused" in error_msg:
                raise Exception("SSH connection refused")
            elif "timeout" in error_msg:
                raise Exception("SSH connection timeout")
            elif "key" in error_msg or "invalid" in error_msg:
                raise Exception("Invalid private key or passphrase")
            else:
                raise Exception(f"SSH connection error: {str(e)}")
    
    def _start_keepalive(self):
        """启动Redis连接保活"""
        self.keepalive_running = True
        
        def keepalive_worker():
            while self.keepalive_running and self.redis_client:
                try:
                    time.sleep(30)  # 每30秒ping一次
                    if self.redis_client and self.keepalive_running:
                        self.redis_client.ping()
                except Exception:
                    break
        
        self.keepalive_thread = threading.Thread(target=keepalive_worker, daemon=True)
        self.keepalive_thread.start()
    
    def get_database_client(self, db_num):
        """获取指定数据库的Redis客户端"""
        if not self.redis_client or not self.current_conn:
            return None
        
        try:
            # 获取当前连接的参数
            connection_kwargs = self.redis_client.connection_pool.connection_kwargs.copy()
            
            # 创建一个新的客户端，指定数据库
            db_client = redis.Redis(
                host=connection_kwargs.get('host'),
                port=connection_kwargs.get('port'),
                password=connection_kwargs.get('password'),
                username=connection_kwargs.get('username'),
                db=db_num,
                decode_responses=True
            )
            
            # 测试连接
            db_client.ping()
            return db_client
            
        except Exception as e:
            print(f"Error creating database client for db {db_num}: {e}")
            return None
    def get_database_client(self, db_num):
        """获取指定数据库的Redis客户端"""
        if not self.redis_client or not self.current_conn:
            return None
        
        try:
            # 获取当前连接的参数
            connection_kwargs = self.redis_client.connection_pool.connection_kwargs.copy()
            
            # 创建一个新的客户端，指定数据库
            db_client = redis.Redis(
                host=connection_kwargs.get('host'),
                port=connection_kwargs.get('port'),
                password=connection_kwargs.get('password'),
                username=connection_kwargs.get('username'),
                db=db_num,
                decode_responses=True
            )
            
            # 测试连接
            db_client.ping()
            return db_client
            
        except Exception as e:
            print(f"Error creating database client for db {db_num}: {e}")
            return None
    
    def _stop_keepalive(self):
        """停止Redis连接保活"""
        self.keepalive_running = False