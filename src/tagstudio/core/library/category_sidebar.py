# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

CATEGORY_SIDEBAR_SETTINGS_ID = 1
FILTER_RULE_TYPE_TAG = "tag"
FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY = "multiple_tags_any"
FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL = "multiple_tags_all"
_OBSOLETE_FILTER_RULE_TYPE_TAG_PREFIX = "tag_prefix"
_OBSOLETE_FILTER_RULE_TYPE_SAVED_SEARCH = "saved_search"


def _make_id() -> str:
    return str(uuid4())


def _as_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _as_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _as_bool(value: Any, fallback: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() not in {"false", "0", "no", "off"}
    if value is None:
        return fallback
    return bool(value)


def normalize_hex_color(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    color = value.strip()
    if not color:
        return None
    if color.startswith("#"):
        color = color[1:]

    if len(color) == 3 and all(char in "0123456789abcdefABCDEF" for char in color):
        return "#" + "".join(char * 2 for char in color).upper()

    if len(color) == 6 and all(char in "0123456789abcdefABCDEF" for char in color):
        return f"#{color.upper()}"

    return None


def _as_int_list(value: Any) -> list[int]:
    if not isinstance(value, list):
        return []

    out: list[int] = []
    for item in value:
        maybe_int = _as_optional_int(item)
        if maybe_int is not None:
            out.append(maybe_int)
    return out


def _next_fallback_name(base_name: str, used_names: set[str]) -> str:
    if base_name not in used_names:
        return base_name

    index = 2
    while f"{base_name} {index}" in used_names:
        index += 1
    return f"{base_name} {index}"


def _normalized_name(name: str | None, fallback_base: str, used_names: set[str]) -> str:
    stripped_name = (name or "").strip()
    if stripped_name:
        return stripped_name
    return _next_fallback_name(fallback_base, used_names)


@dataclass(frozen=True)
class CategoryTagFilter:
    tag_ids: tuple[int, ...]
    include: bool = True
    match_any: bool = False


@dataclass
class CategoryFilterRule:
    type: str
    tag_id: int | None = None
    tag_ids: list[int] = field(default_factory=list)
    tag_name: str | None = None
    tag_names: list[str] = field(default_factory=list)
    include: bool = True

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "CategoryFilterRule | None":
        rule_type = str(data.get("type") or FILTER_RULE_TYPE_TAG)
        if rule_type in {
            _OBSOLETE_FILTER_RULE_TYPE_TAG_PREFIX,
            _OBSOLETE_FILTER_RULE_TYPE_SAVED_SEARCH,
        }:
            return None
        elif rule_type not in {
            FILTER_RULE_TYPE_TAG,
            FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY,
            FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL,
        }:
            return None

        tag_name = data.get("tag_name")
        tag_names = data.get("tag_names")
        return cls(
            type=rule_type,
            tag_id=_as_optional_int(data.get("tag_id")),
            tag_ids=_as_int_list(data.get("tag_ids")),
            tag_name=str(tag_name) if tag_name is not None else None,
            tag_names=[str(name) for name in tag_names] if isinstance(tag_names, list) else [],
            include=_as_bool(data.get("include"), True),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "tag_id": self.tag_id,
            "tag_ids": self.tag_ids,
            "tag_name": self.tag_name,
            "tag_names": self.tag_names,
            "include": self.include,
        }


@dataclass
class CategoryItem:
    id: str = field(default_factory=_make_id)
    name: str = ""
    icon: str = ""
    background_color: str | None = None
    order: int = 0
    filter_rules: list[CategoryFilterRule] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: dict[str, Any], fallback_order: int) -> "CategoryItem":
        filter_rules = data.get("filter_rules")
        if not isinstance(filter_rules, list):
            filter_rules = []

        return cls(
            id=str(data.get("id") or _make_id()),
            name=str(data.get("name") or ""),
            icon=str(data.get("icon") or ""),
            background_color=normalize_hex_color(data.get("background_color")),
            order=_as_int(data.get("order"), fallback_order),
            filter_rules=[
                parsed_rule
                for rule in filter_rules
                if isinstance(rule, dict)
                if (parsed_rule := CategoryFilterRule.from_mapping(rule)) is not None
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "background_color": normalize_hex_color(self.background_color),
            "order": self.order,
            "filter_rules": [rule.to_dict() for rule in self.filter_rules],
        }

    def primary_tag_id(self) -> int | None:
        tag_filter = self.tag_filter()
        if tag_filter is None:
            return None
        if tag_filter.include and len(tag_filter.tag_ids) == 1:
            return tag_filter.tag_ids[0]
        return None

    def tag_filter(self) -> CategoryTagFilter | None:
        if len(self.filter_rules) != 1:
            return None
        rule = self.filter_rules[0]
        if rule.type == FILTER_RULE_TYPE_TAG and rule.tag_id is not None:
            return CategoryTagFilter((rule.tag_id,), rule.include)
        if rule.type == FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY and rule.tag_ids:
            return CategoryTagFilter(
                tuple(dict.fromkeys(rule.tag_ids)),
                rule.include,
                match_any=True,
            )
        if rule.type == FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL and rule.tag_ids:
            return CategoryTagFilter(tuple(dict.fromkeys(rule.tag_ids)), rule.include)
        return None


@dataclass
class CategoryGroup:
    id: str = field(default_factory=_make_id)
    name: str = ""
    order: int = 0
    items: list[CategoryItem] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: dict[str, Any], fallback_order: int) -> "CategoryGroup":
        items = data.get("items")
        if not isinstance(items, list):
            items = []

        return cls(
            id=str(data.get("id") or _make_id()),
            name=str(data.get("name") or ""),
            order=_as_int(data.get("order"), fallback_order),
            items=[
                CategoryItem.from_mapping(item, item_index)
                for item_index, item in enumerate(items)
                if isinstance(item, dict)
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "order": self.order,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass
class CategorySidebarSettings:
    collapsed: bool = False
    groups: list[CategoryGroup] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: dict[str, Any] | None) -> "CategorySidebarSettings":
        if not isinstance(data, dict):
            return cls()

        groups = data.get("groups")
        if not isinstance(groups, list):
            groups = []

        settings = cls(
            collapsed=bool(data.get("collapsed", False)),
            groups=[
                CategoryGroup.from_mapping(group, group_index)
                for group_index, group in enumerate(groups)
                if isinstance(group, dict)
            ],
        )
        return settings.normalized()

    def normalized(self) -> "CategorySidebarSettings":
        used_group_names: set[str] = set()
        groups = sorted(self.groups, key=lambda group: group.order)

        for group_order, group in enumerate(groups):
            group.order = group_order
            group.name = _normalized_name(group.name, "New Group", used_group_names)
            used_group_names.add(group.name)

            used_item_names: set[str] = set()
            group.items = sorted(group.items, key=lambda item: item.order)
            for item_order, item in enumerate(group.items):
                item.order = item_order
                item.name = _normalized_name(item.name, "New Category", used_item_names)
                used_item_names.add(item.name)
                item.icon = item.icon or ""
                item.background_color = normalize_hex_color(item.background_color)

        self.groups = groups
        return self

    def to_dict(self) -> dict[str, Any]:
        normalized = self.normalized()
        return {
            "collapsed": normalized.collapsed,
            "groups": [group.to_dict() for group in normalized.groups],
        }
