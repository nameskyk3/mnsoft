import datetime
import os

import requests

_TREND_URL = "https://openapi.naver.com/v1/datalab/search"


def get_search_trend(keyword: str, days: int = 90, time_unit: str = "week") -> list[dict]:
    """Fetch relative search-volume trend for a keyword via Naver DataLab (free).

    Returns a list of {"period": "YYYY-MM-DD", "ratio": float} points, where
    ratio is relative to the highest point in the range (scaled to 100).
    """
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError(
            "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 설정되어 있지 않습니다."
        )

    end_date = datetime.date.today()  # noqa: DTZ011 - local calendar date is what we want here
    start_date = end_date - datetime.timedelta(days=days)

    response = requests.post(
        _TREND_URL,
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
            "Content-Type": "application/json",
        },
        json={
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "timeUnit": time_unit,
            "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])
    if not results:
        raise RuntimeError("트렌드 데이터를 가져오지 못했습니다.")
    return results[0].get("data", [])
