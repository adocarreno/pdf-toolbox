"""PDF Metadata Editor tool panel."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from pdftoolbox.core.exceptions import PDFToolError
from pdftoolbox.core.metadata import STANDARD_KEYS, read_metadata, write_metadata
from pdftoolbox.core.validation import validate_pdf

from .base import PDFTool, register
from .widget_helpers import make_file_row, pick_open_file, pick_save_file, set_status


@register
class MetadataTool(PDFTool):
    name = "Meta Editor"
    description = "Read and edit PDF document metadata (title, author, etc.)."

    # Human-readable labels for the standard keys
    _LABELS: dict[str, str] = {
        "/Title": "Title",
        "/Author": "Author",
        "/Subject": "Subject",
        "/Keywords": "Keywords",
        "/Creator": "Creator",
        "/Producer": "Producer",
        "/CreationDate": "Creation Date",
        "/ModDate": "Modification Date",
    }

    def build_widget(self, parent: QWidget | None = None) -> QWidget:
        w = QWidget(parent)
        root = QVBoxLayout(w)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        in_row, self._in_edit, in_btn = make_file_row(w, "Input PDF:")
        root.addWidget(in_row)
        in_btn.clicked.connect(self._pick_input)

        load_btn = QPushButton("Load Metadata")
        load_btn.clicked.connect(self._load_metadata)
        root.addWidget(load_btn)

        # ── Scrollable form for metadata fields ──────────────────────────────
        scroll = QScrollArea(w)
        scroll.setWidgetResizable(True)
        form_container = QWidget()
        self._form = QFormLayout(form_container)
        scroll.setWidget(form_container)
        scroll.setMinimumHeight(200)
        root.addWidget(scroll)

        self._field_edits: dict[str, QLineEdit] = {}
        for key in STANDARD_KEYS:
            edit = QLineEdit()
            edit.setPlaceholderText("(empty)")
            self._field_edits[key] = edit
            self._form.addRow(self._LABELS.get(key, key), edit)

        # ── Clear all button ─────────────────────────────────────────────────
        clear_btn = QPushButton("Clear All Metadata")
        clear_btn.clicked.connect(self._clear_fields)
        root.addWidget(clear_btn)

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

        exec_btn = QPushButton("Save Metadata")
        exec_btn.setFixedHeight(32)
        exec_btn.clicked.connect(self._execute)
        root.addWidget(exec_btn)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        root.addWidget(self._status)

        self._input_path: str | None = None
        self._output_path: str | None = None
        self._clear_flag = False

        return w

    def _pick_input(self) -> None:
        path = pick_open_file(self._in_edit)
        if not path:
            return
        try:
            is_encrypted, page_count = validate_pdf(path)
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
                f"'{path.split('/')[-1]}' is encrypted; decrypt it before editing metadata.",
                is_error=True,
            )
            return
        self._input_path = path
        self._in_edit.setText(path)
        set_status(self._status, f"PDF ready ({page_count} page(s)). Click 'Load Metadata'.")

    def _load_metadata(self) -> None:
        if not self._input_path:
            set_status(self._status, "Select an input PDF first.", is_error=True)
            return
        try:
            meta = read_metadata(self._input_path)
        except PDFToolError as exc:
            set_status(self._status, str(exc), is_error=True)
            return

        for key, edit in self._field_edits.items():
            edit.setText(meta.get(key, ""))

        self._clear_flag = False
        set_status(self._status, "Metadata loaded. Edit fields, then save.")

    def _clear_fields(self) -> None:
        for edit in self._field_edits.values():
            edit.clear()
        self._clear_flag = True
        set_status(self._status, "All fields cleared. Save to apply.")

    def _choose_output(self) -> None:
        path = pick_save_file(self._out_label)
        if path:
            self._output_path = path
            self._out_label.setText(path)

    def _execute(self) -> None:
        if not self._input_path:
            set_status(self._status, "Select an input PDF first.", is_error=True)
            return
        if not self._output_path:
            set_status(self._status, "Choose an output file first.", is_error=True)
            return
        updates = {key: edit.text() for key, edit in self._field_edits.items()}
        try:
            write_metadata(
                self._input_path,
                self._output_path,
                updates,
                clear_existing=self._clear_flag,
            )
            set_status(self._status, f"Done — metadata saved to: {self._output_path}")
        except PDFToolError as exc:
            set_status(self._status, str(exc), is_error=True)
