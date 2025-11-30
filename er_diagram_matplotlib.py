import os
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import math
import textwrap


class ERDiagramMatplotlibGenerator:
    def __init__(self):
        pass
    
    def generate(self, tables_info, output_path='er_diagram'):
        fig = None
        try:
            num_tables = len(tables_info)
            if num_tables == 0:
                raise Exception("표시할 테이블이 없습니다.")
            
            cols = max(3, math.ceil(math.sqrt(num_tables * 1.3)))
            rows = math.ceil(num_tables / cols)
            
            fig_width = max(16, cols * 3.5)
            fig_height = max(12, rows * 2.5)
            
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            ax.set_xlim(0, cols * 3.5)
            ax.set_ylim(0, rows * 2.5)
            ax.axis('off')
            ax.set_facecolor('white')
            
            table_positions = {}
            table_width = 2.8
            table_height = 2.0
            spacing_x = 3.5
            spacing_y = 2.5
            
            start_x = 1.8
            start_y = rows * 2.5 - 1.0
            
            idx = 0
            for table_name in tables_info.keys():
                col = idx % cols
                row = idx // cols
                x = start_x + (col * spacing_x)
                y = start_y - (row * spacing_y)
                table_positions[table_name] = (x, y)
                idx += 1
            
            for table_name, (x, y) in table_positions.items():
                table_info = tables_info[table_name]
                
                main_box = FancyBboxPatch(
                    (x - table_width/2, y - table_height/2), 
                    table_width, table_height,
                    boxstyle="round,pad=0.1",
                    edgecolor='#34495e',
                    facecolor='#ffffff',
                    linewidth=2.5,
                    zorder=1
                )
                ax.add_patch(main_box)
                
                header_box = Rectangle(
                    (x - table_width/2, y + table_height/2 - 0.4), 
                    table_width, 0.4,
                    edgecolor='#2c3e50',
                    facecolor='#3498db',
                    linewidth=2,
                    zorder=2
                )
                ax.add_patch(header_box)
                
                table_name_wrapped = '\n'.join(textwrap.wrap(table_name, width=20))
                ax.text(x, y + table_height/2 - 0.2, table_name_wrapped, 
                       ha='center', va='center',
                       fontsize=10, fontweight='bold', color='white',
                       zorder=3)
                
                columns_text = []
                max_cols = 10
                shown_cols = table_info['columns'][:max_cols]
                
                for col in shown_cols:
                    col_name = col['name']
                    col_type = str(col['type']).split('(')[0].split('[')[0]
                    
                    pk_marker = " [PK]" if col_name in table_info['primary_keys'] else ""
                    null_marker = " *" if not col.get('nullable', True) else ""
                    
                    col_display = f"{col_name}{pk_marker}{null_marker}"
                    type_display = col_type[:18] if len(col_type) <= 18 else col_type[:15] + "..."
                    
                    display_text = f"{col_display:25s} {type_display}"
                    columns_text.append(display_text)
                
                if len(table_info['columns']) > max_cols:
                    columns_text.append(f"... (+{len(table_info['columns']) - max_cols}개 더)")
                
                columns_str = '\n'.join(columns_text)
                ax.text(x, y - 0.1, columns_str, 
                       ha='left', va='center',
                       fontsize=7, family='monospace',
                       bbox=dict(boxstyle='round,pad=0.1', facecolor='#f8f9fa', alpha=0.9, edgecolor='#dee2e6'),
                       zorder=2)
            
            drawn_arrows = set()
            for table_name, table_info in tables_info.items():
                for fk in table_info['foreign_keys']:
                    ref_table = fk['referred_table']
                    if ref_table in table_positions:
                        arrow_key = tuple(sorted([table_name, ref_table]))
                        if arrow_key in drawn_arrows:
                            continue
                        drawn_arrows.add(arrow_key)
                        
                        x1, y1 = table_positions[table_name]
                        x2, y2 = table_positions[ref_table]
                        
                        dx = x2 - x1
                        dy = y2 - y1
                        dist = math.sqrt(dx*dx + dy*dy)
                        
                        if dist < 0.1:
                            continue
                        
                        start_x = x1 + (dx / dist) * (table_width/2)
                        start_y = y1 + (dy / dist) * (table_height/2)
                        end_x = x2 - (dx / dist) * (table_width/2)
                        end_y = y2 - (dy / dist) * (table_height/2)
                        
                        arrow = FancyArrowPatch(
                            (start_x, start_y), 
                            (end_x, end_y),
                            arrowstyle='->', 
                            mutation_scale=30,
                            linewidth=2.5, 
                            color='#e74c3c', 
                            alpha=0.8,
                            zorder=0,
                            connectionstyle="arc3,rad=0.15" if abs(dx) > 1 else None
                        )
                        ax.add_patch(arrow)
                        
                        fk_cols = fk['constrained_columns'][:2]
                        label_text = ', '.join(fk_cols)
                        if len(fk['constrained_columns']) > 2:
                            label_text += f" (+{len(fk['constrained_columns'])-2})"
                        
                        mid_x = (start_x + end_x) / 2
                        mid_y = (start_y + end_y) / 2
                        ax.text(mid_x, mid_y - 0.2, label_text,
                               ha='center', fontsize=7, color='#c0392b', fontweight='bold',
                               bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.95, edgecolor='#e74c3c'),
                               zorder=4)
            
            ax.text(cols * 3.5 / 2, 0.3, f'ER 다이어그램 (총 {num_tables}개 테이블)', 
                   ha='center', fontsize=12, style='italic', color='#7f8c8d',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='#ecf0f1', alpha=0.95, edgecolor='#bdc3c7'))
            
            output_file = f"{output_path}.png"
            plt.savefig(output_file, dpi=200, bbox_inches='tight', format='png', 
                       facecolor='white', edgecolor='none', pad_inches=0.2)
            plt.close(fig)
            fig = None
            
            if os.path.exists(output_file):
                return output_file
            else:
                raise Exception("이미지 파일이 생성되지 않았습니다.")
                
        except Exception as e:
            if fig is not None:
                plt.close(fig)
            raise Exception(f"matplotlib 다이어그램 생성 실패: {str(e)}")

