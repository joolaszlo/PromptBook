# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from tagstudio.core.library.alchemy.enums import BrowsingState
from tagstudio.core.library.alchemy.fields import FieldID, TextField
from tagstudio.core.library.alchemy.models import Entry
from tagstudio.core.utils.types import unwrap
from tagstudio.qt.mixed.add_entry_modal import AddEntryModal
from tagstudio.qt.mixed.tag_widget import TagWidget
from tagstudio.qt.ts_qt import QtDriver


def test_browsing_state_update(qt_driver: QtDriver):
    # Given
    entries = qt_driver.lib.all_entries(with_joins=True)
    ids = [e.id for e in entries]
    qt_driver.frame_content = ids
    qt_driver.main_window.thumb_layout.set_entries(ids)

    # no filter, both items are returned
    qt_driver.update_browsing_state()
    assert len(qt_driver.frame_content) == 2

    # filter by tag
    state = BrowsingState.from_tag_name("foo")
    qt_driver.update_browsing_state(state)
    assert len(qt_driver.frame_content) == 1
    entry = unwrap(qt_driver.lib.get_entry_full(qt_driver.frame_content[0]))
    assert list(entry.tags)[0].name == "foo"

    # When state is not changed, previous one is still applied
    qt_driver.update_browsing_state()
    assert len(qt_driver.frame_content) == 1
    entry = unwrap(qt_driver.lib.get_entry_full(qt_driver.frame_content[0]))
    assert list(entry.tags)[0].name == "foo"

    # When state property is changed, previous one is overwritten
    state = BrowsingState.from_path("*bar.md")
    qt_driver.update_browsing_state(state)
    assert len(qt_driver.frame_content) == 1
    entry = unwrap(qt_driver.lib.get_entry_full(qt_driver.frame_content[0]))
    assert list(entry.tags)[0].name == "bar"


def test_close_library(qt_driver: QtDriver):
    # Given
    qt_driver.close_library()

    # Then
    assert qt_driver.lib.library_dir is None
    assert not qt_driver.frame_content
    assert not qt_driver.selected
    assert len(qt_driver.main_window.thumb_layout._entry_ids) == 0

    # close library again to see there's no error
    qt_driver.close_library()
    qt_driver.close_library(is_shutdown=True)


def test_browsing_state_update_multi_tag_and(qt_driver: QtDriver):
    qt_driver.refresh_tag_filter_controls = Mock()

    foo = unwrap(qt_driver.lib.get_tag_by_name("foo"))
    bar = unwrap(qt_driver.lib.get_tag_by_name("bar"))
    entry = Entry(
        id=3,
        folder=unwrap(qt_driver.lib.folder),
        path=Path("foo-bar.txt"),
        fields=qt_driver.lib.default_fields,
    )
    assert qt_driver.lib.add_entries([entry])
    assert qt_driver.lib.add_tags_to_entries(entry.id, [foo.id, bar.id]) == 2

    qt_driver.update_browsing_state(
        BrowsingState.show_all().with_tag_filters({foo.id, bar.id}, set())
    )

    assert qt_driver.active_tag_filter_ids == {foo.id, bar.id}
    assert qt_driver.frame_content == [entry.id]

    qt_driver.update_browsing_state(
        BrowsingState.from_search_query(f"tag_id:{foo.id} tag_id:{bar.id}")
    )

    assert qt_driver.active_tag_filter_ids == {foo.id, bar.id}
    assert qt_driver.frame_content == [entry.id]


def test_edit_media_entry_normalizes_title(qt_driver: QtDriver):
    qt_driver.lib.set_entry_title(1, "Original Title")

    assert qt_driver.edit_entry(1, source_path=None, title="  Trimmed Title  ", prompt="")
    entry = unwrap(qt_driver.lib.get_entry_full(1))
    assert qt_driver.lib.get_entry_field_value(entry, FieldID.TITLE) == "Trimmed Title"

    assert qt_driver.edit_entry(1, source_path=None, title="   ", prompt="")
    entry = unwrap(qt_driver.lib.get_entry_full(1))
    assert not any(field.type.key == FieldID.TITLE.name for field in entry.fields)


def test_edit_text_only_entry_still_requires_title(qt_driver: QtDriver):
    entry = Entry(
        id=101,
        folder=unwrap(qt_driver.lib.folder),
        path=None,
        fields=[
            TextField(
                type_key=FieldID.TITLE.name,
                value="Existing Title",
                position=0,
            )
        ],
    )
    assert qt_driver.lib.add_entries([entry])
    qt_driver.show_error_message = Mock()

    assert not qt_driver.edit_entry(101, source_path=None, title="   ", prompt="")
    qt_driver.show_error_message.assert_called_once()

    entry = unwrap(qt_driver.lib.get_entry_full(101))
    assert qt_driver.lib.get_entry_field_value(entry, FieldID.TITLE) == "Existing Title"


def test_add_text_only_entry_requires_title(qt_driver: QtDriver):
    qt_driver.show_error_message = Mock()
    existing_ids = {entry.id for entry in qt_driver.lib.all_entries()}

    assert not qt_driver.add_entry_from_path(
        source_path=None, title="   ", prompt="", tag_ids=[]
    )
    qt_driver.show_error_message.assert_called_once()
    assert {entry.id for entry in qt_driver.lib.all_entries()} == existing_ids


def test_apply_tag_filter_toggles_shared_tag_selection(qt_driver: QtDriver):
    recorded_states: list[BrowsingState] = []

    def fake_update_browsing_state(state: BrowsingState | None = None) -> None:
        if state is not None:
            qt_driver.browsing_history.push(state)
            recorded_states.append(state)

    qt_driver.update_browsing_state = fake_update_browsing_state

    foo = unwrap(qt_driver.lib.get_tag_by_name("foo"))
    bar = unwrap(qt_driver.lib.get_tag_by_name("bar"))

    qt_driver.apply_tag_filter(foo.id)
    assert qt_driver.active_tag_filter_ids == {foo.id}
    assert not qt_driver.excluded_tag_filter_ids
    assert recorded_states[-1].active_tag_filter_ids == frozenset({foo.id})
    assert not recorded_states[-1].excluded_tag_filter_ids

    qt_driver.apply_excluded_tag_filter(foo.id)
    assert not qt_driver.active_tag_filter_ids
    assert qt_driver.excluded_tag_filter_ids == {foo.id}
    assert not recorded_states[-1].active_tag_filter_ids
    assert recorded_states[-1].excluded_tag_filter_ids == frozenset({foo.id})

    qt_driver.apply_tag_filter(foo.id)
    assert qt_driver.active_tag_filter_ids == {foo.id}
    assert not qt_driver.excluded_tag_filter_ids
    assert recorded_states[-1].active_tag_filter_ids == frozenset({foo.id})
    assert not recorded_states[-1].excluded_tag_filter_ids

    qt_driver.apply_tag_filter(bar.id)
    assert qt_driver.active_tag_filter_ids == {foo.id, bar.id}
    assert recorded_states[-1].active_tag_filter_ids == frozenset({foo.id, bar.id})

    qt_driver.apply_excluded_tag_filter(foo.id)
    assert qt_driver.active_tag_filter_ids == {bar.id}
    assert qt_driver.excluded_tag_filter_ids == {foo.id}
    assert recorded_states[-1].active_tag_filter_ids == frozenset({bar.id})
    assert recorded_states[-1].excluded_tag_filter_ids == frozenset({foo.id})

    qt_driver.apply_excluded_tag_filter(foo.id)
    assert qt_driver.active_tag_filter_ids == {bar.id}
    assert not qt_driver.excluded_tag_filter_ids
    assert recorded_states[-1].active_tag_filter_ids == frozenset({bar.id})
    assert not recorded_states[-1].excluded_tag_filter_ids

    qt_driver.clear_tag_filters()
    assert not qt_driver.active_tag_filter_ids
    assert not qt_driver.excluded_tag_filter_ids
    assert not recorded_states[-1].active_tag_filter_ids
    assert not recorded_states[-1].excluded_tag_filter_ids


def test_refresh_tag_filter_controls_stable_labels_and_highlights(qtbot, qt_driver: QtDriver):
    root = QWidget()
    layout = QVBoxLayout(root)
    tags_button = QPushButton()
    favorite_tags_button = QPushButton()
    reset_tag_selection_button = QPushButton()
    pinned_tags_title = QLabel()
    pinned_tags_container = QWidget()
    pinned_tags_layout = QVBoxLayout(pinned_tags_container)
    pinned_tags_container.setLayout(pinned_tags_layout)
    layout.addWidget(tags_button)
    layout.addWidget(favorite_tags_button)
    layout.addWidget(reset_tag_selection_button)
    layout.addWidget(pinned_tags_title)
    layout.addWidget(pinned_tags_container)
    qtbot.addWidget(root)

    qt_driver.main_window = SimpleNamespace(
        tags_button=tags_button,
        favorite_tags_button=favorite_tags_button,
        reset_tag_selection_button=reset_tag_selection_button,
        pinned_tags_title=pinned_tags_title,
        pinned_tags_container=pinned_tags_container,
        pinned_tags_layout=pinned_tags_layout,
    )

    foo = unwrap(qt_driver.lib.get_tag_by_name("foo"))
    foo.favorite = True
    foo.pinned = True
    qt_driver.lib.update_tag(
        foo,
        set(foo.parent_ids),
        {alias.name for alias in foo.aliases},
        set(foo.alias_ids),
    )
    qt_driver.active_tag_filter_ids = {foo.id}

    qt_driver.refresh_tag_filter_controls()

    assert qt_driver.main_window.tags_button.text() == "Tags"
    assert qt_driver.main_window.favorite_tags_button.text() == "Favorite Tags"
    assert qt_driver.main_window.reset_tag_selection_button.text() == "Reset Selection"
    assert qt_driver.main_window.reset_tag_selection_button.isEnabled()
    assert qt_driver.main_window.tags_button.styleSheet() == ""
    assert qt_driver.main_window.favorite_tags_button.styleSheet() == ""
    assert qt_driver.main_window.reset_tag_selection_button.styleSheet() == ""
    assert qt_driver.main_window.tags_button.graphicsEffect() is None
    assert qt_driver.main_window.favorite_tags_button.graphicsEffect() is None
    assert not qt_driver.main_window.tags_button._selection_dot_indicator.isHidden()
    assert not qt_driver.main_window.favorite_tags_button._selection_dot_indicator.isHidden()
    assert not hasattr(
        qt_driver.main_window.reset_tag_selection_button, "_selection_dot_indicator"
    )
    assert qt_driver.main_window.tags_button.minimumWidth() >= tags_button.sizeHint().width()
    assert qt_driver.main_window.favorite_tags_button.minimumWidth() >= (
        favorite_tags_button.sizeHint().width()
    )
    assert qt_driver.main_window.pinned_tags_layout.count() == 1

    chip = qt_driver.main_window.pinned_tags_layout.itemAt(0).widget()
    assert isinstance(chip, TagWidget)
    assert "border-width: 2px;" in chip.bg_button.styleSheet()
    assert chip.bg_button.graphicsEffect() is not None
    assert chip.bg_button.contextMenuPolicy() == Qt.ContextMenuPolicy.NoContextMenu
    assert chip.bg_button.actions() == []

    qt_driver.active_tag_filter_ids = set()
    qt_driver.excluded_tag_filter_ids = {foo.id}
    qt_driver.refresh_tag_filter_controls()

    chip = qt_driver.main_window.pinned_tags_layout.itemAt(0).widget()
    assert isinstance(chip, TagWidget)
    assert "text-decoration: line-through;" in chip.bg_button.styleSheet()
    assert "border-color: rgba(122, 75, 81, 255);" in chip.bg_button.styleSheet()
    assert chip.bg_button.graphicsEffect() is None


def test_add_entry_pinned_tags_disable_context_menu(qtbot, qt_driver: QtDriver):
    modal = AddEntryModal(lambda file_path, prompt, tags: True, qt_driver.lib)
    qtbot.addWidget(modal)

    foo = unwrap(qt_driver.lib.get_tag_by_name("foo"))
    foo.pinned = True
    modal.set_pinned_tags([foo])

    chip = modal.pinned_tags_layout.itemAt(0).widget()
    assert isinstance(chip, TagWidget)
    assert chip.bg_button.contextMenuPolicy() == Qt.ContextMenuPolicy.NoContextMenu
    assert chip.bg_button.actions() == []
