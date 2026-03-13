import importlib.util
import pathlib

import pytest


MODULE_PATH = pathlib.Path(__file__).with_name("app.py")
SPEC = importlib.util.spec_from_file_location("mcp_server_app", MODULE_PATH)
app_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(app_module)


@pytest.mark.asyncio
async def test_get_news_returns_error_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)

    result = await app_module.get_news("AI")

    assert result["isError"] is True
    assert result["content"][0]["text"] == "NEWS_API_KEY not set"


@pytest.mark.asyncio
async def test_get_news_falls_back_to_english_when_requested_language_is_empty(monkeypatch):
    class FakeResponse:
        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    class FakeAsyncClient:
        def __init__(self):
            self.calls = []

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params, timeout):
            self.calls.append({"url": url, "params": params, "timeout": timeout})

            if params["language"] == "no":
                return FakeResponse({"articles": []})

            return FakeResponse(
                {
                    "articles": [
                        {"title": "English fallback article", "url": "https://example.com/fallback"}
                    ]
                }
            )

    fake_client = FakeAsyncClient()

    monkeypatch.setenv("NEWS_API_KEY", "test-key")
    monkeypatch.setattr(app_module.httpx, "AsyncClient", lambda: fake_client)

    result = await app_module.get_news("kunstig intelligens", "no")

    assert result["isError"] is False
    assert "English fallback article" in result["content"][0]["text"]
    assert [call["params"]["language"] for call in fake_client.calls] == ["no", "en"]
