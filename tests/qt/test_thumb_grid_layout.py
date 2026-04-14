# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pytestqt.qtbot import QtBot
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout

import tagstudio.qt.thumb_grid_layout as thumb_grid_layout_module
import tagstudio.qt.views.main_window as main_window_module


class DummySignal:
    def connect(self, fn):
        self.fn = fn


class DummyRenderer:
    def __init__(self, driver):
        self.updated = DummySignal()

    def render(self, *args, **kwargs):
        return None


class DummyThumbButton:
    def set_selected(self, value):
        return None


class DummyItemThumb(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._size = QSize(128, 140)
        self.thumb_button = DummyThumbButton()
        self.rendered_path = None

    def sizeHint(self):
        return self._size

    def minimumSize(self):
        return self._size

    def update_thumb(self, *args):
        return None

    def update_size(self, *args):
        return None

    def set_filename_text(self, *args):
        return None

    def set_extension(self, *args):
        return None

    def set_item(self, entry):
        self.item_id = entry.id

    def assign_badge(self, *args):
        return None


class DummyPreviewPanel(QWidget):
    def __init__(self, lib, driver):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("preview"))
        self.setMinimumWidth(400)


class DummyLandingWidget(QWidget):
    def __init__(self, driver, ratio):
        super().__init__()


class DummyPagination(QWidget):
    def __init__(self):
        super().__init__()


class DummyResourceManager:
    def get(self, name):
        from PIL import Image

        return Image.new("RGBA", (16, 16), (255, 255, 255, 255))


class DummyLib:
    library_dir = Path(".")

    def get_entries(self, ids):
        return [SimpleNamespace(id=i, path=Path(f"file{i}.png")) for i in ids]

    def get_tag_entries(self, tag_ids, ids):
        return {tag_id: set() for tag_id in tag_ids}


class DummyQueue:
    def __init__(self):
        self.queue = []

    def put(self, item):
        self.queue.append(item)


class DummyDriver:
    def __init__(self):
        self.lib = DummyLib()
        self.settings = SimpleNamespace(show_filenames_in_grid=True)
        self.thumb_job_queue = DummyQueue()
        self._selected = set()


def build_main_window():
    driver = DummyDriver()
    with (
        patch.object(thumb_grid_layout_module, "ThumbRenderer", DummyRenderer),
        patch.object(thumb_grid_layout_module, "ItemThumb", DummyItemThumb),
        patch.object(main_window_module, "PreviewPanel", DummyPreviewPanel),
        patch.object(main_window_module, "LandingWidget", DummyLandingWidget),
        patch.object(main_window_module, "Pagination", DummyPagination),
        patch.object(main_window_module, "ResourceManager", DummyResourceManager),
    ):
        window = main_window_module.MainWindow(driver)
    driver.main_window = window
    window.thumb_layout.set_entries(list(range(100)))
    window.thumb_layout.update()
    return window


def first_row_count(window: main_window_module.MainWindow) -> int:
    count = 0
    for item_thumb in window.thumb_layout._item_thumbs:
        geometry = item_thumb.geometry()
        if geometry.width() == 0:
            continue
        if geometry.y() == 0:
            count += 1
    return count


def expected_columns(window: main_window_module.MainWindow) -> int:
    item_width = window.thumb_layout._item_thumbs[0].sizeHint().width()
    spacing = window.thumb_layout.spacing()
    return max(1, window.entry_scroll_area.viewport().width() // (item_width + spacing))


def test_thumb_grid_reflows_with_entry_viewport_width(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)
    window.show()

    observed_columns = []
    observed_viewport_widths = []
    for width in [1800, 1600, 1400, 1200, 1000, 800, 700]:
        window.resize(width, 1000)
        qtbot.wait(0)
        observed_columns.append(first_row_count(window))
        observed_viewport_widths.append(window.entry_scroll_area.viewport().width())
        assert observed_columns[-1] == expected_columns(window)

    assert observed_columns == [9, 8, 6, 5, 3, 2, 1]
    assert observed_viewport_widths == [1340, 1140, 940, 740, 540, 340, 240]


def test_thumb_grid_accounts_for_preview_panel_width(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)
    window.resize(1800, 1000)
    window.show()
    qtbot.wait(0)

    window.content_splitter.setSizes([1200, 600])
    qtbot.wait(0)
    wide_entry_columns = first_row_count(window)
    wide_entry_viewport = window.entry_scroll_area.viewport().width()

    window.content_splitter.setSizes([900, 900])
    qtbot.wait(0)
    narrow_entry_columns = first_row_count(window)
    narrow_entry_viewport = window.entry_scroll_area.viewport().width()

    assert wide_entry_columns == expected_columns(window) or wide_entry_columns > narrow_entry_columns
    assert narrow_entry_columns == expected_columns(window)
    assert wide_entry_viewport > narrow_entry_viewport
    assert wide_entry_columns > narrow_entry_columns
    assert narrow_entry_columns < max(1, window.width() // (128 + window.thumb_layout.spacing()))
