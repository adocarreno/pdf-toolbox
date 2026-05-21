"""Main application window — shell that reads the tool registry."""

from __future__ import annotations

# Import tool modules to trigger their @register decorators
import pdftoolbox.tools.merger_tool  # noqa: F401
import pdftoolbox.tools.splitter_tool  # noqa: F401
import pdftoolbox.tools.secure_tool  # noqa: F401
import pdftoolbox.tools.unsecure_tool  # noqa: F401
import pdftoolbox.tools.metadata_tool  # noqa: F401

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from pdftoolbox.tools.base import get_tools


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF Tool Box")
        self.resize(880, 600)
        self._build_ui()

    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.setCentralWidget(splitter)

        # ── Left sidebar ─────────────────────────────────────────────────────
        sidebar = QListWidget()
        sidebar.setFixedWidth(160)
        sidebar.setSpacing(4)
        splitter.addWidget(sidebar)

        # ── Right panel (stacked) ────────────────────────────────────────────
        self._stack = QStackedWidget()
        splitter.addWidget(self._stack)
        splitter.setStretchFactor(1, 1)

        # ── Populate from registry ───────────────────────────────────────────
        self._tool_instances = []
        for tool_cls in get_tools():
            tool = tool_cls()
            self._tool_instances.append(tool)

            item = QListWidgetItem(tool.name)
            item.setToolTip(tool.description)
            sidebar.addItem(item)

            panel_container = QWidget()
            layout = QHBoxLayout(panel_container)
            layout.setContentsMargins(12, 12, 12, 12)

            inner = QWidget()
            inner_layout = QVBoxLayout(inner)
            inner_layout.setContentsMargins(0, 0, 0, 0)

            title = QLabel(f"<h2>{tool.name}</h2>")
            desc = QLabel(f"<i>{tool.description}</i>")
            desc.setWordWrap(True)
            inner_layout.addWidget(title)
            inner_layout.addWidget(desc)
            inner_layout.addSpacing(8)

            tool_widget = tool.build_widget(inner)
            inner_layout.addWidget(tool_widget)
            inner_layout.addStretch()

            layout.addWidget(inner)
            self._stack.addWidget(panel_container)

        sidebar.currentRowChanged.connect(self._stack.setCurrentIndex)

        if sidebar.count():
            sidebar.setCurrentRow(0)
