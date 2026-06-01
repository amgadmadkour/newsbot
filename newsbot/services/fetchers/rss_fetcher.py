import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import feedparser
from bs4 import BeautifulSoup

from newsbot.models.news_article import NewsArticle

from .base import NewsFetcher

logger = logging.getLogger(__name__)


@dataclass
class RSSFetcher(NewsFetcher):
    """Fetches news articles from RSS feeds.

    Args:
        config_dir (Path): Directory containing RSS feed URLs files.
    """

    config_dir: Path = field(default_factory=lambda: Path("config/feeds"))

    def __post_init__(self) -> None:
        """Load RSS URLs after initialization."""
        self.rss_urls = self._load_all_feed_urls()

    def _load_all_feed_urls(self) -> List[str]:
        """Load RSS feed URLs from all .txt files in config directory.

        Each feed file's name (without extension) becomes the category for the
        URLs it contains, e.g. ``business.txt`` -> ``business``.
        """
        if not self.config_dir.exists():
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")

        urls = []
        seen = set()
        self.url_categories = {}
        for feed_file in sorted(self.config_dir.glob("*.txt")):
            category = feed_file.stem
            with feed_file.open() as f:
                for line in f:
                    url = line.strip()
                    if not url or url.startswith("#") or url in seen:
                        continue
                    urls.append(url)
                    seen.add(url)
                    self.url_categories[url] = category
        return urls

    def fetch_news(self) -> List[NewsArticle]:
        """Fetch and parse news articles from all RSS feeds."""
        articles = []
        for url in self.rss_urls:
            try:
                feed = feedparser.parse(url)
            except Exception as exc:
                logger.warning("Failed to fetch RSS feed %s: %s", url, exc)
                continue

            if getattr(feed, "bozo", False):
                logger.warning("RSS feed may be malformed: %s", url)

            category = self.url_categories.get(url, "general")
            for entry in feed.entries:
                title = self._clean_text(entry.get("title", ""))
                link = entry.get("link", "").strip()
                if not title or not link:
                    continue

                article = NewsArticle(
                    title=title,
                    body=self._entry_body(entry),
                    url=link,
                    published=self._clean_text(
                        entry.get("published", entry.get("updated", ""))
                    ),
                    category=category,
                )
                articles.append(article)
        return articles

    def _entry_body(self, entry) -> str:
        """Return the best available text body for a feed entry."""
        summary = entry.get("summary", "")
        if summary:
            return self._clean_text(summary)

        description = entry.get("description", "")
        if description:
            return self._clean_text(description)

        content = entry.get("content", [])
        if content:
            return self._clean_text(content[0].get("value", ""))

        return ""

    @staticmethod
    def _clean_text(value: str) -> str:
        """Convert feed-provided HTML/text into normalized plain text."""
        if not value:
            return ""

        soup = BeautifulSoup(value, "html.parser")
        text = soup.get_text(" ")
        return re.sub(r"\s+", " ", text).strip()
