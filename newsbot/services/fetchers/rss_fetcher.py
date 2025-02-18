from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import feedparser

from newsbot.models.news_article import NewsArticle

from .base import NewsFetcher


@dataclass
class RSSFetcher(NewsFetcher):
    """Fetches news articles from RSS feeds.

    Args:
        config_dir (Path): Directory containing RSS feed URLs files.
    """

    config_dir: Path = field(default=Path("config/feeds"))

    def __post_init__(self):
        """Load RSS URLs after initialization."""
        self.rss_urls = self._load_all_feed_urls()

    def _load_all_feed_urls(self) -> List[str]:
        """Load RSS feed URLs from all .txt files in config directory."""
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")

        urls = []
        for feed_file in self.config_dir.glob("*.txt"):
            with feed_file.open() as f:
                urls.extend(
                    [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                )
        return urls

    def fetch_news(self) -> List[NewsArticle]:
        """Fetch and parse news articles from all RSS feeds."""
        articles = []
        for url in self.rss_urls:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                try:
                    article = NewsArticle(
                        title=entry.title,
                        body=entry.summary,
                        url=entry.link,
                        published=entry.published,
                    )
                    articles.append(article)
                except AttributeError:
                    # Skip articles with missing required fields
                    continue
        return articles
