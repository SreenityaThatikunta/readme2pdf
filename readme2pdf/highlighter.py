"""Pygments helpers: inject CSS and highlight fenced code blocks in HTML."""

from __future__ import annotations

import re

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.util import ClassNotFound

# Matches <code class="language-xxx"> ... </code> produced by markdown-it
_CODE_RE = re.compile(
    r'<code class="language-(?P<lang>[^"]+)">(?P<body>.*?)</code>',
    re.DOTALL,
)

# Plain <code> blocks without a language tag
_PLAIN_CODE_RE = re.compile(r"<pre><code>(?P<body>.*?)</code></pre>", re.DOTALL)


def _unescape(html: str) -> str:
    return (
        html.replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )


def _highlight_match(m: re.Match) -> str:
    lang = m.group("lang")
    body = _unescape(m.group("body"))
    try:
        lexer = get_lexer_by_name(lang, stripall=True)
    except ClassNotFound:
        lexer = TextLexer(stripall=True)
    formatter = HtmlFormatter(nowrap=True, cssclass="highlight")
    highlighted = highlight(body, lexer, formatter)
    return f'<code class="language-{lang} highlight">{highlighted}</code>'


def _highlight_plain(m: re.Match) -> str:
    body = _unescape(m.group("body"))
    try:
        lexer = guess_lexer(body)
    except ClassNotFound:
        lexer = TextLexer()
    formatter = HtmlFormatter(nowrap=True, cssclass="highlight")
    highlighted = highlight(body, lexer, formatter)
    return f"<pre><code class='highlight'>{highlighted}</code></pre>"


def apply_highlighting(html: str) -> str:
    """Replace fenced code blocks with Pygments-highlighted equivalents."""
    html = _CODE_RE.sub(_highlight_match, html)
    html = _PLAIN_CODE_RE.sub(_highlight_plain, html)
    return html


def get_pygments_css(style: str = "monokai") -> str:
    """Return the Pygments CSS for *style* scoped to .highlight."""
    return HtmlFormatter(style=style, cssclass="highlight").get_style_defs()
