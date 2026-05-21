"""Shared GUI helpers for tool panels."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget,
)


def pick_open_file(
    parent: QWidget,
    caption: str = "Open PDF",
    filter: str = "PDF Files (*.pdf)",
) -> str | None:
    path, _ = QFileDialog.getOpenFileName(parent, caption, "", filter)
    return path or None


def pick_open_files(
    parent: QWidget,
    caption: str = "Open PDF Files",
    filter: str = "PDF Files (*.pdf)",
) -> list[str]:
    paths, _ = QFileDialog.getOpenFileNames(parent, caption, "", filter)
    return paths


def pick_save_file(
    parent: QWidget,
    caption: str = "Save PDF As",
    filter: str = "PDF Files (*.pdf)",
) -> str | None:
    path, _ = QFileDialog.getSaveFileName(parent, caption, "", filter)
    return path or None


def make_file_row(
    parent: QWidget,
    label_text: str,
    button_text: str = "Browse…",
) -> tuple[QWidget, QLineEdit, QPushButton]:
    """Return a (row_widget, line_edit, button) for a single-file input row."""
    row = QWidget(parent)
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)

    lbl = QLabel(label_text, row)
    lbl.setFixedWidth(90)
    layout.addWidget(lbl)

    edit = QLineEdit(row)
    edit.setPlaceholderText("No file selected")
    edit.setReadOnly(True)
    layout.addWidget(edit)

    btn = QPushButton(button_text, row)
    btn.setFixedWidth(90)
    layout.addWidget(btn)

    return row, edit, btn


def make_status_label(parent: QWidget) -> QLabel:
    lbl = QLabel("", parent)
    lbl.setWordWrap(True)
    lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return lbl


def set_status(label: QLabel, message: str, is_error: bool = False) -> None:
    color = "#cc0000" if is_error else "#006600"
    label.setText(message)
    label.setStyleSheet(f"color: {color};")
