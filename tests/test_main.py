# tests/test_main.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_run_pipeline_with_no_new_articles(capsys):
    with patch("main.fetch_articles", return_value=[]), \
         patch("main.filter_articles", return_value=[]), \
         patch("main.Database") as MockDB:
        mock_db = MagicMock()
        MockDB.return_value = mock_db
        mock_db.init = MagicMock()
        mock_db.close = MagicMock()

        from main import run_pipeline
        await run_pipeline()

        captured = capsys.readouterr()
        assert "ไม่มีข่าวใหม่" in captured.out


@pytest.mark.asyncio
async def test_run_pipeline_sends_when_articles_found():
    mock_article = {
        "title": "SEO Update", "url": "https://a.com/1",
        "content": "content", "source": "SEL"
    }

    with patch("main.fetch_articles", return_value=[mock_article]), \
         patch("main.filter_articles", return_value=[mock_article]), \
         patch("main.summarize_article", return_value="สรุปภาษาไทย"), \
         patch("main.format_digest", return_value="digest message"), \
         patch("main.send_digest", new_callable=AsyncMock) as mock_send, \
         patch("main.Database") as MockDB, \
         patch("main.anthropic.Anthropic"), \
         patch("main.os.getenv", return_value="fake-value"):
        mock_db = MagicMock()
        MockDB.return_value = mock_db
        mock_db.init = MagicMock()
        mock_db.is_sent.return_value = False
        mock_db.mark_sent = MagicMock()
        mock_db.close = MagicMock()

        from main import run_pipeline
        await run_pipeline()

        mock_send.assert_called_once()
