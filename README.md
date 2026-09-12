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

   뉴스 / 쇼핑 / 엔터 / 스포츠 분야별 오늘의 이슈(구글 뉴스 RSS 기반)를 탭으로 보여주는 로컬 화면.
   상단 검색창에 키워드를 입력하면 해당 키워드 탭이 새로 열리고, 같은 키워드로 다시 검색하면
   새 탭을 만들지 않고 기존 탭 내용을 새로고침합니다:

   ```bash
   python -m mnsoft.gui
   ```

5. 테스트 실행

   ```bash
   pytest
   ```

6. 린트 실행

   ```bash
   ruff check .
   ```

## "적용" 버튼 (Claude API 연동, 유료)

각 탭의 목록에서 이슈를 선택하고 "적용" 버튼을 누르면 Claude가 웹 검색으로 사실을 확인한 뒤
자연스러운 블로그 글을 새 창으로 보여줍니다.

- Ctrl(또는 Shift) 클릭으로 **여러 개를 한 번에 선택**할 수 있습니다. 이 경우 "적용"을 누르면
  순서대로 하나씩 처리되면서 완성되는 대로 창이 하나씩 뜹니다. 버튼에 "생성 중... (2/5)"처럼
  진행 상황이 표시되니, 여러 개 선택해두고 자리를 비우셔도 됩니다.
- 이 기능은 다른 기능과 달리 **무료가 아닙니다.** [console.anthropic.com](https://console.anthropic.com)에서
  API 키를 발급받아야 하고, 요청마다 소액이 과금됩니다 (문서 1개당 대략 몇 십 원~몇 백 원 수준).
- 발급받은 키는 환경변수 `ANTHROPIC_API_KEY`로 등록해야 합니다.

  Windows (PowerShell, 현재 세션에만 적용):
  ```powershell
  $env:ANTHROPIC_API_KEY = "여기에-발급받은-키"
  ```

  Windows에서 항상 적용되게 하려면 (새 터미널부터 적용):
  ```powershell
  setx ANTHROPIC_API_KEY "여기에-발급받은-키"
  ```

### 사진 자동 삽입 (Pexels, 무료)

생성된 글에는 헤드라인과 관련된 사진이 문단 사이사이에 자동으로 들어갑니다. 저작권 걱정 없이
상업적으로도 무료로 쓸 수 있는 [Pexels](https://www.pexels.com) 사진을 사용합니다.

1. https://www.pexels.com/api 에서 무료 계정으로 API 키 발급 (신용카드 등록 불필요)
2. 환경변수로 등록:
   ```powershell
   setx PEXELS_API_KEY "여기에-발급받은-키"
   ```

`PEXELS_API_KEY`를 등록하지 않아도 나머지 기능은 그대로 동작하고, 사진만 빠집니다.

사진 아래에 있는 **"사진 복사 (클립보드)"** 버튼을 누르면 그 사진만 클립보드에 복사됩니다
(창의 텍스트를 Ctrl+C로 복사할 때는 사진이 같이 복사되지 않아서, 사진은 이 버튼으로 따로
복사한 뒤 블로그 글쓰기 화면에서 Ctrl+V로 붙여넣으면 됩니다). 이 기능은 Windows 전용입니다.

## 빠른 실행 (Windows)

처음 클론 이후에는 `run.bat`을 더블클릭(또는 터미널에서 `run.bat` 입력)하면
가상환경 생성/활성화, 최신 코드 받기, 의존성 설치, 트렌드 화면 실행까지 한 번에 처리됩니다.

```powershell
run.bat
```

## 프로젝트 구조

```
mnsoft/
├── src/mnsoft/      # 소스 코드
├── tests/           # 테스트 코드
├── pyproject.toml   # 프로젝트/의존성 설정
├── run.bat          # Windows용 원클릭 실행 스크립트
└── .github/workflows/ci.yml  # GitHub Actions CI (자동 테스트)
```

## CI

`main` 브랜치로 push 되거나 PR이 열리면 GitHub Actions가 Python 3.11 / 3.12 / 3.13에서 자동으로 린트와 테스트를 실행합니다. 모두 무료(GitHub의 public 저장소 Actions 무료 제공량) 범위에서 동작합니다.
