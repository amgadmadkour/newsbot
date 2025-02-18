from abc import ABC, abstractmethod
from typing import List

from newsbot.models.news_article import NewsArticle


class NewsFetcher(ABC):
    """Base class for all news fetchers."""

    @abstractmethod
    def fetch_news(self) -> List[NewsArticle]:
        """Fetch news articles from the source."""
        pass
