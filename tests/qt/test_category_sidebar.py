# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel
from pytestqt.qtbot import QtBot

from tagstudio.core.library.category_sidebar import (
    CategoryFilterRule,
    CategoryGroup,
    CategoryItem,
    CategorySidebarSettings,
)
from tagstudio.qt.mixed.category_sidebar import CategorySidebarItemWidget, CategorySidebarWidget


class DummyLibrary:
    def __init__(self) -> None:
        self.library_dir = Path(".")
        self.saved_settings: CategorySidebarSettings | None = None

    def set_category_sidebar_settings(
        self,
        settings: CategorySidebarSettings,
    ) -> CategorySidebarSettings:
        self.saved_settings = settings
        return settings


class DummyDriver:
    def __init__(self) -> None:
        self.lib = DummyLibrary()
        self.included_tag_ids: set[int] = set()
        self.excluded_tag_ids: set[int] = set()

    def apply_tag_filter(self, tag_id: int) -> None:
        if tag_id in self.included_tag_ids:
            self.included_tag_ids.remove(tag_id)
        else:
            self.excluded_tag_ids.discard(tag_id)
            self.included_tag_ids.add(tag_id)

    def apply_excluded_tag_filter(self, tag_id: int) -> None:
        if tag_id in self.excluded_tag_ids:
            self.excluded_tag_ids.remove(tag_id)
        else:
            self.included_tag_ids.discard(tag_id)
            self.excluded_tag_ids.add(tag_id)

    def is_tag_filter_selected(self, tag_id: int) -> bool:
        return tag_id in self.included_tag_ids

    def is_tag_filter_excluded(self, tag_id: int) -> bool:
        return tag_id in self.excluded_tag_ids

    def get_tag_filter_highlight_color(self) -> QColor:
        return QColor("#4da3ff")


def make_settings() -> CategorySidebarSettings:
    return CategorySidebarSettings(
        groups=[
            CategoryGroup(
                id="group",
                name="Group",
                order=0,
                items=[
                    CategoryItem(
                        id="item",
                        name="Item",
                        icon="camera",
                        order=0,
                        filter_rules=[CategoryFilterRule(type="tag", tag_id=1000)],
                    )
                ],
            )
        ]
    )


def test_category_sidebar_empty_state(qtbot: QtBot):
    driver = DummyDriver()
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)

    assert "No category groups yet" in [label.text() for label in sidebar.findChildren(QLabel)]


def test_category_sidebar_renders_items_and_collapses(qtbot: QtBot):
    driver = DummyDriver()
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)

    sidebar.set_settings(make_settings())

    item = sidebar.findChild(CategorySidebarItemWidget)
    assert item is not None
    assert item.contextMenuPolicy() == Qt.ContextMenuPolicy.NoContextMenu
    assert item.text() == "Item"

    sidebar.toggle_collapsed()

    assert driver.lib.saved_settings is not None
    assert driver.lib.saved_settings.collapsed is True
    assert sidebar.findChild(CategorySidebarItemWidget).text() == ""


def test_category_sidebar_item_clicks_use_tag_filter_state(qtbot: QtBot):
    driver = DummyDriver()
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)
    sidebar.set_settings(make_settings())

    item = sidebar.findChild(CategorySidebarItemWidget)
    assert item is not None

    qtbot.mouseClick(item, Qt.MouseButton.LeftButton)
    assert driver.included_tag_ids == {1000}
    assert driver.excluded_tag_ids == set()

    qtbot.mouseClick(item, Qt.MouseButton.RightButton)
    assert driver.included_tag_ids == set()
    assert driver.excluded_tag_ids == {1000}

    qtbot.mouseClick(item, Qt.MouseButton.RightButton)
    assert driver.included_tag_ids == set()
    assert driver.excluded_tag_ids == set()
