import logging

from newsbot.services.bbc_news_fetcher import BBCNewsFetcher

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger.info("Welcome to Newsbot!")
    fetcher = BBCNewsFetcher()
    news = fetcher.fetch_news()
	
    for item in news:
        logger.info(f"Title: {item.title}")
        logger.info(f"Body: {item.body}")
        logger.info(f"URL: {item.url}")
        logger.info(f"Published: {item.published}")
        logger.info("-" * 50)

if __name__ == "__main__":
    main()