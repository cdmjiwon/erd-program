@echo off
chcp 65001 >nul
echo ERD 프로그램 exe 빌드 시작 (spec 파일 사용)...

echo 1단계: spec 파일 생성...
pyinstaller --name=ERDProgram --windowed --icon=NONE ^
    --hidden-import=sqlalchemy ^
    --hidden-import=pymysql ^
    --hidden-import=psycopg2 ^
    --hidden-import=cx_Oracle ^
    --hidden-import=graphviz ^
    --hidden-import=openpyxl ^
    --hidden-import=sqlalchemy.dialects.mysql ^
    --hidden-import=sqlalchemy.dialects.postgresql ^
    --hidden-import=sqlalchemy.dialects.oracle ^
    --hidden-import=sqlalchemy.dialects.sqlite ^
    --hidden-import=sqlalchemy.dialects.mysql.pymysql ^
    --hidden-import=sqlalchemy.dialects.postgresql.psycopg2 ^
    --hidden-import=sqlalchemy.dialects.oracle.cx_oracle ^
    --collect-all=sqlalchemy ^
    --collect-all=pymysql ^
    --collect-all=psycopg2 ^
    --collect-all=cx_Oracle ^
    --collect-all=openpyxl ^
    --noconfirm main.py

echo 2단계: spec 파일 수정 및 재빌드...
if exist ERDProgram.spec (
    echo spec 파일이 생성되었습니다. 빌드를 진행합니다...
    pyinstaller --clean --noconfirm ERDProgram.spec
    echo 빌드 완료! dist 폴더에 exe 파일이 생성되었습니다.
) else (
    echo 오류: spec 파일 생성 실패
)

pause

