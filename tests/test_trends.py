from unittest.mock import MagicMock, patch

import pytest

from mnsoft.trends import get_search_trend

SAMPLE_RESPONSE = {
    "results": [
        {
            "title": "고양이",
            "data": [
                {"period": "2026-06-01", "ratio": 45.2},
                {"period": "2026-06-08", "ratio": 100.0},
            ],
        }
    ]
}


@patch("mnsoft.trends.requests.post")
def test_get_search_trend(mock_post, monkeypatch):
    monkeypatch.setenv("NAVER_CLIENT_ID", "fake-id")
    monkeypatch.setenv("NAVER_CLIENT_SECRET", "fake-secret")
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_RESPONSE
    mock_post.return_value = mock_response

    result = get_search_trend("고양이")

    assert result == SAMPLE_RESPONSE["results"][0]["data"]
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["X-Naver-Client-Id"] == "fake-id"
    assert kwargs["headers"]["X-Naver-Client-Secret"] == "fake-secret"
    assert kwargs["json"]["keywordGroups"][0]["keywords"] == ["고양이"]


def test_get_search_trend_requires_credentials(monkeypatch):
    monkeypatch.delenv("NAVER_CLIENT_ID", raising=False)
    monkeypatch.delenv("NAVER_CLIENT_SECRET", raising=False)

    with pytest.raises(RuntimeError):
        get_search_trend("고양이")
