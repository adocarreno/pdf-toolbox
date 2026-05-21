"""PDF Merger tool panel."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pdftoolbox.core.exceptions import PDFToolError
from pdftoolbox.core.merge import merge_pdfs
from pdftoolbox.core.validation import validate_pdf

from .base import PDFTool, register
from .widget_helpers import pick_open_files, pick_save_file, set_status


@register
class MergerTool(PDFTool):
    name = "PDF Merger"
    description = "Combine multiple PDF files into one, in any order."

    def build_widget(self, parent: QWidget | None = None) -> QWidget:
        w = QWidget(parent)
        root = QVBoxLayout(w)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── File list ────────────────────────────────────────────────────────
        root.addWidget(QLabel("<b>Input PDF files</b> (drag to reorder):"))

        self._list = QListWidget(w)
        self._list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.setMinimumHeight(140)
        root.addWidget(self._list)

        # ── List-management buttons ──────────────────────────────────────────
        btn_row = QWidget(w)
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        add_btn = QPushButton("Add Files…")
        remove_btn = QPushButton("Remove Selected")
        up_btn = QPushButton("Move Up")
        down_btn = QPushButton("Move Down")

        for b in (add_btn, remove_btn, up_btn, down_btn):
            btn_layout.addWidget(b)
        btn_layout.addStretch()
        root.addWidget(btn_row)

        # ── Output path ──────────────────────────────────────────────────────
        out_row = QWidget(w)
        out_layout = QHBoxLayout(out_row)
        out_layout.setContentsMargins(0, 0, 0, 0)
        out_layout.addWidget(QLabel("Output file:"))
        self._out_label = QLabel("<i>not set</i>")
        self._out_label.setWordWrap(True)
        out_layout.addWidget(self._out_label, 1)
        out_btn = QPushButton("Choose…")
        out_layout.addWidget(out_btn)
        root.addWidget(out_row)

        # ── Execute + status ─────────────────────────────────────────────────
        exec_btn = QPushButton("Merge PDFs")
        exec_btn.setFixedHeight(32)
        root.addWidget(exec_btn)

        self._status = QLabel("")
        self._status.setWordWrap(True)
        root.addWidget(self._status)

        # ── State ────────────────────────────────────────────────────────────
        self._output_path: str | None = None

        # ── Connections ──────────────────────────────────────────────────────
        add_btn.clicked.connect(self._add_files)
        remove_btn.clicked.connect(self._remove_selected)
        up_btn.clicked.connect(self._move_up)
        down_btn.clicked.connect(self._move_down)
        out_btn.clicked.connect(self._choose_output)
        exec_btn.clicked.connect(self._execute)

        return w

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _add_files(self) -> None:
        paths = pick_open_files(self._list)
        rejected: list[str] = []
        for p in paths:
            try:
                is_encrypted, page_count = validate_pdf(p)
            except PDFToolError as exc:
                rejected.append(f"{p.split('/')[-1]}: {exc}")
                continue
            if is_encrypted:
                rejected.append(f"{p.split('/')[-1]}: encrypted — decrypt first")
                continue
            item = QListWidgetItem(f"{p.split('/')[-1]}  ({page_count} p)")
            item.setData(Qt.ItemDataRole.UserRole, p)
            item.setToolTip(p)
            self._list.addItem(item)

        if rejected:
            set_status(
                self._status,
                "Skipped (invalid/encrypted): " + "; ".join(rejected),
                is_error=True,
            )
        elif paths:
            set_status(self._status, f"Added {len(paths)} file(s).")

    def _remove_selected(self) -> None:
        for item in self._list.selectedItems():
            self._list.takeItem(self._list.row(item))

    def _move_up(self) -> None:
        row = self._list.currentRow()
        if row > 0:
            item = self._list.takeItem(row)
            self._list.insertItem(row - 1, item)
            self._list.setCurrentRow(row - 1)

    def _move_down(self) -> None:
        row = self._list.currentRow()
        if row < self._list.count() - 1:
            item = self._list.takeItem(row)
            self._list.insertItem(row + 1, item)
            self._list.setCurrentRow(row + 1)

    def _choose_output(self) -> None:
        path = pick_save_file(self._list, "Save Merged PDF As")
        if path:
            self._output_path = path
            self._out_label.setText(path)

    def _execute(self) -> None:
        paths = [
            self._list.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self._list.count())
        ]
        if not paths:
            set_status(self._status, "Add at least one PDF file.", is_error=True)
            return
        if not self._output_path:
            set_status(self._status, "Choose an output file first.", is_error=True)
            return
        try:
            total = merge_pdfs(paths, self._output_path)
            set_status(self._status, f"Done — merged {total} pages into: {self._output_path}")
        except PDFToolError as exc:
            set_status(self._status, str(exc), is_error=True)
