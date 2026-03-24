# readme2pdf

Convert any Markdown file or GitHub README into a polished PDF — right from your terminal.

```bash
readme2pdf README.md --theme dark
readme2pdf https://github.com/psf/requests --theme terminal -o requests.pdf
```

## Features

- **High-fidelity rendering** — headless Chromium (Playwright) produces pixel-perfect CSS layouts
- **3 built-in themes** — `github` (light), `dark`, and `terminal` (green-on-black monospace)
- **Syntax highlighting** — Pygments-powered, 500+ languages, configurable colour schemes
- **GitHub README fetcher** — paste a repo URL and get a PDF instantly
- **Custom CSS** — supply your own stylesheet for full control
- **Flexible page options** — A4, Letter, Legal, A3, landscape, and more

## Installation

```bash
# 1. Install the package
pip install -e .

# 2. Install the Playwright browser
playwright install chromium
```

## Usage

```
Usage: readme2pdf [OPTIONS] SOURCE

  Convert a Markdown file or GitHub README to a PDF.

  SOURCE can be:
    - A local Markdown file path    readme2pdf README.md
    - A GitHub repository URL       readme2pdf https://github.com/user/repo

Options:
  -o, --output PATH              Output PDF path  [default: <source-stem>.pdf]
  --theme [dark|github|terminal] Built-in colour theme  [default: github]
  --css PATH                     Custom CSS file (overrides --theme)
  --pygments-style TEXT          Pygments colour scheme for code blocks  [default: monokai]
  --page-size TEXT               PDF page format: A4, Letter, Legal, A3 …  [default: A4]
  --landscape                    Render in landscape orientation
  --open                         Open the generated PDF after saving
  -V, --version                  Show the version and exit
  -h, --help                     Show this message and exit
```

### Examples

```bash
# Local file, default github theme
readme2pdf README.md

# Dark theme, custom output path
readme2pdf README.md -o docs/output.pdf --theme dark

# Fetch a GitHub repo's README
readme2pdf https://github.com/psf/requests --theme terminal

# Custom CSS with dracula code highlighting
readme2pdf README.md --css mybrand.css --pygments-style dracula

# A3 landscape for wide table-heavy docs
readme2pdf REPORT.md --page-size A3 --landscape

# Open the PDF after generating
readme2pdf README.md --open
```

## Themes

| Theme      | Description                             |
| ---------- | --------------------------------------- |
| `github`   | Clean light theme matching GitHub.com   |
| `dark`     | Dark-dimmed, easy on the eyes           |
| `terminal` | Green-on-black CRT aesthetic, monospace |

Use `--css` to supply a custom theme:

```bash
readme2pdf README.md --css mytheme.css
```

## Project Structure

```
readme2pdf/
├── readme2pdf/
│   ├── __init__.py        # version
│   ├── cli.py             # Click CLI entry point
│   ├── converter.py       # Markdown → HTML → PDF pipeline
│   ├── fetcher.py         # GitHub URL → raw Markdown
│   ├── highlighter.py     # Pygments syntax highlighting
│   └── themes/
│       ├── github.css
│       ├── dark.css
│       └── terminal.css
├── pyproject.toml
└── README.md
```

## Requirements

- Python >= 3.10
- Chromium (installed via `playwright install chromium`)

## License

MIT
