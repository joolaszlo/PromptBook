# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from pytestqt.qtbot import QtBot

import tagstudio.qt.views.main_window as main_window_module
from tagstudio.core.library.category_sidebar import CategorySidebarSettings


class DummyThumbGridLayout(QVBoxLayout):
    def __init__(self, driver, parent=None):
        super().__init__()
        self.addWidget(QLabel("thumbs"))


class DummyPreviewPanel(QWidget):
    def __init__(self, lib, driver):
        super().__init__()
        self.setMinimumWidth(400)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("preview"))


class DummyLandingWidget(QWidget):
    def __init__(self, driver, ratio):
        super().__init__()


class DummyPagination(QWidget):
    pass


class DummyResourceManager:
    def get(self, name):
        from PIL import Image

        return Image.new("RGBA", (16, 16), (255, 255, 255, 255))


class DummyLib:
    library_dir = Path(".")

    def set_category_sidebar_settings(self, settings):
        return settings


class DummyDriver:
    def __init__(self):
        self.lib = DummyLib()
        self.settings = SimpleNamespace(show_filenames_in_grid=True)
        self.active_tag_filter_ids = set()
        self.excluded_tag_filter_ids = set()

    def is_tag_filter_selected(self, tag_id: int) -> bool:
        return False

    def is_tag_filter_excluded(self, tag_id: int) -> bool:
        return False

    def get_tag_filter_highlight_color(self) -> QColor:
        return QColor("#4da3ff")

    def apply_tag_filter(self, tag_id: int) -> None:
        return None

    def apply_excluded_tag_filter(self, tag_id: int) -> None:
        return None


def build_main_window() -> main_window_module.MainWindow:
    with (
        patch.object(main_window_module, "ThumbGridLayout", DummyThumbGridLayout),
        patch.object(main_window_module, "PreviewPanel", DummyPreviewPanel),
        patch.object(main_window_module, "LandingWidget", DummyLandingWidget),
        patch.object(main_window_module, "Pagination", DummyPagination),
        patch.object(main_window_module, "ResourceManager", DummyResourceManager),
    ):
        return main_window_module.MainWindow(DummyDriver())


def wait_for_sidebar_splitter_sync(qtbot: QtBot, window: main_window_module.MainWindow) -> None:
    qtbot.waitUntil(
        lambda: window.content_splitter.sizes()[0] == window.category_sidebar.target_width(),
        timeout=1000,
    )


def test_category_sidebar_splitter_syncs_after_startup_expanded(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)
    window.resize(1800, 1000)
    window.show()

    wait_for_sidebar_splitter_sync(qtbot, window)

    assert window.category_sidebar.width() == window.category_sidebar.EXPANDED_WIDTH
    assert window.entry_list_container.width() > 0
    assert window.preview_panel.width() >= 400


def test_category_sidebar_splitter_syncs_restored_collapsed_state(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)
    window.resize(1800, 1000)
    window.show()
    wait_for_sidebar_splitter_sync(qtbot, window)

    window.category_sidebar.set_settings(CategorySidebarSettings(collapsed=True))

    wait_for_sidebar_splitter_sync(qtbot, window)
    assert window.category_sidebar.width() == window.category_sidebar.COLLAPSED_WIDTH
    assert window.entry_list_container.width() > 0
    assert window.preview_panel.width() >= 400


def test_category_sidebar_runtime_collapse_expand_preserves_preview_width(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)
    window.resize(1800, 1000)
    window.show()
    wait_for_sidebar_splitter_sync(qtbot, window)

    window.content_splitter.setSizes([window.category_sidebar.target_width(), 900, 600])
    qtbot.wait(0)
    preview_width = window.content_splitter.sizes()[2]

    window.category_sidebar.toggle_collapsed()
    wait_for_sidebar_splitter_sync(qtbot, window)
    assert window.content_splitter.sizes()[2] == preview_width

    window.category_sidebar.toggle_collapsed()
    wait_for_sidebar_splitter_sync(qtbot, window)
    assert window.content_splitter.sizes()[2] == preview_width


def test_category_sidebar_search_refresh_repairs_stale_collapsed_splitter_size(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)
    window.resize(1800, 1000)
    window.show()
    wait_for_sidebar_splitter_sync(qtbot, window)

    window.category_sidebar.set_settings(CategorySidebarSettings(collapsed=True))
    wait_for_sidebar_splitter_sync(qtbot, window)

    window.content_splitter.setSizes([window.category_sidebar.EXPANDED_WIDTH, 900, 400])
    qtbot.wait(0)
    assert window.content_splitter.sizes()[0] != window.category_sidebar.target_width()

    window.category_sidebar.set_settings(window.category_sidebar.settings)

    wait_for_sidebar_splitter_sync(qtbot, window)
