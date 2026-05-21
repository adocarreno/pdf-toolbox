"""CLI entry point: python -m pdftoolbox.cli <subcommand> ..."""

from __future__ import annotations

import argparse
import getpass
import sys

from pdftoolbox.core.encrypt import encrypt_pdf
from pdftoolbox.core.exceptions import PDFToolError
from pdftoolbox.core.merge import merge_pdfs
from pdftoolbox.core.metadata import write_metadata
from pdftoolbox.core.split import split_pdf


def cmd_merge(args: argparse.Namespace) -> None:
    try:
        total = merge_pdfs(args.inputs, args.output)
        print(f"Merged {total} pages → {args.output}")
    except PDFToolError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_split(args: argparse.Namespace) -> None:
    try:
        count = split_pdf(args.input, args.pages, args.output)
        print(f"Extracted {count} page(s) → {args.output}")
    except PDFToolError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_encrypt(args: argparse.Namespace) -> None:
    try:
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Error: passwords do not match.", file=sys.stderr)
            sys.exit(1)
        algo = encrypt_pdf(args.input, password, args.output)
        print(f"Encrypted with {algo} → {args.output}")
    except PDFToolError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def cmd_metadata(args: argparse.Namespace) -> None:
    updates: dict[str, str] = {}
    if args.title is not None:
        updates["/Title"] = args.title
    if args.author is not None:
        updates["/Author"] = args.author
    if args.subject is not None:
        updates["/Subject"] = args.subject
    if args.keywords is not None:
        updates["/Keywords"] = args.keywords
    try:
        write_metadata(args.input, args.output, updates, clear_existing=args.clear)
        action = "cleared and updated" if args.clear else "updated"
        print(f"Metadata {action} → {args.output}")
    except PDFToolError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m pdftoolbox.cli",
        description="PDF Tool Box — command-line interface",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── merge ────────────────────────────────────────────────────────────────
    p_merge = sub.add_parser("merge", help="Merge multiple PDFs into one.")
    p_merge.add_argument("inputs", nargs="+", metavar="INPUT", help="Input PDF files")
    p_merge.add_argument("-o", "--output", required=True, metavar="OUTPUT", help="Output PDF path")
    p_merge.set_defaults(func=cmd_merge)

    # ── split ────────────────────────────────────────────────────────────────
    p_split = sub.add_parser("split", help="Extract selected pages from a PDF.")
    p_split.add_argument("input", metavar="INPUT", help="Input PDF file")
    p_split.add_argument("--pages", required=True, metavar="SPEC", help='Page range, e.g. "1-3,5,8-10"')
    p_split.add_argument("-o", "--output", required=True, metavar="OUTPUT", help="Output PDF path")
    p_split.set_defaults(func=cmd_split)

    # ── encrypt ──────────────────────────────────────────────────────────────
    p_enc = sub.add_parser("encrypt", help="Encrypt a PDF (password prompted interactively).")
    p_enc.add_argument("input", metavar="INPUT", help="Input PDF file")
    p_enc.add_argument("-o", "--output", required=True, metavar="OUTPUT", help="Output encrypted PDF path")
    p_enc.set_defaults(func=cmd_encrypt)

    # ── metadata ─────────────────────────────────────────────────────────────
    p_meta = sub.add_parser("metadata", help="Read or update PDF metadata.")
    p_meta.add_argument("input", metavar="INPUT", help="Input PDF file")
    p_meta.add_argument("-o", "--output", required=True, metavar="OUTPUT", help="Output PDF path")
    p_meta.add_argument("--clear", action="store_true", help="Clear all existing metadata before applying updates")
    p_meta.add_argument("--title", metavar="TEXT")
    p_meta.add_argument("--author", metavar="TEXT")
    p_meta.add_argument("--subject", metavar="TEXT")
    p_meta.add_argument("--keywords", metavar="TEXT")
    p_meta.set_defaults(func=cmd_metadata)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
