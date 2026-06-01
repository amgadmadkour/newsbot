import argparse
import logging
import sys
from typing import List, Optional

from newsbot.models.news_article import NewsArticle
from newsbot.services.fetchers import RSSFetcher
from newsbot.services.renderers import render_html

DEFAULT_HTML_PATH = "newsbot.html"


def setup_logging() -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("newsbot.log"),
        ],
    )


def fetch_articles() -> List[NewsArticle]:
    """Fetch news articles from RSS feeds."""
    try:
        fetcher = RSSFetcher()
        return fetcher.fetch_news()
    except Exception as e:
        logging.error("Failed to fetch news: %s", e)
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


def write_html(articles: List[NewsArticle], output_path: str) -> None:
    """Render articles to an HTML file grouped by category."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(render_html(articles))
    logging.info("Wrote %d articles to %s", len(articles), output_path)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="newsbot", description="Aggregate and display news from RSS feeds."
    )
    parser.add_argument(
        "--html",
        nargs="?",
        const=DEFAULT_HTML_PATH,
        metavar="PATH",
        help=(
            "Write output as an HTML page grouped by category "
            f"(default: {DEFAULT_HTML_PATH}) instead of printing to the console."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the newsbot application."""
    args = parse_args(argv)
    setup_logging()
    logging.info("Starting Newsbot...")

    try:
        articles = fetch_articles()
        if args.html:
            write_html(articles, args.html)
        else:
            display_articles(articles)
        return 0
    except Exception as e:
        logging.error("Application error: %s", e)
        return 1
