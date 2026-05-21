"""Shared test helpers — programmatic PDF generation without external fixtures."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfWriter


def make_pdf(path: str | Path, num_pages: int = 3) -> Path:
    """Create a minimal valid PDF with num_pages blank pages at path."""
    path = Path(path)
    writer = PdfWriter()
    for _ in range(num_pages):
        writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as fh:
        writer.write(fh)
    return path
