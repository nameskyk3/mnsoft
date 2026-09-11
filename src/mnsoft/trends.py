from pytrends.request import TrendReq


def get_trending_keywords(country: str = "south_korea") -> list[str]:
    """Fetch today's trending search keywords for a country from Google Trends."""
    pytrends = TrendReq(hl="ko-KR", tz=540)
    df = pytrends.trending_searches(pn=country)
    return df[0].tolist()
