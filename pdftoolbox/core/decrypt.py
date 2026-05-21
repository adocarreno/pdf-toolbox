"""Decrypt an encrypted PDF using a user-supplied password."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter

from .exceptions import InvalidPasswordError, NotEncryptedError, PDFToolError
from .validation import validate_pdf


def decrypt_pdf(
    input_path: str | Path,
    password: str,
    output_path: str | Path,
) -> None:
    """
    Write a decrypted copy of input_path to output_path using password.

    Raises NotEncryptedError if the file is not encrypted.
    Raises InvalidPasswordError if the password is wrong.
    Never attempts to bypass or brute-force encryption.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if output_path.resolve() == input_path.resolve():
        raise PDFToolError("Output path must differ from the input file.")

    # validate_pdf confirms the file is a readable PDF and tells us its encryption state
    is_encrypted, _ = validate_pdf(input_path)
    if not is_encrypted:
        raise NotEncryptedError(f"'{input_path.name}' is not encrypted.")

    try:
        reader = PdfReader(str(input_path))
    except Exception as exc:
        raise PDFToolError(f"Could not open '{input_path.name}': {exc}") from exc

    result = reader.decrypt(password)
    # decrypt() returns 0 on failure, 1 for user password match, 2 for owner password match
    if result == 0:
        raise InvalidPasswordError("Incorrect password.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    try:
        with open(output_path, "wb") as out:
            writer.write(out)
    except OSError as exc:
        raise PDFToolError(f"Could not write output file: {exc}") from exc
