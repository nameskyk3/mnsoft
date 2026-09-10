# mnsoft

Python 프로젝트입니다.

## 요구 사항

- Python 3.11 이상 (권장: [python.org](https://www.python.org/downloads/)에서 배포하는 최신 안정 버전)
- pip (Python 설치 시 함께 제공됨)

## 노트북에서 개발 환경 설정하기

1. 저장소 클론

   ```bash
   git clone https://github.com/nameskyk3/mnsoft.git
   cd mnsoft
   ```

2. 가상환경 생성 및 활성화

   ```bash
   python -m venv .venv
   # macOS / Linux
   source .venv/bin/activate
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   ```

3. 개발용 의존성 설치 (프로젝트 + 테스트/린트 도구)

   ```bash
   pip install -e ".[dev]"
   ```

4. 실행

   ```bash
   python -m mnsoft.main
   ```

5. 테스트 실행

   ```bash
   pytest
   ```

6. 린트 실행

   ```bash
   ruff check .
   ```

## 프로젝트 구조

```
mnsoft/
├── src/mnsoft/      # 소스 코드
├── tests/           # 테스트 코드
├── pyproject.toml   # 프로젝트/의존성 설정
└── .github/workflows/ci.yml  # GitHub Actions CI (자동 테스트)
```

## CI

`main` 브랜치로 push 되거나 PR이 열리면 GitHub Actions가 Python 3.11 / 3.12 / 3.13에서 자동으로 린트와 테스트를 실행합니다. 모두 무료(GitHub의 public 저장소 Actions 무료 제공량) 범위에서 동작합니다.
