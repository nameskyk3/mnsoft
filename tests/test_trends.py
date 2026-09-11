from unittest.mock import MagicMock, patch

import pandas as pd

from mnsoft.trends import get_trending_keywords


@patch("mnsoft.trends.TrendReq")
def test_get_trending_keywords(mock_trend_req):
    mock_instance = MagicMock()
    mock_instance.trending_searches.return_value = pd.DataFrame(["키워드1", "키워드2"])
    mock_trend_req.return_value = mock_instance

    result = get_trending_keywords()

    assert result == ["키워드1", "키워드2"]
