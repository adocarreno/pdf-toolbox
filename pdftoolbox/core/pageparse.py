"""Parse human-readable page range strings into validated zero-based page index lists."""

from __future__ import annotations

from .exceptions import PageRangeError


def parse_page_range(spec: str, total_pages: int) -> list[int]:
    """
    Parse a page range string like "1-3, 5, 8-10" into a list of zero-based page indices.

    Pages are 1-based in the spec; the returned list is 0-based.
    Raises PageRangeError if the spec is syntactically invalid or any page is out of bounds.
    """
    if total_pages < 1:
        raise PageRangeError("Document has no pages.")

    indices: list[int] = []
    parts = spec.split(",")

    for raw_part in parts:
        part = raw_part.strip()
        if not part:
            continue

        if "-" in part:
            dash_count = part.count("-")
            # Allow exactly one dash for a range; negative numbers are not valid page numbers
            if dash_count != 1:
                raise PageRangeError(
                    f"Invalid range segment '{part}': expected format 'start-end'."
                )
            start_str, end_str = part.split("-", 1)
            start_str, end_str = start_str.strip(), end_str.strip()
            if not start_str.isdigit() or not end_str.isdigit():
                raise PageRangeError(
                    f"Invalid range segment '{part}': page numbers must be positive integers."
                )
            start, end = int(start_str), int(end_str)
            if start < 1 or end < 1:
                raise PageRangeError(
                    f"Invalid range '{part}': page numbers must be >= 1."
                )
            if start > end:
                raise PageRangeError(
                    f"Invalid range '{part}': start page must be <= end page."
                )
            if end > total_pages:
                raise PageRangeError(
                    f"Page {end} is out of range; document has {total_pages} page(s)."
                )
            indices.extend(range(start - 1, end))
        else:
            if not part.isdigit():
                raise PageRangeError(
                    f"Invalid page number '{part}': must be a positive integer."
                )
            page = int(part)
            if page < 1:
                raise PageRangeError(f"Invalid page number {page}: must be >= 1.")
            if page > total_pages:
                raise PageRangeError(
                    f"Page {page} is out of range; document has {total_pages} page(s)."
                )
            indices.append(page - 1)

    if not indices:
        raise PageRangeError("Page range is empty.")

    return indices
