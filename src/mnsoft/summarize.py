import os

import requests

_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{_MODEL}:generateContent"

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


def generate_report(headline: str) -> str:
    """Ask Gemini (free tier, no web search) to turn a headline into a blog-ready article.

    Returns the raw model text: a softened title on the first line, a blank
    line, then flowing paragraphs (no 5W1H section headers in the body).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되어 있지 않습니다.")

    response = requests.post(
        _API_URL,
        params={"key": api_key},
        json={
            "system_instruction": {"parts": [{"text": _SYSTEM_PROMPT}]},
            "contents": [
                {"role": "user", "parts": [{"text": f"다음 이슈로 블로그 글을 써줘:\n\n{headline}"}]}
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError("Gemini가 응답을 생성하지 못했습니다.")
    parts = candidates[0]["content"]["parts"]
    return "\n\n".join(part["text"] for part in parts if "text" in part)
