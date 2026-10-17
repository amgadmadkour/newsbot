import html
from collections import OrderedDict
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List, Optional
from urllib.parse import urlparse

from newsbot.models.news_article import NewsArticle

SUMMARY_LENGTH = 200


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


def _parse_date(value: str) -> Optional[datetime]:
    """Parse an RFC 822 (RSS) or ISO 8601 date string, or return None."""
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _source(url: str) -> str:
    """Return the article's host name without a leading ``www.``."""
    host = urlparse(url).netloc
    return host[4:] if host.startswith("www.") else host


def _summary(body: str) -> str:
    """Truncate the body to ``SUMMARY_LENGTH`` characters, marking any cut."""
    body = body or ""
    if len(body) <= SUMMARY_LENGTH:
        return body
    return body[:SUMMARY_LENGTH].rstrip() + "…"


def render_html(articles: List[NewsArticle]) -> str:
    """Render articles to a standalone HTML page.

    Articles are grouped by their ``category`` and the categories are shown as
    a navigation list on the left-hand side of the page (a scrollable strip on
    narrow screens). The page supports light/dark themes and client-side
    filtering, and has no external dependencies.
    """
    groups = _group_by_category(articles)

    nav_items = []
    sections = []
    for category, items in groups.items():
        anchor = _slug(category)
        label = html.escape(category.replace("_", " ").title())
        nav_items.append(
            '        <li><a href="#{anchor}">{label} '
            '<span class="badge">{count}</span></a></li>'.format(
                anchor=anchor, label=label, count=len(items)
            )
        )

        cards = "\n".join(_render_article(a) for a in items)
        sections.append(
            """      <section id="{anchor}" aria-labelledby="{anchor}-title">
        <h2 id="{anchor}-title">{label} <span class="badge">{count}</span></h2>
        <div class="grid">
{cards}
        </div>
      </section>""".format(
                anchor=anchor, label=label, count=len(items), cards=cards
            )
        )

    if not sections:
        sections.append(
            '      <p class="empty">No articles yet. Check the feeds in '
            "<code>config/feeds/</code> and run NewsBot again.</p>"
        )

    return _PAGE.format(
        styles=_STYLES,
        script=_SCRIPT,
        total=len(articles),
        categories=len(groups),
        generated=datetime.now().strftime("%b %d, %Y at %H:%M"),
        nav="\n".join(nav_items),
        sections="\n".join(sections),
    )


def _render_article(article: NewsArticle) -> str:
    parsed = _parse_date(article.published)
    if parsed:
        date = '<time datetime="{iso}">{label}</time>'.format(
            iso=html.escape(parsed.isoformat()),
            label=html.escape(parsed.strftime("%b %d, %Y")),
        )
    else:
        date = "<span>{}</span>".format(html.escape(str(article.published)))

    return """          <article class="card">
            <p class="meta"><span class="source">{source}</span>{date}</p>
            <h3><a href="{url}" target="_blank" rel="noopener">{title}</a></h3>
            <p class="summary">{summary}</p>
          </article>""".format(
        source=html.escape(_source(article.url)),
        date=date,
        url=html.escape(article.url),
        title=html.escape(article.title),
        summary=html.escape(_summary(article.body)),
    )


_STYLES = """
  :root {
    color-scheme: light;
    --bg: #f6f7f9;
    --surface: #ffffff;
    --surface-hover: #f1f3f7;
    --border: #e3e6ec;
    --text: #15171c;
    --text-muted: #5d6573;
    --text-subtle: #8a91a0;
    --accent: #4f46e5;
    --accent-soft: #eceafd;
    --shadow: 0 1px 2px rgb(16 24 40 / .04), 0 1px 3px rgb(16 24 40 / .06);
    --shadow-hover: 0 8px 24px rgb(16 24 40 / .10);
    --radius: 12px;
    --sidebar: 240px;
    --header: 64px;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      color-scheme: dark;
      --bg: #0f1115;
      --surface: #171a21;
      --surface-hover: #1e222b;
      --border: #272c36;
      --text: #e8eaef;
      --text-muted: #a3aab8;
      --text-subtle: #737b8b;
      --accent: #8b87f7;
      --accent-soft: #25243f;
      --shadow: none;
      --shadow-hover: 0 8px 24px rgb(0 0 0 / .35);
    }
  }
  :root[data-theme="dark"] {
    color-scheme: dark;
    --bg: #0f1115;
    --surface: #171a21;
    --surface-hover: #1e222b;
    --border: #272c36;
    --text: #e8eaef;
    --text-muted: #a3aab8;
    --text-subtle: #737b8b;
    --accent: #8b87f7;
    --accent-soft: #25243f;
    --shadow: none;
    --shadow-hover: 0 8px 24px rgb(0 0 0 / .35);
  }

  *, *::before, *::after { box-sizing: border-box; }
  [hidden] { display: none !important; }
  html { scroll-padding-top: calc(var(--header) + 1rem); }
  @media (prefers-reduced-motion: no-preference) {
    html { scroll-behavior: smooth; }
  }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font: 15px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  a { color: inherit; text-decoration: none; }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 6px; }
  code { font-size: .9em; }

  .skip { position: absolute; left: -999px; top: .5rem; padding: .5rem .75rem;
          background: var(--surface); border-radius: 8px; z-index: 10; }
  .skip:focus { left: .5rem; }

  /* Header */
  header {
    position: sticky; top: 0; z-index: 5;
    display: flex; align-items: center; gap: 1rem;
    height: var(--header); padding: 0 1.5rem;
    background: color-mix(in srgb, var(--bg) 82%, transparent);
    backdrop-filter: saturate(180%) blur(12px);
    -webkit-backdrop-filter: saturate(180%) blur(12px);
    border-bottom: 1px solid var(--border);
  }
  .brand { display: flex; align-items: center; gap: .6rem; min-width: 0; }
  .logo {
    display: grid; place-items: center; flex: none;
    width: 32px; height: 32px; border-radius: 9px;
    background: var(--accent); color: #fff; font-weight: 700; font-size: .95rem;
  }
  .brand h1 { font-size: 1.05rem; margin: 0; letter-spacing: -.01em; }
  .brand .count { margin: 0; font-size: .78rem; color: var(--text-subtle); white-space: nowrap; }
  .tools { margin-left: auto; display: flex; align-items: center; gap: .5rem; }
  .search {
    position: relative; display: flex; align-items: center;
  }
  .search svg { position: absolute; left: .7rem; color: var(--text-subtle); pointer-events: none; }
  .search input {
    width: 260px; height: 38px; padding: 0 2.2rem 0 2.2rem;
    border: 1px solid var(--border); border-radius: 10px;
    background: var(--surface); color: var(--text); font: inherit; font-size: .9rem;
  }
  .search input::placeholder { color: var(--text-subtle); }
  .search input:focus { outline: none; border-color: var(--accent);
                        box-shadow: 0 0 0 3px var(--accent-soft); }
  .search kbd {
    position: absolute; right: .6rem; font: inherit; font-size: .72rem;
    color: var(--text-subtle); border: 1px solid var(--border);
    border-radius: 5px; padding: 0 .35rem; pointer-events: none;
  }
  .icon-btn {
    display: grid; place-items: center; width: 38px; height: 38px;
    border: 1px solid var(--border); border-radius: 10px;
    background: var(--surface); color: var(--text-muted); cursor: pointer;
  }
  .icon-btn:hover { background: var(--surface-hover); color: var(--text); }
  .icon-btn .sun { display: none; }
  :root[data-theme="dark"] .icon-btn .sun { display: block; }
  :root[data-theme="dark"] .icon-btn .moon { display: none; }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) .icon-btn .sun { display: block; }
    :root:not([data-theme="light"]) .icon-btn .moon { display: none; }
  }

  /* Layout */
  .layout {
    display: grid; grid-template-columns: var(--sidebar) minmax(0, 1fr);
    max-width: 1400px; margin: 0 auto;
  }
  nav {
    position: sticky; top: var(--header); align-self: start;
    height: calc(100vh - var(--header)); overflow-y: auto;
    padding: 1.5rem 1rem;
  }
  nav .label {
    margin: 0 0 .5rem .6rem; font-size: .72rem; font-weight: 600;
    letter-spacing: .06em; text-transform: uppercase; color: var(--text-subtle);
  }
  nav ul { list-style: none; padding: 0; margin: 0; display: grid; gap: 2px; }
  nav li a {
    display: flex; justify-content: space-between; align-items: center; gap: .5rem;
    padding: .45rem .6rem; border-radius: 8px;
    color: var(--text-muted); font-size: .9rem; font-weight: 500;
    transition: background-color .15s, color .15s;
  }
  nav li a:hover { background: var(--surface-hover); color: var(--text); }
  nav li a.active { background: var(--accent-soft); color: var(--accent); }
  .badge {
    display: inline-block; min-width: 1.6rem; padding: .05rem .45rem;
    border-radius: 999px; background: var(--surface-hover);
    color: var(--text-muted); font-size: .72rem; font-weight: 600;
    text-align: center; font-variant-numeric: tabular-nums;
  }
  nav li a.active .badge { background: var(--accent); color: #fff; }

  main { padding: 1.5rem 1.5rem 4rem; min-width: 0; }
  section { margin-bottom: 2.75rem; }
  section h2 {
    display: flex; align-items: center; gap: .6rem;
    margin: 0 0 1rem; font-size: 1.25rem; letter-spacing: -.015em;
  }

  /* Cards */
  .grid {
    display: grid; gap: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  }
  .card {
    position: relative; display: flex; flex-direction: column; gap: .45rem;
    padding: 1.1rem 1.2rem 1.2rem;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius); box-shadow: var(--shadow);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
  }
  .card:hover {
    transform: translateY(-2px); box-shadow: var(--shadow-hover);
    border-color: color-mix(in srgb, var(--accent) 35%, var(--border));
  }
  .card:focus-within { border-color: var(--accent); }
  .meta {
    display: flex; align-items: center; gap: .5rem; flex-wrap: wrap;
    margin: 0; font-size: .76rem; color: var(--text-subtle);
  }
  .source { color: var(--accent); font-weight: 600; }
  .meta > :not(:first-child)::before { content: "\\00b7"; margin-right: .5rem; }
  .card h3 { margin: 0; font-size: 1rem; line-height: 1.4; font-weight: 600; letter-spacing: -.005em; }
  .card h3 a::after { content: ""; position: absolute; inset: 0; border-radius: var(--radius); }
  .card h3 a:focus-visible { outline: none; }
  .card:hover h3 a { color: var(--accent); }
  .summary {
    margin: 0; font-size: .88rem; color: var(--text-muted);
    display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3;
    line-clamp: 3; overflow: hidden;
  }
  .empty {
    padding: 3rem 1rem; text-align: center; color: var(--text-muted);
    border: 1px dashed var(--border); border-radius: var(--radius);
  }
  footer { margin-top: 2rem; font-size: .78rem; color: var(--text-subtle); }

  /* Narrow screens: categories become a horizontal strip under the header */
  @media (max-width: 820px) {
    :root { --header: 56px; }
    html { scroll-padding-top: calc(var(--header) + 60px); }
    header { padding: 0 1rem; }
    .brand .count, .search kbd { display: none; }
    .search input { width: min(40vw, 220px); }
    .layout { grid-template-columns: minmax(0, 1fr); }
    nav {
      top: var(--header); z-index: 4; height: auto; padding: .6rem 1rem;
      background: color-mix(in srgb, var(--bg) 92%, transparent);
      backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
    }
    nav .label { display: none; }
    nav ul { display: flex; gap: .4rem; overflow-x: auto; scrollbar-width: none; }
    nav ul::-webkit-scrollbar { display: none; }
    nav li a { white-space: nowrap; border: 1px solid var(--border); background: var(--surface); }
    main { padding: 1.25rem 1rem 3rem; }
    .grid { grid-template-columns: minmax(0, 1fr); }
  }
"""

_SCRIPT = """
(() => {
  const root = document.documentElement;
  const KEY = "newsbot-theme";

  // Theme toggle (the stored choice is applied early in <head>).
  document.getElementById("theme-toggle").addEventListener("click", () => {
    const current = root.dataset.theme ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    root.dataset.theme = current === "dark" ? "light" : "dark";
    try { localStorage.setItem(KEY, root.dataset.theme); } catch (e) {}
  });

  // Client-side filter across titles, sources and summaries.
  const input = document.getElementById("search");
  const sections = [...document.querySelectorAll("main section")];
  const noResults = document.getElementById("no-results");
  input.addEventListener("input", () => {
    const query = input.value.trim().toLowerCase();
    let total = 0;
    for (const section of sections) {
      let shown = 0;
      for (const card of section.querySelectorAll(".card")) {
        const match = !query || card.textContent.toLowerCase().includes(query);
        card.hidden = !match;
        if (match) shown++;
      }
      section.hidden = shown === 0;
      section.querySelector("h2 .badge").textContent = shown;
      const link = document.querySelector('nav a[href="#' + section.id + '"]');
      if (link) {
        link.querySelector(".badge").textContent = shown;
        link.parentElement.hidden = shown === 0;
      }
      total += shown;
    }
    noResults.hidden = total > 0 || sections.length === 0;
  });

  // "/" focuses search, Escape clears it.
  document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    } else if (e.key === "Escape" && document.activeElement === input) {
      input.value = "";
      input.dispatchEvent(new Event("input"));
      input.blur();
    }
  });

  // Highlight the category currently in view.
  const links = new Map(
    [...document.querySelectorAll("nav a")].map((a) => [a.hash.slice(1), a])
  );
  const setActive = (id) => {
    links.forEach((a, key) => a.classList.toggle("active", key === id));
    const link = links.get(id);
    if (link && matchMedia("(max-width: 820px)").matches) {
      link.scrollIntoView({ block: "nearest", inline: "nearest" });
    }
  };
  if ("IntersectionObserver" in window && sections.length) {
    const observer = new IntersectionObserver((entries) => {
      const visible = entries.filter((e) => e.isIntersecting)
        .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
      if (visible.length) setActive(visible[0].target.id);
    }, { rootMargin: "-20% 0px -70% 0px" });
    sections.forEach((s) => observer.observe(s));
    setActive(sections[0].id);
  }
})();
"""

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>NewsBot</title>
<script>
  try {{
    const theme = localStorage.getItem("newsbot-theme");
    if (theme) document.documentElement.dataset.theme = theme;
  }} catch (e) {{}}
</script>
<style>{styles}</style>
</head>
<body>
  <a class="skip" href="#content">Skip to articles</a>
  <header>
    <div class="brand">
      <span class="logo" aria-hidden="true">N</span>
      <div>
        <h1>NewsBot</h1>
        <p class="count">{total} articles &middot; {categories} categories</p>
      </div>
    </div>
    <div class="tools">
      <label class="search">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2" stroke-linecap="round" aria-hidden="true">
          <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
        </svg>
        <input id="search" type="search" placeholder="Filter articles"
               aria-label="Filter articles" autocomplete="off">
        <kbd>/</kbd>
      </label>
      <button id="theme-toggle" class="icon-btn" type="button" aria-label="Toggle dark mode">
        <svg class="moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>
        </svg>
        <svg class="sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2" stroke-linecap="round" aria-hidden="true">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>
        </svg>
      </button>
    </div>
  </header>
  <div class="layout">
    <nav aria-label="Categories">
      <p class="label">Categories</p>
      <ul>
{nav}
      </ul>
    </nav>
    <main id="content">
{sections}
      <p id="no-results" class="empty" hidden>No articles match your filter.</p>
      <footer>Generated {generated}</footer>
    </main>
  </div>
<script>{script}</script>
</body>
</html>"""
