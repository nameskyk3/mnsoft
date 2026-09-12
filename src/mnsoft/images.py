import os
import urllib.parse

import requests

_SEARCH_URL = "https://api.pexels.com/v1/search"
_AI_IMAGE_URL = "https://image.pollinations.ai/prompt/{prompt}"


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
            "source": "pexels",
        }
        for photo in data.get("photos", [])
    ]


def download_image_bytes(url: str) -> bytes:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.content


def generate_ai_image(prompt: str, width: int = 768, height: int = 512) -> bytes:
    """Generate an illustration via Pollinations.ai - free, no signup or API key."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = _AI_IMAGE_URL.format(prompt=encoded_prompt)
    response = requests.get(
        url,
        params={"width": width, "height": height, "nologo": "true"},
        timeout=60,
    )
    response.raise_for_status()
    return response.content
