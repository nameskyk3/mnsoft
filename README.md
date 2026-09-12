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

## "적용" 버튼 (Gemini API 연동, 무료)

각 탭의 목록에서 이슈를 선택하고 "적용" 버튼을 누르면 Gemini가 자연스러운 블로그 글을
새 창으로 보여줍니다.

- Ctrl(또는 Shift) 클릭으로 **여러 개를 한 번에 선택**할 수 있습니다. 이 경우 "적용"을 누르면
  순서대로 하나씩 처리되면서 완성되는 대로 창이 하나씩 뜹니다. 버튼에 "생성 중... (2/5)"처럼
  진행 상황이 표시되니, 여러 개 선택해두고 자리를 비우셔도 됩니다.
- **무료입니다.** [Google AI Studio](https://aistudio.google.com/apikey)에서 구글 계정으로
  로그인해 API 키를 발급받으면 되고, 신용카드 등록이 필요 없습니다. 다만 무료 요금제라
  하루/분당 호출 횟수에 제한이 있습니다 (최신 한도는 https://ai.google.dev/pricing 참고). 한도를
  넘으면 "요청이 너무 많습니다" 오류가 뜨는데, 잠시 후 다시 시도하면 됩니다.
- 이 방식은 웹 검색을 하지 않고 Gemini가 알고 있는 지식만으로 글을 쓰므로, 아주 최근에 터진
  속보성 뉴스는 정확도가 떨어질 수 있습니다.
- 사용할 모델 이름은 코드에 고정하지 않고, 매번 구글 API에서 **사용 가능한 모델 목록을 조회해서
  자동으로 선택**합니다 (모델이 단종되거나 이름이 바뀌어도 코드 수정 없이 계속 동작하도록).
  특정 모델을 지정하고 싶으면 환경변수 `GEMINI_MODEL`(예: `gemini-2.0-flash`)을 설정하세요.
- 구글 서버가 일시적으로 과부하 상태(503)일 때는 같은 모델로 잠깐 기다렸다가 자동으로
  재시도하고, 그래도 안 되면 다른 모델로 넘어갑니다.
- 발급받은 키는 환경변수 `GEMINI_API_KEY`로 등록해야 합니다.

  Windows (PowerShell, 현재 세션에만 적용):
  ```powershell
  $env:GEMINI_API_KEY = "여기에-발급받은-키"
  ```

  Windows에서 항상 적용되게 하려면 (새 터미널부터 적용):
  ```powershell
  setx GEMINI_API_KEY "여기에-발급받은-키"
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

**Pexels에 어울리는 사진이 없으면 자동으로 AI가 이미지를 만듭니다** ([Pollinations.ai](https://pollinations.ai),
가입/키 발급 필요 없는 무료 서비스). 아무 설정도 필요 없고, 완전히 자동으로 동작합니다.

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
