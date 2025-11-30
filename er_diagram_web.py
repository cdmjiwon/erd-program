import os
import json
import tempfile
import webbrowser
from pathlib import Path
import http.server
import socketserver
import threading
import time
import math


class ERDiagramWebEditor:
    def __init__(self, tables_info, logger=None):
        self.tables_info = tables_info
        self.logger = logger
        self.port = 8765
        self.server_thread = None
        self.httpd = None
        
    def build_graph(self):
        graph = {}
        degrees = {}
        
        for table_name in self.tables_info.keys():
            graph[table_name] = set()
            degrees[table_name] = 0
        
        for table_name, table_info in self.tables_info.items():
            for fk in table_info['foreign_keys']:
                ref_table = fk['referred_table']
                if ref_table in self.tables_info:
                    graph[table_name].add(ref_table)
                    graph[ref_table].add(table_name)
                    degrees[table_name] += 1
                    degrees[ref_table] += 1
        
        return graph, degrees
    
    def find_connected_groups(self):
        graph, degrees = self.build_graph()
        
        visited = set()
        groups = []
        isolated = []
        
        def dfs(node, group):
            if node in visited:
                return
            visited.add(node)
            group.add(node)
            for neighbor in graph[node]:
                dfs(neighbor, group)
        
        for table_name in self.tables_info.keys():
            if table_name not in visited:
                group = set()
                dfs(table_name, group)
                if len(group) > 1:
                    groups.append(group)
                else:
                    isolated.append(table_name)
        
        return groups, isolated, graph, degrees
    
    def find_center_node(self, group, graph, degrees):
        if len(group) == 1:
            return list(group)[0]
        
        max_degree = -1
        center = None
        for node in group:
            if degrees[node] > max_degree:
                max_degree = degrees[node]
                center = node
        
        return center
    
    def layout_by_layers(self, center, group, graph, table_sizes):
        layers = {}
        layers[0] = [center]
        visited = {center}
        
        current_layer = 0
        while len(visited) < len(group):
            next_layer = []
            for node in layers[current_layer]:
                for neighbor in graph[node]:
                    if neighbor in group and neighbor not in visited:
                        next_layer.append(neighbor)
                        visited.add(neighbor)
            
            if next_layer:
                current_layer += 1
                layers[current_layer] = next_layer
            else:
                break
        
        return layers
    
    def is_parent_table(self, table_name, graph):
        """테이블이 다른 테이블의 부모(참조 대상)인지 확인"""
        for other_table, table_info in self.tables_info.items():
            if other_table == table_name:
                continue
            for fk in table_info.get('foreign_keys', []):
                if fk['referred_table'] == table_name:
                    return True
        return False
    
    def calculate_table_size(self, table_info):
        max_col_name_len = max([len(col['name']) for col in table_info['columns']], default=0)
        max_type_len = max([len(str(col['type']).split('(')[0].split('[')[0]) for col in table_info['columns']], default=0)
        
        table_name_len = len(table_info.get('name', ''))
        num_cols = len(table_info['columns'])
        
        # 더 정확한 크기 계산
        content_width = max(max_col_name_len + max_type_len + 50, table_name_len + 20)
        width = max(350, content_width * 7.5)
        
        # PK, FK, 일반 컬럼 섹션 고려
        pk_count = len([c for c in table_info.get('primary_keys', [])])
        fk_count = len([fk for fk in table_info.get('foreign_keys', [])])
        other_count = num_cols - pk_count - fk_count
        
        # 섹션 구분선과 헤더 고려
        section_headers = 0
        if pk_count > 0:
            section_headers += 1
        if fk_count > 0:
            section_headers += 1
        if other_count > 0:
            section_headers += 1
        
        height = 50 + (num_cols * 22) + (section_headers * 25) + 20
        
        return width, height
    
    def convert_to_visjs_format(self):
        nodes = []
        edges = []
        
        groups, isolated, graph, degrees = self.find_connected_groups()
        
        table_sizes = {}
        for table_name, table_info in self.tables_info.items():
            table_sizes[table_name] = self.calculate_table_size(table_info)
        
        x_start = 600
        y_start = 600
        group_spacing_x = 3000
        group_spacing_y = 3000
        isolated_spacing_x = 500
        isolated_spacing_y = 450
        
        initial_positions = {}
        
        group_idx = 0
        for group in groups:
            center = self.find_center_node(group, graph, degrees)
            layers = self.layout_by_layers(center, group, graph, table_sizes)
            
            group_x = x_start + (group_idx % 2) * group_spacing_x
            group_y = y_start + (group_idx // 2) * group_spacing_y
            
            center_width, center_height = table_sizes[center]
            center_x = group_x
            center_y = group_y
            
            for table_name in group:
                table_info = self.tables_info[table_name]
                width, height = table_sizes[table_name]
                
                if table_name == center:
                    x = center_x
                    y = center_y
                else:
                    layer = None
                    for l, nodes_in_layer in layers.items():
                        if table_name in nodes_in_layer:
                            layer = l
                            break
                    
                    if layer is None:
                        x = center_x
                        y = center_y
                    else:
                        layer_nodes = layers[layer]
                        node_idx = layer_nodes.index(table_name)
                        num_in_layer = len(layer_nodes)
                        
                        if layer == 1:
                            # 각 노드의 실제 크기 계산
                            node_width, node_height = table_sizes[table_name]
                            center_size = max(center_width, center_height)
                            node_size = max(node_width, node_height)
                            
                            # 충분한 간격 확보 (최소 100px 여유)
                            radius = center_size / 2 + node_size / 2 + 350
                            
                            is_parent = self.is_parent_table(table_name, graph)
                            
                            # 부모는 위쪽, 자식은 아래쪽 배치
                            if is_parent:
                                y = center_y - radius
                                # 위쪽에 여러 개일 때 원형 배치
                                if num_in_layer > 1:
                                    angle_step = 2 * math.pi / num_in_layer
                                    angle = node_idx * angle_step - math.pi / 2
                                    x = center_x + radius * 0.9 * math.cos(angle)
                                else:
                                    x = center_x
                            else:
                                y = center_y + radius
                                # 아래쪽에 여러 개일 때 원형 배치
                                if num_in_layer > 1:
                                    angle_step = 2 * math.pi / num_in_layer
                                    angle = node_idx * angle_step + math.pi / 2
                                    x = center_x + radius * 0.9 * math.cos(angle)
                                else:
                                    x = center_x
                        else:
                            prev_layer_nodes = layers[layer - 1]
                            parent_node = None
                            for prev_node in prev_layer_nodes:
                                if table_name in graph[prev_node]:
                                    parent_node = prev_node
                                    break
                            
                            if parent_node:
                                parent_pos = initial_positions.get(parent_node, {'x': center_x, 'y': center_y})
                                parent_width, parent_height = table_sizes[parent_node]
                                parent_size = max(parent_width, parent_height)
                                node_size = max(width, height)
                                
                                # 충분한 간격 확보
                                radius = parent_size / 2 + node_size / 2 + 300
                                
                                siblings = [n for n in layer_nodes if n != table_name and n in graph.get(parent_node, set())]
                                
                                # 부모의 위치에 따라 배치 방향 결정
                                parent_angle = math.atan2(parent_pos['y'] - center_y, parent_pos['x'] - center_x)
                                
                                if len(siblings) == 0:
                                    # 부모 아래쪽에 배치
                                    angle_offset = math.pi / 2
                                else:
                                    # 형제들과 함께 원형 배치
                                    angle_step = 2 * math.pi / (len(siblings) + 1)
                                    sibling_pos = siblings.index(table_name) if table_name in siblings else node_idx
                                    angle_offset = (sibling_pos + 1) * angle_step
                                
                                angle = parent_angle + angle_offset
                                
                                x = parent_pos['x'] + radius * math.cos(angle)
                                y = parent_pos['y'] + radius * math.sin(angle)
                            else:
                                radius = max(center_width, center_height) / 2 + max(width, height) / 2 + 250 * layer
                                angle_step = 2 * math.pi / num_in_layer if num_in_layer > 0 else 0
                                angle = node_idx * angle_step - math.pi / 2
                                x = center_x + radius * math.cos(angle)
                                y = center_y + radius * math.sin(angle)
                
                pk_columns = []
                fk_columns = []
                other_columns = []
                
                for col_info in table_info['columns']:
                    col_name = col_info['name']
                    col_type = str(col_info['type']).split('(')[0].split('[')[0]
                    nullable = col_info.get('nullable', True)
                    
                    is_pk = col_name in table_info['primary_keys']
                    is_fk = any(col_name in fk['constrained_columns'] for fk in table_info.get('foreign_keys', []))
                    
                    col_display = f"{col_name}: {col_type}"
                    if not nullable:
                        col_display += " *"
                    
                    if is_pk:
                        pk_columns.append(col_display)
                    elif is_fk:
                        fk_columns.append(col_display)
                    else:
                        other_columns.append(col_display)
                
                label_parts = [f"<b>{table_name}</b>"]
                
                if pk_columns:
                    label_parts.append("<hr style='margin:2px 0; border:0; border-top:1px solid #333;'>")
                    label_parts.append("<b style='color:#d32f2f;'>PK</b>")
                    label_parts.extend(pk_columns)
                
                if fk_columns:
                    label_parts.append("<hr style='margin:2px 0; border:0; border-top:1px solid #666;'>")
                    label_parts.append("<b style='color:#1976d2;'>FK</b>")
                    label_parts.extend(fk_columns)
                
                if other_columns:
                    if pk_columns or fk_columns:
                        label_parts.append("<hr style='margin:2px 0; border:0; border-top:1px solid #999;'>")
                    label_parts.extend(other_columns)
                
                label = "<br>".join(label_parts)
                
                node_color = {
                    'background': '#fff3e0' if table_name == center else '#e3f2fd',
                    'border': '#f57c00' if table_name == center else '#1976d2',
                    'highlight': {
                        'background': '#ffe0b2' if table_name == center else '#bbdefb',
                        'border': '#e65100' if table_name == center else '#0d47a1'
                    }
                }
                
                node = {
                    'id': table_name,
                    'label': label,
                    'x': x,
                    'y': y,
                    'shape': 'box',
                    'color': {
                        'background': '#ffffff',
                        'border': '#2c3e50',
                        'highlight': {
                            'background': '#ecf0f1',
                            'border': '#34495e'
                        }
                    },
                    'font': {
                        'face': 'Arial',
                        'size': 9,
                        'multi': 'html',
                        'align': 'left'
                    },
                    'widthConstraint': {
                        'maximum': width
                    },
                    'borderWidth': 2,
                    'borderWidthSelected': 3
                }
                nodes.append(node)
                initial_positions[table_name] = {'x': x, 'y': y}
            
            group_idx += 1
        
        isolated_start_x = x_start
        isolated_start_y = y_start + (len(groups) + 1) * group_spacing_y
        
        isolated_cols = max(4, int((len(isolated) ** 0.5) * 1.3))
        isolated_idx = 0
        for table_name in isolated:
            table_info = self.tables_info[table_name]
            col = isolated_idx % isolated_cols
            row = isolated_idx // isolated_cols
            
            width, height = table_sizes[table_name]
            
            x = isolated_start_x + col * isolated_spacing_x
            y = isolated_start_y + row * isolated_spacing_y
            
            pk_columns = []
            fk_columns = []
            other_columns = []
            
            for col_info in table_info['columns']:
                col_name = col_info['name']
                col_type = str(col_info['type']).split('(')[0].split('[')[0]
                nullable = col_info.get('nullable', True)
                
                is_pk = col_name in table_info['primary_keys']
                is_fk = any(col_name in fk['constrained_columns'] for fk in table_info.get('foreign_keys', []))
                
                col_display = f"{col_name}: {col_type}"
                if not nullable:
                    col_display += " *"
                
                if is_pk:
                    pk_columns.append(col_display)
                elif is_fk:
                    fk_columns.append(col_display)
                else:
                    other_columns.append(col_display)
            
            label_parts = [f"<b>{table_name}</b>"]
            
            if pk_columns:
                label_parts.append("<hr style='margin:2px 0; border:0; border-top:1px solid #333;'>")
                label_parts.append("<b style='color:#d32f2f;'>PK</b>")
                label_parts.extend(pk_columns)
            
            if fk_columns:
                label_parts.append("<hr style='margin:2px 0; border:0; border-top:1px solid #666;'>")
                label_parts.append("<b style='color:#1976d2;'>FK</b>")
                label_parts.extend(fk_columns)
            
            if other_columns:
                if pk_columns or fk_columns:
                    label_parts.append("<hr style='margin:2px 0; border:0; border-top:1px solid #999;'>")
                label_parts.extend(other_columns)
            
            label = "<br>".join(label_parts)
            
            node = {
                'id': table_name,
                'label': label,
                'x': x,
                'y': y,
                'shape': 'box',
                'color': {
                    'background': '#f5f5f5',
                    'border': '#757575',
                    'highlight': {
                        'background': '#e0e0e0',
                        'border': '#616161'
                    }
                },
                'font': {
                    'face': 'Arial',
                    'size': 9,
                    'multi': 'html',
                    'align': 'left'
                },
                'widthConstraint': {
                    'maximum': width
                },
                'borderWidth': 2,
                'borderWidthSelected': 3
            }
            nodes.append(node)
            initial_positions[table_name] = {'x': x, 'y': y}
            
            isolated_idx += 1
        
        edge_id = 0
        for table_name, table_info in self.tables_info.items():
            for fk in table_info['foreign_keys']:
                ref_table = fk['referred_table']
                if ref_table in self.tables_info:
                    edge = {
                        'id': f"edge_{edge_id}",
                        'from': table_name,
                        'to': ref_table,
                        'arrows': {
                            'to': {
                                'enabled': True,
                                'scaleFactor': 1.5,
                                'type': 'arrow'
                            }
                        },
                        'color': {
                            'color': '#2c3e50',
                            'highlight': '#34495e'
                        },
                        'label': ', '.join(fk['constrained_columns'][:2]),
                        'font': {
                            'size': 8,
                            'align': 'middle',
                            'color': '#2c3e50'
                        },
                        'smooth': {
                            'type': 'straightCross',
                            'roundness': 0
                        },
                        'width': 2,
                        'dashes': False
                    }
                    edges.append(edge)
                    edge_id += 1
        
        return {'nodes': nodes, 'edges': edges, 'initial_positions': initial_positions}
    
    def create_html_file(self):
        visjs_data = self.convert_to_visjs_format()
        initial_positions = visjs_data.get('initial_positions', {})
        
        initial_positions_json = json.dumps(initial_positions, ensure_ascii=False)
        nodes_json = json.dumps(visjs_data['nodes'], ensure_ascii=False)
        edges_json = json.dumps(visjs_data['edges'], ensure_ascii=False)
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ER 다이어그램 편집기</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: '맑은 고딕', Arial, sans-serif;
            overflow: hidden;
        }}
        #toolbar {{
            background: #f5f5f5;
            padding: 10px;
            border-bottom: 1px solid #ddd;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        button {{
            padding: 8px 16px;
            background: #1976d2;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background: #1565c0;
        }}
        #mynetwork {{
            width: 100%;
            height: calc(100vh - 60px);
            background: white;
        }}
        .info {{
            margin-left: auto;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div id="toolbar">
        <button onclick="saveImage()">이미지 저장</button>
        <button onclick="autoLayout()">자동 배치</button>
        <button onclick="resetLayout()">초기화</button>
        <button onclick="exportJSON()">JSON 내보내기</button>
        <button onclick="importJSON()">JSON 가져오기</button>
        <div class="info">테이블을 드래그하여 이동할 수 있습니다. 마우스 휠로 확대/축소 가능합니다.</div>
    </div>
    <div id="mynetwork"></div>
    
    <script type="text/javascript">
        var nodesData = {nodes_json};
        var edgesData = {edges_json};
        
        var nodes = new vis.DataSet(nodesData);
        var edges = new vis.DataSet(edgesData);
        
        var container = document.getElementById('mynetwork');
        var data = {{
            nodes: nodes,
            edges: edges
        }};
        
        var options = {{
            nodes: {{
                shape: 'box',
                margin: 10,
                font: {{
                    size: 9,
                    face: 'Arial',
                    align: 'left',
                    multi: 'html'
                }},
                borderWidth: 2,
                borderWidthSelected: 3,
                shadow: {{
                    enabled: true,
                    color: 'rgba(0,0,0,0.15)',
                    size: 3,
                    x: 1,
                    y: 1
                }},
                color: {{
                    background: '#ffffff',
                    border: '#2c3e50',
                    highlight: {{
                        background: '#ecf0f1',
                        border: '#34495e'
                    }}
                }}
            }},
            edges: {{
                arrows: {{
                    to: {{
                        enabled: true,
                        scaleFactor: 1.5,
                        type: 'arrow'
                    }}
                }},
                font: {{
                    size: 8,
                    align: 'middle',
                    color: '#2c3e50'
                }},
                smooth: {{
                    type: 'straightCross',
                    roundness: 0
                }},
                color: {{
                    color: '#2c3e50',
                    highlight: '#34495e'
                }},
                width: 2
            }},
            physics: {{
                enabled: false
            }},
            interaction: {{
                dragNodes: true,
                dragView: true,
                zoomView: true,
                tooltipDelay: 100,
                hover: true
            }},
            layout: {{
                improvedLayout: false
            }}
        }};
        
        var network = new vis.Network(container, data, options);
        
        network.fit({{
            animation: {{
                duration: 500,
                easingFunction: 'easeInOutQuad'
            }}
        }});
        
        function saveImage() {{
            var dataURL = network.getCanvas().toDataURL('image/png');
            var link = document.createElement('a');
            link.download = 'er_diagram.png';
            link.href = dataURL;
            link.click();
        }}
        
        function autoLayout() {{
            network.setOptions({{
                physics: {{
                    enabled: true,
                    stabilization: {{
                        enabled: true,
                        iterations: 800,
                        updateInterval: 25
                    }},
                    barnesHut: {{
                        gravitationalConstant: -8000,
                        centralGravity: 0.01,
                        springLength: 500,
                        springConstant: 0.01,
                        damping: 0.3,
                        avoidOverlap: 1.5
                    }}
                }}
            }});
            
            var stabilizationTimeout = setTimeout(function() {{
                network.setOptions({{physics: false}});
                clearTimeout(stabilizationTimeout);
            }}, 15000);
            
            network.once("stabilizationEnd", function() {{
                clearTimeout(stabilizationTimeout);
                network.setOptions({{physics: false}});
            }});
            
            network.fit({{
                animation: {{
                    duration: 1200,
                    easingFunction: 'easeInOutQuad'
                }},
                padding: 150
            }});
        }}
        
        function resetLayout() {{
            var initialPositions = {initial_positions_json};
            network.setOptions({{
                physics: false
            }});
            var updates = [];
            for (var id in initialPositions) {{
                updates.push({{
                    id: id,
                    x: initialPositions[id].x,
                    y: initialPositions[id].y,
                    fixed: false
                }});
            }}
            nodes.update(updates);
            network.fit({{
                animation: {{
                    duration: 500,
                    easingFunction: 'easeInOutQuad'
                }}
            }});
        }}
        
        function exportJSON() {{
            var positions = network.getPositions();
            var data = {{
                nodes: nodes.get(),
                edges: edges.get(),
                positions: positions
            }};
            var blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
            var link = document.createElement('a');
            link.download = 'er_diagram.json';
            link.href = URL.createObjectURL(blob);
            link.click();
        }}
        
        function importJSON() {{
            var input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = function(e) {{
                var file = e.target.files[0];
                var reader = new FileReader();
                reader.onload = function(e) {{
                    var data = JSON.parse(e.target.result);
                    if (data.nodes) nodes.update(data.nodes);
                    if (data.edges) edges.update(data.edges);
                    if (data.positions) {{
                        network.setOptions({{physics: false}});
                        network.setPositions(data.positions);
                    }}
                }};
                reader.readAsText(file);
            }};
            input.click();
        }}
        
        network.on("click", function(params) {{
            if (params.nodes.length > 0) {{
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                console.log("선택된 테이블:", nodeId);
            }}
        }});
        
        network.on("dragEnd", function(params) {{
            if (params.nodes.length > 0) {{
                network.setOptions({{physics: false}});
            }}
        }});
        
        var isStabilizing = false;
        network.on("stabilizationProgress", function(params) {{
            if (!isStabilizing) {{
                isStabilizing = true;
            }}
        }});
        
        network.on("stabilizationEnd", function() {{
            isStabilizing = false;
            network.setOptions({{physics: false}});
        }});
    </script>
</body>
</html>"""
        
        temp_dir = tempfile.gettempdir()
        html_file = os.path.join(temp_dir, f"er_diagram_editor_{os.getpid()}.html")
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return html_file
    
    def start_server(self):
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=tempfile.gettempdir(), **kwargs)
            
            def log_message(self, format, *args):
                if self.server.logger:
                    self.server.logger.debug(f"HTTP: {format % args}")
        
        Handler.logger = self.logger
        
        try:
            self.httpd = socketserver.TCPServer(("", self.port), Handler)
            self.httpd.logger = self.logger
            self.server_thread = threading.Thread(target=self.httpd.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            if self.logger:
                self.logger.info(f"웹 서버 시작: 포트 {self.port}")
            
            time.sleep(0.5)
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"웹 서버 시작 실패: {str(e)}")
            return False
    
    def open_in_browser(self):
        html_file = self.create_html_file()
        
        if not self.start_server():
            webbrowser.open(f"file://{html_file}")
            return
        
        url = f"http://localhost:{self.port}/{os.path.basename(html_file)}"
        
        if self.logger:
            self.logger.info(f"브라우저에서 ER 다이어그램 편집기 열기: {url}")
        
        webbrowser.open(url)
        
        return self.httpd
