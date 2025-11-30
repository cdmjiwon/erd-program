import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import io
import tempfile
import os
from er_diagram import ERDiagramGenerator
from er_diagram_matplotlib import ERDiagramMatplotlibGenerator


class ERDiagramViewer:
    def __init__(self, parent, tables_info, logger=None):
        self.parent = parent
        self.tables_info = tables_info
        self.logger = logger
        self.window = None
        self.image = None
        self.photo = None
        self.scale_factor = 1.0
        
    def show(self):
        if not self.tables_info:
            messagebox.showerror("오류", "표시할 테이블 정보가 없습니다.")
            return
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("ER 다이어그램 뷰어")
        self.window.geometry("1000x700")
        
        toolbar = ttk.Frame(self.window)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="이미지로 저장", command=self.save_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="다시 생성", command=self.regenerate).pack(side=tk.LEFT, padx=5)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        ttk.Button(toolbar, text="확대", command=self.zoom_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="축소", command=self.zoom_out).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="원본 크기", command=self.zoom_reset).pack(side=tk.LEFT, padx=5)
        ttk.Label(toolbar, text="확대/축소: 마우스 휠 또는 버튼 사용", font=("맑은 고딕", 9)).pack(side=tk.LEFT, padx=10)
        
        canvas_frame = ttk.Frame(self.window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(
            canvas_frame,
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set,
            bg="white"
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        h_scrollbar.config(command=self.canvas.xview)
        v_scrollbar.config(command=self.canvas.yview)
        
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
        self.canvas_start_x = 0
        self.canvas_start_y = 0
        self.canvas_scroll_x = 0
        self.canvas_scroll_y = 0
        
        self.generate_and_display()
    
    def generate_and_display(self):
        temp_dir = tempfile.gettempdir()
        temp_base = os.path.join(temp_dir, f"erd_temp_{os.getpid()}")
        
        try:
            if self.logger:
                self.logger.info("ER 다이어그램 생성 시작 (뷰어) - Graphviz 시도")
            
            generator = ERDiagramGenerator()
            result_path = generator.generate(self.tables_info, temp_base)
            
            if result_path and os.path.exists(result_path):
                if self.logger:
                    self.logger.info(f"ER 다이어그램 생성 성공 (Graphviz): {result_path}")
                self.load_image(result_path)
                return
            else:
                raise Exception("Graphviz 다이어그램 생성 실패 - 파일 없음")
                
        except Exception as e:
            error_msg = str(e)
            if self.logger:
                self.logger.warning(f"Graphviz 다이어그램 생성 실패, matplotlib로 대체 시도: {error_msg}")
            
            try:
                if self.logger:
                    self.logger.info("matplotlib로 ER 다이어그램 생성 시작")
                matplotlib_generator = ERDiagramMatplotlibGenerator()
                result_path = matplotlib_generator.generate(self.tables_info, temp_base)
                
                if result_path and os.path.exists(result_path):
                    if self.logger:
                        self.logger.info(f"ER 다이어그램 생성 성공 (matplotlib): {result_path}")
                    self.load_image(result_path)
                else:
                    raise Exception("matplotlib 다이어그램 생성 실패")
                    
            except Exception as e2:
                if self.logger:
                    self.logger.error(f"모든 다이어그램 생성 방법 실패: {str(e2)}", exc_info=True)
                messagebox.showerror(
                    "오류",
                    f"다이어그램 생성에 실패했습니다.\n\n"
                    f"Graphviz 오류: {error_msg}\n"
                    f"matplotlib 오류: {str(e2)}\n\n"
                    "로그 파일을 확인하세요."
                )
    
    def load_image(self, image_path):
        try:
            if self.logger:
                self.logger.debug(f"이미지 로드 시도: {image_path}")
            img = Image.open(image_path)
            self.image = img
            self.update_display()
            if self.logger:
                self.logger.info(f"이미지 로드 성공: {image_path}, 크기: {img.width}x{img.height}")
        except Exception as e:
            if self.logger:
                self.logger.error(f"이미지 로드 실패: {str(e)}", exc_info=True)
            messagebox.showerror("오류", f"이미지 로드 실패: {str(e)}")
    
    def update_display(self):
        if not self.image:
            return
        
        width = int(self.image.width * self.scale_factor)
        height = int(self.image.height * self.scale_factor)
        
        resized_img = self.image.resize((width, height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_img)
        
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
    
    def zoom_in(self):
        self.scale_factor = min(self.scale_factor * 1.2, 3.0)
        self.update_display()
    
    def zoom_out(self):
        self.scale_factor = max(self.scale_factor / 1.2, 0.3)
        self.update_display()
    
    def zoom_reset(self):
        self.scale_factor = 1.0
        self.update_display()
    
    def regenerate(self):
        if self.logger:
            self.logger.info("ER 다이어그램 재생성 요청")
        self.scale_factor = 1.0
        self.generate_and_display()
    
    def on_canvas_click(self, event):
        self.canvas_start_x = event.x
        self.canvas_start_y = event.y
    
    def on_canvas_drag(self, event):
        dx = event.x - self.canvas_start_x
        dy = event.y - self.canvas_start_y
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.canvas_start_x = event.x
        self.canvas_start_y = event.y
    
    def on_canvas_release(self, event):
        pass
    
    def on_mousewheel(self, event):
        if event.delta > 0 or event.num == 4:
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:
            self.zoom_out()
    
    def save_image(self):
        if not self.image:
            messagebox.showwarning("경고", "저장할 이미지가 없습니다.")
            return
        
        output_path = filedialog.asksaveasfilename(
            title="ER 다이어그램 저장",
            defaultextension=".png",
            filetypes=[("PNG 파일", "*.png"), ("JPEG 파일", "*.jpg"), ("모든 파일", "*.*")]
        )
        
        if output_path:
            try:
                self.image.save(output_path)
                messagebox.showinfo("성공", f"이미지가 저장되었습니다.\n{output_path}")
            except Exception as e:
                messagebox.showerror("오류", f"이미지 저장 실패: {str(e)}")
    
    def generate_simple_diagram(self):
        try:
            if self.logger:
                self.logger.info("간단한 다이어그램 생성 시작 (matplotlib)")
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
            
            fig, ax = plt.subplots(figsize=(14, 10))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.axis('off')
            
            table_positions = {}
            num_tables = len(self.tables_info)
            cols = int(num_tables ** 0.5) + 1
            rows = (num_tables + cols - 1) // cols
            
            idx = 0
            for table_name in self.tables_info.keys():
                col = idx % cols
                row = idx // cols
                x = 1 + (col * 3)
                y = 9 - (row * 3)
                table_positions[table_name] = (x, y)
                idx += 1
            
            for table_name, (x, y) in table_positions.items():
                table_info = self.tables_info[table_name]
                
                box = FancyBboxPatch(
                    (x - 0.4, y - 0.6), 0.8, 1.2,
                    boxstyle="round,pad=0.1",
                    edgecolor='black',
                    facecolor='lightblue',
                    linewidth=1.5
                )
                ax.add_patch(box)
                
                ax.text(x, y + 0.4, table_name, ha='center', va='center',
                       fontsize=10, fontweight='bold', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.7))
                
                columns_text = []
                for col in table_info['columns'][:5]:
                    col_name = col['name']
                    if col_name in table_info['primary_keys']:
                        col_name = f"{col_name} [PK]"
                    columns_text.append(col_name)
                
                if len(table_info['columns']) > 5:
                    columns_text.append("...")
                
                ax.text(x, y - 0.2, '\n'.join(columns_text), ha='center', va='center',
                       fontsize=8, family='monospace')
            
            for table_name, table_info in self.tables_info.items():
                for fk in table_info['foreign_keys']:
                    ref_table = fk['referred_table']
                    if ref_table in table_positions:
                        x1, y1 = table_positions[table_name]
                        x2, y2 = table_positions[ref_table]
                        
                        arrow = FancyArrowPatch(
                            (x1, y1 - 0.6), (x2, y2 + 0.6),
                            arrowstyle='->', mutation_scale=20,
                            linewidth=1.5, color='red', alpha=0.6
                        )
                        ax.add_patch(arrow)
            
            ax.text(5, 0.5, '간단한 ER 다이어그램 (Graphviz 미설치)', 
                   ha='center', fontsize=12, style='italic', color='gray')
            
            temp_file = os.path.join(tempfile.gettempdir(), f"erd_simple_{os.getpid()}.png")
            
            try:
                plt.savefig(temp_file, dpi=150, bbox_inches='tight', format='png')
                plt.close(fig)
                
                if os.path.exists(temp_file):
                    if self.logger:
                        self.logger.info(f"간단한 다이어그램 생성 완료: {temp_file}")
                    self.load_image(temp_file)
                else:
                    raise Exception("이미지 파일이 생성되지 않았습니다.")
            except Exception as e:
                plt.close(fig)
                if self.logger:
                    self.logger.error(f"matplotlib 이미지 저장 실패: {str(e)}", exc_info=True)
                raise Exception(f"matplotlib 이미지 저장 실패: {str(e)}")
            
        except ImportError:
            messagebox.showerror("오류", "matplotlib가 설치되어 있지 않습니다.\n설치: pip install matplotlib")
        except Exception as e:
            messagebox.showerror("오류", f"다이어그램 생성 실패: {str(e)}")

