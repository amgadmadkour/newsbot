import logging
import sys
from typing import List

from newsbot.models.news_article import NewsArticle
from newsbot.services.fetchers import RSSFetcher

def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('newsbot.log')
        ]
    )

def fetch_articles() -> List[NewsArticle]:
    """Fetch news articles from RSS feeds."""
    try:
        fetcher = RSSFetcher()
        return fetcher.fetch_news()
    except Exception as e:
        logging.error(f"Failed to fetch news: {e}")
        return []

def display_articles(articles: List[NewsArticle]) -> None:
    """Display fetched articles in a formatted way."""
    if not articles:
        logging.warning("No articles found!")
        return

    for i, article in enumerate(articles, 1):
        logging.info("\n%s", "-" * 50)
        logging.info("Article %d:", i)
        logging.info("Title: %s", article.title)
        logging.info("URL: %s", article.url)
        logging.info("Published: %s", article.published)
        logging.info("Summary: %s...", article.body[:200])
    
    logging.info("\nTotal articles found: %d", len(articles))

def main() -> int:
    """Main entry point for the newsbot application."""
    setup_logging()
    logging.info("Starting Newsbot...")

    try:
        articles = fetch_articles()
        display_articles(articles)
        return 0
    except Exception as e:
        logging.error("Application error: %s", e)
        return 1

if __name__ == "__main__":
    sys.exit(main())