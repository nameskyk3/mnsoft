import os

import requests

_SEARCH_URL = "https://api.pexels.com/v1/search"


def search_images(query: str, count: int = 2) -> list[dict]:
    """Search Pexels for royalty-free photos matching a query.

    Pexels photos are free to use, including commercially, with no
    attribution required (attribution is still included as good practice).
    """
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY 환경변수가 설정되어 있지 않습니다.")

    response = requests.get(
        _SEARCH_URL,
        headers={"Authorization": api_key},
        params={"query": query, "per_page": count},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    return [
        {
            "url": photo["src"]["medium"],
            "photographer": photo["photographer"],
            "page_url": photo["url"],
        }
        for photo in data.get("photos", [])
    ]


def download_image_bytes(url: str) -> bytes:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content
