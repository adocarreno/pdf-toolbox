# PDF Tool Box

A cross-platform desktop GUI (and CLI) suite of independent PDF utilities, built with Python, PySide6, and pypdf.

## Download

Pre-built binaries are attached to every [GitHub Release](https://github.com/adocarreno/pdf-toolbox/releases):

| Platform | File | Install |
|---|---|---|
| macOS | `PDF-Tool-Box-macOS.dmg` | Mount → drag app to Applications |
| Windows | `PDF-Tool-Box-Windows.zip` | Extract → run `PDF Tool Box.exe` |
| Linux | `PDF-Tool-Box-Linux.tar.gz` | Extract → run `PDF\ Tool\ Box/PDF\ Tool\ Box` |

> **macOS Gatekeeper:** Because the build is unsigned, macOS blocks it on first launch.
> Fix: **right-click the app → Open → Open** (once only).

## What it does

| Tool | Description |
|---|---|
| **PDF Merger** | Combine multiple PDFs in any order into a single file |
| **PDF Splitter** | Extract selected pages (e.g. `1-3, 5, 8-10`) into a new file |
| **Secure PDF** | Encrypt a PDF with a password (AES-256) |
| **Unsecure PDF** | Remove encryption using the correct password |
| **Meta Editor** | Read, edit, or clear document metadata (title, author, etc.) |

## Run from source

### Requirements
- Python 3.11+
- No system binaries or OS packages required — just `pip install`.

```bash
git clone https://github.com/adocarreno/pdf-toolbox.git
cd pdf-toolbox
pip install -e .        # installs all deps and registers entry points
```

### Run the GUI

```bash
pdf-toolbox             # from anywhere, after pip install -e .
# or
python -m pdftoolbox.app
```

Select a tool from the left sidebar. Each panel has:
1. A file selection area
2. Tool-specific options
3. An **Execute** button
4. An output path chooser
5. A status/result line

**Input files are never modified.** Every operation writes a new output file.

## CLI usage

All operations are available via `python -m pdftoolbox.cli`:

```bash
# Merge PDFs
python -m pdftoolbox.cli merge a.pdf b.pdf c.pdf -o combined.pdf

# Extract pages (supports ranges and individual pages)
python -m pdftoolbox.cli split report.pdf --pages "1-3,5,8-10" -o excerpt.pdf

# Encrypt a PDF (password prompted interactively — never passed as an argument)
python -m pdftoolbox.cli encrypt contract.pdf -o contract_locked.pdf

# Edit metadata
python -m pdftoolbox.cli metadata report.pdf --title "Annual Report" --author "Jane" -o updated.pdf

# Clear all metadata
python -m pdftoolbox.cli metadata report.pdf --clear -o clean.pdf
```

> **Note:** The decrypt subcommand is intentionally omitted from the CLI. Use the GUI's *Unsecure PDF* panel to decrypt files interactively.

## Run tests

```bash
pytest
```

68 tests cover the core layer and CLI. No GUI tests in v1.

## Build a native executable locally

```bash
pip install pyinstaller
pyinstaller pdf-toolbox.spec
```

Output lands in `dist/`:
- **macOS** → `dist/PDF Tool Box.app`
- **Windows** → `dist/PDF Tool Box/` (folder with `PDF Tool Box.exe` inside)
- **Linux** → `dist/PDF Tool Box/` (folder with `PDF Tool Box` binary inside)

CI builds for all three platforms automatically on every push — see `.github/workflows/ci.yml`.
Pushing a tag like `v1.1.0` triggers a GitHub Release with the platform artifacts attached.

---

## How to add a new tool module

The tool registry makes adding tools a one-file change.

### 1. Create your tool file

Add `pdftoolbox/tools/my_tool.py`:

```python
from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from .base import PDFTool, register

@register                          # ← this is all the registration needed
class MyTool(PDFTool):
    name = "My Tool"
    description = "One-line description shown in the sidebar."

    def build_widget(self, parent: QWidget | None = None) -> QWidget:
        w = QWidget(parent)
        layout = QVBoxLayout(w)
        layout.addWidget(QLabel("Hello from My Tool!"))
        # Add your controls, connect signals, call core functions
        return w
```

### 2. Import it in `main_window.py`

Add one import line alongside the existing tool imports:

```python
import pdftoolbox.tools.my_tool  # noqa: F401
```

That's it. The main window reads the registry at startup and automatically adds your tool to the sidebar. No other files need to change.

### Core layer convention

Put all PDF logic in `pdftoolbox/core/` as pure functions. Never import PySide6 from core modules. Raise typed exceptions from `pdftoolbox/core/exceptions.py` so both the GUI and CLI can catch them cleanly.

---

## Architecture overview

```
pdftoolbox/
  core/          Pure Python PDF logic. No GUI imports
  tools/         GUI panels; each registers itself via @register
  app.py         QApplication entry point
  main_window.py Shell; reads the tool registry to build the sidebar
  cli.py         Thin argparse wrapper over core functions
```
