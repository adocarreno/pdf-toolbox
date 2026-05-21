"""Read and write PDF document metadata."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .exceptions import EncryptedPDFError, PDFToolError
from .validation import validate_pdf

# Standard XMP/Info keys pypdf exposes
STANDARD_KEYS = [
    "/Title",
    "/Author",
    "/Subject",
    "/Keywords",
    "/Creator",
    "/Producer",
    "/CreationDate",
    "/ModDate",
]


def read_metadata(input_path: str | Path) -> dict[str, str]:
    """
    Return a dict of metadata key → value for the given PDF.

    Keys use the raw PDF name format (e.g. '/Title').
    Returns an empty dict if no metadata is present.
    """
    input_path = Path(input_path)

    is_encrypted, _ = validate_pdf(input_path)
    if is_encrypted:
        raise EncryptedPDFError(f"'{input_path.name}' is encrypted; decrypt it first.")

    try:
        reader = PdfReader(str(input_path))
    except Exception as exc:
        raise PDFToolError(f"Could not read '{input_path.name}': {exc}") from exc

    info = reader.metadata
    if info is None:
        return {}

    result: dict[str, str] = {}
    for key in info:
        val = info.get(key)
        if val is not None:
            result[str(key)] = str(val)
    return result


def write_metadata(
    input_path: str | Path,
    output_path: str | Path,
    updates: dict[str, str],
    clear_existing: bool = False,
) -> None:
    """
    Write a new PDF with updated metadata.

    If clear_existing is True, all existing metadata is removed before applying updates.
    updates maps raw PDF key names (e.g. '/Title') to string values.
    Empty-string values are treated as deletions (key removed).
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

    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    if clear_existing:
        # Clone reader into writer then clear all info entries
        writer.add_metadata({})
        # Explicitly clear every standard key
        new_meta: dict[str, str] = {}
    else:
        existing = reader.metadata or {}
        new_meta = {str(k): str(v) for k, v in existing.items() if v is not None}

    for key, value in updates.items():
        if value == "":
            new_meta.pop(key, None)
        else:
            new_meta[key] = value

    writer.add_metadata(new_meta)

    try:
        with open(output_path, "wb") as out:
            writer.write(out)
    except OSError as exc:
        raise PDFToolError(f"Could not write output file: {exc}") from exc
