# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from __future__ import annotations

from typing import TYPE_CHECKING, override

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QMouseEvent, QPalette
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
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
from tagstudio.qt.mixed.category_sidebar_settings import CategorySidebarSettingsPanel
from tagstudio.qt.mixed.tag_widget import (
    get_selection_fill_color,
    get_selection_hover_color,
)

if TYPE_CHECKING:
    from tagstudio.qt.ts_qt import QtDriver


def _theme_color(widget: QWidget, role: QPalette.ColorRole) -> QColor:
    color = QColor(widget.palette().color(role))
    background_role = (
        QPalette.ColorRole.Button
        if role is QPalette.ColorRole.ButtonText
        else QPalette.ColorRole.Window
    )
    background_color = QColor(widget.palette().color(background_role))
    color_scheme = QGuiApplication.styleHints().colorScheme()
    dark_background = background_color.lightness() < 128

    if (color_scheme is Qt.ColorScheme.Dark or dark_background) and color.lightness() < 128:
        return QColor("#d8dde6")
    if (color_scheme is Qt.ColorScheme.Light or not dark_background) and color.lightness() > 128:
        return QColor("#202124")
    return color


def _with_alpha(color: QColor, alpha: int) -> QColor:
    resolved = QColor(color)
    resolved.setAlpha(alpha)
    return resolved


class CategorySidebarItemWidget(QPushButton):
    right_clicked = Signal()

    def __init__(self, item: CategoryItem, collapsed: bool) -> None:
        super().__init__()
        self.item = item
        self._collapsed = collapsed
        self._included = False
        self._excluded = False
        self._highlight_color = QColor("#4da3ff")
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
        self._collapsed = collapsed
        self.setText("" if collapsed else self.item.name)
        self.setToolTip(self.item.name)
        self._apply_style()

    def set_filter_state(
        self,
        included: bool,
        excluded: bool,
        highlight_color: QColor,
    ) -> None:
        self._included = included
        self._excluded = excluded
        self._highlight_color = QColor(highlight_color)
        self._apply_style()

    @override
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            event.accept()
            return
        super().mousePressEvent(event)

    @override
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            if self.rect().contains(event.position().toPoint()):
                self.right_clicked.emit()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _apply_style(self) -> None:
        text_color = _theme_color(self, QPalette.ColorRole.ButtonText)
        border_color = QColor(120, 128, 140, 0)
        hover_border_color = QColor(120, 128, 140, 80)
        background_color = QColor(0, 0, 0, 0)
        hover_background_color = QColor(120, 128, 140, 45)
        text_decoration = "none"
        icon_color = text_color

        if self._included and not self._excluded:
            border_color = QColor(self._highlight_color)
            hover_border_color = get_selection_hover_color(border_color)
            background_color = get_selection_fill_color(border_color)
            hover_background_color = get_selection_fill_color(border_color, 68)
            icon_color = border_color
        elif self._excluded:
            text_color = QColor("#d94b5b")
            icon_color = text_color
            border_color = QColor("#7a4b51")
            hover_border_color = QColor("#d94b5b")
            background_color = QColor("#6b6f76")
            hover_background_color = background_color.lighter(110)
            text_decoration = "line-through"

        self.setIcon(category_sidebar_icon(self.item.icon, color=icon_color, size=18))
        horizontal_padding = 0 if self._collapsed else 8
        self.setStyleSheet(
            "QPushButton#category_sidebar_item {"
            f"background: rgba{background_color.toTuple()};"
            f"color: rgba{text_color.toTuple()};"
            f"border-color: rgba{border_color.toTuple()};"
            "border-style: solid;"
            "border-width: 1px;"
            "border-radius: 6px;"
            f"padding: 5px {horizontal_padding}px;"
            "text-align: left;"
            "font-weight: 600;"
            f"text-decoration: {text_decoration};"
            "}"
            "QPushButton#category_sidebar_item:hover {"
            f"background: rgba{hover_background_color.toTuple()};"
            f"border-color: rgba{hover_border_color.toTuple()};"
            "}"
            "QPushButton#category_sidebar_item:pressed {"
            "background: rgba(77, 163, 255, 60);"
            "border-color: rgba(77, 163, 255, 120);"
            "}"
        )


class CategorySidebarWidget(QFrame):
    EXPANDED_WIDTH = 200
    COLLAPSED_WIDTH = 52
    layout_state_changed = Signal()

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
        self.settings_button.clicked.connect(self.open_settings)
        self.footer_layout.addWidget(self.settings_button)

        self.collapse_button = QPushButton()
        self.collapse_button.setObjectName("category_sidebar_collapse_button")
        self.collapse_button.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.collapse_button.setToolTip("Collapse category sidebar")
        self.collapse_button.clicked.connect(self.toggle_collapsed)
        self.footer_layout.addWidget(self.collapse_button)
        self.root_layout.addWidget(self.footer)

        self._apply_style()
        self.set_settings(self.settings)

    def _apply_style(self) -> None:
        text_color = _theme_color(self, QPalette.ColorRole.WindowText)
        button_text_color = _theme_color(self.settings_button, QPalette.ColorRole.ButtonText)
        group_header_color = _with_alpha(text_color, 165)
        empty_title_color = _with_alpha(text_color, 220)
        empty_hint_color = _with_alpha(text_color, 150)

        self.settings_button.setIcon(
            category_sidebar_icon("settings", color=button_text_color, size=18)
        )
        self.setStyleSheet(
            "QFrame#category_sidebar {"
            "background: rgba(0, 0, 0, 0);"
            "border-right: 1px solid rgba(120, 128, 140, 70);"
            "}"
            "QLabel#category_sidebar_group_header {"
            f"color: rgba{group_header_color.toTuple()};"
            "font-size: 11px;"
            "font-weight: 700;"
            "padding: 6px 6px 2px 6px;"
            "}"
            "QLabel#category_sidebar_empty_title {"
            f"color: rgba{empty_title_color.toTuple()};"
            "font-weight: 700;"
            "padding: 8px 4px 0 4px;"
            "}"
            "QLabel#category_sidebar_empty_hint {"
            f"color: rgba{empty_hint_color.toTuple()};"
            "padding: 0 4px;"
            "}"
            "QFrame#category_sidebar_separator {"
            "background: rgba(120, 128, 140, 65);"
            "max-height: 1px;"
            "}"
            "QPushButton#category_sidebar_settings_button,"
            "QPushButton#category_sidebar_collapse_button {"
            "background: transparent;"
            f"color: rgba{button_text_color.toTuple()};"
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

    def set_settings(self, settings: CategorySidebarSettings) -> None:
        self.settings = settings.normalized()
        self.render()

    def toggle_collapsed(self) -> None:
        self.settings.collapsed = not self.settings.collapsed
        if self.driver.lib.library_dir:
            self.settings = self.driver.lib.set_category_sidebar_settings(self.settings)
        self.render()

    def open_settings(self) -> None:
        self.settings_modal = CategorySidebarSettingsPanel.build_modal(self.driver)
        self.settings_modal.show()

    def render(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

        collapsed = self.settings.collapsed
        self.setFixedWidth(self.target_width())
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

        self.layout_state_changed.emit()

    def target_width(self) -> int:
        return self.COLLAPSED_WIDTH if self.settings.collapsed else self.EXPANDED_WIDTH

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
            item_widget = CategorySidebarItemWidget(item, collapsed)
            tag_id = item.primary_tag_id()
            if tag_id is not None:
                item_widget.clicked.connect(
                    lambda checked=False, tag_id=tag_id: self.driver.apply_tag_filter(tag_id)
                )
                item_widget.right_clicked.connect(
                    lambda tag_id=tag_id: self.driver.apply_excluded_tag_filter(tag_id)
                )
                item_widget.set_filter_state(
                    self.driver.is_tag_filter_selected(tag_id),
                    self.driver.is_tag_filter_excluded(tag_id),
                    self.driver.get_tag_filter_highlight_color(),
                )
            elif query := item.filter_query():
                item_widget.clicked.connect(
                    lambda checked=False, query=query: self._apply_filter_query(query)
                )
                item_widget.set_filter_state(
                    self._current_filter_query() == query,
                    False,
                    self.driver.get_tag_filter_highlight_color(),
                )
            else:
                item_widget.setEnabled(False)
            self.content_layout.addWidget(item_widget)

    def _add_separator(self) -> None:
        separator = QFrame()
        separator.setObjectName("category_sidebar_separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        self.content_layout.addWidget(separator)

    def _current_filter_query(self) -> str:
        browsing_history = getattr(self.driver, "browsing_history", None)
        current = getattr(browsing_history, "current", None)
        return getattr(current, "query", "") or ""

    def _apply_filter_query(self, query: str) -> None:
        browsing_history = getattr(self.driver, "browsing_history", None)
        current = getattr(browsing_history, "current", None)
        if current is None:
            return
        self.driver.update_browsing_state(current.with_search_query(query))
