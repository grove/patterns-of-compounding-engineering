#!/usr/bin/env python3
"""Build and check the field guide with Python 3.10+ and no dependencies.

Link validation and Markdown rendering are adapted from the companion
collections; see NOTICE. The catalogue and page structure are new.
"""
from __future__ import annotations
import argparse
import html
import json
import os
import posixpath
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit
from markdown import reading_minutes, render_markdown, split_header

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '_site'
TITLE = 'Patterns of compounding engineering'
REPO = 'https://github.com/grove/patterns-of-compounding-engineering'
URL = 'https://grove.github.io/patterns-of-compounding-engineering/'
SOURCE_REF = quote(os.environ.get('SITE_SOURCE_REF', 'main'), safe='/')
GROUPS = {
    'reproduce': ('Understand failures and check behavior', 'Keep the evidence that makes the next investigation easier.'),
    'change': ('Make changes easier to carry out', 'Remove recurring obstacles without requiring a rewrite.'),
    'invest': ('Choose what deserves the effort', 'Try alternatives, remove baggage and check whether earlier work helped.'),
}
MARK = '<svg viewBox="0 0 32 32" width="32" height="32" aria-hidden="true" fill="none"><path d="M5 26V16h7v10M12 26V10h7v16M19 26V4h7v22" stroke="currentColor" stroke-width="2"/><path d="M3 27h26" stroke="currentColor" stroke-width="2"/></svg>'


def esc(value: str) -> str:
    return html.escape(str(value), quote=True)


def load_catalog() -> list[dict]:
    entries = json.loads((ROOT / 'site/catalog.json').read_text(encoding='utf-8'))
    slugs = [entry['slug'] for entry in entries]
    files = {path.stem for path in (ROOT / 'patterns').glob('*.md')}
    if len(slugs) != len(set(slugs)) or set(slugs) != files:
        raise ValueError('Catalogue must list every pattern exactly once.')
    for entry in entries:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry['slug']):
            raise ValueError(f'Invalid slug: {entry["slug"]}')
        if entry['group'] not in GROUPS:
            raise ValueError(f'Unknown group: {entry["group"]}')
        md = (ROOT / f'patterns/{entry["slug"]}.md').read_text(encoding='utf-8')
        title, subtitle, body = split_header(md)
        if title != entry['title']:
            raise ValueError(f'Catalogue title differs from {entry["slug"]}.md')
        entry.update(subtitle=subtitle, body=body, minutes=reading_minutes(md))
    return entries


def resolve_link(source: str, href: str) -> str:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme not in {'https', 'http', 'mailto'}:
            raise ValueError(f'Unsupported link scheme: {href}')
        return href
    if not parsed.path:
        return href
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source), unquote(parsed.path)))
    if target.startswith('../') or target.startswith('/'):
        raise ValueError(f'Link escapes repository: {href}')
    if not (ROOT / target).is_file():
        raise ValueError(f'Unknown source link in {source}: {href}')
    if target == 'README.md':
        output = 'index.html'
    elif target == 'guide.md' or target.startswith('patterns/') and target.endswith('.md'):
        output = target[:-3] + '.html'
    else:
        return f'{REPO}/blob/{SOURCE_REF}/{quote(target)}' + (f'#{parsed.fragment}' if parsed.fragment else '')
    relative = posixpath.relpath(output, posixpath.dirname(source) or '.')
    return urlunsplit(('', '', relative, parsed.query, parsed.fragment))


def shell(title: str, description: str, body: str, path: str = '', kind: str = '') -> str:
    prefix = '../' if path.startswith('patterns/') else './'
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#173047">
  <link rel="canonical" href="{URL}{path}">
  <meta property="og:type" content="{'article' if path else 'website'}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{URL}{path}">
  <link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg">
  <link rel="stylesheet" href="{prefix}style.css">
  <script src="{prefix}site.js" defer></script>
</head>
<body class="{kind}">
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="masthead"><div class="masthead-inner">
    <a class="brand" href="{prefix}">{MARK}<span>Compounding engineering<span class="brand-subtitle">A practical field guide</span></span></a>
    <nav aria-label="Main navigation"><a href="{prefix}#patterns">Patterns</a><a href="{prefix}guide.html">Using the guide</a><a href="{REPO}">GitHub</a></nav>
  </div></header>
  {body}
  <footer class="site-footer"><div class="footer-inner">
    <div><strong>Patterns of compounding engineering</strong><p>Written for the work between releases.</p></div>
    <nav aria-label="Related collections"><a href="https://grove.github.io/software-that-improves-with-age/">Software that improves with age</a><a href="https://grove.github.io/engineering-that-compounds/">Engineering that compounds</a><a href="{REPO}/blob/{SOURCE_REF}/LICENSE">Apache License 2.0</a></nav>
  </div></footer>
</body>
</html>
'''


class Inventory(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()
        self.headings: list[tuple[str, str]] = []
        self.h1_count = 0
        self.current_heading: tuple[str, list[str]] | None = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            if values['id'] in self.ids:
                raise ValueError(f'Duplicate ID: {values["id"]}')
            self.ids.add(values['id'])
        if tag == 'h1':
            self.h1_count += 1
        if tag == 'h2':
            self.current_heading = (values.get('id', ''), [])
        for attr in ('href', 'src'):
            if values.get(attr):
                self.links.append(values[attr])

    def handle_data(self, text):
        if self.current_heading:
            self.current_heading[1].append(text)

    def handle_endtag(self, tag):
        if tag == 'h2' and self.current_heading:
            anchor, text = self.current_heading
            self.headings.append((anchor, ''.join(text)))
            self.current_heading = None


def contents_nav(body_html: str) -> str:
    inventory = Inventory()
    inventory.feed(body_html)
    links = ''.join(f'<li><a href="#{esc(anchor)}">{esc(title)}</a></li>' for anchor, title in inventory.headings)
    return f'<nav class="contents" aria-label="On this page"><p class="eyebrow">On this page</p><ol>{links}</ol></nav>'


def article(source, title, subtitle, body_md, *, entry=None, previous=None, following=None) -> str:
    path = source[:-3] + '.html'
    prefix = '../' if source.startswith('patterns/') else './'
    body_html = render_markdown(body_md, lambda href: resolve_link(source, href))
    meta = f'{esc(GROUPS[entry["group"]][0])} <span aria-hidden="true">/</span> {entry["minutes"]} min read' if entry else 'A place to start'
    problem = f'<div class="problem-note"><span class="eyebrow">Use this when</span><p>{esc(entry["problem"])}</p></div>' if entry else ''
    navigation = []
    if previous:
        navigation.append(f'<a href="{previous["slug"]}.html"><span>Previous pattern</span><strong>{esc(previous["title"])}</strong></a>')
    if following:
        navigation.append(f'<a href="{following["slug"]}.html"><span>Next pattern</span><strong>{esc(following["title"])}</strong></a>')
    pager = '<nav class="pager" aria-label="Pattern navigation">' + ''.join(navigation) + '</nav>' if navigation else ''
    body = f'''<main id="main" class="article-layout">
    <aside class="article-aside"><a class="all-patterns" href="{prefix}#patterns">All patterns</a>{contents_nav(body_html)}</aside>
    <div class="article-column"><article>
      <header class="article-header"><p class="eyebrow">{meta}</p><h1>{esc(title)}</h1><p class="subtitle">{esc(subtitle or '')}</p></header>
      {problem}<div class="prose">{body_html}</div>
    </article>{pager}<p class="source-link"><a href="{REPO}/blob/{SOURCE_REF}/{source}">Read or suggest a change on GitHub</a></p></div>
  </main>'''
    return shell(f'{title} — {TITLE}', subtitle or title, body, path, 'article-page')


def home(entries) -> str:
    groups = []
    for group, (heading, description) in GROUPS.items():
        rows = []
        for entry in entries:
            if entry['group'] != group:
                continue
            search = ' '.join(str(entry[key]) for key in ['title', 'problem', 'summary', 'keywords']).lower()
            rows.append(f'''<li class="pattern-row" data-search="{esc(search)}">
              <div class="pattern-problem">{esc(entry['problem'])}</div>
              <div class="pattern-description"><h3><a href="patterns/{entry['slug']}.html">{esc(entry['title'])}</a></h3><p>{esc(entry['summary'])}</p></div>
              <span class="reading-time">{entry['minutes']} min</span>
            </li>''')
        groups.append(f'''<section class="pattern-group" data-group="{group}" aria-labelledby="group-{group}"><header><h2 id="group-{group}">{heading}</h2><p>{description}</p></header><ul class="pattern-list">{''.join(rows)}</ul></section>''')
    body = f'''<main id="main">
    <section class="hero content-width" aria-labelledby="page-title">
      <div><p class="eyebrow">The practical companion to Engineering that compounds</p><h1 id="page-title">Patterns of<br>compounding<br><em>engineering.</em></h1></div>
      <div class="hero-note"><p class="hero-lede">A field guide for the work<br>that keeps coming back.</p><p>A difficult bug, a risky migration, the same comment in every review. {len(entries)} patterns for turning everyday engineering work into capabilities your team can use again.</p><div class="hero-links"><a class="button" href="#patterns">Find a pattern</a><a href="guide.html#use-the-task-already-open">Try it on your next task</a><a href="guide.html#give-the-method-to-the-next-investigator">Try a skill</a></div></div>
    </section>
    <section class="workbench content-width" aria-labelledby="workbench-title"><div><p class="eyebrow">A worked example you can run</p><h2 id="workbench-title">One invoice. Two deliveries of the same event.</h2><p>Reproduce the double payment, check the fix, then compare two invoice calculators. The examples use Python's standard library and synthetic data.</p><a href="{REPO}/tree/{SOURCE_REF}/examples">Open the billing lab</a></div><div class="terminal"><span class="terminal-label">From the repository root</span><pre tabindex="0"><code>python3 examples/billing_lab.py replay
python3 examples/billing_lab.py verify
python3 examples/billing_lab.py compare</code></pre><p>Includes a failing example and its correction.</p></div></section>
    <section class="catalog content-width" id="patterns" aria-labelledby="catalog-title"><header class="catalog-heading"><div><p class="eyebrow">The pattern catalogue</p><h2 id="catalog-title">What is slowing the team down?</h2></div><p>Start with a problem you have.<br>You don't need to adopt the whole collection.</p></header>
      <div class="catalog-tools" hidden><div class="filter-buttons" role="group" aria-label="Filter patterns"><button type="button" data-filter="all" aria-pressed="true">All patterns</button><button type="button" data-filter="reproduce" aria-pressed="false">Failures &amp; evidence</button><button type="button" data-filter="change" aria-pressed="false">Changes &amp; tools</button><button type="button" data-filter="invest" aria-pressed="false">Decisions &amp; upkeep</button></div><div class="search-field"><label for="pattern-search">Search patterns</label><input id="pattern-search" type="search" placeholder="Try migrations or review" autocomplete="off"></div></div>
      <p id="filter-status" class="filter-status" role="status" aria-live="polite" hidden></p>
      {''.join(groups)}
      <p id="no-results" class="no-results" hidden>No patterns match those words. Try a broader term or choose All patterns.</p>
    </section>
    <section class="closing-note content-width" aria-labelledby="keep-title"><p class="eyebrow">A note on the title</p><div><h2 id="keep-title">More tools do not necessarily mean more progress.</h2><p>A retained test or script earns its place when later work uses it. Each pattern covers what to keep, what it costs to maintain, and when to stop. The <a href="patterns/investment-retrospective.html">investment retrospective</a> is there to check the claim.</p><p>The earlier collections make the argument for software and teams that improve with experience. This guide puts that argument to work on individual changes.</p></div></section>
  </main>'''
    return shell(TITLE, f'A practical field guide to recurring software problems: {len(entries)} patterns, worked examples, trade-offs and ways to get started.', body, kind='home-page')


def check_links(pages):
    inventories = {}
    for page in pages:
        inventory = Inventory()
        inventory.feed(page.read_text(encoding='utf-8'))
        if inventory.h1_count != 1:
            raise ValueError(f'Expected exactly one H1: {page}')
        inventories[page.resolve()] = inventory
    for page, inventory in inventories.items():
        for href in inventory.links:
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page
            if not target.is_relative_to(OUT.resolve()):
                raise ValueError(f'Link escapes output: {page.name}: {href}')
            if target.is_dir():
                target = target / 'index.html'
            if not target.is_file():
                raise ValueError(f'Broken local link in {page.name}: {href}')
            if parsed.fragment and target in inventories and unquote(parsed.fragment) not in inventories[target].ids:
                raise ValueError(f'Missing anchor in {page.name}: {href}')


def build():
    entries = load_catalog()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / 'patterns').mkdir(parents=True)
    for name in ['style.css', 'site.js', 'favicon.svg']:
        shutil.copy2(ROOT / 'site' / name, OUT / name)
    (OUT / '.nojekyll').touch()
    (OUT / 'index.html').write_text(home(entries), encoding='utf-8')
    guide_title, subtitle, guide_body = split_header((ROOT / 'guide.md').read_text(encoding='utf-8'))
    (OUT / 'guide.html').write_text(article('guide.md', guide_title, subtitle, guide_body), encoding='utf-8')
    for index, entry in enumerate(entries):
        previous = entries[index - 1] if index else None
        following = entries[index + 1] if index < len(entries) - 1 else None
        path = f'patterns/{entry["slug"]}.md'
        output = article(path, entry['title'], entry['subtitle'], entry['body'], entry=entry, previous=previous, following=following)
        (OUT / path.replace('.md', '.html')).write_text(output, encoding='utf-8')
    pages = sorted(OUT.rglob('*.html'))
    check_links(pages)
    locations = ['' if p.name == 'index.html' else p.relative_to(OUT).as_posix() for p in pages]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{URL}{path}</loc></url>' for path in locations) + '</urlset>\n'
    (OUT / 'sitemap.xml').write_text(sitemap, encoding='utf-8')
    return pages


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Build and validate the catalogue, source links, generated links and anchors. These checks also run on every build.')
    parser.parse_args()
    try:
        pages = build()
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Build failed: {error}\n')
    print(f'Built and checked {len(pages)} pages in _site/.')

