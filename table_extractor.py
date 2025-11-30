from db_connector import DatabaseConnector


class TableExtractor:
    def __init__(self, db_connector):
        self.db = db_connector
    
    def extract_all_tables_info(self):
        tables_info = {}
        tables = self.db.get_tables()
        
        for table_name in tables:
            tables_info[table_name] = self.extract_table_info(table_name)
        
        return tables_info
    
    def extract_table_info(self, table_name):
        columns = self.db.get_table_columns(table_name)
        foreign_keys = self.db.get_foreign_keys(table_name)
        primary_keys = self.db.get_primary_keys(table_name)
        indexes = self.db.get_indexes(table_name)
        
        return {
            'columns': columns,
            'foreign_keys': foreign_keys,
            'primary_keys': primary_keys,
            'indexes': indexes
        }

