"""Extract a subset of pages from a PDF into a new file."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .exceptions import EncryptedPDFError, PDFToolError
from .pageparse import parse_page_range
from .validation import validate_pdf


def split_pdf(
    input_path: str | Path,
    page_spec: str,
    output_path: str | Path,
) -> int:
    """
    Extract pages described by page_spec from input_path and write to output_path.

    page_spec uses 1-based page numbers, e.g. "1-3, 5, 8-10".
    Returns the number of pages written.
    Raises PageRangeError, EncryptedPDFError, or PDFToolError as appropriate.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if output_path.resolve() == input_path.resolve():
        raise PDFToolError("Output path must differ from the input file.")

    is_encrypted, _ = validate_pdf(input_path)
    if is_encrypted:
        raise EncryptedPDFError(f"'{input_path.name}' is encrypted; decrypt it first.")

    try:
        reader = PdfReader(str(input_path))
    except Exception as exc:
        raise PDFToolError(f"Could not read '{input_path.name}': {exc}") from exc

    total_pages = len(reader.pages)
    indices = parse_page_range(page_spec, total_pages)

    writer = PdfWriter()
    for idx in indices:
        writer.add_page(reader.pages[idx])

    try:
        with open(output_path, "wb") as out:
            writer.write(out)
    except OSError as exc:
        raise PDFToolError(f"Could not write output file: {exc}") from exc

    return len(indices)


def get_page_count(input_path: str | Path) -> int:
    """
    Return the number of pages in a PDF.

    Raises NotAPDFError, EncryptedPDFError, EmptyPDFError, or PDFToolError as appropriate.
    """
    input_path = Path(input_path)
    is_encrypted, page_count = validate_pdf(input_path)
    if is_encrypted:
        raise EncryptedPDFError(f"'{input_path.name}' is encrypted; decrypt it first.")
    return page_count
