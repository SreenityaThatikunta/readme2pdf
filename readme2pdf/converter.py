"""Core conversion pipeline: Markdown → HTML → PDF (via Playwright)."""

from __future__ import annotations

import re
from pathlib import Path

import markdown
from markdown.extensions.tables import TableExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.nl2br import Nl2BrExtension
from markdown.extensions.sane_lists import SaneListExtension

from .highlighter import apply_highlighting, get_pygments_css

_THEMES_DIR = Path(__file__).parent / "themes"
_BUILTIN_THEMES = {p.stem: p for p in _THEMES_DIR.glob("*.css")}

_BADGE_RE = re.compile(
    r'<img[^>]+src="https://(?:img\.shields\.io|badge\.fury\.io|github\.com/[^"]+/workflows)[^"]*"[^>]*>',
    re.IGNORECASE,
)


def _load_theme_css(theme: str, custom_css: Path | None) -> str:
    if custom_css:
        return custom_css.read_text(encoding="utf-8")
    stem = theme.lower()
    if stem in _BUILTIN_THEMES:
        return _BUILTIN_THEMES[stem].read_text(encoding="utf-8")
    raise ValueError(
        f"Unknown theme '{theme}'. "
        f"Built-in themes: {', '.join(sorted(_BUILTIN_THEMES))}. "
        "Use --css to supply a custom stylesheet."
    )


def _md_to_html(md_text: str) -> str:
    extensions = [
        TableExtension(),
        FencedCodeExtension(),
        TocExtension(slugify=lambda value, sep: re.sub(r"\s+", sep, value.lower())),
        Nl2BrExtension(),
        SaneListExtension(),
        "attr_list",
        "def_list",
        "footnotes",
        "admonition",
        "meta",
        "smarty",
    ]
    return markdown.markdown(md_text, extensions=extensions, output_format="html")


def _build_page(body_html: str, theme_css: str, pygments_style: str) -> str:
    pyg_css = get_pygments_css(pygments_style)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
/* ── Pygments ──────────────────────────────────────────── */
{pyg_css}

/* ── Theme ─────────────────────────────────────────────── */
{theme_css}

/* ── Print tweaks ───────────────────────────────────────── */
@media print {{
  body {{ margin: 0; padding: 2cm 2.5cm; max-width: none; }}
  pre, blockquote, table {{ page-break-inside: avoid; }}
  h1, h2, h3 {{ page-break-after: avoid; }}
  a::after {{ display: none; }}
}}
  </style>
</head>
<body>
{body_html}
</body>
</html>"""


def convert(
    md_text: str,
    output_path: Path,
    theme: str = "github",
    custom_css: Path | None = None,
    pygments_style: str = "monokai",
    page_size: str = "A4",
    landscape: bool = False,
) -> None:
    """
    Convert *md_text* to a PDF at *output_path*.

    Parameters
    ----------
    md_text       : Raw Markdown source.
    output_path   : Destination .pdf file.
    theme         : Built-in theme name (github | dark | terminal).
    custom_css    : Path to a user-supplied .css file (overrides *theme*).
    pygments_style: Pygments colour scheme for code blocks.
    page_size     : Playwright page format, e.g. "A4", "Letter".
    landscape     : Render in landscape orientation.
    """
    # 1. Markdown → HTML
    body_html = _md_to_html(md_text)

    # 2. Inject syntax highlighting
    body_html = apply_highlighting(body_html)

    # 3. Load theme CSS
    theme_css = _load_theme_css(theme, custom_css)

    # 4. Assemble full HTML page
    page_html = _build_page(body_html, theme_css, pygments_style)

    # 5. Render to PDF with Playwright
    from playwright.sync_api import sync_playwright  # lazy import

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(page_html, wait_until="networkidle")
        page.pdf(
            path=str(output_path),
            format=page_size,
            landscape=landscape,
            margin={"top": "0cm", "bottom": "0cm", "left": "0", "right": "0"},
            print_background=True,
        )
        browser.close()
