"""Tests for core merge functionality."""

import pytest
from pathlib import Path

from pypdf import PdfReader

from pdftoolbox.core.exceptions import PDFToolError
from pdftoolbox.core.merge import merge_pdfs
from .helpers import make_pdf


def test_merge_two_pdfs(tmp_path):
    a = make_pdf(tmp_path / "a.pdf", num_pages=2)
    b = make_pdf(tmp_path / "b.pdf", num_pages=3)
    out = tmp_path / "merged.pdf"

    total = merge_pdfs([a, b], out)

    assert total == 5
    assert out.exists()
    reader = PdfReader(str(out))
    assert len(reader.pages) == 5


def test_merge_preserves_order(tmp_path):
    a = make_pdf(tmp_path / "a.pdf", num_pages=1)
    b = make_pdf(tmp_path / "b.pdf", num_pages=1)
    c = make_pdf(tmp_path / "c.pdf", num_pages=1)
    out = tmp_path / "merged.pdf"

    merge_pdfs([a, b, c], out)
    reader = PdfReader(str(out))
    assert len(reader.pages) == 3


def test_merge_single_file(tmp_path):
    a = make_pdf(tmp_path / "a.pdf", num_pages=4)
    out = tmp_path / "merged.pdf"

    total = merge_pdfs([a], out)
    assert total == 4


def test_merge_no_inputs_raises(tmp_path):
    with pytest.raises(PDFToolError):
        merge_pdfs([], tmp_path / "out.pdf")


def test_merge_missing_file_raises(tmp_path):
    with pytest.raises(PDFToolError):
        merge_pdfs([tmp_path / "missing.pdf"], tmp_path / "out.pdf")


def test_merge_output_differs_from_input(tmp_path):
    a = make_pdf(tmp_path / "a.pdf", num_pages=2)
    with pytest.raises(PDFToolError):
        merge_pdfs([a], a)
