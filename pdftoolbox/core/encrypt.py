"""Encrypt a PDF with a user-supplied password."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .exceptions import EncryptedPDFError, PDFToolError
from .validation import validate_pdf

# Preferred algorithms in descending strength order; pypdf 4.x supports these as strings.
_ALGORITHM_PREFERENCE = ["AES-256", "AES-256-R5", "AES-128"]


def encrypt_pdf(
    input_path: str | Path,
    password: str,
    output_path: str | Path,
) -> str:
    """
    Produce a password-protected copy of input_path at output_path.

    Uses AES-256 when available, falling back to AES-128.
    Returns the algorithm name used.
    Raises EncryptedPDFError if the file is already encrypted.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if output_path.resolve() == input_path.resolve():
        raise PDFToolError("Output path must differ from the input file.")

    if not input_path.exists():
        raise PDFToolError(f"File not found: {input_path}")

    if not password:
        raise PDFToolError("Password must not be empty.")

    is_encrypted, _ = validate_pdf(input_path)
    if is_encrypted:
        raise EncryptedPDFError(f"'{input_path.name}' is already encrypted.")

    try:
        reader = PdfReader(str(input_path))
    except Exception as exc:
        raise PDFToolError(f"Could not read '{input_path.name}': {exc}") from exc

    writer = PdfWriter()
    writer.append_pages_from_reader(reader)

    algorithm_used = "RC4-128 (fallback)"
    for algo in _ALGORITHM_PREFERENCE:
        try:
            writer.encrypt(user_password=password, algorithm=algo)
            algorithm_used = algo
            break
        except Exception:
            continue
    else:
        # All AES algorithms unavailable (missing 'cryptography' package); fall back to RC4-128
        writer.encrypt(user_password=password, algorithm="RC4-128")

    try:
        with open(output_path, "wb") as out:
            writer.write(out)
    except OSError as exc:
        raise PDFToolError(f"Could not write output file: {exc}") from exc

    return algorithm_used
