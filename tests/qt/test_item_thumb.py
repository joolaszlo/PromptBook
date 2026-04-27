# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


from pathlib import Path

import pytest

from tagstudio.core.library.alchemy.enums import ItemType
from tagstudio.qt.mixed.item_thumb import BadgeType, ItemThumb
from tagstudio.qt.ts_qt import QtDriver


@pytest.mark.parametrize("new_value", (True, False))
def test_badge_visual_state(qt_driver: QtDriver, entry_min: int, new_value: bool):
    thumb = ItemThumb(
        ItemType.ENTRY, qt_driver.lib, qt_driver, (100, 100), show_filename_label=False
    )

    qt_driver.frame_content = [entry_min]
    qt_driver.toggle_item_selection(0, append=False, bridge=False)

    thumb.badges[BadgeType.FAVORITE].setChecked(new_value)
    assert thumb.badges[BadgeType.FAVORITE].isChecked() == new_value
    # TODO
    # assert thumb.favorite_badge.isHidden() == initial_state
    assert thumb.is_favorite == new_value


def test_video_extension_does_not_show_duration_badge(qt_driver: QtDriver):
    thumb = ItemThumb(
        ItemType.ENTRY, qt_driver.lib, qt_driver, (100, 100), show_filename_label=False
    )

    thumb.set_extension(Path("example.mp4"))

    assert thumb.ext_badge.isHidden() is False
    assert thumb.count_badge.isHidden() is True


def test_image_extension_badges_are_unchanged(qt_driver: QtDriver):
    thumb = ItemThumb(
        ItemType.ENTRY, qt_driver.lib, qt_driver, (100, 100), show_filename_label=False
    )

    thumb.set_extension(Path("example.png"))

    assert thumb.ext_badge.isHidden() is True
    assert thumb.count_badge.isHidden() is True
