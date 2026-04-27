# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSignalBlocker, Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from tagstudio.core.library.category_sidebar import (
    CategoryFilterRule,
    CategoryGroup,
    CategoryItem,
    CategorySidebarSettings,
)
from tagstudio.qt.category_sidebar_icons import (
    DEFAULT_CATEGORY_SIDEBAR_ICON,
    category_sidebar_icon,
    category_sidebar_icon_names,
)
from tagstudio.qt.views.panel_modal import PanelModal, PanelWidget

if TYPE_CHECKING:
    from tagstudio.core.library.alchemy.models import Tag
    from tagstudio.qt.ts_qt import QtDriver


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

        self.setMinimumSize(780, 500)
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

        self.group_list = QListWidget()
        self.group_list.setObjectName("category_sidebar_group_list")
        self.group_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
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

        self.item_list = QListWidget()
        self.item_list.setObjectName("category_sidebar_item_list")
        self.item_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
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
        item_form.setContentsMargins(0, 0, 0, 0)
        self.item_name_edit = QLineEdit()
        self.item_name_edit.setObjectName("category_sidebar_item_name_edit")
        self.item_name_edit.textEdited.connect(self._on_item_name_changed)
        item_form.addRow("Category Name", self.item_name_edit)

        self.icon_combobox = QComboBox()
        self.icon_combobox.setObjectName("category_sidebar_icon_combobox")
        for icon_name in category_sidebar_icon_names():
            self.icon_combobox.addItem(
                category_sidebar_icon(icon_name, size=18),
                icon_name,
                icon_name,
            )
        self.icon_combobox.currentIndexChanged.connect(self._on_icon_changed)
        item_form.addRow("Icon", self.icon_combobox)

        self.tag_combobox = QComboBox()
        self.tag_combobox.setObjectName("category_sidebar_tag_combobox")
        self.tag_combobox.addItem("No linked tag", None)
        for tag in self._sorted_tags():
            self.tag_combobox.addItem(self._tag_label(tag), tag.id)
        self.tag_combobox.currentIndexChanged.connect(self._on_tag_changed)
        item_form.addRow("Linked Tag", self.tag_combobox)
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

        icon_name = item.icon if item and item.icon else DEFAULT_CATEGORY_SIDEBAR_ICON
        icon_index = self.icon_combobox.findData(icon_name)
        if icon_index < 0:
            icon_index = self.icon_combobox.findData(DEFAULT_CATEGORY_SIDEBAR_ICON)
        self.icon_combobox.setCurrentIndex(max(0, icon_index))

        tag_id = self._tag_id_for_item(item)
        tag_index = self.tag_combobox.findData(tag_id)
        self.tag_combobox.setCurrentIndex(tag_index if tag_index >= 0 else 0)

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
        self._loading_details = False

    def _tag_id_for_item(self, item: CategoryItem | None) -> int | None:
        if not item:
            return None
        for rule in item.filter_rules:
            if rule.type == "tag":
                return rule.tag_id
        return None

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

    def _on_icon_changed(self) -> None:
        if self._loading_details:
            return
        item = self.current_item()
        if not item:
            return
        item.icon = self.icon_combobox.currentData() or DEFAULT_CATEGORY_SIDEBAR_ICON
        current = self.item_list.currentItem()
        if current:
            current.setIcon(category_sidebar_icon(item.icon, size=18))

    def _on_tag_changed(self) -> None:
        if self._loading_details:
            return
        item = self.current_item()
        if not item:
            return
        tag_id = self.tag_combobox.currentData()
        tag = self.driver.lib.get_tag(tag_id) if tag_id is not None else None
        item.filter_rules = (
            [
                CategoryFilterRule(
                    type="tag",
                    tag_id=tag_id,
                    tag_name=tag.name if tag else None,
                )
            ]
            if tag_id is not None
            else []
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
