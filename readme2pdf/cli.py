"""readme2pdf — command-line interface."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from . import __version__
from .fetcher import fetch_markdown
from .converter import convert, _BUILTIN_THEMES


def _default_output(source: str) -> Path:
    """Derive a sensible output filename from the source."""
    if source.startswith("http"):
        # e.g. https://github.com/user/repo → user_repo.pdf
        parts = [p for p in source.split("/") if p and p not in ("http:", "https:", "github.com")]
        stem = "_".join(parts[:2]) if len(parts) >= 2 else "readme"
    else:
        stem = Path(source).stem
    return Path(f"{stem}.pdf")


THEME_NAMES = sorted(_BUILTIN_THEMES.keys())


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version")
@click.argument("source", metavar="SOURCE")
@click.option(
    "-o", "--output",
    type=click.Path(dir_okay=False, writable=True),
    default=None,
    help="Output PDF path.  [default: <source-stem>.pdf]",
)
@click.option(
    "--theme",
    type=click.Choice(THEME_NAMES, case_sensitive=False),
    default="github",
    show_default=True,
    help="Built-in colour theme.",
)
@click.option(
    "--css",
    "custom_css",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    default=None,
    help="Path to a custom CSS file (overrides --theme).",
)
@click.option(
    "--pygments-style",
    default="monokai",
    show_default=True,
    help="Pygments colour scheme for code blocks (e.g. monokai, dracula, github-dark).",
)
@click.option(
    "--page-size",
    default="A4",
    show_default=True,
    help="PDF page format: A4, Letter, Legal, A3 …",
)
@click.option(
    "--landscape",
    is_flag=True,
    default=False,
    help="Render in landscape orientation.",
)
@click.option(
    "--open",
    "open_after",
    is_flag=True,
    default=False,
    help="Open the generated PDF in the system viewer.",
)
def main(
    source: str,
    output: str | None,
    theme: str,
    custom_css: str | None,
    pygments_style: str,
    page_size: str,
    landscape: bool,
    open_after: bool,
) -> None:
    """Convert a Markdown file or GitHub README to a PDF.

    \b
    SOURCE can be:
      • A local Markdown file path    readme2pdf README.md
      • A GitHub repository URL       readme2pdf https://github.com/user/repo

    \b
    Examples:
      readme2pdf README.md
      readme2pdf README.md -o docs/output.pdf --theme dark
      readme2pdf https://github.com/psf/requests --theme terminal
      readme2pdf README.md --css mybrand.css --pygments-style dracula
    """
    out_path = Path(output) if output else _default_output(source)

    # ── Fetch ──────────────────────────────────────────────────────────
    click.echo(f"  fetching  {source}")
    try:
        md_text, display_name = fetch_markdown(source)
    except (FileNotFoundError, ValueError) as exc:
        click.echo(f"✗ {exc}", err=True)
        sys.exit(1)
    click.echo(f"  source    {display_name}")

    # ── Convert ────────────────────────────────────────────────────────
    css_path = Path(custom_css) if custom_css else None
    click.echo(f"  theme     {css_path.name if css_path else theme}")
    click.echo(f"  rendering → {out_path}")

    try:
        convert(
            md_text,
            output_path=out_path,
            theme=theme,
            custom_css=css_path,
            pygments_style=pygments_style,
            page_size=page_size,
            landscape=landscape,
        )
    except Exception as exc:  # noqa: BLE001
        click.echo(f"✗ conversion failed: {exc}", err=True)
        sys.exit(1)

    size_kb = out_path.stat().st_size // 1024
    click.echo(f"✓ saved    {out_path}  ({size_kb} KB)")

    if open_after:
        import subprocess, platform
        cmd = {"darwin": "open", "win32": "start", "linux": "xdg-open"}.get(
            platform.system().lower(), "xdg-open"
        )
        subprocess.Popen([cmd, str(out_path)])


if __name__ == "__main__":
    main()
