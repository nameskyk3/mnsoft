from unittest.mock import MagicMock, patch

import pytest

import mnsoft.summarize as summarize_module
from mnsoft.summarize import _list_candidate_models, generate_report

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


@pytest.fixture(autouse=True)
def _reset_model_cache(monkeypatch):
    monkeypatch.setattr(summarize_module, "_cached_model", None)


def _make_response(status_code: int, json_data: dict | None = None) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    if status_code >= 400 and status_code != 404:
        response.raise_for_status.side_effect = RuntimeError(f"HTTP {status_code}")
    return response


@patch("mnsoft.summarize.requests.post")
def test_generate_report_with_forced_model(mock_post, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")
    mock_post.return_value = _make_response(200, SAMPLE_RESPONSE)

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
@patch("mnsoft.summarize.requests.post")
def test_generate_report_falls_back_past_404(mock_post, mock_get, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    mock_get.return_value = _make_response(200, SAMPLE_MODELS_RESPONSE)
    # first candidate (gemini-2.0-flash, flash models come first) 404s, second succeeds
    mock_post.side_effect = [_make_response(404), _make_response(200, SAMPLE_RESPONSE)]

    result = generate_report("테스트 헤드라인")

    assert result == "문서 내용"
    assert mock_post.call_count == 2


@patch("mnsoft.summarize.requests.get")
def test_list_candidate_models_puts_flash_first(mock_get):
    mock_get.return_value = _make_response(200, SAMPLE_MODELS_RESPONSE)

    result = _list_candidate_models("fake-key")

    assert result == ["gemini-2.0-flash", "gemini-1.0-pro"]
