from unittest.mock import MagicMock, patch

import pytest

from mnsoft.images import download_image_bytes, search_images

SAMPLE_RESPONSE = {
    "photos": [
        {
            "src": {"medium": "https://images.pexels.com/photos/1/medium.jpg"},
            "photographer": "홍길동",
            "url": "https://www.pexels.com/photo/1",
        },
    ]
}


@patch("mnsoft.images.requests.get")
def test_search_images(mock_get, monkeypatch):
    monkeypatch.setenv("PEXELS_API_KEY", "fake-key")
    mock_response = MagicMock()
    mock_response.json.return_value = SAMPLE_RESPONSE
    mock_get.return_value = mock_response

    result = search_images("고양이")

    assert result == [
        {
            "url": "https://images.pexels.com/photos/1/medium.jpg",
            "photographer": "홍길동",
            "page_url": "https://www.pexels.com/photo/1",
        }
    ]
    _, kwargs = mock_get.call_args
    assert kwargs["headers"]["Authorization"] == "fake-key"
    assert kwargs["params"]["query"] == "고양이"


def test_search_images_requires_api_key(monkeypatch):
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        search_images("고양이")


@patch("mnsoft.images.requests.get")
def test_download_image_bytes(mock_get):
    mock_response = MagicMock()
    mock_response.content = b"fake-image-bytes"
    mock_get.return_value = mock_response

    result = download_image_bytes("https://images.pexels.com/photos/1/medium.jpg")

    assert result == b"fake-image-bytes"
