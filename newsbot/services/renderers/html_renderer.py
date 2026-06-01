import html
from collections import OrderedDict
from typing import Dict, List

from newsbot.models.news_article import NewsArticle


def _group_by_category(
    articles: List[NewsArticle],
) -> "OrderedDict[str, List[NewsArticle]]":
    """Group articles by category, preserving first-seen order."""
    groups: "OrderedDict[str, List[NewsArticle]]" = OrderedDict()
    for article in articles:
        groups.setdefault(article.category, []).append(article)
    return groups


def _slug(category: str) -> str:
    """Return a DOM-id-safe anchor for a category name."""
    return "cat-" + "".join(c if c.isalnum() else "-" for c in category.lower())


def render_html(articles: List[NewsArticle]) -> str:
    """Render articles to a standalone HTML page.

    Articles are grouped by their ``category`` and the categories are shown as
    a navigation list on the left-hand side of the page.
    """
    groups = _group_by_category(articles)

    nav_items = []
    sections = []
    for category, items in groups.items():
        anchor = _slug(category)
        label = html.escape(category.replace("_", " ").title())
        nav_items.append(
            '      <li><a href="#{anchor}">{label} '
            '<span class="badge">{count}</span></a></li>'.format(
                anchor=anchor, label=label, count=len(items)
            )
        )

        cards = "\n".join(_render_article(i, a) for i, a in enumerate(items, 1))
        sections.append(
            """    <section id="{anchor}">
      <h2>{label} <span class="badge">{count}</span></h2>
{cards}
    </section>""".format(
                anchor=anchor, label=label, count=len(items), cards=cards
            )
        )

    return _PAGE.format(
        total=len(articles),
        categories=len(groups),
        nav="\n".join(nav_items),
        sections="\n".join(sections),
    )


def _render_article(index: int, article: NewsArticle) -> str:
    return """      <article>
        <h3>{index}. <a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
        <p class="meta">{published}</p>
        <p class="summary">{summary}</p>
      </article>""".format(
        index=index,
        url=html.escape(article.url),
        title=html.escape(article.title),
        published=html.escape(str(article.published)),
        summary=html.escape((article.body or "")[:200]),
    )


_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NewsBot</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; margin: 0;
         color: #1a1a1a; background: #fafafa; display: flex; }}
  nav {{ position: sticky; top: 0; align-self: flex-start; width: 220px;
        height: 100vh; overflow-y: auto; padding: 1.5rem 1rem;
        background: #fff; border-right: 1px solid #e2e2e2; }}
  nav h1 {{ font-size: 1.1rem; margin: 0 0 .25rem; }}
  nav .count {{ color: #888; font-size: .8rem; margin: 0 0 1rem; }}
  nav ul {{ list-style: none; padding: 0; margin: 0; }}
  nav li a {{ display: flex; justify-content: space-between; align-items: center;
             padding: .4rem .6rem; border-radius: 6px; color: #1a1a1a;
             text-decoration: none; font-size: .9rem; }}
  nav li a:hover {{ background: #f0f4ff; }}
  .badge {{ background: #e6efff; color: #0066cc; border-radius: 999px;
           padding: 0 .5rem; font-size: .75rem; font-weight: 600; }}
  main {{ flex: 1; max-width: 860px; padding: 2rem; }}
  section {{ margin-bottom: 2.5rem; }}
  section h2 {{ border-bottom: 2px solid #0066cc; padding-bottom: .4rem;
               display: flex; align-items: center; gap: .5rem; }}
  article {{ background: #fff; border: 1px solid #e2e2e2; border-radius: 8px;
            padding: .85rem 1.1rem; margin: .8rem 0; }}
  article h3 {{ font-size: 1rem; margin: 0 0 .3rem; font-weight: 600; }}
  a {{ color: #0066cc; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .meta {{ color: #888; font-size: .8rem; margin: 0 0 .4rem; }}
  .summary {{ margin: 0; font-size: .9rem; color: #333; }}
</style>
</head>
<body>
  <nav>
    <h1>NewsBot</h1>
    <p class="count">{total} articles &middot; {categories} categories</p>
    <ul>
{nav}
    </ul>
  </nav>
  <main>
{sections}
  </main>
</body>
</html>"""
