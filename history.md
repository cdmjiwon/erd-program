# 작업 이력

## 2024-12-19
- 프로젝트 초기 생성
- DB 접속 및 테이블 정보 추출 기능 구현
- ER 다이어그램 생성 기능 구현
- DDL 생성 기능 구현
- 엑셀 테이블 정의서 생성 기능 구현
- GUI 애플리케이션 구현
- exe 빌드 설정
- 한글 파일명 문제 해결 (영문 이름으로 변경)
- Oracle 및 MariaDB 지원 추가
- PyInstaller 빌드 시 의존성 모듈 포함 문제 해결 (--hidden-import 옵션 추가)
- spec 파일 수정하여 sqlalchemy 및 모든 서브모듈 명시적 포함
- db_connector.py에 import 오류 처리 추가
- cx_Oracle을 oracledb로 변경 (빌드 도구 불필요, Oracle 공식 권장)
- Graphviz 경로 자동 탐지 기능 추가 (er_diagram.py)
- Graphviz 오류 시 사용자 친화적인 메시지 표시
- 접속 정보 저장/불러오기 기능 추가 (config_manager.py)
- 데이터베이스 목록 조회 및 선택 기능 추가
- ER 다이어그램 GUI 뷰어 추가 (er_diagram_viewer.py)
- Graphviz 없을 때 matplotlib로 대체 다이어그램 생성 기능 추가
- 로깅 기능 추가 (logger.py) - 오류 및 작업 이력 기록
- Graphviz 오류 시 matplotlib 자동 대체 기능 개선 (er_diagram_matplotlib.py)
- Graphviz 실행 전 검증 로직 추가 및 타임아웃 처리 개선
- matplotlib 다이어그램 생성 알고리즘 전면 개선 (레이아웃, 색상, 가독성 향상)
- 다이어그램 뷰어에 재생성 및 드래그 기능 추가
- 웹 기반 ER 다이어그램 편집기 추가 (er_diagram_web.py) - vis.js 사용
- 테이블 드래그 앤 드롭, 자동 배치, 이미지 저장 기능 제공
- 다이어그램 보기/편집/저장을 모두 웹 브라우저에서 처리하도록 통합
- 변수 참조 오류 수정 (resetLayout 함수)
- 물리 엔진 기본 비활성화로 다이어그램이 계속 움직이지 않도록 개선
- 자동 배치 시에만 물리 엔진 활성화 후 안정화되면 자동 비활성화

