import pytest
from unittest.mock import Mock, patch
from newsbot.services.bbc_news_fetcher import BBCNewsFetcher
from newsbot.models.news_article import NewsArticle

@pytest.fixture
def bbc_news_fetcher():
	return BBCNewsFetcher(rss_url="http://test.com/rss")

@patch('newsbot.services.news_fetcher.feedparser')
def test_fetch_news_returns_list_of_news_articles(mock_feedparser, bbc_news_fetcher):
	# Arrange
	mock_entry = Mock()
	mock_entry.title = "Test Title"
	mock_entry.summary = "Test Summary" 
	mock_entry.link = "http://test.com/article"
	mock_entry.published = "2023-01-01"

	mock_feed = Mock()
	mock_feed.entries = [mock_entry]
	mock_feedparser.parse.return_value = mock_feed

	# Act
	articles = bbc_news_fetcher.fetch_news()

	# Assert
	assert len(articles) == 1
	assert isinstance(articles[0], NewsArticle)
	assert articles[0].title == "Test Title"
	assert articles[0].body == "Test Summary"
	assert articles[0].url == "http://test.com/article" 
	assert articles[0].published == "2023-01-01"
	mock_feedparser.parse.assert_called_once_with("http://test.com/rss")