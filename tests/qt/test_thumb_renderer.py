# Copyright (C) 2026
# Licensed under the GPL-3.0 License.

from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from pytestqt.qtbot import QtBot

from tagstudio.qt.previews.renderer import ThumbRenderer


@pytest.mark.parametrize("color_scheme", (Qt.ColorScheme.Dark, Qt.ColorScheme.Light))
def test_text_entry_grid_thumbnail_background_is_rounded(
    qtbot: QtBot, color_scheme: Qt.ColorScheme
):
    style_hints = QGuiApplication.styleHints()
    original_scheme = style_hints.colorScheme()
    style_hints.setColorScheme(color_scheme)

    try:
        driver = SimpleNamespace(
            settings=SimpleNamespace(
                cached_thumb_resolution=512,
                title_overlay_font_size_adjust=0,
            ),
            cache_manager=None,
        )
        renderer = ThumbRenderer(driver)  # pyright: ignore[reportArgumentType]

        with qtbot.waitSignal(renderer.updated, timeout=1000) as blocker:
            renderer.render(
                timestamp=0,
                filepath=Path("."),
                base_size=(128, 128),
                pixel_ratio=1,
                is_grid_thumb=True,
                title="Rounded Text Entry",
                is_text_entry=True,
            )

        image = blocker.args[1].toImage()
        assert image.pixelColor(0, 0).alpha() == 0
        assert image.pixelColor(image.width() - 1, 0).alpha() == 0
        assert image.pixelColor(0, image.height() - 1).alpha() == 0
        assert image.pixelColor(image.width() - 1, image.height() - 1).alpha() == 0
        assert image.pixelColor(image.width() // 2, image.height() // 2).alpha() == 255
    finally:
        style_hints.setColorScheme(original_scheme)
