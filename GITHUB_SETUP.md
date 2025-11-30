# GitHub 저장소 업로드 가이드

## 1. GitHub에서 새 저장소 생성

1. GitHub.com에 로그인
2. 우측 상단의 "+" 버튼 클릭 → "New repository" 선택
3. 저장소 이름 입력 (예: `erd-program`)
4. Public 또는 Private 선택
5. "Initialize this repository with a README" 체크 해제 (이미 README.md가 있음)
6. "Create repository" 클릭

## 2. 로컬 저장소와 GitHub 연결

GitHub에서 생성한 저장소의 URL을 복사한 후 아래 명령어 실행:

```bash
git remote add origin https://github.com/YOUR_USERNAME/erd-program.git
```

또는 SSH를 사용하는 경우:

```bash
git remote add origin git@github.com:YOUR_USERNAME/erd-program.git
```

## 3. GitHub에 업로드

```bash
git branch -M main
git push -u origin main
```

## 4. 인증

GitHub에 업로드할 때 인증이 필요할 수 있습니다:
- Personal Access Token 사용 (권장)
- 또는 GitHub CLI 사용

### Personal Access Token 생성 방법:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" 클릭
3. 필요한 권한 선택 (repo 권한 필요)
4. 토큰 생성 후 복사
5. push 시 비밀번호 대신 토큰 입력

## 완료!

이제 GitHub에서 프로젝트를 확인할 수 있습니다.

