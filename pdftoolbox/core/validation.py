"""Pre-flight PDF validation: format, readability, encryption status, and page count."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError, PdfStreamError

from .exceptions import EmptyPDFError, NotAPDFError, PDFToolError

# The PDF spec allows the %PDF- signature within the first 1024 bytes.
_PDF_SIGNATURE = b"%PDF-"
_SIGNATURE_SCAN_BYTES = 1024


def validate_pdf(path: str | Path) -> tuple[bool, int]:
    """
    Validate that path points to a readable, well-formed PDF.

    Returns:
        (is_encrypted, page_count) — both values are only meaningful when the
        file is not encrypted; for encrypted files page_count is 0.

    Raises:
        PDFToolError      — file not found or unreadable (OS error)
        NotAPDFError      — file exists but is not a PDF
        EmptyPDFError     — valid PDF with zero pages
        EncryptedPDFError — not raised here; caller decides what to do with
                            is_encrypted=True
    """
    path = Path(path)

    if not path.exists():
        raise PDFToolError(f"File not found: {path}")
    if not path.is_file():
        raise PDFToolError(f"Path is not a file: {path}")

    # ── Magic-byte check ─────────────────────────────────────────────────────
    try:
        with open(path, "rb") as fh:
            header = fh.read(_SIGNATURE_SCAN_BYTES)
    except OSError as exc:
        raise PDFToolError(f"Cannot read '{path.name}': {exc}") from exc

    if _PDF_SIGNATURE not in header:
        raise NotAPDFError(
            f"'{path.name}' does not appear to be a PDF file "
            f"(missing %PDF- header)."
        )

    # ── Structural parse ─────────────────────────────────────────────────────
    try:
        reader = PdfReader(str(path))
    except (PdfReadError, PdfStreamError) as exc:
        raise NotAPDFError(
            f"'{path.name}' could not be parsed as a PDF: {exc}"
        ) from exc
    except Exception as exc:
        # pypdf may raise other exceptions for severely malformed files
        raise PDFToolError(
            f"Unexpected error reading '{path.name}': {exc}"
        ) from exc

    is_encrypted = reader.is_encrypted

    if is_encrypted:
        # Page count is inaccessible without the password; return 0 as sentinel
        return True, 0

    page_count = len(reader.pages)
    if page_count == 0:
        raise EmptyPDFError(f"'{path.name}' contains no pages.")

    return False, page_count
