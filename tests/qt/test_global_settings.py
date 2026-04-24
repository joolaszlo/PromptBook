# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


from pathlib import Path

from tagstudio.qt.global_settings import (
    DEFAULT_SELECTED_TAG_HIGHLIGHT_COLOR,
    GlobalSettings,
    Theme,
)


def test_read_settings(tmp_path: Path):
    settings_path = tmp_path / "settings.toml"
    with open(settings_path, "w") as settings_file:
        settings_file.write("""
            language = "de"
            open_last_loaded_on_startup = true
            autoplay = true
            show_filenames_in_grid = true
            page_size = 1337
            show_filepath = 0
            dark_mode = 2
            date_format = "%x"
            hour_format = true
            zero_padding = true
        """)

    settings = GlobalSettings.read_settings(settings_path)
    assert settings.language == "de"
    assert settings.open_last_loaded_on_startup
    assert settings.autoplay
    assert settings.show_filenames_in_grid
    assert settings.page_size == 1337
    assert settings.show_filepath == 0
    assert settings.theme == Theme.SYSTEM
    assert settings.date_format == "%x"
    assert settings.hour_format
    assert settings.zero_padding
    assert not settings.show_preview_created_date
    assert not settings.show_preview_modified_date
    assert not settings.show_preview_filename
    assert not settings.show_preview_media_info
    assert settings.selected_tag_highlight_color == DEFAULT_SELECTED_TAG_HIGHLIGHT_COLOR


def test_preview_metadata_settings_persist(tmp_path: Path):
    settings_path = tmp_path / "settings.toml"
    settings = GlobalSettings(loaded_from=settings_path)
    settings.show_preview_created_date = True
    settings.show_preview_modified_date = True
    settings.show_preview_filename = True
    settings.show_preview_media_info = True

    settings.save()

    saved_settings = GlobalSettings.read_settings(settings_path)
    assert saved_settings.show_preview_created_date
    assert saved_settings.show_preview_modified_date
    assert saved_settings.show_preview_filename
    assert saved_settings.show_preview_media_info


def test_selected_tag_highlight_color_persists(tmp_path: Path):
    settings_path = tmp_path / "settings.toml"
    settings = GlobalSettings(loaded_from=settings_path)
    settings.selected_tag_highlight_color = "#12ab34"

    settings.save()

    saved_settings = GlobalSettings.read_settings(settings_path)
    assert saved_settings.selected_tag_highlight_color == "#12ab34"
