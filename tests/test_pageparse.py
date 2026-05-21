"""Tests for pageparse.py — page range parsing."""

import pytest

from pdftoolbox.core.exceptions import PageRangeError
from pdftoolbox.core.pageparse import parse_page_range


class TestValidInputs:
    def test_single_page(self):
        assert parse_page_range("2", 5) == [1]

    def test_first_page(self):
        assert parse_page_range("1", 5) == [0]

    def test_last_page(self):
        assert parse_page_range("5", 5) == [4]

    def test_contiguous_range(self):
        assert parse_page_range("1-3", 5) == [0, 1, 2]

    def test_full_range(self):
        assert parse_page_range("1-5", 5) == [0, 1, 2, 3, 4]

    def test_mixed_spec(self):
        assert parse_page_range("1-3, 5, 8-10", 10) == [0, 1, 2, 4, 7, 8, 9]

    def test_spaces_around_commas(self):
        assert parse_page_range("1 , 3 , 5", 5) == [0, 2, 4]

    def test_single_page_range(self):
        # "2-2" is a degenerate but valid range
        assert parse_page_range("2-2", 5) == [1]

    def test_repeated_pages_allowed(self):
        # User may request the same page twice; we don't deduplicate
        result = parse_page_range("1, 1, 2", 5)
        assert result == [0, 0, 1]


class TestInvalidInputs:
    def test_page_zero(self):
        with pytest.raises(PageRangeError):
            parse_page_range("0", 5)

    def test_page_beyond_total(self):
        with pytest.raises(PageRangeError):
            parse_page_range("6", 5)

    def test_range_end_beyond_total(self):
        with pytest.raises(PageRangeError):
            parse_page_range("3-6", 5)

    def test_reversed_range(self):
        with pytest.raises(PageRangeError):
            parse_page_range("5-3", 5)

    def test_non_numeric(self):
        with pytest.raises(PageRangeError):
            parse_page_range("a-b", 5)

    def test_empty_spec(self):
        with pytest.raises(PageRangeError):
            parse_page_range("", 5)

    def test_only_commas(self):
        with pytest.raises(PageRangeError):
            parse_page_range(",,,", 5)

    def test_double_dash(self):
        with pytest.raises(PageRangeError):
            parse_page_range("1-2-3", 5)

    def test_zero_total_pages(self):
        with pytest.raises(PageRangeError):
            parse_page_range("1", 0)
