from unittest.mock import MagicMock, patch

from mnsoft.news import CATEGORIES, get_headlines, search_headlines

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Google News</title>
    <item>
      <title>헤드라인1</title>
    </item>
    <item>
      <title>헤드라인2</title>
    </item>
  </channel>
</rss>
""".encode()


@patch("mnsoft.news.requests.get")
def test_get_headlines(mock_get):
    mock_response = MagicMock()
    mock_response.content = SAMPLE_RSS
    mock_get.return_value = mock_response

    result = get_headlines("뉴스")

    assert result == ["헤드라인1", "헤드라인2"]


@patch("mnsoft.news.requests.get")
def test_get_headlines_respects_limit(mock_get):
    mock_response = MagicMock()
    mock_response.content = SAMPLE_RSS
    mock_get.return_value = mock_response

    result = get_headlines("뉴스", limit=1)

    assert result == ["헤드라인1"]


def test_all_categories_are_configured():
    for category in CATEGORIES:
        assert isinstance(category, str)


@patch("mnsoft.news.requests.get")
def test_search_headlines(mock_get):
    mock_response = MagicMock()
    mock_response.content = SAMPLE_RSS
    mock_get.return_value = mock_response

    result = search_headlines("아이폰")

    assert result == ["헤드라인1", "헤드라인2"]
    _, kwargs = mock_get.call_args
    assert kwargs["params"]["q"] == "아이폰"
