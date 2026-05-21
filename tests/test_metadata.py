"""Tests for metadata read/write/clear."""

import pytest
from pypdf import PdfReader, PdfWriter

from pdftoolbox.core.exceptions import PDFToolError
from pdftoolbox.core.metadata import read_metadata, write_metadata
from .helpers import make_pdf


def make_pdf_with_meta(path, **meta):
    """Create a PDF with given metadata fields."""
    from pypdf import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_metadata(meta)
    with open(path, "wb") as fh:
        writer.write(fh)
    return path


def test_read_metadata_returns_dict(tmp_path):
    src = make_pdf_with_meta(
        tmp_path / "src.pdf",
        **{"/Title": "Test Title", "/Author": "Test Author"},
    )
    meta = read_metadata(src)
    assert meta.get("/Title") == "Test Title"
    assert meta.get("/Author") == "Test Author"


def test_read_metadata_empty_pdf(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=1)
    meta = read_metadata(src)
    assert isinstance(meta, dict)


def test_write_metadata_updates_fields(tmp_path):
    src = make_pdf_with_meta(tmp_path / "src.pdf", **{"/Title": "Old"})
    out = tmp_path / "out.pdf"

    write_metadata(src, out, {"/Title": "New Title"})

    meta = read_metadata(out)
    assert meta.get("/Title") == "New Title"


def test_write_metadata_preserves_other_fields(tmp_path):
    src = make_pdf_with_meta(
        tmp_path / "src.pdf",
        **{"/Title": "Title", "/Author": "Author"},
    )
    out = tmp_path / "out.pdf"

    write_metadata(src, out, {"/Title": "Updated"})

    meta = read_metadata(out)
    assert meta.get("/Author") == "Author"
    assert meta.get("/Title") == "Updated"


def test_write_metadata_clear_all(tmp_path):
    src = make_pdf_with_meta(
        tmp_path / "src.pdf",
        **{"/Title": "T", "/Author": "A", "/Subject": "S"},
    )
    out = tmp_path / "out.pdf"

    write_metadata(src, out, {}, clear_existing=True)

    meta = read_metadata(out)
    assert meta.get("/Title") is None
    assert meta.get("/Author") is None


def test_write_metadata_empty_value_removes_key(tmp_path):
    src = make_pdf_with_meta(tmp_path / "src.pdf", **{"/Title": "Remove me"})
    out = tmp_path / "out.pdf"

    write_metadata(src, out, {"/Title": ""})

    meta = read_metadata(out)
    assert "/Title" not in meta


def test_write_metadata_does_not_modify_original(tmp_path):
    src = make_pdf_with_meta(tmp_path / "src.pdf", **{"/Title": "Original"})
    original_bytes = src.read_bytes()
    out = tmp_path / "out.pdf"

    write_metadata(src, out, {"/Title": "Changed"})

    assert src.read_bytes() == original_bytes


def test_read_metadata_missing_file_raises(tmp_path):
    with pytest.raises(PDFToolError):
        read_metadata(tmp_path / "missing.pdf")


def test_write_metadata_output_same_as_input_raises(tmp_path):
    src = make_pdf(tmp_path / "src.pdf")
    with pytest.raises(PDFToolError):
        write_metadata(src, src, {})
