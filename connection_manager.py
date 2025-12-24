#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import redis
import paramiko
import socket
import threading
import time
import os
import io
from pathlib import Path

class ConnectionManager:
    def __init__(self):
        self.redis_client = None
        self.ssh_client = None
        self.ssh_tunnel = None
        self.keepalive_thread = None
        self.keepalive_running = False
    
    def connect_redis(self, conn_config):
        """连接Redis"""
        if conn_config.get('use_ssh'):
            self.setup_ssh_tunnel(conn_config)
            redis_host = '127.0.0.1'
            redis_port = self.ssh_tunnel.getsockname()[1]
        else:
            redis_host = conn_config['host']
            redis_port = conn_config['port']
        
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
        self.start_keepalive()
    
    def setup_ssh_tunnel(self, ssh_config):
        """设置SSH隧道"""
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        key_path = ssh_config.get('ssh_key', '').strip()
        key_content = ssh_config.get('ssh_key_content', '').strip()
        
        if key_path or key_content:
            passphrase = ssh_config.get('ssh_key_passphrase') or None
            
            if key_content:
                key_file = io.StringIO(key_content)
                key = None
                for key_class in [paramiko.RSAKey, paramiko.DSSKey, paramiko.ECDSAKey, paramiko.Ed25519Key]:
                    try:
                        key_file.seek(0)
                        key = key_class.from_private_key(key_file, password=passphrase)
                        break
                    except:
                        continue
                
                if not key:
                    raise Exception("Invalid private key content")
                
                self.ssh_client.connect(
                    hostname=ssh_config['ssh_host'],
                    port=ssh_config['ssh_port'],
                    username=ssh_config['ssh_user'],
                    pkey=key,
                    timeout=30
                )
            elif key_path:
                if not os.path.exists(key_path):
                    raise Exception(f"Private key file not found: {key_path}")
                
                self.ssh_client.connect(
                    hostname=ssh_config['ssh_host'],
                    port=ssh_config['ssh_port'],
                    username=ssh_config['ssh_user'],
                    key_filename=key_path,
                    passphrase=passphrase,
                    timeout=30
                )
        else:
            self.ssh_client.connect(
                hostname=ssh_config['ssh_host'],
                port=ssh_config['ssh_port'],
                username=ssh_config['ssh_user'],
                password=ssh_config['ssh_password'],
                timeout=30
            )
        
        # 创建隧道
        local_port = self.find_free_port()
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
        time.sleep(0.5)
    
    def find_free_port(self):
        """查找可用端口"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def start_keepalive(self):
        """启动连接保活"""
        self.keepalive_running = True
        
        def keepalive_worker():
            while self.keepalive_running and self.redis_client:
                try:
                    time.sleep(30)
                    if self.redis_client and self.keepalive_running:
                        self.redis_client.ping()
                except Exception:
                    break
        
        self.keepalive_thread = threading.Thread(target=keepalive_worker, daemon=True)
        self.keepalive_thread.start()
    
    def disconnect(self):
        """断开连接"""
        self.keepalive_running = False
        
        if self.redis_client:
            self.redis_client.close()
            self.redis_client = None
        
        if self.ssh_tunnel:
            self.ssh_tunnel.close()
            self.ssh_tunnel = None
            
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None