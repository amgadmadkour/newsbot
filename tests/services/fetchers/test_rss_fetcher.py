from types import SimpleNamespace

import pytest

from newsbot.services.fetchers.rss_fetcher import RSSFetcher


def test_load_all_feed_urls_ignores_comments_and_duplicates(tmp_path):
    feed_dir = tmp_path / "feeds"
    feed_dir.mkdir()
    (feed_dir / "general.txt").write_text(
        "\n".join(
            [
                "# comment",
                "  # indented comment",
                "https://example.com/rss",
                "https://example.com/rss",
                "https://example.com/other",
            ]
        )
    )

    fetcher = RSSFetcher(config_dir=feed_dir)

    assert fetcher.rss_urls == [
        "https://example.com/rss",
        "https://example.com/other",
    ]


def test_load_all_feed_urls_raises_for_missing_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        RSSFetcher(config_dir=tmp_path / "missing")


def test_fetch_news_uses_fallback_fields(monkeypatch, tmp_path):
    feed_dir = tmp_path / "feeds"
    feed_dir.mkdir()
    (feed_dir / "general.txt").write_text("https://example.com/rss")

    def parse(url):
        assert url == "https://example.com/rss"
        return SimpleNamespace(
            bozo=False,
            entries=[
                {
                    "title": "Summary article",
                    "summary": "Summary",
                    "link": "https://example.com/summary",
                    "published": "2026-05-02",
                },
                {
                    "title": "Updated article",
                    "description": "Description",
                    "link": "https://example.com/updated",
                    "updated": "2026-05-01",
                },
                {
                    "title": "Content article",
                    "content": [{"value": "Content body"}],
                    "link": "https://example.com/content",
                },
                {
                    "title": "No link",
                    "summary": "Missing required link",
                },
            ],
        )

    monkeypatch.setattr("newsbot.services.fetchers.rss_fetcher.feedparser.parse", parse)

    articles = RSSFetcher(config_dir=feed_dir).fetch_news()

    assert [article.url for article in articles] == [
        "https://example.com/summary",
        "https://example.com/updated",
        "https://example.com/content",
    ]
    assert [article.body for article in articles] == [
        "Summary",
        "Description",
        "Content body",
    ]
    assert [article.published for article in articles] == [
        "2026-05-02",
        "2026-05-01",
        "",
    ]


def test_fetch_news_skips_failed_feeds(monkeypatch, tmp_path):
    feed_dir = tmp_path / "feeds"
    feed_dir.mkdir()
    (feed_dir / "general.txt").write_text("https://example.com/rss")

    def parse(_url):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr("newsbot.services.fetchers.rss_fetcher.feedparser.parse", parse)

    assert RSSFetcher(config_dir=feed_dir).fetch_news() == []
