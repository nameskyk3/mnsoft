from unittest.mock import MagicMock, patch

import pytest

from mnsoft.summarize import generate_report

SAMPLE_RESPONSE = {
    "candidates": [
        {"content": {"parts": [{"text": "문서 내용"}]}},
    ]
}


@patch("mnsoft.summarize.requests.post")
def test_generate_report(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_RESPONSE
    mock_post.return_value = mock_response

    result = generate_report("테스트 헤드라인")

    assert result == "문서 내용"
    _, kwargs = mock_post.call_args
    assert kwargs["params"]["key"] == "fake-key"
    assert "테스트 헤드라인" in kwargs["json"]["contents"][0]["parts"][0]["text"]


def test_generate_report_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        generate_report("테스트 헤드라인")
