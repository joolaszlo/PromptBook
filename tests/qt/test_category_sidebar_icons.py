# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from PySide6.QtGui import QIcon
from pytestqt.qtbot import QtBot

from tagstudio.qt.category_sidebar_icons import (
    CATEGORY_SIDEBAR_ICONS,
    DEFAULT_CATEGORY_SIDEBAR_ICON,
    category_sidebar_icon,
    category_sidebar_icon_names,
    category_sidebar_icon_pixmap,
    resolve_category_sidebar_icon_name,
)


def test_category_sidebar_icon_registry_contains_expected_names():
    assert len(CATEGORY_SIDEBAR_ICONS) >= 40
    assert "tag" in CATEGORY_SIDEBAR_ICONS
    assert "circle-slash" in CATEGORY_SIDEBAR_ICONS
    assert category_sidebar_icon_names() == CATEGORY_SIDEBAR_ICONS


def test_resolve_category_sidebar_icon_name_falls_back_to_tag():
    assert resolve_category_sidebar_icon_name("camera") == "camera"
    assert resolve_category_sidebar_icon_name(" CAMERA ") == "camera"
    assert resolve_category_sidebar_icon_name("missing-icon") == DEFAULT_CATEGORY_SIDEBAR_ICON
    assert resolve_category_sidebar_icon_name(None) == DEFAULT_CATEGORY_SIDEBAR_ICON


def test_category_sidebar_icon_helper_returns_renderable_icon(qtbot: QtBot):
    icon = category_sidebar_icon("missing-icon", size=24)
    pixmap = category_sidebar_icon_pixmap("camera", color="#ffffff", size=24)

    assert isinstance(icon, QIcon)
    assert not icon.isNull()
    assert not pixmap.isNull()
    assert pixmap.width() == 24
    assert pixmap.height() == 24
