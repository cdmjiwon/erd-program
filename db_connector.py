try:
    from sqlalchemy import create_engine, inspect, MetaData, text
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    import sys
    print("SQLAlchemy 모듈을 찾을 수 없습니다.")
    print("설치 방법: pip install sqlalchemy")
    sys.exit(1)
import sqlite3


class DatabaseConnector:
    def __init__(self):
        self.engine = None
        self.connection = None
        self.inspector = None
        
    def connect(self, db_type, host=None, port=None, database=None, 
                username=None, password=None, file_path=None, service_name=None):
        try:
            if db_type == 'MySQL' or db_type == 'MariaDB':
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
                self.engine = create_engine(connection_string)
                
            elif db_type == 'PostgreSQL':
                connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
                self.engine = create_engine(connection_string)
                
            elif db_type == 'Oracle':
                if service_name:
                    dsn = f"{host}:{port}/{service_name}"
                else:
                    dsn = f"{host}:{port}/{database}"
                connection_string = f"oracle+oracledb://{username}:{password}@{dsn}"
                self.engine = create_engine(connection_string)
                
            elif db_type == 'SQLite':
                connection_string = f"sqlite:///{file_path}"
                self.engine = create_engine(connection_string)
                
            else:
                raise ValueError(f"지원하지 않는 DB 타입: {db_type}")
            
            self.connection = self.engine.connect()
            self.inspector = inspect(self.engine)
            return True
            
        except SQLAlchemyError as e:
            print(f"DB 연결 오류: {e}")
            return False
    
    def get_tables(self):
        if not self.inspector:
            return []
        return self.inspector.get_table_names()
    
    def get_table_columns(self, table_name):
        if not self.inspector:
            return []
        return self.inspector.get_columns(table_name)
    
    def get_foreign_keys(self, table_name):
        if not self.inspector:
            return []
        return self.inspector.get_foreign_keys(table_name)
    
    def get_primary_keys(self, table_name):
        if not self.inspector:
            return []
        pk_constraint = self.inspector.get_pk_constraint(table_name)
        return pk_constraint.get('constrained_columns', [])
    
    def get_indexes(self, table_name):
        if not self.inspector:
            return []
        return self.inspector.get_indexes(table_name)
    
    def get_databases(self, db_type):
        try:
            if db_type == 'MySQL' or db_type == 'MariaDB':
                if not self.connection:
                    return []
                result = self.connection.execute(text("SHOW DATABASES"))
                return [row[0] for row in result if row[0] not in ['information_schema', 'performance_schema', 'mysql', 'sys']]
            
            elif db_type == 'PostgreSQL':
                if not self.connection:
                    return []
                result = self.connection.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false"))
                return [row[0] for row in result]
            
            elif db_type == 'Oracle':
                if not self.connection:
                    return []
                result = self.connection.execute(text("SELECT username FROM all_users ORDER BY username"))
                return [row[0] for row in result]
            
            return []
        except Exception as e:
            print(f"데이터베이스 목록 조회 오류: {e}")
            return []
    
    def connect_without_database(self, db_type, host=None, port=None, 
                                  username=None, password=None, service_name=None):
        try:
            if db_type == 'MySQL' or db_type == 'MariaDB':
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/"
                self.engine = create_engine(connection_string)
                
            elif db_type == 'PostgreSQL':
                connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/postgres"
                self.engine = create_engine(connection_string)
                
            elif db_type == 'Oracle':
                if service_name:
                    dsn = f"{host}:{port}/{service_name}"
                else:
                    dsn = f"{host}:{port}/"
                connection_string = f"oracle+oracledb://{username}:{password}@{dsn}"
                self.engine = create_engine(connection_string)
                
            else:
                return False
            
            self.connection = self.engine.connect()
            return True
            
        except SQLAlchemyError as e:
            print(f"DB 연결 오류: {e}")
            return False
    
    def close(self):
        if self.connection:
            self.connection.close()
        if self.engine:
            self.engine.dispose()

