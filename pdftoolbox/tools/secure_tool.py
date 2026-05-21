"""Secure PDF (encrypt) tool panel."""

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

from pdftoolbox.core.encrypt import encrypt_pdf
from pdftoolbox.core.exceptions import PDFToolError
from pdftoolbox.core.validation import validate_pdf

from .base import PDFTool, register
from .widget_helpers import make_file_row, pick_open_file, pick_save_file, set_status


@register
class SecureTool(PDFTool):
    name = "Secure PDF"
    description = "Encrypt a PDF with a password (AES-256)."

    def build_widget(self, parent: QWidget | None = None) -> QWidget:
        w = QWidget(parent)
        root = QVBoxLayout(w)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        in_row, self._in_edit, in_btn = make_file_row(w, "Input PDF:")
        root.addWidget(in_row)
        in_btn.clicked.connect(self._pick_input)

        # ── Password fields ──────────────────────────────────────────────────
        pw_row = QWidget(w)
        pw_layout = QHBoxLayout(pw_row)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.addWidget(QLabel("Password:"))
        self._pw_edit = QLineEdit()
        self._pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._pw_edit.setPlaceholderText("Enter password")
        pw_layout.addWidget(self._pw_edit)
        root.addWidget(pw_row)

        confirm_row = QWidget(w)
        confirm_layout = QHBoxLayout(confirm_row)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        confirm_layout.addWidget(QLabel("Confirm:"))
        self._confirm_edit = QLineEdit()
        self._confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_edit.setPlaceholderText("Re-enter password")
        confirm_layout.addWidget(self._confirm_edit)
        root.addWidget(confirm_row)

        # ── Output file ──────────────────────────────────────────────────────
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

        exec_btn = QPushButton("Encrypt PDF")
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
        if is_encrypted:
            self._input_path = None
            self._in_edit.clear()
            set_status(
                self._status,
                f"'{path.split('/')[-1]}' is already encrypted. Decrypt it first if you want to re-encrypt.",
                is_error=True,
            )
            return
        self._input_path = path
        self._in_edit.setText(path)
        set_status(self._status, "PDF ready. Enter a password and choose an output file.")

    def _choose_output(self) -> None:
        path = pick_save_file(self._out_label)
        if path:
            self._output_path = path
            self._out_label.setText(path)

    def _execute(self) -> None:
        if not self._input_path:
            set_status(self._status, "Select an input PDF first.", is_error=True)
            return
        pw = self._pw_edit.text()
        if not pw:
            set_status(self._status, "Enter a password.", is_error=True)
            return
        if pw != self._confirm_edit.text():
            set_status(self._status, "Passwords do not match.", is_error=True)
            return
        if not self._output_path:
            set_status(self._status, "Choose an output file first.", is_error=True)
            return
        try:
            algo = encrypt_pdf(self._input_path, pw, self._output_path)
            set_status(
                self._status,
                f"Done — encrypted with {algo}: {self._output_path}",
            )
            self._pw_edit.clear()
            self._confirm_edit.clear()
        except PDFToolError as exc:
            set_status(self._status, str(exc), is_error=True)
