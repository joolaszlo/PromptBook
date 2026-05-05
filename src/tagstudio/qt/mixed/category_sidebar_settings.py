# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, QSignalBlocker, Qt
from PySide6.QtGui import QColor, QDragEnterEvent, QDragMoveEvent, QDropEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QColorDialog,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tagstudio.core.library.category_sidebar import (
    CategoryFilterRule,
    CategoryGroup,
    CategoryItem,
    CategorySidebarSettings,
    FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL,
    FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY,
    FILTER_RULE_TYPE_TAG,
    FILTER_RULE_TYPE_TAG_PREFIX,
    normalize_hex_color,
)
from tagstudio.qt.category_sidebar_icons import (
    DEFAULT_CATEGORY_SIDEBAR_ICON,
    category_sidebar_icon,
    category_sidebar_icon_names,
    resolve_category_sidebar_icon_name,
)
from tagstudio.qt.translations import Translations
from tagstudio.qt.views.panel_modal import PanelModal, PanelWidget

if TYPE_CHECKING:
    from tagstudio.core.library.alchemy.models import Tag
    from tagstudio.qt.ts_qt import QtDriver


ICON_PICKER_BUTTON_SIZE = 44
ICON_PICKER_ICON_SIZE = 28
ICON_PICKER_AREA_MIN_HEIGHT = 220
ICON_PICKER_AREA_MAX_HEIGHT = 260
MULTIPLE_TAGS_LIST_MAX_HEIGHT = 150


class CategorySidebarListWidget(QListWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropOverwriteMode(False)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)


class CategorySidebarGroupListWidget(CategorySidebarListWidget):
    def __init__(self, panel: "CategorySidebarSettingsPanel") -> None:
        super().__init__()
        self.panel = panel
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if event.source() is self.panel.item_list:
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
            return
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:  # noqa: N802
        if event.source() is self.panel.item_list:
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        if event.source() is self.panel.item_list:
            target_group = self.itemAt(event.position().toPoint())
            if target_group is None:
                event.ignore()
                return

            target_group_id = target_group.data(Qt.ItemDataRole.UserRole)
            if self.panel.move_current_item_to_group(target_group_id):
                event.setDropAction(Qt.DropAction.MoveAction)
                event.accept()
                return

            event.ignore()
            return

        super().dropEvent(event)
        self.panel.sync_group_order_from_list()


class CategorySidebarItemListWidget(CategorySidebarListWidget):
    def __init__(self, panel: "CategorySidebarSettingsPanel") -> None:
        super().__init__()
        self.panel = panel
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        super().dropEvent(event)
        self.panel.sync_current_item_order_from_list()


class CategorySidebarSettingsPanel(PanelWidget):
    def __init__(self, driver: "QtDriver") -> None:
        super().__init__()
        self.driver = driver
        self.settings = CategorySidebarSettings.from_mapping(
            driver.lib.get_category_sidebar_settings().to_dict()
            if driver.lib.library_dir
            else CategorySidebarSettings().to_dict()
        )
        self._loading_details = False
        self._last_group_id: str | None = None
        self._last_item_id: str | None = None
        self._icon_buttons: dict[str, QPushButton] = {}
        self._selected_icon_name = DEFAULT_CATEGORY_SIDEBAR_ICON

        self.setMinimumSize(820, 640)
        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(0, 6, 0, 0)
        self.root_layout.setSpacing(8)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.root_layout.addWidget(self.splitter, 1)

        self._build_group_panel()
        self._build_item_panel()
        self._build_details_panel()
        self._apply_style()
        self._reload_groups()

    def parent_post_init(self) -> None:
        if not self.parent_modal:
            return

        self.apply_button = QPushButton("Apply")
        self.apply_button.setObjectName("category_sidebar_apply_button")
        self.apply_button.clicked.connect(self.apply_settings)
        save_button = getattr(self.parent_modal, "save_button", None)
        insert_index = self.parent_modal.button_layout.indexOf(save_button)
        if insert_index < 0:
            insert_index = self.parent_modal.button_layout.count()
        self.parent_modal.button_layout.insertWidget(insert_index, self.apply_button)

    def _build_group_panel(self) -> None:
        panel = QWidget()
        panel.setObjectName("category_sidebar_settings_panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title = QLabel("Category Groups")
        title.setObjectName("category_sidebar_settings_header")
        layout.addWidget(title)

        self.group_list = CategorySidebarGroupListWidget(self)
        self.group_list.setObjectName("category_sidebar_group_list")
        self.group_list.currentRowChanged.connect(self._on_group_row_changed)
        layout.addWidget(self.group_list, 1)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self.add_group_button = QPushButton("Add")
        self.add_group_button.clicked.connect(self.add_group)
        self.delete_group_button = QPushButton("Delete")
        self.delete_group_button.clicked.connect(self.delete_group)
        row.addWidget(self.add_group_button)
        row.addWidget(self.delete_group_button)
        layout.addLayout(row)

        order_row = QHBoxLayout()
        order_row.setContentsMargins(0, 0, 0, 0)
        self.group_up_button = QPushButton("Up")
        self.group_up_button.clicked.connect(lambda: self.move_group(-1))
        self.group_down_button = QPushButton("Down")
        self.group_down_button.clicked.connect(lambda: self.move_group(1))
        order_row.addWidget(self.group_up_button)
        order_row.addWidget(self.group_down_button)
        layout.addLayout(order_row)

        self.splitter.addWidget(panel)

    def _build_item_panel(self) -> None:
        panel = QWidget()
        panel.setObjectName("category_sidebar_settings_panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        title = QLabel("Categories")
        title.setObjectName("category_sidebar_settings_header")
        layout.addWidget(title)

        self.item_list = CategorySidebarItemListWidget(self)
        self.item_list.setObjectName("category_sidebar_item_list")
        self.item_list.currentRowChanged.connect(self._on_item_row_changed)
        layout.addWidget(self.item_list, 1)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        self.add_item_button = QPushButton("Add")
        self.add_item_button.clicked.connect(self.add_item)
        self.delete_item_button = QPushButton("Delete")
        self.delete_item_button.clicked.connect(self.delete_item)
        row.addWidget(self.add_item_button)
        row.addWidget(self.delete_item_button)
        layout.addLayout(row)

        order_row = QHBoxLayout()
        order_row.setContentsMargins(0, 0, 0, 0)
        self.item_up_button = QPushButton("Up")
        self.item_up_button.clicked.connect(lambda: self.move_item(-1))
        self.item_down_button = QPushButton("Down")
        self.item_down_button.clicked.connect(lambda: self.move_item(1))
        order_row.addWidget(self.item_up_button)
        order_row.addWidget(self.item_down_button)
        layout.addLayout(order_row)

        sort_row = QHBoxLayout()
        sort_row.setContentsMargins(0, 0, 0, 0)
        self.item_sort_az_button = QPushButton("Sort A-Z")
        self.item_sort_az_button.clicked.connect(
            lambda: self.sort_current_group_items(reverse=False)
        )
        self.item_sort_za_button = QPushButton("Sort Z-A")
        self.item_sort_za_button.clicked.connect(
            lambda: self.sort_current_group_items(reverse=True)
        )
        sort_row.addWidget(self.item_sort_az_button)
        sort_row.addWidget(self.item_sort_za_button)
        layout.addLayout(sort_row)

        self.splitter.addWidget(panel)

    def _build_details_panel(self) -> None:
        panel = QWidget()
        panel.setObjectName("category_sidebar_settings_panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(10)

        title = QLabel("Details")
        title.setObjectName("category_sidebar_settings_header")
        layout.addWidget(title)

        group_form = QFormLayout()
        group_form.setContentsMargins(0, 0, 0, 0)
        self.group_name_edit = QLineEdit()
        self.group_name_edit.setObjectName("category_sidebar_group_name_edit")
        self.group_name_edit.textEdited.connect(self._on_group_name_changed)
        group_form.addRow("Group Name", self.group_name_edit)
        layout.addLayout(group_form)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("category_sidebar_settings_separator")
        layout.addWidget(separator)

        self.item_details_widget = QWidget()
        item_form = QFormLayout(self.item_details_widget)
        self.item_form = item_form
        item_form.setContentsMargins(0, 0, 0, 0)
        self.item_name_edit = QLineEdit()
        self.item_name_edit.setObjectName("category_sidebar_item_name_edit")
        self.item_name_edit.textEdited.connect(self._on_item_name_changed)
        item_form.addRow("Category Name", self.item_name_edit)

        self.item_background_color_widget = QWidget()
        item_background_color_layout = QHBoxLayout(self.item_background_color_widget)
        item_background_color_layout.setContentsMargins(0, 0, 0, 0)
        item_background_color_layout.setSpacing(6)
        self.item_background_color_dialog = QColorDialog(self)
        self.item_background_color_button = QPushButton()
        self.item_background_color_button.setObjectName("category_sidebar_background_color_button")
        self.item_background_color_button.clicked.connect(self._select_item_background_color)
        item_background_color_layout.addWidget(self.item_background_color_button)
        self.item_background_color_reset_button = QPushButton(Translations["generic.reset"])
        self.item_background_color_reset_button.clicked.connect(
            self._reset_item_background_color
        )
        item_background_color_layout.addWidget(self.item_background_color_reset_button)
        item_background_color_layout.addStretch(1)
        item_form.addRow(
            Translations["category_sidebar.background_color"],
            self.item_background_color_widget,
        )

        self.rule_type_combobox = QComboBox()
        self.rule_type_combobox.setObjectName("category_sidebar_rule_type_combobox")
        self.rule_type_combobox.addItem("Single tag", FILTER_RULE_TYPE_TAG)
        self.rule_type_combobox.addItem("Tag prefix", FILTER_RULE_TYPE_TAG_PREFIX)
        self.rule_type_combobox.addItem("Multiple tags", FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY)
        self.rule_type_combobox.currentIndexChanged.connect(self._on_rule_type_changed)
        item_form.addRow("Rule Type", self.rule_type_combobox)

        self.rule_include_combobox = QComboBox()
        self.rule_include_combobox.setObjectName("category_sidebar_rule_include_combobox")
        self.rule_include_combobox.addItem("Include", True)
        self.rule_include_combobox.addItem("Exclude", False)
        self.rule_include_combobox.currentIndexChanged.connect(self._on_rule_include_changed)
        item_form.addRow("Rule State", self.rule_include_combobox)

        self.icon_picker_widget = QWidget()
        icon_picker_layout = QVBoxLayout(self.icon_picker_widget)
        icon_picker_layout.setContentsMargins(0, 0, 0, 0)
        icon_picker_layout.setSpacing(6)

        self.icon_search_edit = QLineEdit()
        self.icon_search_edit.setObjectName("category_sidebar_icon_search_edit")
        self.icon_search_edit.setPlaceholderText("Search icons")
        self.icon_search_edit.textChanged.connect(self._refresh_icon_grid)
        icon_picker_layout.addWidget(self.icon_search_edit)

        self.icon_scroll_area = QScrollArea()
        self.icon_scroll_area.setObjectName("category_sidebar_icon_scroll_area")
        self.icon_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.icon_scroll_area.setWidgetResizable(True)
        self.icon_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.icon_scroll_area.setMinimumHeight(ICON_PICKER_AREA_MIN_HEIGHT)
        self.icon_scroll_area.setMaximumHeight(ICON_PICKER_AREA_MAX_HEIGHT)

        self.icon_grid_widget = QWidget()
        self.icon_grid_widget.setObjectName("category_sidebar_icon_grid_widget")
        self.icon_grid_layout = QGridLayout(self.icon_grid_widget)
        self.icon_grid_layout.setContentsMargins(0, 0, 0, 0)
        self.icon_grid_layout.setSpacing(4)
        self.icon_scroll_area.setWidget(self.icon_grid_widget)
        icon_picker_layout.addWidget(self.icon_scroll_area)
        item_form.addRow("Icon", self.icon_picker_widget)

        self.single_tag_combobox = QComboBox()
        self.single_tag_combobox.setObjectName("category_sidebar_single_tag_combobox")
        self.single_tag_combobox.addItem("No linked tag", None)
        for tag in self._sorted_tags():
            self.single_tag_combobox.addItem(self._tag_label(tag), tag.id)
        self.single_tag_combobox.currentIndexChanged.connect(self._on_single_tag_changed)
        item_form.addRow("Linked Tag", self.single_tag_combobox)

        self.prefix_edit = QLineEdit()
        self.prefix_edit.setObjectName("category_sidebar_prefix_edit")
        self.prefix_edit.setPlaceholderText("story_")
        self.prefix_edit.textEdited.connect(self._on_prefix_changed)
        item_form.addRow("Tag Prefix", self.prefix_edit)

        self.multiple_match_combobox = QComboBox()
        self.multiple_match_combobox.setObjectName("category_sidebar_multiple_match_combobox")
        self.multiple_match_combobox.addItem(
            "Any selected tag",
            FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY,
        )
        self.multiple_match_combobox.addItem(
            "All selected tags",
            FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL,
        )
        self.multiple_match_combobox.currentIndexChanged.connect(self._on_multiple_match_changed)
        item_form.addRow("Match", self.multiple_match_combobox)

        self.multiple_tags_list = QListWidget()
        self.multiple_tags_list.setObjectName("category_sidebar_multiple_tags_list")
        self.multiple_tags_list.setMaximumHeight(MULTIPLE_TAGS_LIST_MAX_HEIGHT)
        for tag in self._sorted_tags():
            tag_item = QListWidgetItem(self._tag_label(tag))
            tag_item.setData(Qt.ItemDataRole.UserRole, tag.id)
            tag_item.setFlags(tag_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            tag_item.setCheckState(Qt.CheckState.Unchecked)
            self.multiple_tags_list.addItem(tag_item)
        self.multiple_tags_list.itemChanged.connect(self._on_multiple_tags_changed)
        item_form.addRow("Tags", self.multiple_tags_list)
        layout.addWidget(self.item_details_widget)

        self.empty_details_label = QLabel("Select a group or category to edit its details.")
        self.empty_details_label.setObjectName("category_sidebar_empty_details")
        self.empty_details_label.setWordWrap(True)
        layout.addWidget(self.empty_details_label)
        layout.addStretch(1)

        self.splitter.addWidget(panel)
        self.splitter.setSizes([180, 240, 360])

    def _apply_style(self) -> None:
        self.setStyleSheet(
            "QWidget#category_sidebar_settings_panel {"
            "background: #1a1d22;"
            "}"
            "QLabel#category_sidebar_settings_header {"
            "color: #d8dde6;"
            "font-weight: 700;"
            "font-size: 13px;"
            "padding: 2px 0 4px 0;"
            "}"
            "QLabel#category_sidebar_empty_details {"
            "color: #8f98a6;"
            "}"
            "QFrame#category_sidebar_settings_separator {"
            "background: rgba(120, 128, 140, 70);"
            "max-height: 1px;"
            "}"
            "QListWidget {"
            "background: #14171c;"
            "color: #d8dde6;"
            "border: 1px solid rgba(120, 128, 140, 80);"
            "border-radius: 6px;"
            "padding: 4px;"
            "}"
            "QListWidget::item {"
            "padding: 6px;"
            "border-radius: 4px;"
            "}"
            "QListWidget::item:selected {"
            "background: rgba(77, 163, 255, 80);"
            "color: #ffffff;"
            "}"
            "QLineEdit, QComboBox {"
            "background: #101318;"
            "color: #d8dde6;"
            "border: 1px solid rgba(120, 128, 140, 90);"
            "border-radius: 6px;"
            "padding: 5px;"
            "}"
            "QScrollArea#category_sidebar_icon_scroll_area {"
            "background: #101318;"
            "border: 1px solid rgba(120, 128, 140, 80);"
            "border-radius: 6px;"
            "}"
            "QWidget#category_sidebar_icon_grid_widget {"
            "background: #101318;"
            "}"
            "QPushButton {"
            "background: #242a32;"
            "color: #d8dde6;"
            "border: 1px solid rgba(120, 128, 140, 85);"
            "border-radius: 6px;"
            "padding: 5px 10px;"
            "}"
            "QPushButton:hover {"
            "background: #2d3540;"
            "border-color: rgba(120, 128, 140, 130);"
            "}"
            "QPushButton:disabled {"
            "color: #626a75;"
            "background: #171a1f;"
            "}"
            "QPushButton#category_sidebar_icon_button {"
            f"min-width: {ICON_PICKER_BUTTON_SIZE}px;"
            f"max-width: {ICON_PICKER_BUTTON_SIZE}px;"
            f"min-height: {ICON_PICKER_BUTTON_SIZE}px;"
            f"max-height: {ICON_PICKER_BUTTON_SIZE}px;"
            "padding: 0;"
            "}"
            "QPushButton#category_sidebar_icon_button:checked {"
            "background: rgba(77, 163, 255, 80);"
            "border-color: rgba(77, 163, 255, 170);"
            "}"
        )

    def _sorted_tags(self) -> list["Tag"]:
        return sorted(self.driver.lib.tags, key=lambda tag: self._tag_label(tag).lower())

    def _tag_label(self, tag: "Tag") -> str:
        return self.driver.lib.tag_display_name(tag)

    def _reload_groups(self, selected_group_id: str | None = None) -> None:
        selected_group_id = selected_group_id or self._last_group_id
        with QSignalBlocker(self.group_list):
            self.group_list.clear()
            for group in self.settings.groups:
                item = QListWidgetItem(group.name)
                item.setData(Qt.ItemDataRole.UserRole, group.id)
                self.group_list.addItem(item)

        selected_row = self._row_for_id(self.group_list, selected_group_id)
        if selected_row < 0 and self.group_list.count():
            selected_row = 0
        self.group_list.setCurrentRow(selected_row)
        self._on_group_row_changed(selected_row)

    def _reload_items(self, selected_item_id: str | None = None) -> None:
        selected_item_id = selected_item_id or self._last_item_id
        group = self.current_group()
        with QSignalBlocker(self.item_list):
            self.item_list.clear()
            if group:
                for item_model in group.items:
                    row = QListWidgetItem(
                        category_sidebar_icon(item_model.icon, size=18),
                        item_model.name,
                    )
                    row.setData(Qt.ItemDataRole.UserRole, item_model.id)
                    self.item_list.addItem(row)

        selected_row = self._row_for_id(self.item_list, selected_item_id)
        if selected_row < 0 and self.item_list.count():
            selected_row = 0
        self.item_list.setCurrentRow(selected_row)
        self._on_item_row_changed(selected_row)

    def _row_for_id(self, list_widget: QListWidget, model_id: str | None) -> int:
        if model_id is None:
            return -1
        for row in range(list_widget.count()):
            if list_widget.item(row).data(Qt.ItemDataRole.UserRole) == model_id:
                return row
        return -1

    def current_group(self) -> CategoryGroup | None:
        row = self.group_list.currentRow()
        if row < 0 or row >= len(self.settings.groups):
            return None
        return self.settings.groups[row]

    def current_item(self) -> CategoryItem | None:
        group = self.current_group()
        row = self.item_list.currentRow()
        if not group or row < 0 or row >= len(group.items):
            return None
        return group.items[row]

    def _on_group_row_changed(self, row: int) -> None:
        group = self.current_group()
        self._last_group_id = group.id if group else None
        self._last_item_id = None
        self._reload_items()
        self._update_details()

    def _on_item_row_changed(self, row: int) -> None:
        item = self.current_item()
        self._last_item_id = item.id if item else None
        self._update_details()

    def _update_details(self) -> None:
        self._loading_details = True
        group = self.current_group()
        item = self.current_item()

        self.group_name_edit.setEnabled(group is not None)
        self.group_name_edit.setText(group.name if group else "")

        self.item_details_widget.setVisible(item is not None)
        self.empty_details_label.setVisible(group is None)
        self.item_name_edit.setText(item.name if item else "")
        self._set_item_background_color(item.background_color if item else None, update_item=False)

        icon_name = resolve_category_sidebar_icon_name(item.icon if item else None)
        if item:
            item.icon = icon_name
        self._set_selected_icon(icon_name)

        rule = self._current_rule(item)
        rule_type = rule.type if rule else FILTER_RULE_TYPE_TAG
        if rule_type == FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL:
            rule_type_index = self.rule_type_combobox.findData(FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY)
        else:
            rule_type_index = self.rule_type_combobox.findData(rule_type)
        self.rule_type_combobox.setCurrentIndex(max(0, rule_type_index))

        include_index = self.rule_include_combobox.findData(rule.include if rule else True)
        self.rule_include_combobox.setCurrentIndex(max(0, include_index))

        tag_id = rule.tag_id if rule and rule.type == FILTER_RULE_TYPE_TAG else None
        tag_index = self.single_tag_combobox.findData(tag_id)
        self.single_tag_combobox.setCurrentIndex(tag_index if tag_index >= 0 else 0)

        self.prefix_edit.setText(
            rule.prefix if rule and rule.type == FILTER_RULE_TYPE_TAG_PREFIX and rule.prefix else ""
        )

        match_type = (
            rule.type
            if rule and rule.type == FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL
            else FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY
        )
        match_index = self.multiple_match_combobox.findData(match_type)
        self.multiple_match_combobox.setCurrentIndex(max(0, match_index))
        selected_tag_ids = set(
            rule.tag_ids
            if rule
            and rule.type
            in {FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY, FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL}
            else []
        )
        with QSignalBlocker(self.multiple_tags_list):
            for row in range(self.multiple_tags_list.count()):
                tag_item = self.multiple_tags_list.item(row)
                tag_item.setCheckState(
                    Qt.CheckState.Checked
                    if tag_item.data(Qt.ItemDataRole.UserRole) in selected_tag_ids
                    else Qt.CheckState.Unchecked
                )
        self._update_rule_editor_visibility(rule_type)

        has_group = group is not None
        has_item = item is not None
        self.delete_group_button.setEnabled(has_group)
        self.group_up_button.setEnabled(has_group and self.group_list.currentRow() > 0)
        self.group_down_button.setEnabled(
            has_group and self.group_list.currentRow() < self.group_list.count() - 1
        )
        self.add_item_button.setEnabled(has_group)
        self.delete_item_button.setEnabled(has_item)
        self.item_up_button.setEnabled(has_item and self.item_list.currentRow() > 0)
        self.item_down_button.setEnabled(
            has_item and self.item_list.currentRow() < self.item_list.count() - 1
        )
        self.item_sort_az_button.setEnabled(has_group and self.item_list.count() > 1)
        self.item_sort_za_button.setEnabled(has_group and self.item_list.count() > 1)
        self._loading_details = False

    def _current_rule(self, item: CategoryItem | None = None) -> CategoryFilterRule | None:
        item = item or self.current_item()
        if not item or not item.filter_rules:
            return None
        return item.filter_rules[0]

    def _set_current_rule(self, rule: CategoryFilterRule | None) -> None:
        item = self.current_item()
        if not item:
            return
        item.filter_rules = [rule] if rule else []

    def _tag_name_for_id(self, tag_id: int | None) -> str | None:
        if tag_id is None:
            return None
        tag = self.driver.lib.get_tag(tag_id)
        return tag.name if tag else None

    def _checked_multiple_tag_ids(self) -> list[int]:
        tag_ids: list[int] = []
        for row in range(self.multiple_tags_list.count()):
            tag_item = self.multiple_tags_list.item(row)
            if tag_item.checkState() == Qt.CheckState.Checked:
                tag_id = tag_item.data(Qt.ItemDataRole.UserRole)
                if tag_id is not None:
                    tag_ids.append(tag_id)
        return tag_ids

    def _update_rule_editor_visibility(self, rule_type: str) -> None:
        is_single_tag = rule_type == FILTER_RULE_TYPE_TAG
        is_prefix = rule_type == FILTER_RULE_TYPE_TAG_PREFIX
        is_multiple = rule_type in {
            FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY,
            FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL,
        }
        for widget, visible in (
            (self.single_tag_combobox, is_single_tag),
            (self.prefix_edit, is_prefix),
            (self.multiple_match_combobox, is_multiple),
            (self.multiple_tags_list, is_multiple),
        ):
            widget.setVisible(visible)
            if label := self.item_form.labelForField(widget):
                label.setVisible(visible)

    def _on_group_name_changed(self, text: str) -> None:
        if self._loading_details:
            return
        group = self.current_group()
        if not group:
            return
        group.name = text
        current = self.group_list.currentItem()
        if current:
            current.setText(text)

    def _on_item_name_changed(self, text: str) -> None:
        if self._loading_details:
            return
        item = self.current_item()
        if not item:
            return
        item.name = text
        current = self.item_list.currentItem()
        if current:
            current.setText(text)

    def _set_item_background_color(
        self,
        color_value: str | QColor | None,
        *,
        update_item: bool = True,
    ) -> None:
        color_hex = normalize_hex_color(
            color_value.name() if isinstance(color_value, QColor) else color_value
        )
        if update_item and not self._loading_details:
            item = self.current_item()
            if item:
                item.background_color = color_hex

        if color_hex is None:
            self.item_background_color_button.setText(Translations["color.title.no_color"])
            self.item_background_color_button.setStyleSheet(
                "QPushButton#category_sidebar_background_color_button {"
                "background: #242a32;"
                "color: #d8dde6;"
                "border: 1px solid rgba(120, 128, 140, 85);"
                "border-radius: 6px;"
                "padding: 5px 10px;"
                "font-weight: 600;"
                "}"
            )
            return

        color = QColor(color_hex)
        text_color = QColor("#101010") if color.lightness() > 150 else QColor("#f7f7f7")
        self.item_background_color_button.setText(color_hex)
        self.item_background_color_button.setStyleSheet(
            "QPushButton#category_sidebar_background_color_button {"
            f"background: rgba{color.toTuple()};"
            f"color: rgba{text_color.toTuple()};"
            f"border: 1px solid rgba{color.toTuple()};"
            "border-radius: 6px;"
            "padding: 5px 10px;"
            "font-weight: 600;"
            "}"
        )

    def _select_item_background_color(self) -> None:
        if self._loading_details or not self.current_item():
            return
        initial = QColor(self.current_item().background_color or "#4DA3FF")
        color = self.item_background_color_dialog.getColor(initial=initial)
        if color.isValid():
            self._set_item_background_color(color)

    def _reset_item_background_color(self) -> None:
        if self._loading_details or not self.current_item():
            return
        self._set_item_background_color(None)

    def _refresh_icon_grid(self) -> None:
        while self.icon_grid_layout.count():
            item = self.icon_grid_layout.takeAt(0)
            if item and item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()

        query = self.icon_search_edit.text().strip().casefold()
        matching_icon_names = [
            icon_name
            for icon_name in category_sidebar_icon_names()
            if not query or query in icon_name.casefold()
        ]
        self._icon_buttons = {}
        for index, icon_name in enumerate(matching_icon_names):
            button = QPushButton()
            button.setObjectName("category_sidebar_icon_button")
            button.setCheckable(True)
            button.setToolTip(icon_name)
            button.setIcon(category_sidebar_icon(icon_name, size=ICON_PICKER_ICON_SIZE))
            button.setIconSize(QSize(ICON_PICKER_ICON_SIZE, ICON_PICKER_ICON_SIZE))
            button.clicked.connect(lambda checked=False, name=icon_name: self.select_icon(name))
            self._icon_buttons[icon_name] = button
            self.icon_grid_layout.addWidget(button, index // 7, index % 7)

        self.icon_grid_layout.setRowStretch((len(matching_icon_names) // 7) + 1, 1)
        self._sync_icon_button_states()

    def _set_selected_icon(self, icon_name: str | None) -> None:
        self._selected_icon_name = resolve_category_sidebar_icon_name(icon_name)
        if not self._icon_buttons:
            self._refresh_icon_grid()
            return
        self._sync_icon_button_states()

    def _sync_icon_button_states(self) -> None:
        for icon_name, button in self._icon_buttons.items():
            with QSignalBlocker(button):
                button.setChecked(icon_name == self._selected_icon_name)

    def select_icon(self, icon_name: str | None) -> None:
        if self._loading_details:
            return
        item = self.current_item()
        if not item:
            return
        item.icon = resolve_category_sidebar_icon_name(icon_name)
        self._set_selected_icon(item.icon)
        current = self.item_list.currentItem()
        if current:
            current.setIcon(category_sidebar_icon(item.icon, size=18))

    def _on_rule_type_changed(self, *args) -> None:
        if self._loading_details:
            return
        rule_type = self.rule_type_combobox.currentData() or FILTER_RULE_TYPE_TAG
        self._update_rule_editor_visibility(rule_type)

        if rule_type == FILTER_RULE_TYPE_TAG:
            self._on_single_tag_changed()
        elif rule_type == FILTER_RULE_TYPE_TAG_PREFIX:
            self._on_prefix_changed(self.prefix_edit.text())
        else:
            self._on_multiple_tags_changed()

    def _on_rule_include_changed(self, *args) -> None:
        if self._loading_details:
            return
        rule = self._current_rule()
        if not rule:
            self._on_rule_type_changed()
            return
        rule.include = bool(self.rule_include_combobox.currentData())

    def _on_single_tag_changed(self, *args) -> None:
        if self._loading_details:
            return
        tag_id = self.single_tag_combobox.currentData()
        self._set_current_rule(
            CategoryFilterRule(
                type=FILTER_RULE_TYPE_TAG,
                tag_id=tag_id,
                tag_name=self._tag_name_for_id(tag_id),
                include=bool(self.rule_include_combobox.currentData()),
            )
            if tag_id is not None
            else None
        )

    def _on_prefix_changed(self, text: str) -> None:
        if self._loading_details:
            return
        prefix = text.strip()
        self._set_current_rule(
            CategoryFilterRule(
                type=FILTER_RULE_TYPE_TAG_PREFIX,
                prefix=prefix,
                include=bool(self.rule_include_combobox.currentData()),
            )
            if prefix
            else None
        )

    def _on_multiple_match_changed(self, *args) -> None:
        if self._loading_details:
            return
        self._on_multiple_tags_changed()

    def _on_multiple_tags_changed(self, *args) -> None:
        if self._loading_details:
            return
        tag_ids = self._checked_multiple_tag_ids()
        self._set_current_rule(
            CategoryFilterRule(
                type=(
                    self.multiple_match_combobox.currentData()
                    or FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY
                ),
                tag_ids=tag_ids,
                tag_names=[
                    tag_name
                    for tag_id in tag_ids
                    if (tag_name := self._tag_name_for_id(tag_id)) is not None
                ],
                include=bool(self.rule_include_combobox.currentData()),
            )
            if tag_ids
            else None
        )

    def add_group(self) -> None:
        group = CategoryGroup(order=len(self.settings.groups))
        self.settings.groups.append(group)
        self.settings.normalized()
        self._reload_groups(group.id)

    def delete_group(self) -> None:
        row = self.group_list.currentRow()
        if row < 0:
            return
        del self.settings.groups[row]
        self.settings.normalized()
        next_row = min(row, len(self.settings.groups) - 1)
        selected_group_id = self.settings.groups[next_row].id if next_row >= 0 else None
        self._reload_groups(selected_group_id)

    def move_group(self, offset: int) -> None:
        row = self.group_list.currentRow()
        new_row = row + offset
        if row < 0 or new_row < 0 or new_row >= len(self.settings.groups):
            return
        self.settings.groups[row], self.settings.groups[new_row] = (
            self.settings.groups[new_row],
            self.settings.groups[row],
        )
        for index, group in enumerate(self.settings.groups):
            group.order = index
        self.settings.normalized()
        self._reload_groups(self.settings.groups[new_row].id)

    def sync_group_order_from_list(self) -> None:
        ordered_ids = [
            self.group_list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.group_list.count())
        ]
        groups_by_id = {group.id: group for group in self.settings.groups}
        self.settings.groups = [
            groups_by_id[group_id] for group_id in ordered_ids if group_id in groups_by_id
        ]
        for index, group in enumerate(self.settings.groups):
            group.order = index
        current = self.group_list.currentItem()
        current_id = current.data(Qt.ItemDataRole.UserRole) if current else None
        self.settings.normalized()
        self._reload_groups(current_id)

    def add_item(self) -> None:
        group = self.current_group()
        if not group:
            return
        item = CategoryItem(icon=DEFAULT_CATEGORY_SIDEBAR_ICON, order=len(group.items))
        group.items.append(item)
        self.settings.normalized()
        self._reload_items(item.id)

    def delete_item(self) -> None:
        group = self.current_group()
        row = self.item_list.currentRow()
        if not group or row < 0:
            return
        del group.items[row]
        self.settings.normalized()
        next_row = min(row, len(group.items) - 1)
        selected_item_id = group.items[next_row].id if next_row >= 0 else None
        self._reload_items(selected_item_id)

    def move_item(self, offset: int) -> None:
        group = self.current_group()
        row = self.item_list.currentRow()
        new_row = row + offset
        if not group or row < 0 or new_row < 0 or new_row >= len(group.items):
            return
        group.items[row], group.items[new_row] = group.items[new_row], group.items[row]
        for index, item in enumerate(group.items):
            item.order = index
        self.settings.normalized()
        self._reload_items(group.items[new_row].id)

    def sync_current_item_order_from_list(self) -> None:
        group = self.current_group()
        if not group:
            return

        ordered_ids = [
            self.item_list.item(row).data(Qt.ItemDataRole.UserRole)
            for row in range(self.item_list.count())
        ]
        items_by_id = {item.id: item for item in group.items}
        group.items = [items_by_id[item_id] for item_id in ordered_ids if item_id in items_by_id]
        for index, item in enumerate(group.items):
            item.order = index
        self.settings.normalized()
        current = self.item_list.currentItem()
        self._reload_items(current.data(Qt.ItemDataRole.UserRole) if current else None)

    def move_current_item_to_group(self, target_group_id: str) -> bool:
        source_group = self.current_group()
        item = self.current_item()
        target_group = next(
            (group for group in self.settings.groups if group.id == target_group_id),
            None,
        )
        if not source_group or not item or not target_group or source_group.id == target_group.id:
            return False

        source_group.items = [
            candidate for candidate in source_group.items if candidate.id != item.id
        ]
        item.order = len(target_group.items)
        target_group.items.append(item)
        for group in (source_group, target_group):
            for index, group_item in enumerate(group.items):
                group_item.order = index

        self.settings.normalized()
        self._reload_groups(target_group.id)
        self._reload_items(item.id)
        return True

    def sort_current_group_items(self, *, reverse: bool) -> None:
        group = self.current_group()
        if not group:
            return

        selected_item_id = self.current_item().id if self.current_item() else None
        group.items.sort(key=lambda item: item.name.casefold(), reverse=reverse)
        for index, item in enumerate(group.items):
            item.order = index
        self.settings.normalized()
        self._reload_items(selected_item_id)

    def apply_settings(self) -> None:
        self.settings = self.settings.normalized()
        if self.driver.lib.library_dir:
            self.settings = self.driver.lib.set_category_sidebar_settings(self.settings)
        self.driver.refresh_category_sidebar()
        self._reload_groups()

    def reset(self) -> None:
        if self.driver.lib.library_dir:
            self.settings = CategorySidebarSettings.from_mapping(
                self.driver.lib.get_category_sidebar_settings().to_dict()
            )
        else:
            self.settings = CategorySidebarSettings()
        self._reload_groups()

    @classmethod
    def build_modal(cls, driver: "QtDriver") -> PanelModal:
        panel = cls(driver)
        modal = PanelModal(
            widget=panel,
            title="Category Sidebar Settings",
            done_callback=panel.apply_settings,
            has_save=True,
        )
        modal.setObjectName("category_sidebar_settings_modal")
        return modal
