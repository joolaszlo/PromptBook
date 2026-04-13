# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from collections.abc import Callable
from pathlib import Path
from typing import override

from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class FilenameConflictDialog(QDialog):
    def __init__(self, existing_path: Path, suggested_name: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Filename Conflict")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumWidth(420)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(12, 12, 12, 12)
        self.root_layout.setSpacing(8)

        title = QLabel("A file with this name already exists in the current library directory.")
        title.setWordWrap(True)
        self.root_layout.addWidget(title)

        self.existing_path_label = QLabel(str(existing_path))
        self.existing_path_label.setWordWrap(True)
        self.existing_path_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.root_layout.addWidget(self.existing_path_label)

        self.filename_label = QLabel("Rename file")
        self.root_layout.addWidget(self.filename_label)

        self.filename_field = QLineEdit(suggested_name)
        self.filename_field.selectAll()
        self.root_layout.addWidget(self.filename_field)

        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #e22c3c;")
        self.error_label.hide()
        self.root_layout.addWidget(self.error_label)

        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.addStretch(1)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

        self.rename_button = QPushButton("Rename")
        self.rename_button.setDefault(True)
        self.rename_button.clicked.connect(self._confirm_rename)
        self.button_layout.addWidget(self.rename_button)

        self.root_layout.addWidget(self.button_container)

    @property
    def filename(self) -> str:
        return self.filename_field.text().strip()

    def _confirm_rename(self) -> None:
        filename = self.filename
        if not filename:
            self._set_error("Filename is required.")
            return

        path = Path(filename)
        if path.name != filename or filename in {".", ".."}:
            self._set_error("Enter a filename only, not a path.")
            return

        self._set_error("")
        self.accept()

    def _set_error(self, text: str) -> None:
        self.error_label.setText(text)
        self.error_label.setVisible(bool(text))

    @override
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:  # noqa N802
        if event.key() in (QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return):
            self._confirm_rename()
            return
        super().keyPressEvent(event)


class AddEntryModal(QWidget):
    def __init__(
        self,
        submit_callback: Callable[[Path, str], bool],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._submit_callback = submit_callback
        self._selected_file: Path | None = None

        self.setWindowTitle("Add New Entry")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumSize(520, 360)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(12, 12, 12, 12)
        self.root_layout.setSpacing(10)

        self.media_title = QLabel("Add Media")
        self.media_title.setStyleSheet("font-weight:bold;font-size:14px;")
        self.root_layout.addWidget(self.media_title)

        self.media_row = QWidget()
        self.media_layout = QHBoxLayout(self.media_row)
        self.media_layout.setContentsMargins(0, 0, 0, 0)
        self.media_layout.setSpacing(8)

        self.file_field = QLineEdit()
        self.file_field.setReadOnly(True)
        self.media_layout.addWidget(self.file_field)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._browse_for_media)
        self.media_layout.addWidget(self.browse_button)

        self.root_layout.addWidget(self.media_row)

        self.prompt_title = QLabel("Prompt")
        self.prompt_title.setStyleSheet("font-weight:bold;font-size:14px;")
        self.root_layout.addWidget(self.prompt_title)

        self.prompt_field = QPlainTextEdit()
        self.prompt_field.setPlaceholderText("Enter prompt text")
        self.root_layout.addWidget(self.prompt_field)

        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #e22c3c;")
        self.error_label.hide()
        self.root_layout.addWidget(self.error_label)

        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self.button_container)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.addStretch(1)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._cancel)
        self.button_layout.addWidget(self.cancel_button)

        self.add_entry_button = QPushButton("Add Entry")
        self.add_entry_button.setDefault(True)
        self.add_entry_button.clicked.connect(self._submit)
        self.button_layout.addWidget(self.add_entry_button)

        self.root_layout.addWidget(self.button_container)

    def _browse_for_media(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Select Media")
        if not filename:
            return

        self._selected_file = Path(filename)
        self.file_field.setText(str(self._selected_file))
        self._set_error("")

    def _submit(self) -> None:
        if self._selected_file is None:
            self._set_error("Select a file to add.")
            return

        if not self._selected_file.exists():
            self._set_error("The selected file could not be found.")
            return

        self._set_error("")
        if self._submit_callback(self._selected_file, self.prompt_field.toPlainText()):
            self.hide()
            self.reset()

    def _cancel(self) -> None:
        self.hide()
        self.reset()

    def reset(self) -> None:
        self._selected_file = None
        self.file_field.clear()
        self.prompt_field.clear()
        self._set_error("")

    def _set_error(self, text: str) -> None:
        self.error_label.setText(text)
        self.error_label.setVisible(bool(text))

    @override
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:  # noqa N802
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self._cancel()
            return
        super().keyPressEvent(event)

    @override
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.reset()
        event.accept()
