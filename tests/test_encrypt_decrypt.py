"""Tests for encrypt/decrypt round trip."""

import pytest
from pypdf import PdfReader

from pdftoolbox.core.decrypt import decrypt_pdf
from pdftoolbox.core.encrypt import encrypt_pdf
from pdftoolbox.core.exceptions import (
    EncryptedPDFError,
    InvalidPasswordError,
    NotEncryptedError,
    PDFToolError,
)
from .helpers import make_pdf


def test_encrypt_produces_encrypted_file(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=2)
    enc = tmp_path / "enc.pdf"

    encrypt_pdf(src, "secret", enc)

    reader = PdfReader(str(enc))
    assert reader.is_encrypted


def test_encrypt_does_not_modify_original(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=2)
    original_bytes = src.read_bytes()
    enc = tmp_path / "enc.pdf"

    encrypt_pdf(src, "secret", enc)

    assert src.read_bytes() == original_bytes


def test_decrypt_round_trip(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=3)
    enc = tmp_path / "enc.pdf"
    dec = tmp_path / "dec.pdf"

    encrypt_pdf(src, "roundtrip", enc)
    decrypt_pdf(enc, "roundtrip", dec)

    reader = PdfReader(str(dec))
    assert not reader.is_encrypted
    assert len(reader.pages) == 3


def test_decrypt_wrong_password_raises(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=2)
    enc = tmp_path / "enc.pdf"

    encrypt_pdf(src, "correct", enc)

    with pytest.raises(InvalidPasswordError):
        decrypt_pdf(enc, "wrong", tmp_path / "dec.pdf")


def test_decrypt_not_encrypted_raises(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=2)
    with pytest.raises(NotEncryptedError):
        decrypt_pdf(src, "any", tmp_path / "dec.pdf")


def test_encrypt_already_encrypted_raises(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=2)
    enc = tmp_path / "enc.pdf"
    enc2 = tmp_path / "enc2.pdf"

    encrypt_pdf(src, "first", enc)

    with pytest.raises(EncryptedPDFError):
        encrypt_pdf(enc, "second", enc2)


def test_encrypt_empty_password_raises(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=2)
    with pytest.raises(PDFToolError):
        encrypt_pdf(src, "", tmp_path / "enc.pdf")


def test_encrypt_output_same_as_input_raises(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=2)
    with pytest.raises(PDFToolError):
        encrypt_pdf(src, "pw", src)
