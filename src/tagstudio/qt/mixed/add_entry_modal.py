# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING
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

from tagstudio.core.library.alchemy.models import Tag
from tagstudio.core.library.alchemy.fields import FieldID
from tagstudio.qt.mixed.tag_widget import TagWidget
from tagstudio.qt.views.layouts.flow_layout import FlowLayout, FlowWidget

if TYPE_CHECKING:
    from tagstudio.core.library.alchemy.library import Library
    from tagstudio.core.library.alchemy.models import Entry


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


class AddEntryModal(QDialog):
    def __init__(
        self,
        submit_callback: Callable[[Path | None, str, str, list[int]], bool],
        library: "Library",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._submit_callback = submit_callback
        self.lib = library
        self._selected_file: Path | None = None
        self._pinned_tags: list[Tag] = []
        self._selected_tag_ids: set[int] = set()
        self._tag_widgets: dict[int, TagWidget] = {}

        self.setWindowFlag(Qt.WindowType.Dialog, True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
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

        self.title_title = QLabel("Title")
        self.title_title.setStyleSheet("font-weight:bold;font-size:14px;")
        self.root_layout.addWidget(self.title_title)

        self.title_field = QLineEdit()
        self.title_field.setPlaceholderText("Enter title")
        self.root_layout.addWidget(self.title_field)

        self.prompt_title = QLabel("Prompt")
        self.prompt_title.setStyleSheet("font-weight:bold;font-size:14px;")
        self.root_layout.addWidget(self.prompt_title)

        self.prompt_field = QPlainTextEdit()
        self.prompt_field.setPlaceholderText("Enter prompt text")
        self.root_layout.addWidget(self.prompt_field)

        self.pinned_tags_title = QLabel("Pinned Tags")
        self.pinned_tags_title.setStyleSheet("font-weight:bold;font-size:14px;")
        self.root_layout.addWidget(self.pinned_tags_title)

        self.pinned_tags_container = FlowWidget()
        self.pinned_tags_layout = FlowLayout(self.pinned_tags_container)
        self.pinned_tags_layout.setContentsMargins(0, 0, 0, 0)
        self.pinned_tags_layout.setSpacing(6)
        self.pinned_tags_container.setLayout(self.pinned_tags_layout)
        self.root_layout.addWidget(self.pinned_tags_container)

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
        if self._selected_file is not None and not self._selected_file.exists():
            self._set_error("The selected file could not be found.")
            return

        title = self.title_field.text().strip()
        if self._selected_file is None and not title:
            self._set_error("Title is required when no media is selected.")
            return

        self._set_error("")
        if self._submit_callback(
            self._selected_file,
            title,
            self.prompt_field.toPlainText(),
            sorted(self._selected_tag_ids),
        ):
            self.hide()
            self.reset()

    def _cancel(self) -> None:
        self.hide()
        self.reset()

    def reset(self) -> None:
        self._selected_file = None
        self.file_field.clear()
        self.title_field.clear()
        self.prompt_field.clear()
        self._selected_tag_ids.clear()
        self._render_pinned_tags()
        self._set_error("")

    def set_pinned_tags(self, tags: list[Tag]) -> None:
        self._pinned_tags = tags
        self._render_pinned_tags()

    def _set_error(self, text: str) -> None:
        self.error_label.setText(text)
        self.error_label.setVisible(bool(text))

    def _render_pinned_tags(self) -> None:
        self._tag_widgets.clear()

        while self.pinned_tags_layout.count():
            item = self.pinned_tags_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        has_tags = bool(self._pinned_tags)
        self.pinned_tags_title.setVisible(has_tags)
        self.pinned_tags_container.setVisible(has_tags)
        if not has_tags:
            return

        for tag in self._pinned_tags:
            tag_widget = TagWidget(
                tag,
                has_edit=False,
                has_remove=False,
                library=self.lib,
                enable_context_menu=False,
            )
            tag_widget.search_for_tag_action.setVisible(False)
            tag_widget.pinned_action.setVisible(False)
            tag_widget.favorite_action.setVisible(False)
            tag_widget.on_click.connect(lambda t=tag: self._add_tag(t))
            self._tag_widgets[tag.id] = tag_widget
            self.pinned_tags_layout.addWidget(tag_widget)
            self._update_tag_widget_state(tag)

        self.pinned_tags_container.updateGeometry()

    def _add_tag(self, tag: Tag) -> None:
        self._selected_tag_ids.add(tag.id)
        self._update_tag_widget_state(tag)

    def _update_tag_widget_state(self, tag: Tag) -> None:
        tag_widget = self._tag_widgets.get(tag.id)
        if tag_widget is None:
            return

        tag_widget.set_tag(tag)
        if tag.id in self._selected_tag_ids:
            display_name = self.lib.tag_display_name(tag)
            tag_widget.bg_button.setText(f"Added: {display_name}")
            tag_widget.bg_button.setToolTip("Will be added to this entry")
        else:
            tag_widget.bg_button.setToolTip("")

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


class EditEntryModal(QDialog):
    def __init__(
        self,
        submit_callback: Callable[[int, Path | None, str, str], bool],
        library: "Library",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._submit_callback = submit_callback
        self.lib = library
        self._entry_id: int | None = None
        self._selected_file: Path | None = None

        self.setWindowFlag(Qt.WindowType.Dialog, True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setWindowTitle("Edit Entry")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setMinimumSize(520, 360)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(12, 12, 12, 12)
        self.root_layout.setSpacing(10)

        self.media_title = QLabel("Media")
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

        self.title_title = QLabel("Title")
        self.title_title.setStyleSheet("font-weight:bold;font-size:14px;")
        self.root_layout.addWidget(self.title_title)

        self.title_field = QLineEdit()
        self.title_field.setPlaceholderText("Enter title")
        self.root_layout.addWidget(self.title_field)

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
        self.cancel_button.clicked.connect(self.hide)
        self.button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("Save Entry")
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self._submit)
        self.button_layout.addWidget(self.save_button)
        self.root_layout.addWidget(self.button_container)

    def set_entry(self, entry: "Entry") -> None:
        self._entry_id = entry.id
        self._selected_file = None
        self.file_field.setText(str(entry.path or "No media"))
        self.title_field.setText(self.lib.get_entry_title(entry))
        self.prompt_field.setPlainText(self.lib.get_entry_field_value(entry, FieldID.DESCRIPTION))
        self._set_error("")

    def _submit(self) -> None:
        if self._entry_id is None:
            return
        entry = self.lib.get_entry(self._entry_id)
        title = self.title_field.text().strip()
        has_media_after_save = bool((entry and entry.has_media) or self._selected_file)
        if not has_media_after_save and not title:
            self._set_error("Title is required when no media is selected.")
            return
        self._set_error("")
        if self._submit_callback(
            self._entry_id, self._selected_file, title, self.prompt_field.toPlainText()
        ):
            self.hide()

    def _set_error(self, text: str) -> None:
        self.error_label.setText(text)
        self.error_label.setVisible(bool(text))

    def _browse_for_media(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(self, "Select Media")
        if not filename:
            return
        self._selected_file = Path(filename)
        self.file_field.setText(str(self._selected_file))
        self._set_error("")
