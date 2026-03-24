# fzap ⚡

> A blazing-fast file search and replace tool for the terminal.

![version](https://img.shields.io/badge/version-2.1.0-blue)
![python](https://img.shields.io/badge/python-3.10%2B-green)
![license](https://img.shields.io/badge/license-MIT-orange)

---

## Installation

```bash
pip install fzap
```

Or from source:

```bash
git clone https://github.com/example/fzap
cd fzap
pip install -e .
```

---

## Usage

```
Usage: fzap [OPTIONS] PATTERN REPLACEMENT PATH

Options:
  -r, --recursive     Search subdirectories
  -e, --ext TEXT      Filter by file extension (e.g. .py, .md)
  -n, --dry-run       Preview changes without writing
  -i, --ignore TEXT   Glob pattern to ignore
  -h, --help          Show this message and exit
```

### Examples

```bash
# Replace all occurrences of "foo" with "bar" in current directory
fzap foo bar .

# Recursive, only .py files
fzap foo bar . -r -e .py

# Dry run to preview
fzap TODO FIXME ./src -r --dry-run
```

---

## Benchmarks

Tested on a 50k file codebase (MacBook M2, Python 3.12):

| Tool     | Time (s) | Memory (MB) | Recursive |
|----------|----------|-------------|-----------|
| fzap     | 0.41     | 18          | ✅        |
| sed      | 1.23     | 8           | ❌        |
| ripgrep  | 0.38     | 22          | ✅        |
| grep -r  | 2.10     | 12          | ✅        |

---

## How It Works

fzap uses a two-phase approach:

1. **Index phase** — walks the directory tree and builds a list of candidate files using parallelised I/O
2. **Replace phase** — streams each file line by line, applies regex substitution, writes atomically via a temp file swap

```python
def replace_in_file(path: Path, pattern: str, replacement: str) -> int:
    """Returns number of replacements made."""
    tmp = path.with_suffix(".fzap.tmp")
    count = 0
    with path.open() as src, tmp.open("w") as dst:
        for line in src:
            new_line, n = re.subn(pattern, replacement, line)
            dst.write(new_line)
            count += n
    tmp.replace(path)
    return count
```

---

## Configuration

You can place a `.fzaprc` file in your project root:

```toml
[defaults]
recursive = true
extensions = [".py", ".md", ".txt"]
ignore = ["node_modules", ".git", "__pycache__"]
```

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

1. Fork the repo
2. Create your branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

MIT © 2024 example
