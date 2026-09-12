import xml.etree.ElementTree as ET

import requests

CATEGORIES = ["뉴스", "쇼핑", "엔터", "스포츠"]

_CATEGORY_CONFIG: dict[str, tuple[str, dict[str, str]]] = {
    "뉴스": ("https://news.google.com/rss", {}),
    "쇼핑": ("https://news.google.com/rss/search", {"q": "쇼핑"}),
    "엔터": ("https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT", {}),
    "스포츠": ("https://news.google.com/rss/headlines/section/topic/SPORTS", {}),
}

_SEARCH_URL = "https://news.google.com/rss/search"


def _fetch_titles(url: str, extra_params: dict[str, str], limit: int) -> list[str]:
    params = {"hl": "ko", "gl": "KR", "ceid": "KR:ko", **extra_params}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    return [item.findtext("title") for item in root.iter("item")][:limit]


def get_headlines(category: str, limit: int = 15) -> list[str]:
    """Fetch today's headlines for a category from Google News' RSS feed."""
    url, extra_params = _CATEGORY_CONFIG[category]
    return _fetch_titles(url, extra_params, limit)


def search_headlines(query: str, limit: int = 15) -> list[str]:
    """Fetch today's headlines matching a free-text search query."""
    return _fetch_titles(_SEARCH_URL, {"q": query}, limit)
