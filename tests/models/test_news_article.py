import pytest

from newsbot.models.news_article import NewsArticle


@pytest.fixture
def article():
    return NewsArticle(
        title="Test", body="Content", url="http://test.com", published="2024-02-15"
    )


def test_article_creation(article):
    assert article.title == "Test"
    assert article.body == "Content"
    assert article.url == "http://test.com"
    assert article.published == "2024-02-15"


def test_article_equality(article):
    same_article = NewsArticle(
        title="Test", body="Content", url="http://test.com", published="2024-02-15"
    )
    different_article = NewsArticle(
        title="Different",
        body="Different Content",
        url="http://different.com",
        published="2024-02-15",
    )
    different_type = "Not an article"

    assert article == same_article
    assert article != different_article
    assert article != different_type
