from newsbot import cli
from newsbot.models.news_article import NewsArticle


def _articles():
    return [
        NewsArticle("Biz", "b", "https://example.com/b", "2026-05-31", "business"),
        NewsArticle("Gen", "g", "https://example.com/g", "2026-05-31", "general"),
    ]


def test_parse_args_html_uses_default_path():
    args = cli.parse_args(["--html"])
    assert args.html == cli.DEFAULT_HTML_PATH


def test_parse_args_html_accepts_explicit_path():
    args = cli.parse_args(["--html", "out.html"])
    assert args.html == "out.html"


def test_parse_args_defaults_to_console():
    args = cli.parse_args([])
    assert args.html is None


def test_main_html_writes_grouped_file(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "fetch_articles", _articles)
    output = tmp_path / "report.html"

    assert cli.main(["--html", str(output)]) == 0

    page = output.read_text()
    assert "<section" in page
    assert "#cat-business" in page
    assert "#cat-general" in page


def test_main_console_does_not_write_html(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "fetch_articles", _articles)
    monkeypatch.chdir(tmp_path)

    assert cli.main([]) == 0

    assert not (tmp_path / cli.DEFAULT_HTML_PATH).exists()
