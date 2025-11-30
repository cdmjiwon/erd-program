from graphviz import Digraph
import os
import sys
import shutil
from pathlib import Path


class ERDiagramGenerator:
    def __init__(self):
        self.graph = None
        self._setup_graphviz_path()
    
    def _setup_graphviz_path(self):
        graphviz_paths = []
        
        if sys.platform == 'win32':
            common_paths = [
                r'C:\Program Files\Graphviz\bin',
                r'C:\Program Files (x86)\Graphviz\bin',
                os.path.expanduser(r'~\AppData\Local\Programs\Graphviz\bin'),
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    graphviz_paths.append(path)
            
            path_env = os.environ.get('PATH', '')
            for path in path_env.split(os.pathsep):
                if 'graphviz' in path.lower() and os.path.exists(path):
                    graphviz_paths.append(path)
        
        dot_path = shutil.which('dot')
        if dot_path:
            dot_dir = os.path.dirname(dot_path)
            if dot_dir not in graphviz_paths:
                graphviz_paths.insert(0, dot_dir)
        
        if graphviz_paths:
            os.environ['PATH'] = os.pathsep.join(graphviz_paths) + os.pathsep + os.environ.get('PATH', '')
    
    def generate(self, tables_info, output_path='er_diagram'):
        try:
            import subprocess
            import sys
            
            dot_path = shutil.which('dot')
            if not dot_path:
                raise Exception("Graphviz 'dot' 실행 파일을 찾을 수 없습니다.")
            
            try:
                test_result = subprocess.run(
                    [dot_path, '-V'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
            except subprocess.TimeoutExpired:
                raise Exception("Graphviz 'dot' 실행이 타임아웃되었습니다. Graphviz 설치에 문제가 있을 수 있습니다.")
            except Exception as test_error:
                raise Exception(f"Graphviz 'dot' 실행 테스트 실패: {str(test_error)}")
            
            if test_result.returncode != 0:
                raise Exception(f"Graphviz 'dot' 실행 테스트 실패: {test_result.stderr}")
            
            self.graph = Digraph(comment='ER Diagram', format='png')
            self.graph.attr(rankdir='LR')
            self.graph.attr('node', shape='record', style='rounded')
            
            for table_name, table_info in tables_info.items():
                self._add_table_node(table_name, table_info)
            
            for table_name, table_info in tables_info.items():
                self._add_relationships(table_name, table_info, tables_info)
            
            try:
                result_path = self.graph.render(output_path, cleanup=True)
                if result_path and os.path.exists(result_path):
                    return result_path
                else:
                    expected_path = f"{output_path}.png"
                    if os.path.exists(expected_path):
                        return expected_path
                    raise Exception("Graphviz 렌더링 결과 파일을 찾을 수 없습니다.")
            except Exception as render_error:
                error_msg = str(render_error)
                if 'NoneType' in error_msg or 'write' in error_msg.lower() or 'timeout' in error_msg.lower():
                    raise Exception(f"Graphviz 실행 중 오류 발생. Graphviz 설치를 확인하세요: {error_msg}")
                raise
                
        except Exception as e:
            error_msg = str(e)
            if 'dot' in error_msg.lower() or 'graphviz' in error_msg.lower() or 'failed to execute' in error_msg.lower() or 'NoneType' in error_msg or 'timeout' in error_msg.lower():
                raise Exception(f"Graphviz 실행 실패: {error_msg}")
            raise
    
    def _add_table_node(self, table_name, table_info):
        label_parts = [f"<{table_name}> {table_name}"]
        
        for col in table_info['columns']:
            col_name = col['name']
            col_type = str(col['type'])
            
            pk_marker = " [PK]" if col_name in table_info['primary_keys'] else ""
            nullable = "" if col.get('nullable', True) else " [NOT NULL]"
            
            label_parts.append(f"{col_name}: {col_type}{pk_marker}{nullable}")
        
        label = "|".join(label_parts)
        self.graph.node(table_name, label=label)
    
    def _add_relationships(self, table_name, table_info, all_tables_info):
        for fk in table_info['foreign_keys']:
            ref_table = fk['referred_table']
            if ref_table in all_tables_info:
                from_cols = ", ".join(fk['constrained_columns'])
                to_cols = ", ".join(fk['referred_columns'])
                
                self.graph.edge(
                    table_name,
                    ref_table,
                    label=f"{from_cols} -> {to_cols}"
                )

