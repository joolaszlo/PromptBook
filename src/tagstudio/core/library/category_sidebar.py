# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

CATEGORY_SIDEBAR_SETTINGS_ID = 1
FILTER_RULE_TYPE_TAG = "tag"
FILTER_RULE_TYPE_TAG_PREFIX = "tag_prefix"
FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY = "multiple_tags_any"
FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL = "multiple_tags_all"
FILTER_RULE_TYPE_SAVED_SEARCH = "saved_search"


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


def _query_literal(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _tag_term(tag_id: int | None, tag_name: str | None = None) -> str:
    if tag_id is not None:
        return f"tag_id:{tag_id}"
    if tag_name:
        return f"tag:{_query_literal(tag_name)}"
    return ""


def _apply_rule_include(term: str, include: bool) -> str:
    return term if include else f"not {term}"


@dataclass
class CategoryFilterRule:
    type: str
    tag_id: int | None = None
    tag_ids: list[int] = field(default_factory=list)
    tag_name: str | None = None
    tag_names: list[str] = field(default_factory=list)
    prefix: str | None = None
    include: bool = True
    saved_search: str | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, Any]) -> "CategoryFilterRule":
        tag_name = data.get("tag_name")
        tag_names = data.get("tag_names")
        prefix = data.get("prefix")
        saved_search = data.get("saved_search")
        return cls(
            type=str(data.get("type") or "tag"),
            tag_id=_as_optional_int(data.get("tag_id")),
            tag_ids=_as_int_list(data.get("tag_ids")),
            tag_name=str(tag_name) if tag_name is not None else None,
            tag_names=[str(name) for name in tag_names] if isinstance(tag_names, list) else [],
            prefix=str(prefix) if prefix is not None else None,
            include=_as_bool(data.get("include"), True),
            saved_search=str(saved_search) if saved_search is not None else None,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "tag_id": self.tag_id,
            "tag_ids": self.tag_ids,
            "tag_name": self.tag_name,
            "tag_names": self.tag_names,
            "prefix": self.prefix,
            "include": self.include,
            "saved_search": self.saved_search,
        }

    def to_query(self) -> str:
        if self.type == FILTER_RULE_TYPE_TAG:
            return _apply_rule_include(_tag_term(self.tag_id, self.tag_name), self.include)

        if self.type == FILTER_RULE_TYPE_TAG_PREFIX:
            prefix = (self.prefix or "").strip()
            if not prefix:
                return ""
            return _apply_rule_include(f"tag:{_query_literal(f'{prefix}%')}", self.include)

        if self.type in {FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY, FILTER_RULE_TYPE_MULTIPLE_TAGS_ALL}:
            terms = [
                _tag_term(tag_id, self.tag_names[index] if index < len(self.tag_names) else None)
                for index, tag_id in enumerate(self.tag_ids)
            ]
            terms = [term for term in terms if term]
            if not terms:
                return ""
            operator = " or " if self.type == FILTER_RULE_TYPE_MULTIPLE_TAGS_ANY else " "
            term = f"({operator.join(terms)})" if len(terms) > 1 else terms[0]
            return _apply_rule_include(term, self.include)

        if self.type == FILTER_RULE_TYPE_SAVED_SEARCH and self.saved_search:
            term = f"({self.saved_search})"
            return _apply_rule_include(term, self.include)

        return ""


@dataclass
class CategoryItem:
    id: str = field(default_factory=_make_id)
    name: str = ""
    icon: str = ""
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
            order=_as_int(data.get("order"), fallback_order),
            filter_rules=[
                CategoryFilterRule.from_mapping(rule)
                for rule in filter_rules
                if isinstance(rule, dict)
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "order": self.order,
            "filter_rules": [rule.to_dict() for rule in self.filter_rules],
        }

    def filter_query(self) -> str:
        return " ".join(
            rule_query for rule in self.filter_rules if (rule_query := rule.to_query())
        )

    def primary_tag_id(self) -> int | None:
        if len(self.filter_rules) != 1:
            return None
        rule = self.filter_rules[0]
        if rule.type == FILTER_RULE_TYPE_TAG and rule.include and rule.tag_id is not None:
            return rule.tag_id
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

        self.groups = groups
        return self

    def to_dict(self) -> dict[str, Any]:
        normalized = self.normalized()
        return {
            "collapsed": normalized.collapsed,
            "groups": [group.to_dict() for group in normalized.groups],
        }
