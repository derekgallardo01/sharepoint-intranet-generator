"""Render the intranet model to self-contained static HTML.

Stdlib only. Every page is a complete HTML document with inline CSS — no external
stylesheets, fonts, scripts, or CDN — so the ``out/`` folder opens anywhere offline.
All dynamic text is escaped via :func:`html.escape`.

The public entry point is :func:`render_all`, which returns a mapping of
``filename -> html string``.
"""

from __future__ import annotations

from html import escape

from .model import Intranet, Site


def _css(theme: dict) -> str:
    primary = str(theme.get("primary", "#1f5673"))
    accent = str(theme.get("accent", "#c9a14a"))
    return f"""
    :root {{ --primary: {escape(primary)}; --accent: {escape(accent)}; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: 'Segoe UI', Arial, sans-serif; color: #222;
            background: #f3f4f6; }}
    a {{ color: var(--primary); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    header.topbar {{ background: var(--primary); color: #fff; padding: 0 24px;
            display: flex; align-items: center; gap: 28px; height: 56px; }}
    .brand {{ font-weight: 700; font-size: 18px; }}
    nav.global {{ display: flex; gap: 18px; flex-wrap: wrap; }}
    nav.global a {{ color: #fff; font-size: 14px; opacity: .92; }}
    nav.global a:hover {{ opacity: 1; }}
    main {{ max-width: 1040px; margin: 0 auto; padding: 24px; }}
    .hero {{ background: linear-gradient(135deg, var(--primary), #2c7da0);
            color: #fff; border-radius: 10px; padding: 40px 32px; margin-bottom: 24px; }}
    .hero h1 {{ margin: 0 0 8px; font-size: 30px; }}
    .hero p {{ margin: 0; opacity: .9; }}
    h2.section {{ border-left: 4px solid var(--accent); padding-left: 10px;
            margin-top: 32px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px; }}
    .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
            padding: 16px; }}
    .card h3 {{ margin: 0 0 6px; font-size: 16px; }}
    .card .date {{ color: #6b7280; font-size: 12px; }}
    .quicklinks {{ display: flex; flex-wrap: wrap; gap: 10px; list-style: none;
            padding: 0; }}
    .quicklinks li a {{ display: inline-block; background: #fff; border: 1px solid #e5e7eb;
            border-radius: 20px; padding: 6px 14px; font-size: 14px; }}
    table {{ width: 100%; border-collapse: collapse; background: #fff;
            border: 1px solid #e5e7eb; border-radius: 8px; overflow: hidden; }}
    th, td {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid #eef0f3;
            font-size: 14px; }}
    th {{ background: #fafbfc; color: #374151; font-weight: 600; }}
    tr:last-child td {{ border-bottom: none; }}
    .tag {{ display: inline-block; padding: 1px 8px; border-radius: 12px;
            font-size: 12px; background: #eef2ff; color: var(--primary); }}
    footer {{ max-width: 1040px; margin: 24px auto; padding: 16px 24px; color: #6b7280;
            font-size: 12px; }}
    .meta {{ color: #6b7280; font-size: 13px; }}
    .faq details {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
            padding: 12px 16px; margin-bottom: 8px; }}
    .faq summary {{ cursor: pointer; font-weight: 600; }}
    .faq .answer {{ margin-top: 8px; color: #374151; font-size: 14px; }}
    .people {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 14px; }}
    .person-card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
            padding: 14px; text-align: center; }}
    .person-card img, .person-card .photo-placeholder {{ width: 72px; height: 72px;
            border-radius: 50%; object-fit: cover; background: #e5e7eb;
            display: block; margin: 0 auto 8px; }}
    .person-card h3 {{ margin: 4px 0 2px; font-size: 15px; }}
    """


def _nav_html(net: Intranet, active: str) -> str:
    items = []
    for link in net.nav:
        href = "index.html" if link.page == "index" else f"{link.page}.html"
        cls = ' style="font-weight:700;opacity:1"' if link.page == active else ""
        items.append(f'<a href="{escape(href)}"{cls}>{escape(link.label)}</a>')
    return '<nav class="global">' + "".join(items) + "</nav>"


def _layout(net: Intranet, active: str, title: str, body: str) -> str:
    brand = escape(str(net.theme.get("logoText", net.org)))
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(title)} · {escape(net.org)}</title>"
        f"<style>{_css(net.theme)}</style></head><body>"
        f'<header class="topbar"><span class="brand">{brand}</span>'
        f"{_nav_html(net, active)}</header>"
        f"<main>{body}</main>"
        f'<footer>Static preview generated from site-definition.json · '
        f"{escape(net.org)} · tenant: {escape(net.tenant)}</footer>"
        "</body></html>"
    )


def render_home(net: Intranet) -> str:
    hub_desc = str(net.hub.get("description", ""))
    hero = (
        '<section class="hero">'
        f"<h1>Welcome to the {escape(net.org)} Intranet</h1>"
        f"<p>{escape(hub_desc)}</p></section>"
    )

    news_cards = []
    for item in net.news:
        news_cards.append(
            '<div class="card">'
            f'<div class="date">{escape(item.date)}</div>'
            f"<h3>{escape(item.title)}</h3>"
            f"<p class=\"meta\">{escape(item.summary)}</p></div>"
        )
    news = (
        '<h2 class="section">Company news</h2>'
        '<div class="cards">' + "".join(news_cards) + "</div>"
    )

    link_items = []
    for site in net.sites:
        href = f"{site.key}.html"
        link_items.append(f'<li><a href="{escape(href)}">{escape(site.title)}</a></li>')
    link_items.append('<li><a href="document-center.html">Document Center</a></li>')
    quicklinks = (
        '<h2 class="section">Quick links</h2>'
        '<ul class="quicklinks">' + "".join(link_items) + "</ul>"
    )

    body = hero + news + quicklinks
    return _layout(net, "index", "Home", body)


def render_section(net: Intranet, site: Site) -> str:
    parts = [f'<h2 class="section">{escape(site.title)}</h2>']
    if site.summary:
        parts.append(f'<p class="meta">{escape(site.summary)}</p>')

    if site.links:
        items = "".join(
            f'<li><a href="#">{escape(l)}</a></li>' for l in site.links
        )
        parts.append('<h3>Quick links</h3><ul class="quicklinks">' + items + "</ul>")

    for lib in site.libraries:
        parts.append(f'<h3>{escape(lib.name)}</h3>')
        if lib.content_type:
            parts.append(f'<p class="meta">Content type: {escape(lib.content_type)}</p>')
        head = "".join(
            f"<th>{escape(c.name)}{' *' if c.required else ''}</th>" for c in lib.columns
        )
        typerow = "".join(f"<td>{escape(c.type)}</td>" for c in lib.columns)
        parts.append(
            "<table><thead><tr>" + head + "</tr></thead>"
            "<tbody><tr>" + typerow + "</tr></tbody></table>"
        )
        if lib.retention:
            parts.append(f'<p class="meta">Retention: {escape(lib.retention)}</p>')

    perms = site.permissions
    if perms:
        parts.append('<h3>Permissions</h3>')
        rows = []
        for role in ("owners", "members", "visitors"):
            if role in perms:
                rows.append(
                    f"<tr><td>{escape(role.capitalize())}</td>"
                    f"<td>{escape(str(perms[role]))}</td></tr>"
                )
        if "inheritance" in perms:
            rows.append(
                f"<tr><td>Inheritance</td><td>{escape(str(perms['inheritance']))}</td></tr>"
            )
        parts.append(
            "<table><thead><tr><th>Role</th><th>Group</th></tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody></table>"
        )

    return _layout(net, site.key, site.title, "".join(parts))


def render_document_center(net: Intranet) -> str:
    dc = net.document_center
    parts = [f'<h2 class="section">{escape(dc.title)}</h2>']
    if dc.summary:
        parts.append(f'<p class="meta">{escape(dc.summary)}</p>')

    for lib in dc.libraries:
        parts.append(f'<h3>{escape(lib.name)}</h3>')
        cols = ["Title"] + list(lib.columns)
        head = "".join(f"<th>{escape(c)}</th>" for c in cols)
        rows = []
        for doc in lib.documents:
            cells = []
            for c in cols:
                val = doc.get(c, "")
                if c == "Status" and val:
                    cells.append(f'<td><span class="tag">{escape(val)}</span></td>')
                else:
                    cells.append(f"<td>{escape(val)}</td>")
            rows.append("<tr>" + "".join(cells) + "</tr>")
        parts.append(
            "<table><thead><tr>" + head + "</tr></thead>"
            "<tbody>" + "".join(rows) + "</tbody></table>"
        )

    return _layout(net, "document-center", dc.title, "".join(parts))


def render_faq(net: Intranet, site: Site) -> str:
    parts = [f'<h2 class="section">{escape(site.title)}</h2>']
    if site.summary:
        parts.append(f'<p class="meta">{escape(site.summary)}</p>')
    parts.append('<div class="faq">')
    for entry in site.questions:
        parts.append(
            "<details>"
            f"<summary>{escape(entry.q)}</summary>"
            f'<div class="answer">{escape(entry.a)}</div>'
            "</details>"
        )
    parts.append("</div>")
    return _layout(net, site.key, site.title, "".join(parts))


def render_people(net: Intranet, site: Site) -> str:
    parts = [f'<h2 class="section">{escape(site.title)}</h2>']
    if site.summary:
        parts.append(f'<p class="meta">{escape(site.summary)}</p>')
    parts.append('<div class="people">')
    for p in site.people:
        if p.photo_url:
            photo = f'<img src="{escape(p.photo_url)}" alt="{escape(p.name)}">'
        else:
            photo = '<div class="photo-placeholder"></div>'
        email = (f'<a href="mailto:{escape(p.email)}">{escape(p.email)}</a>'
                 if p.email else "")
        parts.append(
            '<div class="person-card">'
            f"{photo}"
            f"<h3>{escape(p.name)}</h3>"
            f'<p class="meta">{escape(p.title)}</p>'
            f'<p class="meta">{email}</p>'
            "</div>"
        )
    parts.append("</div>")
    return _layout(net, site.key, site.title, "".join(parts))


def render_site(net: Intranet, site: Site) -> str:
    if site.type == "faq":
        return render_faq(net, site)
    if site.type == "people":
        return render_people(net, site)
    return render_section(net, site)


def render_all(net: Intranet) -> dict[str, str]:
    """Render every page. Returns ``{filename: html}`` in deterministic order."""
    pages: dict[str, str] = {}
    pages["index.html"] = render_home(net)
    for site in net.sites:
        pages[f"{site.key}.html"] = render_site(net, site)
    # A News page reuses the home news block as its own section for the nav link.
    pages["news.html"] = _render_news_page(net)
    pages["document-center.html"] = render_document_center(net)
    return pages


def _render_news_page(net: Intranet) -> str:
    cards = []
    for item in net.news:
        cards.append(
            '<div class="card">'
            f'<div class="date">{escape(item.date)}</div>'
            f"<h3>{escape(item.title)}</h3>"
            f'<p class="meta">{escape(item.summary)}</p></div>'
        )
    body = (
        '<h2 class="section">News</h2>'
        '<div class="cards">' + "".join(cards) + "</div>"
    )
    return _layout(net, "news", "News", body)
