import requests
from bs4 import BeautifulSoup
from typing import List
from dataclasses import dataclass
from newsbot.models.news_article import NewsArticle
import requests
from bs4 import BeautifulSoup

@dataclass
class OpenNewsWireFetcher:
	base_url: str = "https://feed.opennewswire.org/?languages=en"

	def fetch_news(self) -> List[NewsArticle]:
		try:
			response = requests.get(self.base_url)
			response.raise_for_status()
			
			soup = BeautifulSoup(response.content, "html.parser")
			articles = soup.find_all("article")
			
			return self._parse_articles(articles)
		
		except requests.RequestException as e:
			print(f"Error fetching news from OpenNewsWire: {e}")
			return []

	def _parse_articles(self, articles) -> List[NewsArticle]:
		news_items = []
		
		for article in articles:
			try:
				title = article.find("h2").text.strip()
				link = article.find("a", href=True)["href"]
				summary = article.find("p").text.strip() if article.find("p") else "No summary available"
				
				news_items.append(NewsArticle(
					title=title,
					link=link,
					summary=summary
				))
				
			except AttributeError as e:
				print(f"Error parsing article: {e}")
				continue
				
		return news_items
