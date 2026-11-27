# Editing and publishing the guide

## Local work

Use Python 3.10 or later. The build and examples use only the standard library.

```sh
python3 -m unittest discover -s tests -v
python3 site/build.py --check
python3 -m http.server --directory _site 8000
```

Open [localhost:8000](http://localhost:8000). The build always checks the catalogue, local source links, generated links and section anchors. The `--check` spelling is retained as an explicit validation command. It does not contact external websites.

Generated `_site/` files are ignored. Site checks and example tests run on every pull request.

## Add or edit a pattern

Each entry lives in `patterns/` as Markdown. Use one opening title, an italic subtitle, and descriptive second-level headings. Add its slug, title, problem, summary, group and search terms to `site/catalog.json`. That file controls the website order; update the README reading list too.

The small renderer supports headings, paragraphs, inline emphasis and links, fenced code, blockquotes, flat lists and simple pipe tables. Use a blank line between blocks. Nested lists, HTML, footnotes and pipe characters within table cells are outside its supported subset.

Source links between entries use relative Markdown paths. The generator converts them to HTML links. Links to example code and repository documentation go to GitHub. If you add a new top-level page, add its routing and build step explicitly.

Each pattern should give a reader:

- A problem they can recognize from ordinary work.
- An intervention small enough to try.
- A concrete example with sufficient detail to adapt.
- The costs, constraints and conditions under which the attempt should stop.
- A way to check whether later work benefited.
- Sources that explain where the technique came from, and related patterns.

These are editorial requirements, not compulsory section titles. Let the example determine the article's structure.

## Editorial approach

Write as an engineer explaining a decision to a colleague. Prefer a specific failure, command or trade-off to a sentence about the importance of engineering excellence. Remove repeated promises, slogans, forced contrasts and conclusions that simply repeat the introduction.

Do not invent personal experience, quotations, customer results or measurements. Identify hypothetical examples. Attribute factual technical claims to primary sources and explain the limits of those sources. Distinguish the existing technique from this collection's proposed pattern name.

A useful pattern includes the upkeep it creates. Claims about AI saving time or a practice compounding need evidence. If the evidence is only a plausible mechanism, say so. A source list is not a substitute for explaining which claim a source supports.

Keep runnable examples honest. A command presented as part of this repository must work from the documented directory. Label adaptation sketches and pseudocode. Tests should exercise both the deliberately broken behavior and the corrected behavior.

For substantial changes, use the [technical review skill](./skills/technical-review/SKILL.md) to check what the example demonstrates and what it leaves open. The [compounding pass](./skills/compounding-pass/SKILL.md) can suggest a worthwhile follow-up after work is complete. Both are optional, and neither grants authority to make changes. Keep the [skill collection](./skills/README.md) small; exercise an existing method before adding another one.

## GitHub Pages

In [Settings → Pages](https://github.com/grove/patterns-of-compounding-engineering/settings/pages), set **Build and deployment → Source** to **GitHub Actions**. This repository setting is separate from the files in a pull request.

The workflow in `.github/workflows/pages.yml` runs the example and renderer tests, builds the site and validates internal links. Pull requests upload a `site-preview` artifact; download and extract it, then serve that directory locally to review the rendered pages. Source and example links in this artifact point to the pull request commit, so they also work before merge. Local builds default to `main`; set `SITE_SOURCE_REF` to a branch or commit to override that.

A push to `main`, including merging a pull request, publishes the generated site to:

https://grove.github.io/patterns-of-compounding-engineering/

The workflow can also be dispatched manually on `main`. Pull requests do not deploy. Only the deployment job receives `pages: write` and `id-token: write`; all other jobs have read access to repository contents. Existing environment approvals and branch rules still apply.

See GitHub's [publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and [custom workflow guide](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Presentation and accessibility

The Nordic Crisp theme is defined by CSS variables in `site/style.css`: white and cool grey surfaces, deep navy text, fjord blue links and teal accents. Dark mode follows the reader's system preference. Fonts are local system fonts; the site has no external font, analytics or JavaScript dependencies.

Keep body text readable, keyboard focus visible and code and tables scrollable on narrow screens. The catalogue's optional JavaScript filters the existing list; it does not fetch article content. Every page and link must remain usable with JavaScript disabled.

## Attribution

Keep `LICENSE`, `NOTICE` and the notices in the adapted renderer and build code. The earlier collections supplied the Markdown renderer and the approach to build validation. This series adds its own catalogue, layout and examples.

