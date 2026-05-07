# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from types import SimpleNamespace
from unittest.mock import patch

from PySide6.QtWidgets import QApplication, QLabel, QSizePolicy, QVBoxLayout, QWidget
from pytestqt.qtbot import QtBot

import tagstudio.qt.views.main_window as main_window_module
from tagstudio.qt.translations import Translations


class DummyThumbGridLayout(QVBoxLayout):
    def __init__(self, driver, parent=None):
        super().__init__()
        self.addWidget(QLabel("thumbs"))


class DummyPreviewPanel(QWidget):
    def __init__(self, lib, driver):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("preview"))


class DummyLandingWidget(QWidget):
    def __init__(self, driver, ratio):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("landing"))


class DummyPagination(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("pagination"))


class DummyResourceManager:
    def get(self, name):
        from PIL import Image

        return Image.new("RGBA", (16, 16), (255, 255, 255, 255))


class DummyDriver:
    lib = object()
    settings = SimpleNamespace(show_category_sidebar=False)


def build_main_window():
    with (
        patch.object(main_window_module, "ThumbGridLayout", DummyThumbGridLayout),
        patch.object(main_window_module, "PreviewPanel", DummyPreviewPanel),
        patch.object(main_window_module, "LandingWidget", DummyLandingWidget),
        patch.object(main_window_module, "Pagination", DummyPagination),
        patch.object(main_window_module, "ResourceManager", DummyResourceManager),
    ):
        return main_window_module.MainWindow(DummyDriver())


def set_pinned_tags(window: main_window_module.MainWindow, count: int) -> None:
    while window.pinned_tags_layout.count():
        item = window.pinned_tags_layout.takeAt(0)
        if item and item.widget():
            item.widget().deleteLater()

    for index in range(count):
        chip = QLabel(f"pinned-tag-{index}")
        chip.setStyleSheet("border:1px solid white; padding:2px;")
        chip.setMinimumWidth(110)
        window.pinned_tags_layout.addWidget(chip)

    window.pinned_tags_container.updateGeometry()
    window.central_layout.activate()
    QApplication.processEvents()


def sync_toolbar_layout(window: main_window_module.MainWindow) -> None:
    QApplication.processEvents()
    window._update_top_toolbar_widths()
    QApplication.processEvents()


def test_main_window_pinned_tags_row_stays_compact_on_resize(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)
    set_pinned_tags(window, 6)

    window.resize(1316, 740)
    window.show()
    qtbot.wait(0)

    row4_height = window.central_layout.itemAtPosition(4, 0).geometry().height()
    row5_y = window.central_layout.itemAtPosition(5, 0).geometry().y()
    title_geometry = window.pinned_tags_title.geometry()
    container_geometry = window.pinned_tags_container.geometry()

    window.resize(1316, 1000)
    qtbot.wait(0)

    assert window.central_layout.itemAtPosition(4, 0).geometry().height() == row4_height
    assert window.central_layout.itemAtPosition(5, 0).geometry().y() == row5_y
    assert window.pinned_tags_title.geometry() == title_geometry
    assert window.pinned_tags_container.geometry() == container_geometry


def test_main_window_pinned_tags_row_grows_only_for_more_rows(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)
    window.resize(600, 740)
    window.show()

    set_pinned_tags(window, 3)
    qtbot.wait(0)
    compact_row_height = window.central_layout.itemAtPosition(4, 0).geometry().height()
    compact_container_height = window.pinned_tags_container.height()

    set_pinned_tags(window, 30)
    qtbot.wait(0)
    expanded_row_height = window.central_layout.itemAtPosition(4, 0).geometry().height()
    expanded_container_height = window.pinned_tags_container.height()

    assert expanded_row_height > compact_row_height
    assert expanded_container_height > compact_container_height

    window.resize(600, 1000)
    qtbot.wait(0)

    assert window.central_layout.itemAtPosition(4, 0).geometry().height() == expanded_row_height
    assert window.pinned_tags_container.height() == expanded_container_height


def test_top_search_row_keeps_bounded_search_pair_and_edge_action(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)

    window.resize(1316, 740)
    window.show()
    sync_toolbar_layout(window)

    search_widgets = [
        window.search_bar_layout.itemAt(index).widget()
        for index in range(window.search_bar_layout.count())
    ]

    assert search_widgets == [
        window.back_button,
        window.forward_button,
        window.search_field,
    ]
    assert window.library_toolbar_layout.itemAtPosition(0, 0).widget() == (
        window.search_cluster_container
    )
    assert window.library_toolbar_layout.itemAtPosition(0, 1).widget() == window.search_button
    assert window.library_toolbar_layout.itemAtPosition(0, 3).widget() == window.add_entry_button
    assert window.library_toolbar_layout.itemAtPosition(1, 0).widget() == (
        window.tag_filter_selector_container
    )
    assert window.library_toolbar_layout.columnStretch(2) == 1
    assert window.search_field.geometry().right() < window.search_button.geometry().left()
    assert window.search_button.geometry().right() < window.add_entry_button.geometry().left()
    assert window.add_entry_button.text() == Translations["entry.add_prompt"]
    assert window.search_button.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed
    assert window.add_entry_button.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed
    assert window.search_field.maximumWidth() <= int(
        window.central_widget.width() * window.SEARCH_FIELD_MAX_WIDTH_RATIO
    )
    assert window.search_field.width() <= window.search_field.maximumWidth()
    assert window.add_entry_button.maximumWidth() == window.add_entry_button.sizeHint().width()
    assert window.search_field.maximumWidth() > int(window.central_widget.width() * 0.46)

    window.resize(2200, 900)
    sync_toolbar_layout(window)
    assert window.search_field.maximumWidth() == window.SEARCH_FIELD_MAX_WIDTH_CAP
    assert window.add_entry_button.geometry().right() <= window.central_widget.geometry().right()

    window.resize(520, 740)
    sync_toolbar_layout(window)
    assert window.search_field.minimumWidth() == 0
    assert window.search_field.maximumWidth() >= window.SEARCH_FIELD_MIN_MAX_WIDTH
    assert window.search_field.geometry().right() < window.search_button.geometry().left()
    assert window.search_button.geometry().right() < window.add_entry_button.geometry().left()


def test_search_scope_controls_align_to_search_field_end_when_space_allows(qtbot: QtBot):
    window = build_main_window()
    qtbot.addWidget(window)

    def central_left(widget: QWidget) -> int:
        return widget.mapTo(window.central_widget, widget.rect().topLeft()).x()

    def central_right(widget: QWidget) -> int:
        return widget.mapTo(window.central_widget, widget.rect().topRight()).x()

    for width in (1316, 2200):
        window.resize(width, 740)
        window.show()
        sync_toolbar_layout(window)

        field_right = central_right(window.search_field)
        scope_left = central_left(window.search_scope_label)
        scope_right = central_right(window.search_scope_prompt_checkbox)
        reset_right = central_right(window.reset_tag_selection_button)
        selector_right = central_right(window.tag_filter_selector_container)

        if (
            window.tag_filter_selector_container.minimumSizeHint().width()
            <= window.search_cluster_container.maximumWidth()
        ):
            assert abs(scope_right - field_right) <= 1
            assert scope_left - reset_right > 200
        else:
            assert scope_right <= selector_right
            assert scope_right > field_right
        assert reset_right < scope_left < scope_right

    window.resize(520, 740)
    sync_toolbar_layout(window)

    assert central_right(window.reset_tag_selection_button) < central_left(
        window.search_scope_label
    )
    assert central_right(window.search_scope_prompt_checkbox) < central_left(
        window.search_button
    )
