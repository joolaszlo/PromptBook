# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication, QLabel, QSizePolicy
from pytestqt.qtbot import QtBot

from tagstudio.core.library.alchemy.enums import BrowsingState
from tagstudio.core.library.alchemy.models import Tag, TagColorGroup
from tagstudio.core.library.category_sidebar import (
    CategoryFilterRule,
    CategoryGroup,
    CategoryItem,
    CategorySidebarSettings,
    FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL,
    FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY,
)
from tagstudio.qt.mixed.category_sidebar import CategorySidebarItemWidget, CategorySidebarWidget
from tagstudio.qt.mixed.category_sidebar_settings import CategorySidebarSettingsPanel


class DummyLibrary:
    def __init__(self) -> None:
        self.library_dir = Path(".")
        self.saved_settings = CategorySidebarSettings()
        person = Tag(id=1000, name="Person")
        person.color = TagColorGroup(
            slug="person",
            namespace="promptbook-test",
            name="Person",
            primary="#AA5500",
        )
        place = Tag(id=1001, name="Place")
        place.color = TagColorGroup(
            slug="place",
            namespace="promptbook-test",
            name="Place",
            primary="#3366AA",
        )
        self.tags = [person, place]

    def get_category_sidebar_settings(self) -> CategorySidebarSettings:
        return CategorySidebarSettings.from_mapping(self.saved_settings.to_dict())

    def set_category_sidebar_settings(
        self,
        settings: CategorySidebarSettings,
    ) -> CategorySidebarSettings:
        self.saved_settings = CategorySidebarSettings.from_mapping(settings.to_dict())
        return self.saved_settings

    def tag_display_name(self, tag: Tag | None) -> str:
        return tag.name if tag else "<NO TAG>"

    def get_tag(self, tag_id: int) -> Tag | None:
        for tag in self.tags:
            if tag.id == tag_id:
                return tag
        return None


class DummyDriver:
    def __init__(self) -> None:
        self.lib = DummyLibrary()
        self.included_tag_ids: set[int] = set()
        self.excluded_tag_ids: set[int] = set()
        self.category_any_tag_ids: set[int] = set()
        self.refresh_category_sidebar_count = 0
        self.browsing_history = type(
            "DummyHistory",
            (),
            {"current": BrowsingState.from_search_query("")},
        )()

    def apply_tag_filter(self, tag_id: int) -> None:
        if tag_id in self.included_tag_ids:
            self.included_tag_ids.remove(tag_id)
        else:
            self.excluded_tag_ids.discard(tag_id)
            self.included_tag_ids.add(tag_id)

    def apply_category_sidebar_tag_filter(self, tag_id: int) -> None:
        self.apply_category_sidebar_tag_filters([tag_id])

    def apply_category_sidebar_tag_filters(
        self, tag_ids: list[int] | tuple[int, ...], *, include: bool = True
    ) -> None:
        tag_ids_set = set(tag_ids)
        if include:
            self.category_any_tag_ids.clear()
            if self.included_tag_ids == tag_ids_set:
                self.included_tag_ids.clear()
            else:
                self.included_tag_ids = tag_ids_set
                self.excluded_tag_ids.difference_update(tag_ids_set)
        elif tag_ids_set.issubset(self.excluded_tag_ids):
            self.excluded_tag_ids.difference_update(tag_ids_set)
        else:
            self.included_tag_ids.difference_update(tag_ids_set)
            self.excluded_tag_ids.update(tag_ids_set)

    def apply_category_sidebar_any_tag_filters(
        self, tag_ids: list[int] | tuple[int, ...]
    ) -> None:
        tag_ids_set = set(tag_ids)
        if self.category_any_tag_ids == tag_ids_set:
            self.category_any_tag_ids.clear()
        else:
            self.category_any_tag_ids = tag_ids_set
            self.excluded_tag_ids.difference_update(tag_ids_set)

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

    def is_category_sidebar_tag_filter_selected(
        self, tag_ids: list[int] | tuple[int, ...], *, include: bool = True
    ) -> bool:
        tag_ids_set = set(tag_ids)
        selected_ids = self.included_tag_ids if include else self.excluded_tag_ids
        return bool(tag_ids_set) and tag_ids_set.issubset(selected_ids)

    def is_category_sidebar_any_tag_filter_selected(
        self, tag_ids: list[int] | tuple[int, ...]
    ) -> bool:
        tag_ids_set = set(tag_ids)
        return bool(tag_ids_set) and self.category_any_tag_ids == tag_ids_set

    def get_tag_filter_highlight_color(self) -> QColor:
        return QColor("#4da3ff")

    def refresh_category_sidebar(self) -> None:
        self.refresh_category_sidebar_count += 1

    def update_browsing_state(self, state: BrowsingState) -> None:
        self.browsing_history.current = state


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


def make_two_category_settings() -> CategorySidebarSettings:
    settings = make_settings()
    settings.groups[0].items.append(
        CategoryItem(
            id="item-2",
            name="Item 2",
            icon="tag",
            order=1,
            filter_rules=[CategoryFilterRule(type="tag", tag_id=1001)],
        )
    )
    return settings


def test_category_sidebar_empty_state(qtbot: QtBot):
    driver = DummyDriver()
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)

    assert "No category groups yet" in [label.text() for label in sidebar.findChildren(QLabel)]


def test_category_sidebar_renders_items_and_collapses(qtbot: QtBot):
    driver = DummyDriver()
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)

    settings = make_settings()
    settings.groups[0].items[0].background_color = "#123456"
    sidebar.set_settings(settings)

    item = sidebar.findChild(CategorySidebarItemWidget)
    assert item is not None
    assert item.contextMenuPolicy() == Qt.ContextMenuPolicy.NoContextMenu
    assert item.text() == "Item"
    assert "background: rgba(18, 52, 86, 255);" in item.styleSheet()

    sidebar.toggle_collapsed()

    assert driver.lib.saved_settings is not None
    assert driver.lib.saved_settings.collapsed is True
    collapsed_item = sidebar.findChild(CategorySidebarItemWidget)
    assert collapsed_item.text() == ""
    assert collapsed_item.width() == CategorySidebarItemWidget.COLLAPSED_SIZE
    assert collapsed_item.height() == CategorySidebarItemWidget.COLLAPSED_SIZE
    assert collapsed_item.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Fixed
    assert "background: rgba(18, 52, 86, 255);" in collapsed_item.styleSheet()
    assert "text-align: center;" in collapsed_item.styleSheet()


def test_category_sidebar_uses_restart_palette_text_colors(qtbot: QtBot):
    app = QApplication.instance()
    assert app is not None
    original_palette = QPalette(app.palette())

    def render_with_text_color(color: QColor, background_color: QColor) -> tuple[str, str]:
        palette = QPalette(original_palette)
        palette.setColor(QPalette.ColorRole.Window, background_color)
        palette.setColor(QPalette.ColorRole.Button, background_color)
        palette.setColor(QPalette.ColorRole.WindowText, color)
        palette.setColor(QPalette.ColorRole.ButtonText, color)
        app.setPalette(palette)

        sidebar = CategorySidebarWidget(DummyDriver())
        qtbot.addWidget(sidebar)
        sidebar.set_settings(make_settings())
        item = sidebar.findChild(CategorySidebarItemWidget)
        assert item is not None
        return sidebar.styleSheet(), item.styleSheet()

    try:
        dark_sidebar_style, dark_item_style = render_with_text_color(
            QColor("#d8dde6"), QColor("#1e1e1e")
        )
        light_sidebar_style, light_item_style = render_with_text_color(
            QColor("#202124"), QColor("#ffffff")
        )
        restored_dark_sidebar_style, restored_dark_item_style = render_with_text_color(
            QColor("#d8dde6"), QColor("#1e1e1e")
        )
    finally:
        app.setPalette(original_palette)

    assert "color: rgba(216, 221, 230, 255);" in dark_item_style
    assert "color: rgba(216, 221, 230, 165);" in dark_sidebar_style
    assert "color: rgba(32, 33, 36, 255);" in light_item_style
    assert "color: rgba(32, 33, 36, 165);" in light_sidebar_style
    assert "color: rgba(216, 221, 230, 255);" in restored_dark_item_style
    assert "color: rgba(216, 221, 230, 165);" in restored_dark_sidebar_style


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


def test_category_sidebar_include_is_single_select_and_exclude_stays_multi(qtbot: QtBot):
    driver = DummyDriver()
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)
    sidebar.set_settings(make_two_category_settings())
    items = sidebar.findChildren(CategorySidebarItemWidget)
    assert len(items) == 2

    qtbot.mouseClick(items[0], Qt.MouseButton.LeftButton)
    assert driver.included_tag_ids == {1000}
    assert driver.excluded_tag_ids == set()

    qtbot.mouseClick(items[1], Qt.MouseButton.LeftButton)
    assert driver.included_tag_ids == {1001}
    assert driver.excluded_tag_ids == set()

    qtbot.mouseClick(items[1], Qt.MouseButton.LeftButton)
    assert driver.included_tag_ids == set()
    assert driver.excluded_tag_ids == set()

    qtbot.mouseClick(items[0], Qt.MouseButton.RightButton)
    qtbot.mouseClick(items[1], Qt.MouseButton.RightButton)
    assert driver.included_tag_ids == set()
    assert driver.excluded_tag_ids == {1000, 1001}

    qtbot.mouseClick(items[0], Qt.MouseButton.LeftButton)
    assert driver.included_tag_ids == {1000}
    assert driver.excluded_tag_ids == {1001}


def test_category_sidebar_excluded_state_has_visible_border_with_background(qtbot: QtBot):
    driver = DummyDriver()
    settings = make_settings()
    settings.groups[0].items[0].background_color = "#123456"
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)
    sidebar.set_settings(settings)

    item = sidebar.findChild(CategorySidebarItemWidget)
    assert item is not None
    item.set_filter_state(False, True, QColor("#4da3ff"))

    assert "background: rgba(18, 52, 86, 255);" in item.styleSheet()
    assert "border-color: rgba(229, 57, 70, 255);" in item.styleSheet()
    assert "border-width: 2px;" in item.styleSheet()
    assert "text-decoration: line-through;" in item.styleSheet()

    settings.collapsed = True
    sidebar.set_settings(settings)
    collapsed_item = sidebar.findChild(CategorySidebarItemWidget)
    assert collapsed_item is not None
    collapsed_item.set_filter_state(False, True, QColor("#4da3ff"))

    assert collapsed_item.width() == CategorySidebarItemWidget.COLLAPSED_SIZE
    assert collapsed_item.height() == CategorySidebarItemWidget.COLLAPSED_SIZE
    assert "background: rgba(18, 52, 86, 255);" in collapsed_item.styleSheet()
    assert "border-color: rgba(229, 57, 70, 255);" in collapsed_item.styleSheet()
    assert "border-width: 2px;" in collapsed_item.styleSheet()


def test_category_sidebar_multi_tag_clicks_use_tag_filter_state(qtbot: QtBot):
    driver = DummyDriver()
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)
    sidebar.set_settings(
        CategorySidebarSettings(
            groups=[
                CategoryGroup(
                    name="Group",
                    items=[
                        CategoryItem(
                            name="People",
                            filter_rules=[
                                CategoryFilterRule(
                                    type=FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL,
                                    tag_ids=[1000, 1001],
                                    include=True,
                                )
                            ],
                        )
                    ],
                )
            ]
        )
    )

    item = sidebar.findChild(CategorySidebarItemWidget)
    assert item is not None

    qtbot.mouseClick(item, Qt.MouseButton.LeftButton)
    assert driver.included_tag_ids == {1000, 1001}
    assert driver.excluded_tag_ids == set()

    qtbot.mouseClick(item, Qt.MouseButton.LeftButton)
    assert driver.included_tag_ids == set()
    assert driver.excluded_tag_ids == set()


def test_category_sidebar_any_multi_tag_clicks_use_category_any_state(qtbot: QtBot):
    driver = DummyDriver()
    sidebar = CategorySidebarWidget(driver)
    qtbot.addWidget(sidebar)
    sidebar.set_settings(
        CategorySidebarSettings(
            groups=[
                CategoryGroup(
                    name="Group",
                    items=[
                        CategoryItem(
                            name="People",
                            filter_rules=[
                                CategoryFilterRule(
                                    type=FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY,
                                    tag_ids=[1000, 1001],
                                    include=True,
                                )
                            ],
                        )
                    ],
                )
            ]
        )
    )

    item = sidebar.findChild(CategorySidebarItemWidget)
    assert item is not None

    qtbot.mouseClick(item, Qt.MouseButton.LeftButton)
    assert driver.category_any_tag_ids == {1000, 1001}
    assert driver.included_tag_ids == set()
    assert driver.excluded_tag_ids == set()

    qtbot.mouseClick(item, Qt.MouseButton.LeftButton)
    assert driver.category_any_tag_ids == set()
    assert driver.included_tag_ids == set()
    assert driver.excluded_tag_ids == set()


def test_category_sidebar_settings_adds_group_and_item(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_item()

    panel.group_name_edit.clear()
    panel._on_group_name_changed("")
    panel.item_name_edit.clear()
    panel._on_item_name_changed("")
    panel._set_item_background_color("#445566")
    panel.select_icon("camera")
    panel.single_tag_combobox.setCurrentIndex(panel.single_tag_combobox.findData(1000))
    panel.apply_settings()

    settings = driver.lib.saved_settings
    assert driver.refresh_category_sidebar_count == 1
    assert [group.name for group in settings.groups] == ["New Group"]
    assert [item.name for item in settings.groups[0].items] == ["New Category"]
    assert settings.groups[0].items[0].icon == "camera"
    assert settings.groups[0].items[0].background_color == "#445566"
    assert settings.groups[0].items[0].filter_rules[0].tag_id == 1000


def test_category_sidebar_settings_auto_fills_color_from_single_linked_tag(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_item()

    assert panel.current_item().background_color is None

    panel.single_tag_combobox.setCurrentIndex(panel.single_tag_combobox.findData(1000))

    assert panel.current_item().background_color == "#AA5500"
    assert panel.item_background_color_button.text() == "#AA5500"


def test_category_sidebar_settings_auto_color_uses_first_added_multiple_tag(
    qtbot: QtBot,
):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_item()
    panel.rule_type_combobox.setCurrentIndex(
        panel.rule_type_combobox.findData(FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY)
    )

    panel.multiple_tags_list.item(1).setCheckState(Qt.CheckState.Checked)
    panel.multiple_tags_list.item(0).setCheckState(Qt.CheckState.Checked)

    rule = panel.current_item().filter_rules[0]
    assert rule.tag_ids == [1000, 1001]
    assert panel.current_item().background_color == "#3366AA"
    assert panel.item_background_color_button.text() == "#3366AA"


def test_category_sidebar_settings_auto_color_does_not_replace_existing_color(
    qtbot: QtBot,
):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_item()
    panel._set_item_background_color("#445566")

    panel.single_tag_combobox.setCurrentIndex(panel.single_tag_combobox.findData(1000))
    panel.rule_type_combobox.setCurrentIndex(
        panel.rule_type_combobox.findData(FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY)
    )
    panel.multiple_tags_list.item(1).setCheckState(Qt.CheckState.Checked)

    assert panel.current_item().background_color == "#445566"
    assert panel.item_background_color_button.text() == "#445566"


def test_category_sidebar_settings_does_not_offer_obsolete_prefix_mode(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    assert panel.rule_type_combobox.findText("Tag prefix") == -1
    assert not hasattr(panel, "prefix_edit")
    assert hasattr(panel, "multiple_match_combobox")


def test_category_sidebar_settings_builds_multiple_tag_rule(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_item()
    panel.rule_type_combobox.setCurrentIndex(
        panel.rule_type_combobox.findData(FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY)
    )
    panel.multiple_tags_list.item(0).setCheckState(Qt.CheckState.Checked)
    panel.multiple_tags_list.item(1).setCheckState(Qt.CheckState.Checked)
    panel.apply_settings()

    rule = driver.lib.saved_settings.groups[0].items[0].filter_rules[0]
    assert rule.type == FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY
    assert rule.tag_ids == [1000, 1001]

    panel.multiple_match_combobox.setCurrentIndex(
        panel.multiple_match_combobox.findData(FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL)
    )
    panel.apply_settings()

    rule = driver.lib.saved_settings.groups[0].items[0].filter_rules[0]
    assert rule.type == FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL
    assert rule.tag_ids == [1000, 1001]


def test_category_sidebar_settings_icon_picker_search_and_fallback(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_item()

    assert "tag" in panel._icon_buttons
    assert "alarm-clock" not in panel._icon_buttons

    panel.icon_search_edit.setText("cam")

    assert "camera" in panel._icon_buttons
    assert "tag" not in panel._icon_buttons
    assert panel.icon_scroll_area.minimumHeight() == 220
    assert panel.icon_scroll_area.maximumHeight() == 260
    assert panel._icon_buttons["camera"].iconSize().width() == 28

    panel.icon_search_edit.setText("alarm-clock")
    assert "alarm-clock" in panel._icon_buttons
    panel.select_icon("alarm-clock")
    assert panel.current_item().icon == "alarm-clock"
    panel.apply_settings()

    reopened_panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(reopened_panel)
    assert reopened_panel.current_item().icon == "alarm-clock"
    assert reopened_panel._selected_icon_name == "alarm-clock"

    panel.select_icon("missing-icon")
    assert panel.current_item().icon == "tag"


def test_category_sidebar_settings_layout_has_more_room(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    assert panel.minimumHeight() >= 640
    assert panel.multiple_tags_list.maximumHeight() == 150


def test_category_sidebar_settings_persists_order(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_group()
    panel.move_group(-1)
    panel.add_item()
    panel.add_item()
    panel.move_item(-1)
    panel.apply_settings()

    settings = driver.lib.saved_settings
    assert [group.name for group in settings.groups] == ["New Group 2", "New Group"]
    assert [group.order for group in settings.groups] == [0, 1]
    assert [item.name for item in settings.groups[0].items] == [
        "New Category 2",
        "New Category",
    ]
    assert [item.order for item in settings.groups[0].items] == [0, 1]


def test_category_sidebar_settings_syncs_dragged_group_order(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_group()
    moved = panel.group_list.takeItem(1)
    panel.group_list.insertItem(0, moved)
    panel.group_list.setCurrentRow(0)
    panel.sync_group_order_from_list()
    panel.apply_settings()

    settings = driver.lib.saved_settings
    assert [group.name for group in settings.groups] == ["New Group 2", "New Group"]
    assert [group.order for group in settings.groups] == [0, 1]


def test_category_sidebar_settings_syncs_dragged_item_order(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_item()
    panel.add_item()
    moved = panel.item_list.takeItem(1)
    panel.item_list.insertItem(0, moved)
    panel.item_list.setCurrentRow(0)
    panel.sync_current_item_order_from_list()
    panel.apply_settings()

    settings = driver.lib.saved_settings
    assert [item.name for item in settings.groups[0].items] == [
        "New Category 2",
        "New Category",
    ]
    assert [item.order for item in settings.groups[0].items] == [0, 1]


def test_category_sidebar_settings_moves_item_between_groups(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    first_group_id = panel.current_group().id
    panel.add_item()
    panel.item_name_edit.setText("Subject")
    panel._on_item_name_changed("Subject")
    panel.single_tag_combobox.setCurrentIndex(panel.single_tag_combobox.findData(1000))
    panel.add_group()
    second_group_id = panel.current_group().id
    panel.group_list.setCurrentRow(0)
    panel.item_list.setCurrentRow(0)

    assert panel.move_current_item_to_group(second_group_id)
    panel.apply_settings()

    settings = driver.lib.saved_settings
    first_group = next(group for group in settings.groups if group.id == first_group_id)
    second_group = next(group for group in settings.groups if group.id == second_group_id)
    assert first_group.items == []
    assert [item.name for item in second_group.items] == ["Subject"]
    assert second_group.items[0].filter_rules[0].tag_id == 1000


def test_category_sidebar_settings_sorts_selected_group_items(qtbot: QtBot):
    driver = DummyDriver()
    panel = CategorySidebarSettingsPanel(driver)
    qtbot.addWidget(panel)

    panel.add_group()
    panel.add_item()
    panel.item_name_edit.setText("Beta")
    panel._on_item_name_changed("Beta")
    panel.add_item()
    panel.item_name_edit.setText("Alpha")
    panel._on_item_name_changed("Alpha")

    panel.sort_current_group_items(reverse=False)
    assert [item.name for item in panel.current_group().items] == ["Alpha", "Beta"]

    panel.sort_current_group_items(reverse=True)
    assert [item.name for item in panel.current_group().items] == ["Beta", "Alpha"]
