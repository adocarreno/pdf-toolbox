"""PDF Splitter tool panel."""

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

from pdftoolbox.core.exceptions import PDFToolError
from pdftoolbox.core.split import get_page_count, split_pdf

from .base import PDFTool, register
from .widget_helpers import (
    make_file_row,
    pick_open_file,
    pick_save_file,
    set_status,
)


@register
class SplitterTool(PDFTool):
    name = "PDF Splitter"
    description = "Extract selected pages from a PDF into a new file."

    def build_widget(self, parent: QWidget | None = None) -> QWidget:
        w = QWidget(parent)
        root = QVBoxLayout(w)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Input file ───────────────────────────────────────────────────────
        in_row, self._in_edit, in_btn = make_file_row(w, "Input PDF:")
        root.addWidget(in_row)
        in_btn.clicked.connect(self._pick_input)

        self._page_count_label = QLabel("")
        root.addWidget(self._page_count_label)

        # ── Page range ───────────────────────────────────────────────────────
        spec_row = QWidget(w)
        spec_layout = QHBoxLayout(spec_row)
        spec_layout.setContentsMargins(0, 0, 0, 0)
        spec_layout.addWidget(QLabel("Pages:"))
        self._spec_edit = QLineEdit()
        self._spec_edit.setPlaceholderText('e.g. "1-3, 5, 8-10"')
        spec_layout.addWidget(self._spec_edit)
        root.addWidget(spec_row)

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

        # ── Execute + status ─────────────────────────────────────────────────
        exec_btn = QPushButton("Extract Pages")
        exec_btn.setFixedHeight(32)
        exec_btn.clicked.connect(self._execute)
        root.addWidget(exec_btn)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        root.addWidget(self._status)

        self._input_path: str | None = None
        self._output_path: str | None = None

        return w

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _pick_input(self) -> None:
        path = pick_open_file(self._in_edit)
        if path:
            self._input_path = path
            self._in_edit.setText(path)
            try:
                count = get_page_count(path)
                self._page_count_label.setText(f"Pages in document: {count}")
            except PDFToolError as exc:
                self._page_count_label.setText("")
                set_status(self._status, str(exc), is_error=True)

    def _choose_output(self) -> None:
        path = pick_save_file(self._out_label)
        if path:
            self._output_path = path
            self._out_label.setText(path)

    def _execute(self) -> None:
        if not self._input_path:
            set_status(self._status, "Select an input PDF first.", is_error=True)
            return
        spec = self._spec_edit.text().strip()
        if not spec:
            set_status(self._status, "Enter a page range.", is_error=True)
            return
        if not self._output_path:
            set_status(self._status, "Choose an output file first.", is_error=True)
            return
        try:
            count = split_pdf(self._input_path, spec, self._output_path)
            set_status(self._status, f"Done — wrote {count} page(s) to: {self._output_path}")
        except PDFToolError as exc:
            set_status(self._status, str(exc), is_error=True)
