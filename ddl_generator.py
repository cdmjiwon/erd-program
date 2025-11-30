from db_connector import DatabaseConnector


class DDLGenerator:
    def __init__(self, db_connector):
        self.db = db_connector
    
    def generate_ddl(self, tables_info):
        ddl_statements = []
        
        for table_name, table_info in tables_info.items():
            ddl = self._generate_table_ddl(table_name, table_info)
            ddl_statements.append(ddl)
        
        return "\n\n".join(ddl_statements)
    
    def _generate_table_ddl(self, table_name, table_info):
        lines = [f"CREATE TABLE {table_name} ("]
        
        column_defs = []
        for col in table_info['columns']:
            col_def = self._generate_column_def(col, table_info['primary_keys'])
            column_defs.append(f"    {col_def}")
        
        lines.extend(column_defs)
        
        if table_info['primary_keys']:
            pk_cols = ", ".join(table_info['primary_keys'])
            lines.append(f"    PRIMARY KEY ({pk_cols})")
        
        lines.append(");")
        
        for fk in table_info['foreign_keys']:
            fk_def = self._generate_foreign_key_def(table_name, fk)
            lines.append(fk_def)
        
        return "\n".join(lines)
    
    def _generate_column_def(self, col, primary_keys):
        col_name = col['name']
        col_type = str(col['type'])
        
        nullable = "" if col.get('nullable', True) else " NOT NULL"
        
        default = ""
        if col.get('default') is not None:
            default_val = col['default']
            if isinstance(default_val, str):
                default = f" DEFAULT '{default_val}'"
            else:
                default = f" DEFAULT {default_val}"
        
        return f"{col_name} {col_type}{nullable}{default}"
    
    def _generate_foreign_key_def(self, table_name, fk):
        fk_name = fk.get('name', f"fk_{table_name}_{fk['referred_table']}")
        from_cols = ", ".join(fk['constrained_columns'])
        ref_table = fk['referred_table']
        to_cols = ", ".join(fk['referred_columns'])
        
        return f"ALTER TABLE {table_name} ADD CONSTRAINT {fk_name} FOREIGN KEY ({from_cols}) REFERENCES {ref_table}({to_cols});"

