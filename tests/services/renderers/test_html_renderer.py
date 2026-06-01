from newsbot.models.news_article import NewsArticle
from newsbot.services.renderers.html_renderer import render_html


def _article(title, category):
    return NewsArticle(
        title=title,
        body="Body for " + title,
        url="https://example.com/" + title.lower().replace(" ", "-"),
        published="2026-05-31",
        category=category,
    )


def test_render_html_groups_by_category():
    articles = [
        _article("Markets up", "business"),
        _article("Election news", "general"),
        _article("New chip", "business"),
    ]

    page = render_html(articles)

    # One section per distinct category, with a left-hand nav entry each.
    assert page.count("<section") == 2
    assert '<a href="#cat-business">Business' in page
    assert '<a href="#cat-general">General' in page
    # Badge counts reflect the grouping.
    assert "Business <span class=\"badge\">2</span>" in page
    assert "General <span class=\"badge\">1</span>" in page
    assert "3 articles &middot; 2 categories" in page


def test_render_html_escapes_and_truncates():
    long_body = "x" * 500
    articles = [
        NewsArticle(
            title="<script>alert(1)</script>",
            body=long_body,
            url="https://example.com/x?a=1&b=2",
            published="2026-05-31",
            category="general",
        )
    ]

    page = render_html(articles)

    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
    assert "&amp;b=2" in page
    # Summary is truncated to 200 characters.
    assert "x" * 200 in page
    assert "x" * 201 not in page


def test_render_html_handles_no_articles():
    page = render_html([])

    assert "0 articles" in page
    assert "<section" not in page
