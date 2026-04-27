# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from pathlib import Path
from types import SimpleNamespace

from PySide6.QtCore import Qt
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


def test_category_sidebar_empty_state(qtbot: QtBot):
    driver = SimpleNamespace(lib=DummyLibrary())
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)

    assert "No category groups yet" in [label.text() for label in sidebar.findChildren(QLabel)]


def test_category_sidebar_renders_items_and_collapses(qtbot: QtBot):
    library = DummyLibrary()
    sidebar = CategorySidebarWidget(SimpleNamespace(lib=library))
    qtbot.addWidget(sidebar)

    sidebar.set_settings(
        CategorySidebarSettings(
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
    )

    item = sidebar.findChild(CategorySidebarItemWidget)
    assert item is not None
    assert item.contextMenuPolicy() == Qt.ContextMenuPolicy.NoContextMenu
    assert item.text() == "Item"

    sidebar.toggle_collapsed()

    assert library.saved_settings is not None
    assert library.saved_settings.collapsed is True
    assert sidebar.findChild(CategorySidebarItemWidget).text() == ""
