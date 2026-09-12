import os

import requests

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
_MAX_MODEL_ATTEMPTS = 5

_SYSTEM_PROMPT = (
    "너는 블로그 글쓰기 도우미야. 사용자가 준 이슈(헤드라인)에 대해 블로그에 바로 올릴 수 있는 "
    "자연스러운 글을 써줘.\n\n"
    "규칙:\n"
    "- 첫 줄에는 원래 헤드라인을 그대로 쓰지 말고, 부드럽고 자연스러운 제목으로 바꿔서 "
    "순수 텍스트로만 적어 (기호나 굵게 표시 없이).\n"
    "- 둘째 줄은 비워두고, 그 다음부터 본문을 이어서 써.\n"
    "- 언제·어디서·무엇을·어떻게·왜에 해당하는 내용은 참고만 하고, 그걸 소제목이나 항목으로 "
    "나누지 말고 사람에게 말하듯 자연스럽게 이어지는 문단 속에 녹여서 써.\n"
    "- 문장이 뚝뚝 끊기지 않게 3~5개 문단 정도의 부드러운 흐름으로 작성해.\n"
    "- 확인되지 않은 내용은 단정하지 말고 '~로 알려졌다', '~라는 이야기가 있다'처럼 "
    "완곡하게 표현해."
)

_cached_model: str | None = None


def _list_candidate_models(api_key: str) -> list[str]:
    """List models this key can call generateContent on, flash models first."""
    response = requests.get(f"{_BASE_URL}/models", params={"key": api_key}, timeout=15)
    response.raise_for_status()
    models = response.json().get("models", [])

    names = [
        model["name"].removeprefix("models/")
        for model in models
        if "generateContent" in model.get("supportedGenerationMethods", [])
    ]
    if not names:
        raise RuntimeError("사용 가능한 Gemini 모델을 찾지 못했습니다.")

    flash_names = [name for name in names if "flash" in name]
    other_names = [name for name in names if name not in flash_names]
    return flash_names + other_names


def _call_gemini(model: str, api_key: str, payload: dict) -> requests.Response:
    return requests.post(
        f"{_BASE_URL}/models/{model}:generateContent",
        params={"key": api_key},
        json=payload,
        timeout=60,
    )


def generate_report(headline: str) -> str:
    """Ask Gemini (free tier, no web search) to turn a headline into a blog-ready article.

    Model names get retired/renamed over time, so instead of trusting one
    hardcoded name, this first retries the last-known-working model, and
    only queries the models list (an extra network call) if that fails -
    trying candidates from it in order until one actually answers.

    Returns the raw model text: a softened title on the first line, a blank
    line, then flowing paragraphs (no 5W1H section headers in the body).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")

    payload = {
        "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
        "contents": [
            {"role": "user", "parts": [{"text": f"다음 이슈로 블로그 글을 써줘:\n\n{headline}"}]}
        ],
    }

    tried: set[str] = set()
    response: requests.Response | None = None

    def try_model(model: str | None) -> bool:
        nonlocal response
        global _cached_model
        if not model or model in tried:
            return False
        tried.add(model)
        response = _call_gemini(model, api_key, payload)
        if response.status_code == 404:
            return False
        response.raise_for_status()
        _cached_model = model
        return True

    forced_model = os.environ.get("GEMINI_MODEL")
    success = try_model(forced_model) or try_model(_cached_model)

    if not success:
        for model in _list_candidate_models(api_key):
            if len(tried) >= _MAX_MODEL_ATTEMPTS:
                break
            if try_model(model):
                success = True
                break

    if not success or response is None:
        raise RuntimeError(
            "이 API 키로 사용 가능한 Gemini 모델을 찾지 못했습니다.\n"
            "Google AI Studio에서 계정 상태를 확인해주세요."
        )

    data = response.json()
    result_candidates = data.get("candidates", [])
    if not result_candidates:
        raise RuntimeError("Gemini가 응답을 생성하지 못했습니다.")
    parts = result_candidates[0]["content"]["parts"]
    return "\n\n".join(part["text"] for part in parts if "text" in part)
