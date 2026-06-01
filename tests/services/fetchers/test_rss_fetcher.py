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
                    "title": "<b>Summary</b> &amp; article",
                    "summary": "<p>Summary&nbsp;<strong>body</strong></p>",
                    "link": "https://example.com/summary",
                    "published": "2026-05-02",
                },
                {
                    "title": "Updated article",
                    "description": "Description\n\nwith     whitespace",
                    "link": "https://example.com/updated",
                    "updated": "2026-05-01",
                },
                {
                    "title": "Content article",
                    "content": [{"value": "<div>Content<br>body</div>"}],
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
        "Summary body",
        "Description with whitespace",
        "Content body",
    ]
    assert articles[0].title == "Summary & article"
    assert [article.published for article in articles] == [
        "2026-05-02",
        "2026-05-01",
        "",
    ]


def test_fetch_news_assigns_category_from_feed_filename(monkeypatch, tmp_path):
    feed_dir = tmp_path / "feeds"
    feed_dir.mkdir()
    (feed_dir / "business.txt").write_text("https://example.com/biz")
    (feed_dir / "general.txt").write_text("https://example.com/gen")

    def parse(url):
        slug = url.rsplit("/", 1)[-1]
        return SimpleNamespace(
            bozo=False,
            entries=[
                {
                    "title": f"Title {slug}",
                    "summary": "body",
                    "link": f"https://example.com/{slug}/article",
                }
            ],
        )

    monkeypatch.setattr("newsbot.services.fetchers.rss_fetcher.feedparser.parse", parse)

    articles = RSSFetcher(config_dir=feed_dir).fetch_news()

    categories = {article.url: article.category for article in articles}
    assert categories == {
        "https://example.com/biz/article": "business",
        "https://example.com/gen/article": "general",
    }


def test_fetch_news_skips_failed_feeds(monkeypatch, tmp_path):
    feed_dir = tmp_path / "feeds"
    feed_dir.mkdir()
    (feed_dir / "general.txt").write_text("https://example.com/rss")

    def parse(_url):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr("newsbot.services.fetchers.rss_fetcher.feedparser.parse", parse)

    assert RSSFetcher(config_dir=feed_dir).fetch_news() == []
