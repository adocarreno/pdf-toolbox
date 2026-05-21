"""Tests for the validate_pdf pre-flight check."""

from __future__ import annotations

import pytest

from pdftoolbox.core.exceptions import EmptyPDFError, NotAPDFError, PDFToolError
from pdftoolbox.core.validation import validate_pdf
from .helpers import make_pdf


def test_valid_unencrypted_pdf(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=3)
    is_encrypted, page_count = validate_pdf(src)
    assert is_encrypted is False
    assert page_count == 3


def test_valid_encrypted_pdf(tmp_path):
    from pdftoolbox.core.encrypt import encrypt_pdf

    src = make_pdf(tmp_path / "src.pdf", num_pages=2)
    enc = tmp_path / "enc.pdf"
    encrypt_pdf(src, "pw", enc)

    is_encrypted, page_count = validate_pdf(enc)
    assert is_encrypted is True
    assert page_count == 0  # page count inaccessible without password


def test_missing_file_raises(tmp_path):
    with pytest.raises(PDFToolError):
        validate_pdf(tmp_path / "missing.pdf")


def test_not_a_pdf_raises(tmp_path):
    bad = tmp_path / "fake.pdf"
    bad.write_text("This is just plain text, not a PDF.")
    with pytest.raises(NotAPDFError):
        validate_pdf(bad)


def test_binary_non_pdf_raises(tmp_path):
    bad = tmp_path / "image.pdf"
    # PNG magic bytes — definitely not a PDF
    bad.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    with pytest.raises(NotAPDFError):
        validate_pdf(bad)


def test_empty_file_raises(tmp_path):
    empty = tmp_path / "empty.pdf"
    empty.write_bytes(b"")
    with pytest.raises(NotAPDFError):
        validate_pdf(empty)


def test_truncated_pdf_raises(tmp_path):
    """A file that starts with %PDF- but has no valid structure."""
    bad = tmp_path / "truncated.pdf"
    bad.write_bytes(b"%PDF-1.4\n%%EOF")
    # pypdf may or may not raise — but it should never silently succeed with 0 pages
    # Accept either NotAPDFError or EmptyPDFError
    with pytest.raises((NotAPDFError, EmptyPDFError, PDFToolError)):
        validate_pdf(bad)


def test_pdf_with_pages_returns_correct_count(tmp_path):
    for n in (1, 5, 10):
        src = make_pdf(tmp_path / f"p{n}.pdf", num_pages=n)
        _, count = validate_pdf(src)
        assert count == n
