"""Small Markdown renderer adapted from grove/engineering-that-compounds.

Modified for Patterns of compounding engineering: table support, code labels,
and stable heading navigation. Distributed under Apache-2.0; see NOTICE.
"""
from __future__ import annotations
import html
import math
import re

def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "section"


def strip_markdown(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_]+", "", text)
    return " ".join(text.split())


def reading_minutes(text: str) -> int:
    words = len(re.findall(r"\b\w+(?:['’]\w+)*\b", strip_markdown(text)))
    return max(1, math.ceil(words / 230))


def render_inline(text: str, resolve_link) -> str:
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "`":
            end = text.find("`", i + 1)
            if end != -1:
                out.append(f"<code>{html.escape(text[i + 1 : end])}</code>")
                i = end + 1
                continue
        elif ch == "[":
            close_bracket = text.find("]", i + 1)
            if close_bracket != -1 and close_bracket + 1 < n and text[close_bracket + 1] == "(":
                depth = 1
                j = close_bracket + 2
                while j < n and depth > 0:
                    if text[j] == "(":
                        depth += 1
                    elif text[j] == ")":
                        depth -= 1
                    j += 1
                if depth == 0:
                    label = render_inline(text[i + 1 : close_bracket], resolve_link)
                    href = resolve_link(text[close_bracket + 2 : j - 1].strip())
                    out.append(f'<a href="{html.escape(href, quote=True)}">{label}</a>')
                    i = j
                    continue
        elif text.startswith("**", i):
            end = text.find("**", i + 2)
            if end != -1 and end > i + 2:
                out.append(f"<strong>{render_inline(text[i + 2 : end], resolve_link)}</strong>")
                i = end + 2
                continue
        elif ch == "*":
            end = text.find("*", i + 1)
            if end != -1 and end > i + 1 and not text[i + 1].isspace():
                out.append(f"<em>{render_inline(text[i + 1 : end], resolve_link)}</em>")
                i = end + 1
                continue
        out.append(html.escape(ch))
        i += 1
    return "".join(out)


def render_markdown(md: str, resolve_link, *, heading_ids: set[str] | None = None) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    blocks: list[str] = []
    seen_ids = set() if heading_ids is None else heading_ids
    i, n = 0, len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("```"):
            language = stripped[3:].strip()
            code_lines: list[str] = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i == n:
                raise ValueError("Unclosed code fence")
            i += 1
            label = f'<span class="code-label">{html.escape(language)}</span>' if language else ''
            blocks.append(f'<div class="code-block">{label}<pre tabindex="0"><code>{html.escape(chr(10).join(code_lines))}</code></pre></div>')
            continue


        if stripped.startswith('|') and i + 1 < n and re.fullmatch(r'\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?', lines[i + 1].strip()):
            headers = [cell.strip() for cell in stripped.strip('|').split('|')]
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith('|'):
                cells = [cell.strip() for cell in lines[i].strip().strip('|').split('|')]
                if len(cells) != len(headers):
                    raise ValueError('Table row does not match its header')
                rows.append('<tr>' + ''.join(f'<td>{render_inline(cell, resolve_link)}</td>' for cell in cells) + '</tr>')
                i += 1
            head = ''.join(f'<th scope="col">{render_inline(cell, resolve_link)}</th>' for cell in headers)
            blocks.append(f'<div class="table-scroll" role="region" aria-label="Comparison table" tabindex="0"><table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            level = len(heading.group(1))
            raw = heading.group(2).strip()
            base_id = slugify(strip_markdown(raw))
            hid = base_id
            suffix = 2
            while hid in seen_ids:
                hid = f"{base_id}-{suffix}"
                suffix += 1
            seen_ids.add(hid)
            blocks.append(f'<h{level} id="{hid}">{render_inline(raw, resolve_link)}</h{level}>')
            i += 1
            continue

        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            blocks.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < n and lines[i].strip().startswith(">"):
                q = lines[i].lstrip()[1:]
                quote_lines.append(q[1:] if q.startswith(" ") else q)
                i += 1
            inner = render_markdown("\n".join(quote_lines), resolve_link, heading_ids=seen_ids)
            blocks.append(f"<blockquote>\n{inner}\n</blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            items: list[str] = []
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip(), count=1))
                i += 1
            rendered = "\n".join(f"<li>{render_inline(it, resolve_link)}</li>" for it in items)
            blocks.append(f"<ul>\n{rendered}\n</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip(), count=1))
                i += 1
            rendered = "\n".join(f"<li>{render_inline(it, resolve_link)}</li>" for it in items)
            blocks.append(f"<ol>\n{rendered}\n</ol>")
            continue

        para_lines: list[str] = []
        while i < n:
            cur = lines[i].strip()
            if (
                not cur
                or cur.startswith("```")
                or cur.startswith(">")
                or re.match(r"^(#{1,6})\s+", cur)
                or re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", cur)
                or re.match(r"^([-*]|\d+\.)\s+", cur)
            ):
                break
            para_lines.append(cur)
            i += 1
        blocks.append(f"<p>{render_inline(' '.join(para_lines), resolve_link)}</p>")

    return "\n".join(blocks)


def split_header(md: str) -> tuple[str, str | None, str]:
    """Extract leading '# Title', optional '*Subtitle*', and remaining body."""
    lines = md.replace("\r\n", "\n").split("\n")
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    title = ""
    if idx < len(lines) and lines[idx].startswith("# "):
        title = lines[idx][2:].strip()
        idx += 1
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    subtitle = None
    if idx < len(lines):
        cand = lines[idx].strip()
        if cand.startswith("*") and cand.endswith("*") and not cand.startswith("**") and cand.count("*") == 2:
            subtitle = cand[1:-1].strip()
            idx += 1
    body = "\n".join(lines[idx:]).strip()
    return title, subtitle, body
