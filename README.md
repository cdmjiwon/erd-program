# ERD 프로그램 (ERD Program)

데이터베이스에서 ER 다이어그램을 생성하고, DDL 스크립트와 엑셀 테이블 정의서를 만드는 GUI 프로그램입니다.

## 주요 기능

- 📊 **ER 다이어그램 생성**: 데이터베이스 스키마를 시각화
- 🔧 **DDL 생성**: 테이블 생성 스크립트 자동 생성
- 📋 **엑셀 테이블 정의서**: 테이블 정보를 엑셀 파일로 내보내기
- 🌐 **웹 기반 편집기**: ERwin 스타일의 인터랙티브 다이어그램 편집
- 💾 **연결 정보 저장**: 데이터베이스 연결 정보 저장 및 불러오기
- 📝 **로깅**: 작업 이력 및 오류 로깅

## 지원 데이터베이스

- MySQL
- MariaDB
- PostgreSQL
- Oracle
- SQLite

## 요구사항

- Python 3.8 이상
- Graphviz (ER 다이어그램 생성용, 선택사항 - 없으면 matplotlib 사용)

## 설치 방법

1. 저장소 클론:
```bash
git clone https://github.com/YOUR_USERNAME/erd-program.git
cd erd-program
```

2. 가상환경 생성 및 활성화 (권장):
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. 의존성 설치:
```bash
pip install -r requirements.txt
```

4. Graphviz 설치 (선택사항):
- Windows: [Graphviz 다운로드](https://graphviz.org/download/) 후 PATH에 추가
- Linux: `sudo apt-get install graphviz` (Ubuntu/Debian)
- Mac: `brew install graphviz`

## 사용 방법

### GUI 실행

```bash
python main.py
```

### 실행 파일 빌드

Windows에서 실행 파일(.exe)을 만들려면:

```bash
build_exe.bat
```

빌드된 파일은 `dist` 폴더에 생성됩니다.

## 기능 설명

### 1. 데이터베이스 연결
- 데이터베이스 타입 선택 (MySQL, MariaDB, PostgreSQL, Oracle, SQLite)
- 호스트, 포트, 사용자명, 비밀번호 입력
- 데이터베이스 목록 조회 및 선택
- 연결 정보 저장 및 불러오기

### 2. ER 다이어그램 생성
- **웹 편집기**: 브라우저에서 ERwin 스타일로 편집 가능
  - 테이블 드래그 앤 드롭
  - 자동 배치
  - 이미지 저장
  - JSON 내보내기/가져오기
- **이미지 저장**: PNG 형식으로 저장

### 3. DDL 생성
- 테이블 생성 스크립트 자동 생성
- Primary Key, Foreign Key, Index 포함

### 4. 엑셀 테이블 정의서
- 테이블명, 컬럼명, 데이터 타입, NULL 여부 등 포함
- 엑셀 파일로 저장

## 프로젝트 구조

```
erd-program/
├── main.py                 # 메인 GUI 애플리케이션
├── db_connector.py         # 데이터베이스 연결 및 메타데이터 추출
├── er_diagram.py           # Graphviz 기반 ER 다이어그램 생성
├── er_diagram_matplotlib.py # Matplotlib 기반 ER 다이어그램 생성 (대체)
├── er_diagram_web.py       # 웹 기반 ER 다이어그램 편집기
├── er_diagram_viewer.py    # GUI 다이어그램 뷰어
├── ddl_generator.py        # DDL 스크립트 생성
├── excel_generator.py      # 엑셀 테이블 정의서 생성
├── config_manager.py       # 연결 정보 관리
├── logger.py              # 로깅 기능
├── requirements.txt        # Python 패키지 의존성
├── build_exe.bat         # 실행 파일 빌드 스크립트
├── ERDProgram.spec       # PyInstaller 설정 파일
└── README.md             # 프로젝트 설명서
```

## 주요 기술 스택

- **GUI**: Tkinter
- **데이터베이스**: SQLAlchemy
- **ER 다이어그램**: Graphviz, Matplotlib, Vis.js
- **엑셀 처리**: openpyxl
- **패키징**: PyInstaller

## 로그 파일

로그 파일은 `%USERPROFILE%\.erd_program\erd_program.log`에 저장됩니다.

## 라이선스

이 프로젝트는 자유롭게 사용할 수 있습니다.

## 기여하기

버그 리포트나 기능 제안은 Issues에 등록해주세요.

## 개발 이력

자세한 개발 이력은 `history.md` 파일을 참조하세요.
