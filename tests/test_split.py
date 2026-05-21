"""Tests for core split functionality."""

import pytest
from pypdf import PdfReader

from pdftoolbox.core.exceptions import PageRangeError, PDFToolError
from pdftoolbox.core.split import get_page_count, split_pdf
from .helpers import make_pdf


def test_split_contiguous_range(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=5)
    out = tmp_path / "out.pdf"

    count = split_pdf(src, "1-3", out)

    assert count == 3
    reader = PdfReader(str(out))
    assert len(reader.pages) == 3


def test_split_mixed_spec(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=10)
    out = tmp_path / "out.pdf"

    count = split_pdf(src, "1-3, 5, 8-10", out)

    assert count == 7
    reader = PdfReader(str(out))
    assert len(reader.pages) == 7


def test_split_single_page(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=5)
    out = tmp_path / "out.pdf"

    count = split_pdf(src, "3", out)

    assert count == 1


def test_split_invalid_range_raises(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=5)
    out = tmp_path / "out.pdf"

    with pytest.raises(PageRangeError):
        split_pdf(src, "4-10", out)


def test_split_missing_file_raises(tmp_path):
    with pytest.raises(PDFToolError):
        split_pdf(tmp_path / "missing.pdf", "1", tmp_path / "out.pdf")


def test_split_output_same_as_input_raises(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=3)
    with pytest.raises(PDFToolError):
        split_pdf(src, "1", src)


def test_get_page_count(tmp_path):
    src = make_pdf(tmp_path / "src.pdf", num_pages=7)
    assert get_page_count(src) == 7
