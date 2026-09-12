import anthropic

_MODEL = "claude-opus-5"

_SYSTEM_PROMPT = (
    "너는 뉴스 정리 도우미야. 사용자가 준 이슈(헤드라인)에 대해 필요하면 웹 검색으로 사실을 "
    "확인하고, 아래 형식의 한국어 문서를 작성해. 확인할 수 없는 내용은 추측해서 단정하지 말고 "
    "'확인되지 않음'이라고 적어.\n\n"
    "## 언제\n\n## 어디서\n\n## 무엇을\n\n## 어떻게\n\n## 왜\n"
)


def generate_report(headline: str) -> str:
    """Ask Claude to research a headline and turn it into a 5W1H-style Korean document."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=_MODEL,
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 3}],
        messages=[{"role": "user", "content": f"다음 이슈를 정리해줘:\n\n{headline}"}],
    )
    return "\n\n".join(block.text for block in response.content if block.type == "text")
