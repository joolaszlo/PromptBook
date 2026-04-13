# Copyright (C) 2025 Travis Abendshien (CyanVoxel).
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from tagstudio.core.library.alchemy.enums import FieldID


def get_field_display_name(name: str, key: str | None = None) -> str:
    """Return a user-facing field name without changing the backing field key."""
    if key == FieldID.DESCRIPTION.name:
        return "Prompt"

    return name
