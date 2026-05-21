"""Tests for CLI argument parsing and end-to-end subcommand invocations."""

from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from pypdf import PdfReader

from pdftoolbox.cli import build_parser, cmd_merge, cmd_metadata, cmd_split
from .helpers import make_pdf


# ── Parser tests ────────────────────────────────────────────────────────────

class TestParser:
    def setup_method(self):
        self.parser = build_parser()

    def test_merge_parses_inputs_and_output(self):
        args = self.parser.parse_args(["merge", "a.pdf", "b.pdf", "-o", "out.pdf"])
        assert args.command == "merge"
        assert args.inputs == ["a.pdf", "b.pdf"]
        assert args.output == "out.pdf"

    def test_split_parses_pages_and_output(self):
        args = self.parser.parse_args(["split", "src.pdf", "--pages", "1-3", "-o", "out.pdf"])
        assert args.command == "split"
        assert args.input == "src.pdf"
        assert args.pages == "1-3"
        assert args.output == "out.pdf"

    def test_encrypt_parses_input_and_output(self):
        args = self.parser.parse_args(["encrypt", "src.pdf", "-o", "enc.pdf"])
        assert args.command == "encrypt"
        assert args.input == "src.pdf"
        assert args.output == "enc.pdf"

    def test_metadata_parses_clear_flag(self):
        args = self.parser.parse_args(["metadata", "src.pdf", "-o", "out.pdf", "--clear"])
        assert args.clear is True

    def test_metadata_parses_fields(self):
        args = self.parser.parse_args([
            "metadata", "src.pdf", "-o", "out.pdf",
            "--title", "My Title", "--author", "Jane",
        ])
        assert args.title == "My Title"
        assert args.author == "Jane"

    def test_no_subcommand_exits(self):
        with pytest.raises(SystemExit):
            self.parser.parse_args([])


# ── End-to-end subcommand tests ──────────────────────────────────────────────

class TestMergeCLI:
    def test_merge_produces_combined_pdf(self, tmp_path):
        a = make_pdf(tmp_path / "a.pdf", num_pages=2)
        b = make_pdf(tmp_path / "b.pdf", num_pages=3)
        out = tmp_path / "merged.pdf"

        parser = build_parser()
        args = parser.parse_args(["merge", str(a), str(b), "-o", str(out)])
        cmd_merge(args)

        assert out.exists()
        reader = PdfReader(str(out))
        assert len(reader.pages) == 5

    def test_merge_missing_file_exits(self, tmp_path):
        parser = build_parser()
        args = parser.parse_args([
            "merge", str(tmp_path / "missing.pdf"), "-o", str(tmp_path / "out.pdf")
        ])
        with pytest.raises(SystemExit) as exc_info:
            cmd_merge(args)
        assert exc_info.value.code == 1


class TestSplitCLI:
    def test_split_extracts_correct_pages(self, tmp_path):
        src = make_pdf(tmp_path / "src.pdf", num_pages=5)
        out = tmp_path / "out.pdf"

        parser = build_parser()
        args = parser.parse_args(["split", str(src), "--pages", "1-3", "-o", str(out)])
        cmd_split(args)

        reader = PdfReader(str(out))
        assert len(reader.pages) == 3

    def test_split_invalid_range_exits(self, tmp_path):
        src = make_pdf(tmp_path / "src.pdf", num_pages=5)
        parser = build_parser()
        args = parser.parse_args([
            "split", str(src), "--pages", "4-10", "-o", str(tmp_path / "out.pdf")
        ])
        with pytest.raises(SystemExit) as exc_info:
            cmd_split(args)
        assert exc_info.value.code == 1


class TestMetadataCLI:
    def test_metadata_sets_title(self, tmp_path):
        src = make_pdf(tmp_path / "src.pdf", num_pages=1)
        out = tmp_path / "out.pdf"

        parser = build_parser()
        args = parser.parse_args([
            "metadata", str(src), "-o", str(out), "--title", "CLI Title"
        ])
        cmd_metadata(args)

        from pdftoolbox.core.metadata import read_metadata
        meta = read_metadata(out)
        assert meta.get("/Title") == "CLI Title"

    def test_metadata_clear_removes_fields(self, tmp_path):
        from pypdf import PdfWriter
        src = tmp_path / "src.pdf"
        w = PdfWriter()
        w.add_blank_page(width=612, height=792)
        w.add_metadata({"/Title": "Remove me"})
        with open(src, "wb") as fh:
            w.write(fh)

        out = tmp_path / "out.pdf"
        parser = build_parser()
        args = parser.parse_args([
            "metadata", str(src), "-o", str(out), "--clear"
        ])
        cmd_metadata(args)

        from pdftoolbox.core.metadata import read_metadata
        meta = read_metadata(out)
        assert "/Title" not in meta
