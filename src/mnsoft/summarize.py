import anthropic

_MODEL = "claude-opus-5"

_SYSTEM_PROMPT = (
    "너는 블로그 글쓰기 도우미야. 사용자가 준 이슈(헤드라인)에 대해 필요하면 웹 검색으로 "
    "사실을 확인한 뒤, 블로그에 바로 올릴 수 있는 자연스러운 글을 써줘.\n\n"
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
    """Ask Claude to turn a headline into a soft, blog-ready Korean article.

    Returns the raw model text: a softened title on the first line, a blank
    line, then flowing paragraphs (no 5W1H section headers in the body).
    """
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=_MODEL,
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}],
        messages=[{"role": "user", "content": f"다음 이슈로 블로그 글을 써줘:\n\n{headline}"}],
    )
    return "\n\n".join(block.text for block in response.content if block.type == "text")
