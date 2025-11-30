import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import traceback
from db_connector import DatabaseConnector
from table_extractor import TableExtractor
from er_diagram import ERDiagramGenerator
from ddl_generator import DDLGenerator
from excel_generator import ExcelGenerator
from config_manager import ConfigManager
from er_diagram_viewer import ERDiagramViewer
from er_diagram_web import ERDiagramWebEditor
from logger import AppLogger


class ERDApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("ERD 프로그램")
        self.root.geometry("650x650")
        
        self.db_connector = DatabaseConnector()
        self.table_extractor = None
        self.tables_info = {}
        self.config_manager = ConfigManager()
        self.logger = AppLogger()
        
        self.logger.info("=" * 50)
        self.logger.info("ERD 프로그램 시작")
        self.logger.info(f"로그 파일 위치: {self.logger.get_log_path()}")
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="DB 타입:", font=("맑은 고딕", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.db_type_var = tk.StringVar(value="MySQL")
        db_type_combo = ttk.Combobox(main_frame, textvariable=self.db_type_var, 
                                     values=["MySQL", "MariaDB", "PostgreSQL", "Oracle", "SQLite"], 
                                     state="readonly", width=20)
        db_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="호스트:", font=("맑은 고딕", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(main_frame, textvariable=self.host_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="포트:", font=("맑은 고딕", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar(value="3306")
        ttk.Entry(main_frame, textvariable=self.port_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="데이터베이스:", font=("맑은 고딕", 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        db_frame = ttk.Frame(main_frame)
        db_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        db_frame.columnconfigure(0, weight=1)
        self.database_var = tk.StringVar()
        self.database_combo = ttk.Combobox(db_frame, textvariable=self.database_var, width=25, state="readonly")
        self.database_combo.grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(db_frame, text="조회", command=self.load_databases, width=8).grid(row=0, column=1, padx=5)
        
        self.service_name_label = ttk.Label(main_frame, text="서비스명 (Oracle):", font=("맑은 고딕", 10))
        self.service_name_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.service_name_var = tk.StringVar()
        self.service_name_entry = ttk.Entry(main_frame, textvariable=self.service_name_var, width=30)
        self.service_name_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="사용자명:", font=("맑은 고딕", 10)).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.username_var, width=30).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="비밀번호:", font=("맑은 고딕", 10)).grid(row=6, column=0, sticky=tk.W, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, show="*", width=30).grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.file_path_label = ttk.Label(main_frame, text="파일 경로 (SQLite):", font=("맑은 고딕", 10))
        self.file_path_label.grid(row=7, column=0, sticky=tk.W, pady=5)
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        file_frame.columnconfigure(0, weight=1)
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=25)
        self.file_path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(file_frame, text="찾아보기", command=self.browse_file).grid(row=0, column=1, padx=5)
        
        connection_button_frame = ttk.Frame(main_frame)
        connection_button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(connection_button_frame, text="저장된 연결 불러오기", 
                  command=self.load_saved_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(connection_button_frame, text="현재 연결 저장", 
                  command=self.save_current_connection).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(main_frame, text="DB 연결", command=self.connect_db, 
                  style="Accent.TButton").grid(row=9, column=0, columnspan=2, pady=10)
        
        self.status_label = ttk.Label(main_frame, text="DB에 연결해주세요.", 
                                      font=("맑은 고딕", 9), foreground="gray")
        self.status_label.grid(row=10, column=0, columnspan=2, pady=5)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="ER 다이어그램 보기/편집", 
                  command=self.edit_er_diagram, state="disabled").pack(side=tk.LEFT, padx=5)
        self.er_edit_button = button_frame.winfo_children()[0]
        
        ttk.Button(button_frame, text="ER 다이어그램 저장 (이미지)", 
                  command=self.generate_er_diagram, state="disabled").pack(side=tk.LEFT, padx=5)
        self.er_button = button_frame.winfo_children()[1]
        
        ttk.Button(button_frame, text="DDL 생성", 
                  command=self.generate_ddl, state="disabled").pack(side=tk.LEFT, padx=5)
        self.ddl_button = button_frame.winfo_children()[2]
        
        ttk.Button(button_frame, text="엑셀 정의서 생성", 
                  command=self.generate_excel, state="disabled").pack(side=tk.LEFT, padx=5)
        self.excel_button = button_frame.winfo_children()[3]
        
        self.update_db_type_fields()
        self.db_type_var.trace('w', lambda *args: self.update_db_type_fields())
    
    def update_db_type_fields(self):
        db_type = self.db_type_var.get()
        if db_type == "SQLite":
            self.host_var.set("")
            self.port_var.set("")
            self.database_var.set("")
            self.username_var.set("")
            self.password_var.set("")
            self.service_name_var.set("")
            self.database_combo.master.grid_remove()
            self.service_name_label.grid_remove()
            self.service_name_entry.grid_remove()
            self.file_path_label.grid()
            self.file_path_entry.master.grid()
        elif db_type == "Oracle":
            if not self.host_var.get():
                self.host_var.set("localhost")
            if not self.port_var.get():
                self.port_var.set("1521")
            self.database_combo.master.grid()
            self.service_name_label.grid()
            self.service_name_entry.grid()
            self.file_path_label.grid_remove()
            self.file_path_entry.master.grid_remove()
        else:
            if not self.host_var.get():
                self.host_var.set("localhost")
            if not self.port_var.get():
                if db_type == "MySQL" or db_type == "MariaDB":
                    self.port_var.set("3306")
                elif db_type == "PostgreSQL":
                    self.port_var.set("5432")
                else:
                    self.port_var.set("")
            self.database_combo.master.grid()
            self.service_name_label.grid_remove()
            self.service_name_entry.grid_remove()
            self.file_path_label.grid_remove()
            self.file_path_entry.master.grid_remove()
    
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="SQLite 데이터베이스 파일 선택",
            filetypes=[("SQLite 파일", "*.db"), ("모든 파일", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
    
    def load_databases(self):
        db_type = self.db_type_var.get()
        
        if db_type == "SQLite":
            messagebox.showinfo("알림", "SQLite는 데이터베이스 목록 조회가 불가능합니다.")
            return
        
        host = self.host_var.get()
        port = self.port_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        service_name = self.service_name_var.get()
        
        if not all([host, port, username]):
            messagebox.showerror("오류", "호스트, 포트, 사용자명을 입력해주세요.")
            return
        
        if not password:
            messagebox.showerror("오류", "비밀번호를 입력해주세요.")
            return
        
        try:
            self.status_label.config(text="데이터베이스 목록 조회 중...", foreground="blue")
            self.root.update()
            
            temp_connector = DatabaseConnector()
            if db_type == "Oracle" and service_name:
                success = temp_connector.connect_without_database(
                    db_type, host=host, port=port, 
                    username=username, password=password, service_name=service_name
                )
            else:
                success = temp_connector.connect_without_database(
                    db_type, host=host, port=port, 
                    username=username, password=password
                )
            
            if success:
                databases = temp_connector.get_databases(db_type)
                temp_connector.close()
                
                if databases:
                    self.database_combo['values'] = databases
                    self.database_combo['state'] = 'readonly'
                    if len(databases) > 0:
                        self.database_var.set(databases[0])
                    self.status_label.config(text=f"{len(databases)}개의 데이터베이스를 찾았습니다.", foreground="green")
                    messagebox.showinfo("성공", f"{len(databases)}개의 데이터베이스를 찾았습니다.")
                else:
                    self.status_label.config(text="데이터베이스를 찾을 수 없습니다.", foreground="orange")
                    messagebox.showwarning("알림", "데이터베이스를 찾을 수 없습니다.")
            else:
                temp_connector.close()
                self.status_label.config(text="연결 실패.", foreground="red")
                messagebox.showerror("오류", "데이터베이스 목록 조회에 실패했습니다.\n연결 정보를 확인해주세요.")
                
        except Exception as e:
            self.status_label.config(text="조회 실패.", foreground="red")
            messagebox.showerror("오류", f"데이터베이스 목록 조회 중 오류 발생: {str(e)}")
    
    def load_saved_connection(self):
        connections = self.config_manager.load_all_connections()
        
        if not connections:
            messagebox.showinfo("알림", "저장된 연결 정보가 없습니다.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("저장된 연결 정보")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="저장된 연결 정보를 선택하세요:", font=("맑은 고딕", 10)).pack(anchor=tk.W, pady=5)
        
        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, font=("맑은 고딕", 9))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        for conn in connections:
            display_text = f"{conn.get('connection_name', 'Unnamed')} - {conn['db_type']}://{conn['username']}@{conn['host']}:{conn['port']}/{conn['database']}"
            listbox.insert(tk.END, display_text)
        
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def load_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("경고", "연결 정보를 선택해주세요.")
                return
            
            conn = connections[selection[0]]
            self.db_type_var.set(conn['db_type'])
            self.host_var.set(conn['host'])
            self.port_var.set(str(conn['port']))
            self.database_var.set(conn['database'])
            self.username_var.set(conn['username'])
            self.password_var.set(conn['password'])
            if conn.get('service_name'):
                self.service_name_var.set(conn['service_name'])
            else:
                self.service_name_var.set("")
            
            self.update_db_type_fields()
            dialog.destroy()
        
        def delete_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("경고", "삭제할 연결 정보를 선택해주세요.")
                return
            
            conn = connections[selection[0]]
            if messagebox.askyesno("확인", "선택한 연결 정보를 삭제하시겠습니까?"):
                self.config_manager.delete_connection(
                    conn['db_type'], conn['host'], conn['port'], 
                    conn['database'], conn['username']
                )
                dialog.destroy()
                self.load_saved_connection()
        
        ttk.Button(button_frame, text="불러오기", command=load_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="삭제", command=delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="취소", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_current_connection(self):
        db_type = self.db_type_var.get()
        
        if db_type == "SQLite":
            messagebox.showinfo("알림", "SQLite 연결 정보는 저장할 수 없습니다.")
            return
        
        host = self.host_var.get()
        port = self.port_var.get()
        database = self.database_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        service_name = self.service_name_var.get()
        
        if not all([host, port, database, username]):
            messagebox.showerror("오류", "호스트, 포트, 데이터베이스, 사용자명을 입력해주세요.")
            return
        
        connection_name = simpledialog.askstring(
            "연결 정보 저장",
            "연결 이름을 입력하세요:",
            initialvalue=f"{db_type}_{host}_{database}"
        )
        
        if connection_name:
            success = self.config_manager.save_connection(
                db_type, host, port, database, username, password,
                service_name if service_name else None, connection_name
            )
            
            if success:
                messagebox.showinfo("성공", "연결 정보가 저장되었습니다.")
            else:
                messagebox.showerror("오류", "연결 정보 저장에 실패했습니다.")
    
    def connect_db(self):
        db_type = self.db_type_var.get()
        
        try:
            if db_type == "SQLite":
                file_path = self.file_path_var.get()
                if not file_path:
                    messagebox.showerror("오류", "SQLite 파일 경로를 입력해주세요.")
                    return
                success = self.db_connector.connect(db_type, file_path=file_path)
            else:
                host = self.host_var.get()
                port = self.port_var.get()
                database = self.database_var.get()
                username = self.username_var.get()
                password = self.password_var.get()
                service_name = self.service_name_var.get()
                
                if db_type == "Oracle":
                    if not all([host, port, username]):
                        messagebox.showerror("오류", "호스트, 포트, 사용자명을 입력해주세요.")
                        return
                    if not database and not service_name:
                        messagebox.showerror("오류", "데이터베이스명 또는 서비스명을 입력해주세요.")
                        return
                else:
                    if not all([host, port, username]):
                        messagebox.showerror("오류", "호스트, 포트, 사용자명을 입력해주세요.")
                        return
                    if not database:
                        messagebox.showerror("오류", "데이터베이스를 선택해주세요.")
                        return
                
                success = self.db_connector.connect(
                    db_type, host=host, port=port, 
                    database=database, username=username, password=password,
                    service_name=service_name if service_name else None
                )
            
            if success:
                self.table_extractor = TableExtractor(self.db_connector)
                self.tables_info = self.table_extractor.extract_all_tables_info()
                
                table_count = len(self.tables_info)
                self.status_label.config(
                    text=f"연결 성공! {table_count}개의 테이블을 찾았습니다.",
                    foreground="green"
                )
                
                self.er_edit_button.config(state="normal")
                self.er_button.config(state="normal")
                self.ddl_button.config(state="normal")
                self.excel_button.config(state="normal")
                
                messagebox.showinfo("성공", f"DB 연결 성공!\n{table_count}개의 테이블을 찾았습니다.")
            else:
                self.status_label.config(text="연결 실패. 정보를 확인해주세요.", foreground="red")
                messagebox.showerror("오류", "DB 연결에 실패했습니다.")
                
        except Exception as e:
            messagebox.showerror("오류", f"연결 중 오류 발생: {str(e)}")
            self.status_label.config(text="연결 실패.", foreground="red")
    
    def view_er_diagram(self):
        if not self.tables_info:
            messagebox.showerror("오류", "먼저 DB에 연결해주세요.")
            return
        
        try:
            self.logger.info("ER 다이어그램 뷰어 열기")
            viewer = ERDiagramViewer(self.root, self.tables_info, self.logger)
            viewer.show()
        except Exception as e:
            self.logger.error(f"ER 다이어그램 뷰어 오류: {str(e)}", exc_info=True)
            messagebox.showerror("오류", f"ER 다이어그램 뷰어 오류: {str(e)}")
    
    def edit_er_diagram(self):
        if not self.tables_info:
            messagebox.showerror("오류", "먼저 DB에 연결해주세요.")
            return
        
        try:
            self.logger.info("ER 다이어그램 웹 편집기/뷰어 열기")
            editor = ERDiagramWebEditor(self.tables_info, self.logger)
            editor.open_in_browser()
            messagebox.showinfo(
                "알림",
                "웹 브라우저에서 ER 다이어그램 편집기가 열렸습니다.\n\n"
                "주요 기능:\n"
                "✓ 테이블 드래그로 이동\n"
                "✓ 마우스 휠로 확대/축소\n"
                "✓ 자동 배치 버튼으로 레이아웃 정리\n"
                "✓ 이미지 저장 버튼으로 PNG 저장\n"
                "✓ JSON 내보내기/가져오기로 레이아웃 저장"
            )
        except Exception as e:
            self.logger.error(f"ER 다이어그램 웹 편집기 오류: {str(e)}", exc_info=True)
            messagebox.showerror("오류", f"ER 다이어그램 편집기 오류: {str(e)}\n\n로그 파일: {self.logger.get_log_path()}")
    
    def generate_er_diagram(self):
        if not self.tables_info:
            messagebox.showerror("오류", "먼저 DB에 연결해주세요.")
            return
        
        try:
            self.logger.info("ER 다이어그램 저장 시작")
            output_path = filedialog.asksaveasfilename(
                title="ER 다이어그램 저장",
                defaultextension=".png",
                filetypes=[("PNG 파일", "*.png"), ("모든 파일", "*.*")]
            )
            
            if output_path:
                self.logger.info(f"ER 다이어그램 저장 경로: {output_path}")
                
                try:
                    generator = ERDiagramGenerator()
                    result_path = generator.generate(self.tables_info, output_path)
                    self.logger.info(f"ER 다이어그램 생성 완료 (Graphviz): {result_path}")
                    messagebox.showinfo("성공", f"ER 다이어그램이 생성되었습니다.\n{result_path}")
                except Exception as e:
                    error_msg = str(e)
                    self.logger.warning(f"Graphviz 실패, matplotlib로 대체: {error_msg}")
                    
                    try:
                        from er_diagram_matplotlib import ERDiagramMatplotlibGenerator
                        matplotlib_generator = ERDiagramMatplotlibGenerator()
                        result_path = matplotlib_generator.generate(self.tables_info, output_path)
                        self.logger.info(f"ER 다이어그램 생성 완료 (matplotlib): {result_path}")
                        messagebox.showinfo(
                            "성공", 
                            f"ER 다이어그램이 생성되었습니다.\n"
                            f"(Graphviz 대신 matplotlib 사용)\n{result_path}"
                        )
                    except Exception as e2:
                        self.logger.error(f"모든 다이어그램 생성 방법 실패: {str(e2)}", exc_info=True)
                        raise
        except FileNotFoundError as e:
            error_msg = str(e)
            self.logger.error(f"ER 다이어그램 생성 오류 (FileNotFound): {error_msg}", exc_info=True)
            if 'dot' in error_msg.lower() or 'graphviz' in error_msg.lower():
                messagebox.showerror(
                    "오류", 
                    "Graphviz를 찾을 수 없습니다.\n\n"
                    "해결 방법:\n"
                    "1. Graphviz를 설치하세요: https://graphviz.org/download/\n"
                    "2. 설치 후 시스템 PATH에 Graphviz bin 폴더를 추가하세요.\n"
                    "   예: C:\\Program Files\\Graphviz\\bin\n\n"
                    f"로그 파일: {self.logger.get_log_path()}"
                )
            else:
                messagebox.showerror("오류", f"ER 다이어그램 생성 중 오류 발생: {error_msg}\n\n로그 파일: {self.logger.get_log_path()}")
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"ER 다이어그램 생성 오류: {error_msg}", exc_info=True)
            if 'dot' in error_msg.lower() or 'graphviz' in error_msg.lower():
                messagebox.showerror(
                    "오류", 
                    "Graphviz 실행 오류가 발생했습니다.\n\n"
                    "해결 방법:\n"
                    "1. Graphviz가 설치되어 있는지 확인하세요.\n"
                    "2. 시스템 PATH에 Graphviz bin 폴더가 추가되어 있는지 확인하세요.\n"
                    f"상세 오류: {error_msg}\n\n"
                    f"로그 파일: {self.logger.get_log_path()}"
                )
            else:
                messagebox.showerror("오류", f"ER 다이어그램 생성 중 오류 발생: {error_msg}\n\n로그 파일: {self.logger.get_log_path()}")
    
    def generate_ddl(self):
        if not self.tables_info:
            messagebox.showerror("오류", "먼저 DB에 연결해주세요.")
            return
        
        try:
            self.logger.info("DDL 생성 시작")
            output_path = filedialog.asksaveasfilename(
                title="DDL 파일 저장",
                defaultextension=".sql",
                filetypes=[("SQL 파일", "*.sql"), ("모든 파일", "*.*")]
            )
            
            if output_path:
                self.logger.info(f"DDL 저장 경로: {output_path}")
                generator = DDLGenerator(self.db_connector)
                ddl_content = generator.generate_ddl(self.tables_info)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(ddl_content)
                
                self.logger.info(f"DDL 생성 완료: {output_path}")
                messagebox.showinfo("성공", f"DDL 파일이 생성되었습니다.\n{output_path}")
        except Exception as e:
            self.logger.error(f"DDL 생성 오류: {str(e)}", exc_info=True)
            messagebox.showerror("오류", f"DDL 생성 중 오류 발생: {str(e)}\n\n로그 파일: {self.logger.get_log_path()}")
    
    def generate_excel(self):
        if not self.tables_info:
            messagebox.showerror("오류", "먼저 DB에 연결해주세요.")
            return
        
        try:
            self.logger.info("엑셀 정의서 생성 시작")
            output_path = filedialog.asksaveasfilename(
                title="엑셀 파일 저장",
                defaultextension=".xlsx",
                filetypes=[("Excel 파일", "*.xlsx"), ("모든 파일", "*.*")]
            )
            
            if output_path:
                self.logger.info(f"엑셀 저장 경로: {output_path}")
                generator = ExcelGenerator()
                result_path = generator.generate(self.tables_info, output_path)
                self.logger.info(f"엑셀 생성 완료: {result_path}")
                messagebox.showinfo("성공", f"엑셀 테이블 정의서가 생성되었습니다.\n{result_path}")
        except Exception as e:
            self.logger.error(f"엑셀 생성 오류: {str(e)}", exc_info=True)
            messagebox.showerror("오류", f"엑셀 생성 중 오류 발생: {str(e)}\n\n로그 파일: {self.logger.get_log_path()}")


def main():
    root = tk.Tk()
    app = ERDApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()

