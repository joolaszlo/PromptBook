# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


from PySide6.QtGui import QGuiApplication

from tagstudio.core.library.alchemy.fields import FieldID
from tagstudio.core.library.alchemy.library import Library
from tagstudio.core.library.alchemy.models import Entry
from tagstudio.qt.controllers.preview_panel_controller import PreviewPanel
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


def test_update_selection_single(qt_driver: QtDriver, library: Library, entry_full: Entry):
    panel = PreviewPanel(library, qt_driver)

    # Select the single entry
    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)

    # Panel should enable UI that allows for entry modification
    assert panel.add_buttons_enabled
    assert not panel.copy_prompt_enabled


def test_update_selection_multiple(qt_driver: QtDriver, library: Library):
    panel = PreviewPanel(library, qt_driver)

    # Select the multiple entries
    qt_driver.toggle_item_selection(1, append=False, bridge=False)
    qt_driver.toggle_item_selection(2, append=True, bridge=False)
    panel.set_selection(qt_driver.selected)

    # Panel should enable UI that allows for entry modification
    assert panel.add_buttons_enabled
    assert not panel.copy_prompt_enabled


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
