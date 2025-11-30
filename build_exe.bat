@echo off
chcp 65001 >nul
echo ERD 프로그램 exe 빌드 시작...
echo.
echo spec 파일을 사용하여 빌드합니다...
pyinstaller --clean --noconfirm ERDProgram.spec
echo.
if exist dist\ERDProgram.exe (
    echo 빌드 완료! dist 폴더에 ERDProgram.exe 파일이 생성되었습니다.
) else (
    echo 빌드 실패. 오류를 확인해주세요.
)
pause

