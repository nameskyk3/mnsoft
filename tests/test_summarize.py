from unittest.mock import MagicMock, patch

import pytest

import mnsoft.summarize as summarize_module
from mnsoft.summarize import _discover_model, generate_report

SAMPLE_RESPONSE = {
    "candidates": [
        {"content": {"parts": [{"text": "문서 내용"}]}},
    ]
}

SAMPLE_MODELS_RESPONSE = {
    "models": [
        {"name": "models/gemini-1.0-pro", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/gemini-2.0-flash", "supportedGenerationMethods": ["generateContent"]},
        {"name": "models/embedding-001", "supportedGenerationMethods": ["embedContent"]},
    ]
}


@patch("mnsoft.summarize.requests.post")
def test_generate_report(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_RESPONSE
    mock_post.return_value = mock_response

    result = generate_report("테스트 헤드라인")

    assert result == "문서 내용"
    args, kwargs = mock_post.call_args
    assert args[0].endswith("gemini-test-model:generateContent")
    assert kwargs["params"]["key"] == "fake-key"
    assert "테스트 헤드라인" in kwargs["json"]["contents"][0]["parts"][0]["text"]


def test_generate_report_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        generate_report("테스트 헤드라인")


@patch("mnsoft.summarize.requests.get")
def test_discover_model_prefers_flash(mock_get, monkeypatch):
    monkeypatch.setattr(summarize_module, "_cached_model", None)
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_MODELS_RESPONSE
    mock_get.return_value = mock_response

    result = _discover_model("fake-key")

    assert result == "gemini-2.0-flash"
