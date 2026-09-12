from unittest.mock import MagicMock, patch

from mnsoft.summarize import generate_report


@patch("mnsoft.summarize.anthropic.Anthropic")
def test_generate_report(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_block = MagicMock(type="text", text="문서 내용")
    mock_response = MagicMock(content=[mock_block])
    mock_client.messages.create.return_value = mock_response
    mock_anthropic_cls.return_value = mock_client

    result = generate_report("테스트 헤드라인")

    assert result == "문서 내용"
    _, kwargs = mock_client.messages.create.call_args
    assert kwargs["model"] == "claude-opus-5"
    assert "테스트 헤드라인" in kwargs["messages"][0]["content"]
