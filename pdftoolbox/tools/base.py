"""PDFTool abstract base class and tool registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

_REGISTRY: list[type["PDFTool"]] = []


def register(cls: type["PDFTool"]) -> type["PDFTool"]:
    """Class decorator that adds a PDFTool subclass to the registry."""
    _REGISTRY.append(cls)
    return cls


def get_tools() -> list[type["PDFTool"]]:
    """Return all registered PDFTool classes in registration order."""
    return list(_REGISTRY)


class PDFTool(ABC):
    """Abstract base class for all PDF Tool Box tool panels."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short display name shown in the sidebar."""

    @property
    @abstractmethod
    def description(self) -> str:
        """One-line description shown as a tooltip or subtitle."""

    @abstractmethod
    def build_widget(self, parent: "QWidget | None" = None) -> "QWidget":
        """Build and return the tool's QWidget panel."""
