from unittest.mock import MagicMock, patch

from mnsoft.trends import get_trending_keywords

SAMPLE_RSS = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Daily Search Trends</title>
    <item>
      <title>\xed\x82\xa4\xec\x9b\x8c\xeb\x93\x9c1</title>
    </item>
    <item>
      <title>\xed\x82\xa4\xec\x9b\x8c\xeb\x93\x9c2</title>
    </item>
  </channel>
</rss>
"""


@patch("mnsoft.trends.requests.get")
def test_get_trending_keywords(mock_get):
    mock_response = MagicMock()
    mock_response.content = SAMPLE_RSS
    mock_get.return_value = mock_response

    result = get_trending_keywords()

    assert result == ["키워드1", "키워드2"]
