from dataclasses import dataclass, field
import feedparser
from typing import List
from newsbot.models.news_article import NewsArticle

@dataclass
class BBCNewsFetcher:
	rss_url: str = field(default="https://feeds.bbci.co.uk/news/rss.xml")

	def fetch_news(self) -> List[NewsArticle]:
		feed = feedparser.parse(self.rss_url)
		print(feed.entries[0].keys())
		return [
			NewsArticle(
				title=entry.title,
				body=entry.summary,
				url=entry.link,
				published=entry.published
			)
			for entry in feed.entries
		]