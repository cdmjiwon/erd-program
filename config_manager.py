import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self, config_file='db_connections.json'):
        self.config_file = config_file
        self.config_dir = Path.home() / '.erd_program'
        self.config_path = self.config_dir / config_file
        
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def save_connection(self, db_type, host, port, database, username, password, service_name=None, connection_name=None):
        if not connection_name:
            connection_name = f"{db_type}_{host}_{database}"
        
        connection = {
            'db_type': db_type,
            'host': host,
            'port': port,
            'database': database,
            'username': username,
            'password': password,
            'service_name': service_name or '',
            'connection_name': connection_name
        }
        
        connections = self.load_all_connections()
        
        existing_index = None
        for idx, conn in enumerate(connections):
            if (conn['db_type'] == db_type and 
                conn['host'] == host and 
                conn['port'] == port and 
                conn['database'] == database and 
                conn['username'] == username):
                existing_index = idx
                break
        
        if existing_index is not None:
            connections[existing_index] = connection
        else:
            connections.append(connection)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(connections, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"설정 저장 오류: {e}")
            return False
    
    def load_all_connections(self):
        if not self.config_path.exists():
            return []
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"설정 불러오기 오류: {e}")
            return []
    
    def delete_connection(self, db_type, host, port, database, username):
        connections = self.load_all_connections()
        connections = [
            conn for conn in connections
            if not (conn['db_type'] == db_type and 
                   conn['host'] == host and 
                   conn['port'] == port and 
                   conn['database'] == database and 
                   conn['username'] == username)
        ]
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(connections, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"설정 삭제 오류: {e}")
            return False

