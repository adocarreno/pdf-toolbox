"""Typed exceptions for PDF Tool Box core operations."""


class PDFToolError(Exception):
    """Base exception for all PDF Tool Box errors."""


class NotAPDFError(PDFToolError):
    """Raised when a file is not a valid PDF (wrong format or unreadable structure)."""


class InvalidPasswordError(PDFToolError):
    """Raised when a supplied password is incorrect."""


class EncryptedPDFError(PDFToolError):
    """Raised when an operation requires an unencrypted PDF but finds an encrypted one."""


class NotEncryptedError(PDFToolError):
    """Raised when an operation requires an encrypted PDF but finds an unencrypted one."""


class PageRangeError(PDFToolError):
    """Raised when a page range specification is invalid or out of bounds."""


class EmptyPDFError(PDFToolError):
    """Raised when a PDF contains zero pages."""
