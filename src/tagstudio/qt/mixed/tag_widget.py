# Copyright (C) 2025 Travis Abendshien (CyanVoxel).
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


from collections.abc import Callable
from typing import TYPE_CHECKING, override

import structlog
from PySide6.QtCore import QEvent, QObject, QRectF, QSignalBlocker, Qt, Signal
from PySide6.QtGui import (
    QAction,
    QColor,
    QEnterEvent,
    QFontMetrics,
    QMouseEvent,
    QPainter,
    QPaintEvent,
)
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from tagstudio.core.library.alchemy.enums import TagColorEnum
from tagstudio.core.library.alchemy.models import Tag
from tagstudio.qt.global_settings import DEFAULT_SELECTED_TAG_HIGHLIGHT_COLOR
from tagstudio.qt.helpers.escape_text import escape_text
from tagstudio.qt.models.palette import ColorType, get_tag_color
from tagstudio.qt.translations import Translations

logger = structlog.get_logger(__name__)

# Only import for type checking/autocompletion, will not be imported at runtime.
if TYPE_CHECKING:
    from tagstudio.core.library.alchemy.library import Library


class TagAliasWidget(QWidget):
    on_remove = Signal()

    def __init__(
        self,
        id: int | None = 0,
        alias: str | None = None,
        on_remove_callback: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self.id = id

        # if on_click_callback:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.base_layout = QHBoxLayout(self)
        self.base_layout.setObjectName("baseLayout")
        self.base_layout.setContentsMargins(0, 0, 0, 0)

        self.on_remove.connect(on_remove_callback)

        self.text_field = QLineEdit(self)
        self.text_field.textChanged.connect(self._adjust_width)

        if alias is not None:
            self.text_field.setText(alias)
        else:
            self.text_field.setText("")

        self._adjust_width()

        self.remove_button = QPushButton(self)
        self.remove_button.setFlat(True)
        self.remove_button.setText("–")
        self.remove_button.setHidden(False)
        self.remove_button.setStyleSheet(
            f"color: {get_tag_color(ColorType.PRIMARY, TagColorEnum.DEFAULT)};"
            f"background: {get_tag_color(ColorType.TEXT, TagColorEnum.DEFAULT)};"
            f"font-weight: 800;"
            f"border-radius: 4px;"
            f"border-width:0;"
            f"padding-bottom: 4px;"
            f"font-size: 14px"
        )
        self.remove_button.setMinimumSize(19, 19)
        self.remove_button.setMaximumSize(19, 19)
        self.remove_button.clicked.connect(self.on_remove.emit)

        self.base_layout.addWidget(self.remove_button)
        self.base_layout.addWidget(self.text_field)

    def _adjust_width(self):
        text = self.text_field.text() or self.text_field.placeholderText()
        font_metrics = QFontMetrics(self.text_field.font())
        text_width = font_metrics.horizontalAdvance(text) + 10  # Add padding

        # Set the minimum width of the QLineEdit
        self.text_field.setMinimumWidth(text_width)
        self.text_field.adjustSize()

    @override
    def enterEvent(self, event: QEnterEvent) -> None:
        self.update()
        return super().enterEvent(event)

    @override
    def leaveEvent(self, event: QEvent) -> None:
        self.update()
        return super().leaveEvent(event)


class SelectionDotIndicator(QWidget):
    DOT_SIZE = 6
    SPACING = 6

    def __init__(self, parent: QWidget, color: QColor) -> None:
        super().__init__(parent)
        self._color = QColor(color)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        parent.installEventFilter(self)
        self.hide()

    def set_color(self, color: QColor) -> None:
        self._color = QColor(color)
        self.update()

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.parentWidget() and event.type() in {
            QEvent.Type.FontChange,
            QEvent.Type.Resize,
            QEvent.Type.Show,
        }:
            parent = self.parentWidget()
            if parent:
                self.setGeometry(parent.rect())
        return super().eventFilter(watched, event)

    @override
    def paintEvent(self, event: QPaintEvent) -> None:
        parent = self.parentWidget()
        if not parent:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        font_metrics = QFontMetrics(parent.font())
        text_width = font_metrics.horizontalAdvance(parent.text())
        size = self.DOT_SIZE
        x = (self.width() + text_width) / 2 + self.SPACING
        y = (self.height() - size) / 2
        x = min(x, self.width() - size - self.SPACING)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(get_selection_glow_color(self._color, 255))
        painter.drawEllipse(QRectF(x, y, size, size))


class TagWidget(QWidget):
    on_remove = Signal()
    on_click = Signal()
    on_edit = Signal()
    on_right_click = Signal()

    tag: Tag | None

    def __init__(
        self,
        tag: Tag | None,
        has_edit: bool,
        has_remove: bool,
        library: "Library | None" = None,
        on_remove_callback: Callable[[], None] | None = None,
        on_click_callback: Callable[[], None] | None = None,
        on_edit_callback: Callable[[], None] | None = None,
        enable_context_menu: bool = True,
        enable_exclude_action: bool = False,
    ) -> None:
        super().__init__()
        self.tag = tag
        self.lib: Library | None = library
        self.has_edit = has_edit
        self.has_remove = has_remove
        self.enable_context_menu = enable_context_menu
        self.enable_exclude_action = enable_exclude_action
        self._selected = False
        self._category_active = False
        self._excluded = False
        self._selected_border_color = resolve_selected_tag_highlight_color()
        self._category_active_border_color = resolve_selected_tag_highlight_color()

        # if on_click_callback:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.base_layout = QVBoxLayout(self)
        self.base_layout.setObjectName("baseLayout")
        self.base_layout.setContentsMargins(0, 0, 0, 0)

        self.bg_button = QPushButton(self)
        self.bg_button.setFlat(True)
        self.bg_button.installEventFilter(self)

        # add callbacks
        if on_remove_callback is not None:
            self.on_remove.connect(on_remove_callback)
        if on_click_callback is not None:
            self.on_click.connect(on_click_callback)
        if on_edit_callback is not None:
            self.on_edit.connect(on_edit_callback)

        # add edit action
        if has_edit:
            edit_action = QAction(self)
            edit_action.setText(Translations["generic.edit"])
            edit_action.triggered.connect(self.on_edit.emit)
            if enable_context_menu:
                self.bg_button.addAction(edit_action)
        self.bg_button.setContextMenuPolicy(
            Qt.ContextMenuPolicy.ActionsContextMenu
            if enable_context_menu
            else Qt.ContextMenuPolicy.NoContextMenu
        )

        # TODO: This currently doesn't work in "Add Tag" menus. Either fix this or
        # disable it in that context.
        self.search_for_tag_action = QAction(self)
        self.search_for_tag_action.setText(Translations["tag.search_for_tag"])

        self.pinned_action = QAction(self)
        self.pinned_action.setText("Pinned")
        self.pinned_action.setCheckable(True)

        self.favorite_action = QAction(self)
        self.favorite_action.setText("Favorite")
        self.favorite_action.setCheckable(True)
        self.exclude_action = QAction(self)
        self.exclude_action.setText("Exclude from search")
        if enable_context_menu:
            self.bg_button.addAction(self.search_for_tag_action)
            self.bg_button.addAction(self.pinned_action)
            self.bg_button.addAction(self.favorite_action)
            if enable_exclude_action:
                self.bg_button.addAction(self.exclude_action)
        # add_to_search_action = QAction(self)
        # add_to_search_action.setText(Translations.translate_formatted("tag.add_to_search"))
        # self.bg_button.addAction(add_to_search_action)

        self.inner_layout = QHBoxLayout()
        self.inner_layout.setObjectName("innerLayout")
        self.inner_layout.setContentsMargins(0, 0, 0, 0)

        self.remove_button = QPushButton(self)
        self.remove_button.setFlat(True)
        self.remove_button.setText("–")
        self.remove_button.setHidden(True)
        self.remove_button.setMinimumSize(22, 22)
        self.remove_button.setMaximumSize(22, 22)
        self.remove_button.clicked.connect(self.on_remove.emit)
        self.remove_button.setHidden(True)
        self.inner_layout.addWidget(self.remove_button)
        self.inner_layout.addStretch(1)

        self.bg_button.setLayout(self.inner_layout)
        self.bg_button.setMinimumSize(44, 22)

        self.bg_button.setMinimumHeight(22)
        self.bg_button.setMaximumHeight(22)

        self.base_layout.addWidget(self.bg_button)

        # NOTE: Do this if you don't want the tag to stretch, like in a search.
        # self.bg_button.setMaximumWidth(self.bg_button.sizeHint().width())

        self.bg_button.clicked.connect(self.on_click.emit)

        self.set_tag(tag)

    def set_tag(self, tag: Tag | None) -> None:
        self.tag = tag

        if not tag:
            return

        self._apply_style()

        if self.lib:
            self.bg_button.setText(escape_text(self.lib.tag_display_name(tag)))
        else:
            self.bg_button.setText(escape_text(tag.name))

        pinned_blocker = QSignalBlocker(self.pinned_action)
        favorite_blocker = QSignalBlocker(self.favorite_action)
        self.pinned_action.setChecked(tag.pinned)
        self.favorite_action.setChecked(tag.favorite)

    def set_selected(self, selected: bool, border_color: QColor | None = None) -> None:
        self._selected = selected
        self._selected_border_color = resolve_selected_tag_highlight_color(border_color)
        if self.tag:
            self._apply_style()

    def set_category_active(self, active: bool, border_color: QColor | None = None) -> None:
        self._category_active = active
        self._category_active_border_color = resolve_selected_tag_highlight_color(border_color)
        if self.tag:
            self._apply_style()

    def set_excluded(self, excluded: bool) -> None:
        self._excluded = excluded
        if self.tag:
            self._apply_style()

    def _apply_style(self) -> None:
        tag = self.tag
        if not tag:
            return

        primary_color = get_primary_color(tag)
        border_color = (
            get_border_color(primary_color)
            if not (tag.color and tag.color.secondary and tag.color.color_border)
            else (QColor(tag.color.secondary))
        )
        highlight_color = get_highlight_color(
            primary_color
            if not (tag.color and tag.color.secondary)
            else QColor(tag.color.secondary)
        )
        text_color: QColor
        if tag.color and tag.color.secondary:
            text_color = QColor(tag.color.secondary)
        else:
            text_color = get_text_color(primary_color, highlight_color)

        effective_border_color = border_color
        hover_border_color = highlight_color
        selected_glow_color = get_selection_glow_color(self._selected_border_color)
        selected_fill_color = get_selection_fill_color(self._selected_border_color)
        selected_hover_fill_color = get_selection_fill_color(self._selected_border_color, 68)
        border_width = 2
        if self._selected:
            effective_border_color = QColor(self._selected_border_color)
            hover_border_color = get_selection_hover_color(effective_border_color)
        elif self._category_active:
            effective_border_color = QColor(self._category_active_border_color)
            hover_border_color = get_selection_hover_color(effective_border_color)
        text_decoration = "line-through" if self._excluded else "none"
        excluded_bg_color: QColor | None = None
        if self._excluded:
            text_color = QColor("#d94b5b")
            effective_border_color = QColor("#7a4b51")
            hover_border_color = QColor("#d94b5b")
            excluded_bg_color = QColor("#6b6f76")
        apply_selection_glow(
            self.bg_button,
            selected_glow_color,
            self._selected and not self._excluded,
        )

        selected_bg_color = (
            selected_fill_color if self._selected and not self._excluded else primary_color
        )
        if excluded_bg_color:
            selected_bg_color = excluded_bg_color
        hover_bg_color = (
            selected_hover_fill_color if self._selected and not self._excluded else primary_color
        )
        if excluded_bg_color:
            hover_bg_color = excluded_bg_color.lighter(110)
        self.bg_button.setStyleSheet(
            f"QPushButton{{"
            f"background: rgba{selected_bg_color.toTuple()};"
            f"color: rgba{text_color.toTuple()};"
            f"text-decoration: {text_decoration};"
            f"font-weight: 600;"
            f"border-color: rgba{effective_border_color.toTuple()};"
            f"border-radius: 6px;"
            f"border-style:solid;"
            f"border-width: {border_width}px;"
            f"padding-right: 4px;"
            f"padding-left: 4px;"
            f"font-size: 13px"
            f"}}"
            f"QPushButton::hover{{"
            f"border-color: rgba{hover_border_color.toTuple()};"
            f"background: rgba"
            f"{hover_bg_color.toTuple()};"
            f"}}"
            f"QPushButton::pressed{{"
            f"background: rgba{highlight_color.toTuple()};"
            f"color: rgba{primary_color.toTuple()};"
            f"border-color: rgba{effective_border_color.toTuple()};"
            f"}}"
            f"QPushButton::focus{{"
            f"padding-right: 0px;"
            f"padding-left: 0px;"
            f"outline-style: solid;"
            f"outline-width: 1px;"
            f"outline-radius: 4px;"
            f"outline-color: rgba{text_color.toTuple()};"
            f"}}"
        )

        self.remove_button.setStyleSheet(
            f"QPushButton{{"
            f"color: rgba{primary_color.toTuple()};"
            f"background: rgba{text_color.toTuple()};"
            f"font-weight: 800;"
            f"border-radius: 5px;"
            f"border-width: 4;"
            f"border-color: rgba(0,0,0,0);"
            f"padding-bottom: 4px;"
            f"font-size: 14px"
            f"}}"
            f"QPushButton::hover{{"
            f"background: rgba{primary_color.toTuple()};"
            f"color: rgba{text_color.toTuple()};"
            f"border-color: rgba{highlight_color.toTuple()};"
            f"border-width: 2;"
            f"border-radius: 6px;"
            f"}}"
            f"QPushButton::pressed{{"
            f"background: rgba{border_color.toTuple()};"
            f"color: rgba{highlight_color.toTuple()};"
            f"}}"
            f"QPushButton::focus{{"
            f"background: rgba{border_color.toTuple()};"
            f"outline:none;"
            f"}}"
        )

    def set_has_remove(self, has_remove: bool):
        self.has_remove = has_remove

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            watched == self.bg_button
            and not self.enable_context_menu
            and isinstance(event, QMouseEvent)
            and event.button() == Qt.MouseButton.RightButton
        ):
            if event.type() == QEvent.Type.MouseButtonRelease:
                self.on_right_click.emit()
            return True
        return super().eventFilter(watched, event)

    @override
    def enterEvent(self, event: QEnterEvent) -> None:
        if self.has_remove:
            self.remove_button.setHidden(False)
        self.update()
        return super().enterEvent(event)

    @override
    def leaveEvent(self, event: QEvent) -> None:
        if self.has_remove:
            self.remove_button.setHidden(True)
        self.update()
        return super().leaveEvent(event)


def get_primary_color(tag: Tag) -> QColor:
    primary_color = QColor(
        get_tag_color(ColorType.PRIMARY, TagColorEnum.DEFAULT)
        if not tag.color
        else tag.color.primary
    )

    return primary_color


def get_border_color(primary_color: QColor) -> QColor:
    border_color: QColor = QColor(primary_color)
    border_color.setRed(min(border_color.red() + 20, 255))
    border_color.setGreen(min(border_color.green() + 20, 255))
    border_color.setBlue(min(border_color.blue() + 20, 255))

    return border_color


def get_highlight_color(primary_color: QColor) -> QColor:
    highlight_color: QColor = QColor(primary_color)
    highlight_color = highlight_color.toHsl()
    highlight_color.setHsl(highlight_color.hue(), min(highlight_color.saturation(), 200), 225, 255)
    highlight_color = highlight_color.toRgb()

    return highlight_color


def get_selection_hover_color(selection_color: QColor) -> QColor:
    hover_color = QColor(selection_color)
    hover_color = hover_color.toHsl()
    hover_color.setHsl(
        hover_color.hue(),
        max(hover_color.saturation(), 220),
        min(max(hover_color.lightness(), 190) + 24, 255),
        255,
    )
    return hover_color.toRgb()


def get_selection_glow_color(selection_color: QColor, alpha: int = 210) -> QColor:
    glow_color = QColor(selection_color)
    glow_color = glow_color.toHsl()
    glow_color.setHsl(
        glow_color.hue(),
        max(glow_color.saturation(), 235),
        min(max(glow_color.lightness(), 205), 245),
        max(0, min(alpha, 255)),
    )
    return glow_color.toRgb()


def get_selection_fill_color(selection_color: QColor, alpha: int = 48) -> QColor:
    fill_color = get_selection_glow_color(selection_color, alpha)
    fill_color.setAlpha(max(0, min(alpha, 255)))
    return fill_color


def apply_selection_glow(widget: QWidget, color: QColor, enabled: bool) -> None:
    if not enabled:
        widget.setGraphicsEffect(None)
        return

    glow_color = QColor(color)
    glow_color.setAlpha(190)
    glow = QGraphicsDropShadowEffect(widget)
    glow.setBlurRadius(18)
    glow.setOffset(0, 0)
    glow.setColor(glow_color)
    widget.setGraphicsEffect(glow)


def reserve_selection_dot_space(widget: QPushButton) -> None:
    reserved_width = (
        widget.sizeHint().width()
        + SelectionDotIndicator.DOT_SIZE
        + (SelectionDotIndicator.SPACING * 2)
    )
    widget.setMinimumWidth(max(widget.minimumWidth(), reserved_width))


def apply_selection_dot_indicator(widget: QPushButton, color: QColor, enabled: bool) -> None:
    indicator = getattr(widget, "_selection_dot_indicator", None)
    reserve_selection_dot_space(widget)
    if indicator is None and not enabled:
        return
    if indicator is None:
        indicator = SelectionDotIndicator(widget, color)
        widget._selection_dot_indicator = indicator

    indicator.set_color(color)
    indicator.setGeometry(widget.rect())
    indicator.setVisible(enabled)
    if enabled:
        indicator.raise_()


def get_text_color(primary_color: QColor, highlight_color: QColor) -> QColor:
    # logger.info("[TagWidget] Evaluating tag text color", lightness=primary_color.lightness())
    if primary_color.lightness() > 120:
        text_color = QColor(primary_color)
        text_color = text_color.toHsl()
        text_color.setHsl(text_color.hue(), text_color.saturation(), 50, 255)
        return text_color.toRgb()
    else:
        return highlight_color


def resolve_selected_tag_highlight_color(color_value: str | QColor | None = None) -> QColor:
    color = QColor(color_value or DEFAULT_SELECTED_TAG_HIGHLIGHT_COLOR)
    if not color.isValid():
        color = QColor(DEFAULT_SELECTED_TAG_HIGHLIGHT_COLOR)
    color.setAlpha(255)
    return color
