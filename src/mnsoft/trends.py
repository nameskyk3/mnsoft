import xml.etree.ElementTree as ET

import requests

TRENDS_RSS_URL = "https://trends.google.com/trends/trendingsearches/daily/rss"


def get_trending_keywords(geo: str = "KR") -> list[str]:
    """Fetch today's trending search keywords for a country from Google Trends' RSS feed."""
    response = requests.get(TRENDS_RSS_URL, params={"geo": geo}, timeout=10)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    return [item.findtext("title") for item in root.iter("item")]
