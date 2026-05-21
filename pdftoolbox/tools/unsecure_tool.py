"""Unsecure PDF (decrypt) tool panel."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pdftoolbox.core.decrypt import decrypt_pdf
from pdftoolbox.core.exceptions import PDFToolError
from pdftoolbox.core.validation import validate_pdf

from .base import PDFTool, register
from .widget_helpers import make_file_row, pick_open_file, pick_save_file, set_status


@register
class UnsecureTool(PDFTool):
    name = "Unsecure PDF"
    description = "Remove password protection from an encrypted PDF (requires the password)."

    def build_widget(self, parent: QWidget | None = None) -> QWidget:
        w = QWidget(parent)
        root = QVBoxLayout(w)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        root.addWidget(
            QLabel(
                "This tool removes encryption using the correct password.\n"
                "It will NOT attempt to guess or bypass the password."
            )
        )

        in_row, self._in_edit, in_btn = make_file_row(w, "Encrypted PDF:")
        root.addWidget(in_row)
        in_btn.clicked.connect(self._pick_input)

        pw_row = QWidget(w)
        pw_layout = QHBoxLayout(pw_row)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.addWidget(QLabel("Password:"))
        self._pw_edit = QLineEdit()
        self._pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_edit.setPlaceholderText("Enter current password")
        pw_layout.addWidget(self._pw_edit)
        root.addWidget(pw_row)

        out_row = QWidget(w)
        out_layout = QHBoxLayout(out_row)
        out_layout.setContentsMargins(0, 0, 0, 0)
        out_layout.addWidget(QLabel("Output file:"))
        self._out_label = QLabel("<i>not set</i>")
        self._out_label.setWordWrap(True)
        out_layout.addWidget(self._out_label, 1)
        out_btn = QPushButton("Choose…")
        out_btn.clicked.connect(self._choose_output)
        out_layout.addWidget(out_btn)
        root.addWidget(out_row)

        exec_btn = QPushButton("Decrypt PDF")
        exec_btn.setFixedHeight(32)
        exec_btn.clicked.connect(self._execute)
        root.addWidget(exec_btn)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        root.addWidget(self._status)

        self._input_path: str | None = None
        self._output_path: str | None = None

        return w

    def _pick_input(self) -> None:
        path = pick_open_file(self._in_edit)
        if not path:
            return
        try:
            is_encrypted, _ = validate_pdf(path)
        except PDFToolError as exc:
            self._input_path = None
            self._in_edit.clear()
            set_status(self._status, str(exc), is_error=True)
            return
        if not is_encrypted:
            self._input_path = None
            self._in_edit.clear()
            set_status(
                self._status,
                f"'{path.split('/')[-1]}' is not encrypted — nothing to decrypt.",
                is_error=True,
            )
            return
        self._input_path = path
        self._in_edit.setText(path)
        set_status(self._status, "Encrypted PDF selected. Enter the password and choose an output file.")

    def _choose_output(self) -> None:
        path = pick_save_file(self._out_label)
        if path:
            self._output_path = path
            self._out_label.setText(path)

    def _execute(self) -> None:
        if not self._input_path:
            set_status(self._status, "Select an encrypted PDF first.", is_error=True)
            return
        pw = self._pw_edit.text()
        if not pw:
            set_status(self._status, "Enter the PDF password.", is_error=True)
            return
        if not self._output_path:
            set_status(self._status, "Choose an output file first.", is_error=True)
            return
        try:
            decrypt_pdf(self._input_path, pw, self._output_path)
            set_status(self._status, f"Done — decrypted PDF saved to: {self._output_path}")
            self._pw_edit.clear()
        except PDFToolError as exc:
            set_status(self._status, str(exc), is_error=True)
