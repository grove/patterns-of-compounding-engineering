"""Checks for reader-visible Markdown, source links and generated navigation.

Run with: python3 -m unittest discover -s tests -v
The build smoke test uses an isolated miniature collection, not the live _site.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "site"))
import build as site_build
from markdown import render_inline, render_markdown


class HTMLFacts(HTMLParser):
    """Read rendered output without relying on the production link inventory."""

    def __init__(self, markup):
        super().__init__()
        self.tags = []
        self.links = []
        self.ids = []
        self.text = []
        self.feed(markup)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if "href" in attrs:
            self.links.append(attrs["href"])
        if "id" in attrs:
            self.ids.append(attrs["id"])

    def handle_data(self, data):
        self.text.append(data)


class MarkdownTests(unittest.TestCase):
    def test_table_preserves_code_links_and_cell_boundaries(self):
        markup = render_markdown(
            "| Fixture | Expected result |\n"
            "| --- | --- |\n"
            "| A handler imports `stripe` | Reject & explain |\n"
            "| [Read the pattern](./guardrail.md) | Accept |",
            lambda href: href.replace(".md", ".html"),
        )
        result = HTMLFacts(markup)
        self.assertEqual(result.tags.count("th"), 2)
        self.assertEqual(result.tags.count("td"), 4)
        self.assertIn("code", result.tags)
        self.assertIn("Reject & explain", "".join(result.text))
        self.assertEqual(result.links, ["./guardrail.html"])

    def test_link_with_parenthesized_url_keeps_the_whole_address(self):
        url = "https://doi.org/10.1016/0165-6074(85)90032-8?x=1&y=2"
        result = HTMLFacts(render_inline(f"Read [the paper]({url}).", lambda href: href))
        self.assertEqual(result.links, [url])
        self.assertEqual("".join(result.text), "Read the paper.")

    def test_code_and_raw_html_are_displayed_without_becoming_elements(self):
        source = (
            'Use `<script>alert("x")</script>` literally.\n\n'
            '<img src=x onerror="alert(1)">\n\n'
            '```python\nif amount < 0:\n    print("**refund** & retry")\n```'
        )
        result = HTMLFacts(render_markdown(source, lambda href: href))
        self.assertNotIn("script", result.tags)
        self.assertNotIn("img", result.tags)
        self.assertNotIn("strong", result.tags)
        self.assertIn('if amount < 0:\n    print("**refund** & retry")', "".join(result.text))

    def test_unclosed_code_fence_reports_an_authoring_error(self):
        with self.assertRaisesRegex(ValueError, "Unclosed code fence"):
            render_markdown("```python\nprint('incomplete')", lambda href: href)

    def test_repeated_and_numbered_headings_have_distinct_navigation_targets(self):
        markup = render_markdown(
            "## Notes\n\n## Notes\n\n## Notes 2\n\n> ## Notes",
            lambda href: href,
        )
        result = HTMLFacts(markup)
        self.assertEqual(len(result.ids), 4)
        self.assertEqual(len(set(result.ids)), 4)
        navigation = HTMLFacts(site_build.contents_nav(markup))
        self.assertEqual({link[1:] for link in navigation.links}, set(result.ids))


class CatalogueConsistencyTests(unittest.TestCase):
    def test_readme_lists_all_catalogue_patterns_in_order(self):
        entries = json.loads((REPOSITORY / "site/catalog.json").read_text(encoding="utf-8"))
        readme = (REPOSITORY / "README.md").read_text(encoding="utf-8")
        listed = re.findall(r"^\d+\. \*\*\[([^\]]+)\]\(\./patterns/([^/)]+)\.md\)\*\*", readme, re.MULTILINE)
        self.assertEqual(listed, [(entry["title"], entry["slug"]) for entry in entries],
                         "Update the README list when editing the catalogue.")


class SiteBuildTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="compounding-site-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output = self.root / "_site"
        globals_patch = patch.multiple(site_build, ROOT=self.root, OUT=self.output)
        globals_patch.start()
        self.addCleanup(globals_patch.stop)
        self.write("README.md", "# Patterns\n")
        self.write("examples/README.md", "# Billing lab\n")
        self.write("examples/billing_lab.py", "print('synthetic example')\n")
        self.write("examples/evolving-billing/replay.py", "print('evolving example')\n")
        self.write(
            "examples/evolving-billing/README.md",
            "# Evolving billing\n\n*Follow the next change.*\n\n"
            "## Try a restart\n\n[Runner](./replay.py), "
            "[guide](../../guide.md#choose-a-problem) and "
            "[reproducer](../../patterns/persistent-reproducer.md).\n",
        )
        self.write(
            "guide.md",
            "# Using the guide\n\n*Start with a problem.*\n\n"
            "## Use the task already open\n\nTry one small improvement.\n\n"
            "## Give the method to the next investigator\n\nTry a skill.\n\n"
            "## Make a difficult subsystem replaceable\n\nTry known cases.\n\n"
            "## Reduce recurring review work\n\nCheck an agreed rule.\n\n"
            "## Delegate one kind of task\n\nKeep the boundary narrow.\n\n"
            "## Choose a problem\n\n[Replay](./patterns/persistent-reproducer.md)\n",
        )
        self.write(
            "patterns/persistent-reproducer.md",
            "# Persistent reproducer\n\n*Keep a repeatable case.*\n\n"
            "## Run it\n\n[Lab](../examples/README.md) and "
            "[code](../examples/billing_lab.py).\n\n"
            "[Next step](./investment-retrospective.md#maintenance).\n\n"
            "[Guide](../guide.md#choose-a-problem).\n",
        )
        self.write(
            "patterns/investment-retrospective.md",
            "# Investment retrospective\n\n*Check the upkeep.*\n\n"
            "## Maintenance\n\nReview one investment.\n",
        )
        entries = [
            ("persistent-reproducer", "Persistent reproducer", "reproduce"),
            ("investment-retrospective", "Investment retrospective", "invest"),
        ]
        self.write("site/catalog.json", json.dumps([
            dict(slug=slug, title=title, group=group, problem="A recurring problem.",
                 summary="An example pattern.", keywords="example")
            for slug, title, group in entries
        ]))
        for name in ["style.css", "site.js", "favicon.svg"]:
            self.write(f"site/{name}", "")

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_source_links_route_articles_and_repository_files_correctly(self):
        source = "patterns/persistent-reproducer.md"
        cases = {
            "./investment-retrospective.md#maintenance": "investment-retrospective.html#maintenance",
            "../guide.md?view=print#choose-a-problem": "../guide.html?view=print#choose-a-problem",
            "../README.md": "../index.html",
            "../examples/README.md": f"{site_build.REPO}/blob/main/examples/README.md",
            "../examples/evolving-billing/README.md#try-a-restart": "../examples/evolving-billing/index.html#try-a-restart",
            "../examples/billing_lab.py#L1": f"{site_build.REPO}/blob/main/examples/billing_lab.py#L1",
            "#run-it": "#run-it",
        }
        for href, expected in cases.items():
            with self.subTest(href=href):
                self.assertEqual(site_build.resolve_link(source, href), expected)

    def test_source_links_reject_missing_files_escape_paths_and_script_urls(self):
        for href in ["./missing.md", "../../outside.md", "..%2F..%2Foutside.md", "javascript:alert(1)"]:
            with self.subTest(href=href), self.assertRaises(ValueError):
                site_build.resolve_link("patterns/persistent-reproducer.md", href)

    def test_build_makes_a_navigable_collection_without_publishing_markdown_paths(self):
        pages = site_build.build()
        article = self.output / "patterns/persistent-reproducer.html"
        self.assertIn(article, pages)
        homepage = HTMLFacts((self.output / "index.html").read_text(encoding="utf-8"))
        self.assertIn("guide.html#give-the-method-to-the-next-investigator", homepage.links)
        result = HTMLFacts(article.read_text(encoding="utf-8"))
        self.assertIn("investment-retrospective.html#maintenance", result.links)
        self.assertIn("../guide.html#choose-a-problem", result.links)
        self.assertTrue((self.output / ".nojekyll").is_file())
        for page in pages:
            for href in HTMLFacts(page.read_text(encoding="utf-8")).links:
                if not href.startswith(("https://", "http://", "mailto:")):
                    self.assertNotIn(".md", href)

    def test_generated_validation_rejects_a_broken_anchor(self):
        pages = site_build.build()
        article = self.output / "patterns/persistent-reproducer.html"
        content = article.read_text(encoding="utf-8")
        article.write_text(content.replace("#maintenance", "#does-not-exist"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing anchor"):
            site_build.check_links(pages)

    def test_nested_walkthrough_keeps_assets_navigation_and_source_links_usable(self):
        pages = site_build.build()
        walkthrough = self.output / "examples/evolving-billing/index.html"
        self.assertIn(walkthrough, pages)
        result = HTMLFacts(walkthrough.read_text(encoding="utf-8"))
        self.assertIn("../../guide.html#choose-a-problem", result.links)
        self.assertIn("../../patterns/persistent-reproducer.html", result.links)
        self.assertIn("../../#patterns", result.links)
        self.assertIn("../../favicon.svg", result.links)
        self.assertTrue(any(link.startswith("../../style.css?v=") for link in result.links))
        self.assertIn(f"{site_build.REPO}/blob/main/examples/evolving-billing/replay.py", result.links)
        homepage = HTMLFacts((self.output / "index.html").read_text(encoding="utf-8"))
        self.assertIn("examples/evolving-billing/index.html", homepage.links)
        sitemap = (self.output / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn(f"<loc>{site_build.URL}examples/evolving-billing/index.html</loc>", sitemap)

    def test_generated_validation_rejects_a_missing_asset(self):
        pages = site_build.build()
        (self.output / "style.css").unlink()
        with self.assertRaisesRegex(ValueError, "Broken local link"):
            site_build.check_links(pages)


if __name__ == "__main__":
    unittest.main()
