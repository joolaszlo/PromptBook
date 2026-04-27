# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from __future__ import annotations

from typing import TYPE_CHECKING, override

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tagstudio.core.library.category_sidebar import (
    CategoryGroup,
    CategoryItem,
    CategorySidebarSettings,
)
from tagstudio.qt.category_sidebar_icons import category_sidebar_icon

if TYPE_CHECKING:
    from tagstudio.qt.ts_qt import QtDriver


class CategorySidebarItemWidget(QPushButton):
    def __init__(self, item: CategoryItem, collapsed: bool) -> None:
        super().__init__()
        self.item = item
        self.setObjectName("category_sidebar_item")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFlat(True)
        self.setMinimumHeight(32)
        self.setIcon(category_sidebar_icon(item.icon, size=18))
        self.setIconSize(QSize(18, 18))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.set_collapsed(collapsed)

    def set_collapsed(self, collapsed: bool) -> None:
        self.setText("" if collapsed else self.item.name)
        self.setToolTip(self.item.name)

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
            return
        super().mousePressEvent(event)

    @override
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
            return
        super().mouseReleaseEvent(event)


class CategorySidebarWidget(QFrame):
    EXPANDED_WIDTH = 220
    COLLAPSED_WIDTH = 52

    def __init__(self, driver: "QtDriver") -> None:
        super().__init__()
        self.driver = driver
        self.settings = CategorySidebarSettings()
        self.setObjectName("category_sidebar")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(8, 8, 8, 8)
        self.root_layout.setSpacing(8)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("category_sidebar_scroll_area")
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(6)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.content_widget)
        self.root_layout.addWidget(self.scroll_area, 1)

        self.footer = QWidget()
        self.footer_layout = QHBoxLayout(self.footer)
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.footer_layout.setSpacing(6)

        self.settings_button = QPushButton()
        self.settings_button.setObjectName("category_sidebar_settings_button")
        self.settings_button.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.settings_button.setIcon(category_sidebar_icon("settings", size=18))
        self.settings_button.setIconSize(QSize(18, 18))
        self.settings_button.setToolTip("Category sidebar settings")
        self.settings_button.clicked.connect(self.open_settings_placeholder)
        self.footer_layout.addWidget(self.settings_button)

        self.collapse_button = QPushButton()
        self.collapse_button.setObjectName("category_sidebar_collapse_button")
        self.collapse_button.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.collapse_button.setToolTip("Collapse category sidebar")
        self.collapse_button.clicked.connect(self.toggle_collapsed)
        self.footer_layout.addWidget(self.collapse_button)
        self.root_layout.addWidget(self.footer)

        self.setStyleSheet(
            "QFrame#category_sidebar {"
            "background: rgba(26, 29, 34, 180);"
            "border-right: 1px solid rgba(120, 128, 140, 70);"
            "}"
            "QLabel#category_sidebar_group_header {"
            "color: #9aa3ad;"
            "font-size: 11px;"
            "font-weight: 700;"
            "padding: 6px 6px 2px 6px;"
            "}"
            "QLabel#category_sidebar_empty_title {"
            "color: #cfd5df;"
            "font-weight: 700;"
            "padding: 8px 4px 0 4px;"
            "}"
            "QLabel#category_sidebar_empty_hint {"
            "color: #8f98a6;"
            "padding: 0 4px;"
            "}"
            "QFrame#category_sidebar_separator {"
            "background: rgba(120, 128, 140, 65);"
            "max-height: 1px;"
            "}"
            "QPushButton#category_sidebar_item {"
            "background: transparent;"
            "color: #d8dde6;"
            "border: 1px solid transparent;"
            "border-radius: 6px;"
            "padding: 5px 8px;"
            "text-align: left;"
            "font-weight: 600;"
            "}"
            "QPushButton#category_sidebar_item:hover {"
            "background: rgba(120, 128, 140, 45);"
            "border-color: rgba(120, 128, 140, 80);"
            "}"
            "QPushButton#category_sidebar_item:pressed {"
            "background: rgba(77, 163, 255, 60);"
            "border-color: rgba(77, 163, 255, 120);"
            "}"
            "QPushButton#category_sidebar_settings_button,"
            "QPushButton#category_sidebar_collapse_button {"
            "background: transparent;"
            "color: #d8dde6;"
            "border: 1px solid rgba(120, 128, 140, 65);"
            "border-radius: 6px;"
            "min-height: 30px;"
            "}"
            "QPushButton#category_sidebar_settings_button:hover,"
            "QPushButton#category_sidebar_collapse_button:hover {"
            "background: rgba(120, 128, 140, 45);"
            "border-color: rgba(120, 128, 140, 110);"
            "}"
        )
        self.set_settings(self.settings)

    def set_settings(self, settings: CategorySidebarSettings) -> None:
        self.settings = settings.normalized()
        self.render()

    def toggle_collapsed(self) -> None:
        self.settings.collapsed = not self.settings.collapsed
        if self.driver.lib.library_dir:
            self.settings = self.driver.lib.set_category_sidebar_settings(self.settings)
        self.render()

    def open_settings_placeholder(self) -> None:
        QMessageBox.information(
            self,
            "Category Sidebar",
            "Category sidebar settings will be added here.",
        )

    def render(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

        collapsed = self.settings.collapsed
        self.setFixedWidth(self.COLLAPSED_WIDTH if collapsed else self.EXPANDED_WIDTH)
        self.collapse_button.setText(">" if collapsed else "<")
        self.collapse_button.setToolTip(
            "Expand category sidebar" if collapsed else "Collapse category sidebar"
        )
        self.footer_layout.setDirection(
            QHBoxLayout.Direction.TopToBottom
            if collapsed
            else QHBoxLayout.Direction.LeftToRight
        )

        groups_with_items = [group for group in self.settings.groups if group.items]
        if not groups_with_items and not collapsed:
            self._add_empty_state()
        else:
            for group_index, group in enumerate(self.settings.groups):
                self._add_group(group, collapsed)
                if group_index < len(self.settings.groups) - 1:
                    self._add_separator()

        if not groups_with_items and collapsed:
            self.content_layout.addStretch(1)

    def _add_empty_state(self) -> None:
        title = QLabel("No category groups yet")
        title.setObjectName("category_sidebar_empty_title")
        title.setWordWrap(True)
        self.content_layout.addWidget(title)

        hint = QLabel("Use the gear icon to add categories")
        hint.setObjectName("category_sidebar_empty_hint")
        hint.setWordWrap(True)
        self.content_layout.addWidget(hint)
        self.content_layout.addStretch(1)

    def _add_group(self, group: CategoryGroup, collapsed: bool) -> None:
        if not collapsed:
            header = QLabel(group.name)
            header.setObjectName("category_sidebar_group_header")
            header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            self.content_layout.addWidget(header)
        elif group.items:
            self.content_layout.addSpacing(4)

        for item in group.items:
            self.content_layout.addWidget(CategorySidebarItemWidget(item, collapsed))

    def _add_separator(self) -> None:
        separator = QFrame()
        separator.setObjectName("category_sidebar_separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        self.content_layout.addWidget(separator)
