"""Merge multiple PDF files into a single output file."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .exceptions import EncryptedPDFError, PDFToolError
from .validation import validate_pdf


def merge_pdfs(input_paths: list[str | Path], output_path: str | Path) -> int:
    """
    Merge PDFs in the given order into output_path.

    Returns the total number of pages in the merged document.
    Raises NotAPDFError if any input is not a valid PDF.
    Raises EncryptedPDFError if any input is encrypted.
    Raises EmptyPDFError if any input has no pages.
    Raises PDFToolError for other failures.
    """
    if not input_paths:
        raise PDFToolError("No input files provided.")

    output_path = Path(output_path)
    if output_path.resolve() in [Path(p).resolve() for p in input_paths]:
        raise PDFToolError("Output path must not be the same as any input file.")

    # Validate all inputs before doing any writing
    for path in input_paths:
        is_encrypted, _ = validate_pdf(path)
        if is_encrypted:
            raise EncryptedPDFError(
                f"'{Path(path).name}' is encrypted; decrypt it first."
            )

    writer = PdfWriter()
    for path in input_paths:
        path = Path(path)
        try:
            reader = PdfReader(str(path))
            writer.append_pages_from_reader(reader)
        except Exception as exc:
            raise PDFToolError(f"Could not read '{path.name}': {exc}") from exc

    try:
        with open(output_path, "wb") as out:
            writer.write(out)
    except OSError as exc:
        raise PDFToolError(f"Could not write output file: {exc}") from exc

    return writer.get_num_pages()
