# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


from PySide6.QtGui import QGuiApplication
from pytestqt.qtbot import QtBot

from tagstudio.core.library.alchemy.fields import FieldID, TextField
from tagstudio.core.library.alchemy.library import Library
from tagstudio.core.library.alchemy.models import Entry
from tagstudio.core.utils.types import unwrap
from tagstudio.qt.controllers.preview_panel_controller import PreviewPanel
from tagstudio.qt.mixed.file_attributes import FileAttributeData
from tagstudio.qt.mixed.settings_panel import SettingsPanel
from tagstudio.qt.ts_qt import QtDriver


def test_update_selection_empty(qt_driver: QtDriver, library: Library):
    panel = PreviewPanel(library, qt_driver)

    # Clear the library selection (selecting 1 then unselecting 1)
    qt_driver.toggle_item_selection(1, append=False, bridge=False)
    qt_driver.toggle_item_selection(1, append=True, bridge=False)
    panel.set_selection(qt_driver.selected)

    # Panel should disable UI that allows for entry modification
    assert not panel.add_buttons_enabled
    assert not panel.copy_prompt_enabled
    assert not panel.edit_prompt_enabled


def test_update_selection_single(qt_driver: QtDriver, library: Library, entry_full: Entry):
    panel = PreviewPanel(library, qt_driver)

    # Select the single entry
    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)

    # Panel should enable UI that allows for entry modification
    assert panel.add_buttons_enabled
    assert not panel.copy_prompt_enabled
    assert panel.edit_prompt_enabled


def test_text_only_entry_shows_title_preview(qt_driver: QtDriver, library: Library):
    panel = PreviewPanel(library, qt_driver)
    entry = Entry(
        id=100,
        folder=unwrap(library.folder),
        path=None,
        fields=[
            TextField(
                type_key=FieldID.TITLE.name,
                value="A Long Text Entry Title For Preview",
                position=0,
            )
        ],
    )
    assert library.add_entries([entry])

    panel.set_selection([entry.id])

    assert panel.preview_thumb.text_preview_visible
    assert panel.preview_thumb.text_preview_title == "A Long Text Entry Title For Preview"


def test_update_selection_multiple(qt_driver: QtDriver, library: Library):
    panel = PreviewPanel(library, qt_driver)

    # Select the multiple entries
    qt_driver.toggle_item_selection(1, append=False, bridge=False)
    qt_driver.toggle_item_selection(2, append=True, bridge=False)
    panel.set_selection(qt_driver.selected)

    # Panel should enable UI that allows for entry modification
    assert panel.add_buttons_enabled
    assert not panel.copy_prompt_enabled
    assert not panel.edit_prompt_enabled


def test_copy_prompt_enabled_and_copies_content(
    qt_driver: QtDriver, library: Library, entry_full: Entry
):
    panel = PreviewPanel(library, qt_driver)

    description_field = next(f for f in entry_full.fields if f.type.key == FieldID.DESCRIPTION.name)
    library.update_entry_field(entry_full.id, description_field, "Prompt body")

    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)

    assert panel.copy_prompt_enabled

    panel._copy_prompt_button_callback()
    assert QGuiApplication.clipboard().text() == "Prompt body"


def test_edit_prompt_button_adds_missing_prompt_field(
    qt_driver: QtDriver, library: Library, entry_full: Entry
):
    panel = PreviewPanel(library, qt_driver)

    description_field = next(
        (f for f in entry_full.fields if f.type.key == FieldID.DESCRIPTION.name), None
    )
    if description_field:
        library.remove_entry_field(description_field, [entry_full.id])

    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)
    panel._edit_prompt_button_callback()

    updated_entry = library.get_entry_full(entry_full.id)
    assert updated_entry is not None
    assert any(f.type.key == FieldID.DESCRIPTION.name for f in updated_entry.fields)


def test_preview_metadata_hidden_by_default(qt_driver: QtDriver, library: Library):
    panel = PreviewPanel(library, qt_driver)

    qt_driver.toggle_item_selection(2, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)
    file_attributes = panel._file_attributes_widget  # pyright: ignore[reportPrivateUsage]

    assert file_attributes.date_created_label.isHidden()
    assert file_attributes.date_modified_label.isHidden()
    assert file_attributes.file_label.isHidden()
    assert file_attributes.dimensions_label.isHidden()


def test_preview_metadata_settings_show_sections(qt_driver: QtDriver, library: Library):
    panel = PreviewPanel(library, qt_driver)
    qt_driver.settings.show_preview_created_date = True
    qt_driver.settings.show_preview_modified_date = True
    qt_driver.settings.show_preview_filename = True
    qt_driver.settings.show_preview_media_info = True

    qt_driver.toggle_item_selection(2, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)
    file_attributes = panel._file_attributes_widget  # pyright: ignore[reportPrivateUsage]

    assert not file_attributes.date_created_label.isHidden()
    assert not file_attributes.date_modified_label.isHidden()
    assert not file_attributes.file_label.isHidden()
    assert not file_attributes.dimensions_label.isHidden()


def test_settings_panel_preview_metadata_controls(qtbot: QtBot, qt_driver: QtDriver):
    settings_panel = SettingsPanel(qt_driver)
    qtbot.addWidget(settings_panel)

    assert not settings_panel.show_preview_created_date_checkbox.isChecked()
    assert not settings_panel.show_preview_modified_date_checkbox.isChecked()
    assert not settings_panel.show_preview_filename_checkbox.isChecked()
    assert not settings_panel.show_preview_media_info_checkbox.isChecked()

    settings_panel.show_preview_created_date_checkbox.setChecked(True)
    settings_panel.show_preview_modified_date_checkbox.setChecked(True)
    settings_panel.show_preview_filename_checkbox.setChecked(True)
    settings_panel.show_preview_media_info_checkbox.setChecked(True)

    settings = settings_panel.get_settings()
    assert settings["show_preview_created_date"]
    assert settings["show_preview_modified_date"]
    assert settings["show_preview_filename"]
    assert settings["show_preview_media_info"]


def test_preview_metadata_settings_hide_sections_independently(
    qt_driver: QtDriver, library: Library
):
    panel = PreviewPanel(library, qt_driver)
    file_attributes = panel._file_attributes_widget  # pyright: ignore[reportPrivateUsage]
    filepath = unwrap(library.library_dir) / "metadata.jpg"
    stats = FileAttributeData(width=100, height=50)

    qt_driver.settings.show_preview_created_date = True
    qt_driver.settings.show_preview_modified_date = False
    qt_driver.settings.show_preview_filename = True
    qt_driver.settings.show_preview_media_info = False

    file_attributes.update_date_label(filepath)
    file_attributes.update_stats(filepath, stats)

    assert not file_attributes.date_created_label.isHidden()
    assert file_attributes.date_modified_label.isHidden()
    assert not file_attributes.file_label.isHidden()
    assert file_attributes.dimensions_label.isHidden()
