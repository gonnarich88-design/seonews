# tests/test_summarizer.py
import pytest
from unittest.mock import MagicMock, patch
from modules.summarizer import summarize_article

ARTICLE = {
    "title": "Google Core Update April 2026",
    "url": "https://searchengineland.com/google-core-update",
    "content": "Google has released a major core algorithm update affecting many websites...",
    "source": "Search Engine Land",
}

MOCK_RESPONSE = MagicMock()
MOCK_RESPONSE.content = [MagicMock(text="Google ปล่อย Core Update ครั้งใหญ่ในเดือนเมษายน 2569 ส่งผลต่อเว็บไซต์จำนวนมาก")]

def test_summarize_returns_thai_text():
    with patch("modules.summarizer.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.return_value = MOCK_RESPONSE
        result = summarize_article(ARTICLE, mock_client)
    assert isinstance(result, str)
    assert len(result) > 0

def test_summarize_calls_api_with_correct_model():
    with patch("modules.summarizer.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.return_value = MOCK_RESPONSE
        summarize_article(ARTICLE, mock_client, model="claude-haiku-4-5-20251001")
        call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5-20251001"

def test_summarize_returns_fallback_on_api_error():
    with patch("modules.summarizer.anthropic.Anthropic") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.side_effect = Exception("API Error")
        result = summarize_article(ARTICLE, mock_client)
    assert result == ""
