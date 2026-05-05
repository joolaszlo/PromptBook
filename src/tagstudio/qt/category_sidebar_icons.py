# Copyright (C) 2026
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

from __future__ import annotations

import json
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QByteArray, QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
    QPolygonF,
)
from PySide6.QtSvg import QSvgRenderer

DEFAULT_CATEGORY_SIDEBAR_ICON = "tag"
LUCIDE_ICON_DATA_PATH = (
    Path(__file__).parents[1] / "resources" / "lucide" / "icons.json"
)

CATEGORY_SIDEBAR_ICONS: tuple[str, ...] = (
"accessibility",
"activity",
"archive",
"badge",
"ban",
"book-open",
"bot",
"box",
"brain",
"calendar",
"camera",
"car",
"circle-slash",
"clock",
"drama",
"eye",
"film",
"folder",
"footprints",
"gamepad-2",
"globe",
"hand",
"heart",
"home",
"image",
"images",
"layers",
"layout-grid",
"map-pin",
"message-circle",
"music",
"palette",
"scan-face",
"search",
"settings",
"shelving-unit",
"shirt",
"sliders-horizontal",
"smile",
"sparkles",
"star",
"tag",
"tags",
"user",
"users",
"utensils",
"video",
"wand",
"zap",
)

_ICON_SET = set(CATEGORY_SIDEBAR_ICONS)


def category_sidebar_icon_names() -> tuple[str, ...]:
    return CATEGORY_SIDEBAR_ICONS


def category_sidebar_search_icon_names() -> tuple[str, ...]:
    return _lucide_icon_names()


def resolve_category_sidebar_icon_name(icon_name: str | None) -> str:
    normalized = (icon_name or "").strip().lower()
    if normalized in _lucide_icon_name_set():
        return normalized
    return DEFAULT_CATEGORY_SIDEBAR_ICON


def category_sidebar_icon(
    icon_name: str | None,
    color: QColor | str | None = None,
    size: int = 20,
) -> QIcon:
    return QIcon(category_sidebar_icon_pixmap(icon_name, color=color, size=size))


def category_sidebar_icon_pixmap(
    icon_name: str | None,
    color: QColor | str | None = None,
    size: int = 20,
) -> QPixmap:
    resolved_name = resolve_category_sidebar_icon_name(icon_name)
    icon_color = _resolve_color(color)
    icon_size = max(12, size)

    pixmap = QPixmap(icon_size, icon_size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    if not _render_lucide_icon(pixmap, painter, resolved_name, icon_color, icon_size):
        pen = QPen(icon_color, max(1.6, icon_size / 11))
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        _draw_icon(painter, resolved_name, float(icon_size))
    painter.end()
    return pixmap


def _resolve_color(color: QColor | str | None) -> QColor:
    if isinstance(color, QColor):
        return QColor(color)
    if isinstance(color, str):
        resolved = QColor(color)
        if resolved.isValid():
            return resolved
    return QColor("#d8dde6")


@lru_cache(maxsize=1)
def _lucide_icon_data() -> dict[str, dict[str, object]]:
    with LUCIDE_ICON_DATA_PATH.open(encoding="utf-8") as file:
        data = json.load(file)

    icons = data.get("icons")
    aliases = data.get("aliases", {})
    if not isinstance(icons, dict):
        return {}
    if not isinstance(aliases, dict):
        aliases = {}

    resolved_icons: dict[str, dict[str, object]] = {
        str(name): icon_data
        for name, icon_data in icons.items()
        if isinstance(icon_data, dict)
    }
    for alias_name, alias_data in aliases.items():
        if not isinstance(alias_data, dict):
            continue
        parent = alias_data.get("parent")
        if isinstance(parent, str) and parent in resolved_icons:
            resolved_icons[str(alias_name)] = resolved_icons[parent]

    return resolved_icons


@lru_cache(maxsize=1)
def _lucide_icon_names() -> tuple[str, ...]:
    return tuple(sorted(_ICON_SET.union(_lucide_icon_data())))


@lru_cache(maxsize=1)
def _lucide_icon_name_set() -> frozenset[str]:
    return frozenset(_lucide_icon_names())


def _lucide_icon_body(icon_name: str) -> str | None:
    icon_data = _lucide_icon_data().get(icon_name)
    body = icon_data.get("body") if icon_data else None
    return body if isinstance(body, str) else None


def _render_lucide_icon(
    pixmap: QPixmap,
    painter: QPainter,
    icon_name: str,
    icon_color: QColor,
    icon_size: int,
) -> bool:
    body = _lucide_icon_body(icon_name)
    if body is None:
        return False

    body = body.replace("currentColor", icon_color.name(QColor.NameFormat.HexRgb))
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{icon_size}" height="{icon_size}" viewBox="0 0 24 24">'
        f"{body}</svg>"
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    if not renderer.isValid():
        return False

    renderer.render(painter, QRectF(pixmap.rect()))
    return True


def _p(size: float, x: float, y: float) -> QPointF:
    return QPointF(size * x, size * y)


def _r(size: float, x: float, y: float, w: float, h: float) -> QRectF:
    return QRectF(size * x, size * y, size * w, size * h)


def _line(painter: QPainter, size: float, start: tuple[float, float], end: tuple[float, float]):
    painter.drawLine(_p(size, *start), _p(size, *end))


def _polyline(painter: QPainter, size: float, points: Iterable[tuple[float, float]]):
    scaled = list(points)
    for index in range(len(scaled) - 1):
        _line(painter, size, scaled[index], scaled[index + 1])


def _draw_icon(painter: QPainter, name: str, size: float) -> None:
    if name in {"user", "users", "scan-face", "smile", "bot", "brain"}:
        _draw_person_icon(painter, name, size)
    elif name in {"tag", "tags", "badge"}:
        _draw_tag_icon(painter, name, size)
    elif name in {"folder", "archive", "box"}:
        _draw_container_icon(painter, name, size)
    elif name in {"image", "images", "camera", "video", "film"}:
        _draw_media_icon(painter, name, size)
    elif name in {"heart", "star", "sparkles", "wand", "zap"}:
        _draw_favorite_icon(painter, name, size)
    elif name in {"settings", "sliders-horizontal", "search"}:
        _draw_tool_icon(painter, name, size)
    elif name in {"clock", "calendar", "globe", "home", "map-pin"}:
        _draw_place_time_icon(painter, name, size)
    elif name in {"car", "music", "gamepad-2", "activity", "accessibility"}:
        _draw_activity_icon(painter, name, size)
    elif name in {"book-open", "palette", "message-circle", "eye", "hand", "footprints"}:
        _draw_life_icon(painter, name, size)
    elif name in {"layers", "layout-grid"}:
        _draw_layout_icon(painter, name, size)
    elif name in {"ban", "circle-slash"}:
        _draw_ban_icon(painter, size)
    elif name == "shirt":
        _draw_shirt_icon(painter, size)
    else:
        _draw_tag_icon(painter, DEFAULT_CATEGORY_SIDEBAR_ICON, size)


def _draw_person_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "bot":
        painter.drawRoundedRect(_r(size, 0.25, 0.3, 0.5, 0.42), size * 0.08, size * 0.08)
        _line(painter, size, (0.5, 0.18), (0.5, 0.3))
        painter.drawEllipse(_p(size, 0.38, 0.48), size * 0.025, size * 0.025)
        painter.drawEllipse(_p(size, 0.62, 0.48), size * 0.025, size * 0.025)
        _line(painter, size, (0.4, 0.62), (0.6, 0.62))
        return
    if name == "brain":
        painter.drawEllipse(_r(size, 0.18, 0.25, 0.64, 0.48))
        _polyline(painter, size, ((0.38, 0.27), (0.34, 0.45), (0.45, 0.55), (0.38, 0.72)))
        _polyline(painter, size, ((0.58, 0.27), (0.66, 0.42), (0.55, 0.56), (0.62, 0.72)))
        return
    if name in {"scan-face", "smile"}:
        painter.drawEllipse(_r(size, 0.22, 0.2, 0.56, 0.56))
        painter.drawEllipse(_p(size, 0.4, 0.42), size * 0.018, size * 0.018)
        painter.drawEllipse(_p(size, 0.6, 0.42), size * 0.018, size * 0.018)
        painter.drawArc(_r(size, 0.38, 0.42, 0.24, 0.2), 210 * 16, 120 * 16)
        if name == "scan-face":
            _draw_corner_marks(painter, size)
        return

    painter.drawEllipse(_r(size, 0.34, 0.18, 0.32, 0.32))
    painter.drawArc(_r(size, 0.22, 0.5, 0.56, 0.38), 20 * 16, 140 * 16)
    if name == "users":
        painter.drawEllipse(_r(size, 0.62, 0.24, 0.2, 0.2))
        painter.drawArc(_r(size, 0.58, 0.53, 0.34, 0.25), 20 * 16, 120 * 16)


def _draw_tag_icon(painter: QPainter, name: str, size: float) -> None:
    offset = 0.0 if name != "tags" else -0.08
    points = QPolygonF(
        [
            _p(size, 0.2 + offset, 0.24),
            _p(size, 0.56 + offset, 0.24),
            _p(size, 0.82 + offset, 0.5),
            _p(size, 0.5 + offset, 0.82),
            _p(size, 0.2 + offset, 0.52),
        ]
    )
    painter.drawPolygon(points)
    painter.drawEllipse(_p(size, 0.38 + offset, 0.4), size * 0.035, size * 0.035)
    if name == "tags":
        _line(painter, size, (0.54, 0.22), (0.9, 0.58))
    elif name == "badge":
        painter.drawEllipse(_r(size, 0.2, 0.2, 0.6, 0.6))


def _draw_container_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "folder":
        path = QPainterPath()
        path.moveTo(_p(size, 0.14, 0.32))
        path.lineTo(_p(size, 0.38, 0.32))
        path.lineTo(_p(size, 0.46, 0.42))
        path.lineTo(_p(size, 0.86, 0.42))
        path.lineTo(_p(size, 0.86, 0.78))
        path.lineTo(_p(size, 0.14, 0.78))
        path.closeSubpath()
        painter.drawPath(path)
        return
    if name == "archive":
        painter.drawRoundedRect(_r(size, 0.16, 0.24, 0.68, 0.16), size * 0.04, size * 0.04)
        painter.drawRoundedRect(_r(size, 0.22, 0.4, 0.56, 0.4), size * 0.05, size * 0.05)
        _line(painter, size, (0.4, 0.53), (0.6, 0.53))
        return
    points = QPolygonF(
        [
            _p(size, 0.5, 0.16),
            _p(size, 0.82, 0.34),
            _p(size, 0.82, 0.68),
            _p(size, 0.5, 0.84),
            _p(size, 0.18, 0.68),
            _p(size, 0.18, 0.34),
        ]
    )
    painter.drawPolygon(points)
    _line(painter, size, (0.18, 0.34), (0.5, 0.52))
    _line(painter, size, (0.82, 0.34), (0.5, 0.52))
    _line(painter, size, (0.5, 0.52), (0.5, 0.84))


def _draw_media_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "camera":
        painter.drawRoundedRect(_r(size, 0.16, 0.3, 0.68, 0.46), size * 0.06, size * 0.06)
        _line(painter, size, (0.32, 0.3), (0.38, 0.22))
        _line(painter, size, (0.38, 0.22), (0.62, 0.22))
        _line(painter, size, (0.62, 0.22), (0.68, 0.3))
        painter.drawEllipse(_r(size, 0.38, 0.42, 0.24, 0.24))
        return
    if name == "video":
        painter.drawRoundedRect(_r(size, 0.14, 0.32, 0.48, 0.38), size * 0.05, size * 0.05)
        painter.drawPolygon(QPolygonF([_p(size, 0.62, 0.45), _p(size, 0.86, 0.32), _p(size, 0.86, 0.7), _p(size, 0.62, 0.58)]))
        return
    if name == "film":
        painter.drawRoundedRect(_r(size, 0.2, 0.16, 0.6, 0.68), size * 0.04, size * 0.04)
        for y in (0.28, 0.5, 0.72):
            _line(painter, size, (0.28, y), (0.32, y))
            _line(painter, size, (0.68, y), (0.72, y))
        return
    if name == "images":
        painter.drawRoundedRect(_r(size, 0.26, 0.18, 0.56, 0.48), size * 0.04, size * 0.04)
    painter.drawRoundedRect(_r(size, 0.18, 0.3, 0.56, 0.48), size * 0.04, size * 0.04)
    painter.drawEllipse(_p(size, 0.34, 0.44), size * 0.035, size * 0.035)
    _polyline(painter, size, ((0.22, 0.72), (0.4, 0.56), (0.52, 0.66), (0.66, 0.52), (0.74, 0.6)))


def _draw_favorite_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "heart":
        path = QPainterPath()
        path.moveTo(_p(size, 0.5, 0.78))
        path.cubicTo(_p(size, 0.14, 0.5), _p(size, 0.2, 0.24), _p(size, 0.38, 0.28))
        path.cubicTo(_p(size, 0.46, 0.3), _p(size, 0.5, 0.38), _p(size, 0.5, 0.38))
        path.cubicTo(_p(size, 0.5, 0.38), _p(size, 0.56, 0.3), _p(size, 0.64, 0.28))
        path.cubicTo(_p(size, 0.82, 0.24), _p(size, 0.86, 0.5), _p(size, 0.5, 0.78))
        painter.drawPath(path)
        return
    if name == "star":
        _draw_star(painter, size, 0.5, 0.5, 0.34)
        return
    if name == "sparkles":
        _draw_star(painter, size, 0.36, 0.38, 0.18)
        _draw_star(painter, size, 0.68, 0.64, 0.12)
        return
    if name == "wand":
        _line(painter, size, (0.24, 0.76), (0.72, 0.28))
        _draw_star(painter, size, 0.74, 0.26, 0.1)
        return
    _polyline(painter, size, ((0.58, 0.12), (0.28, 0.52), (0.5, 0.52), (0.42, 0.88), (0.72, 0.46), (0.5, 0.46), (0.58, 0.12)))


def _draw_tool_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "search":
        painter.drawEllipse(_r(size, 0.2, 0.2, 0.46, 0.46))
        _line(painter, size, (0.58, 0.58), (0.82, 0.82))
        return
    if name == "settings":
        painter.drawEllipse(_r(size, 0.34, 0.34, 0.32, 0.32))
        for x1, y1, x2, y2 in (
            (0.5, 0.12, 0.5, 0.24),
            (0.5, 0.76, 0.5, 0.88),
            (0.12, 0.5, 0.24, 0.5),
            (0.76, 0.5, 0.88, 0.5),
            (0.24, 0.24, 0.32, 0.32),
            (0.68, 0.68, 0.76, 0.76),
            (0.76, 0.24, 0.68, 0.32),
            (0.32, 0.68, 0.24, 0.76),
        ):
            _line(painter, size, (x1, y1), (x2, y2))
        return
    for y, knob in ((0.28, 0.36), (0.5, 0.64), (0.72, 0.46)):
        _line(painter, size, (0.18, y), (0.82, y))
        painter.drawEllipse(_p(size, knob, y), size * 0.045, size * 0.045)


def _draw_place_time_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "clock":
        painter.drawEllipse(_r(size, 0.18, 0.18, 0.64, 0.64))
        _line(painter, size, (0.5, 0.34), (0.5, 0.52))
        _line(painter, size, (0.5, 0.52), (0.64, 0.6))
        return
    if name == "calendar":
        painter.drawRoundedRect(_r(size, 0.18, 0.22, 0.64, 0.58), size * 0.04, size * 0.04)
        _line(painter, size, (0.18, 0.4), (0.82, 0.4))
        _line(painter, size, (0.34, 0.16), (0.34, 0.28))
        _line(painter, size, (0.66, 0.16), (0.66, 0.28))
        return
    if name == "globe":
        painter.drawEllipse(_r(size, 0.18, 0.18, 0.64, 0.64))
        _line(painter, size, (0.18, 0.5), (0.82, 0.5))
        painter.drawArc(_r(size, 0.34, 0.18, 0.32, 0.64), 90 * 16, 180 * 16)
        painter.drawArc(_r(size, 0.34, 0.18, 0.32, 0.64), -90 * 16, 180 * 16)
        return
    if name == "home":
        painter.drawPolygon(QPolygonF([_p(size, 0.16, 0.48), _p(size, 0.5, 0.2), _p(size, 0.84, 0.48)]))
        painter.drawRoundedRect(_r(size, 0.26, 0.46, 0.48, 0.36), size * 0.04, size * 0.04)
        return
    painter.drawEllipse(_r(size, 0.28, 0.14, 0.44, 0.44))
    _polyline(painter, size, ((0.5, 0.86), (0.34, 0.54), (0.66, 0.54), (0.5, 0.86)))


def _draw_activity_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "car":
        painter.drawRoundedRect(_r(size, 0.16, 0.42, 0.68, 0.24), size * 0.04, size * 0.04)
        _polyline(painter, size, ((0.28, 0.42), (0.38, 0.28), (0.62, 0.28), (0.72, 0.42)))
        painter.drawEllipse(_p(size, 0.32, 0.72), size * 0.055, size * 0.055)
        painter.drawEllipse(_p(size, 0.68, 0.72), size * 0.055, size * 0.055)
        return
    if name == "music":
        _line(painter, size, (0.58, 0.2), (0.58, 0.68))
        _line(painter, size, (0.58, 0.2), (0.78, 0.28))
        painter.drawEllipse(_r(size, 0.34, 0.62, 0.24, 0.16))
        return
    if name == "gamepad-2":
        painter.drawRoundedRect(_r(size, 0.16, 0.38, 0.68, 0.28), size * 0.12, size * 0.12)
        _line(painter, size, (0.3, 0.52), (0.44, 0.52))
        _line(painter, size, (0.37, 0.45), (0.37, 0.59))
        painter.drawEllipse(_p(size, 0.66, 0.5), size * 0.025, size * 0.025)
        painter.drawEllipse(_p(size, 0.75, 0.55), size * 0.025, size * 0.025)
        return
    if name == "accessibility":
        painter.drawEllipse(_r(size, 0.44, 0.14, 0.12, 0.12))
        _line(painter, size, (0.5, 0.3), (0.5, 0.72))
        _line(painter, size, (0.26, 0.4), (0.74, 0.4))
        _line(painter, size, (0.5, 0.72), (0.34, 0.88))
        _line(painter, size, (0.5, 0.72), (0.66, 0.88))
        return
    _polyline(painter, size, ((0.12, 0.56), (0.3, 0.56), (0.4, 0.34), (0.54, 0.76), (0.64, 0.48), (0.84, 0.48)))


def _draw_life_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "book-open":
        painter.drawRoundedRect(_r(size, 0.14, 0.24, 0.32, 0.52), size * 0.03, size * 0.03)
        painter.drawRoundedRect(_r(size, 0.54, 0.24, 0.32, 0.52), size * 0.03, size * 0.03)
        _line(painter, size, (0.5, 0.28), (0.5, 0.8))
        return
    if name == "palette":
        painter.drawEllipse(_r(size, 0.18, 0.2, 0.64, 0.56))
        painter.drawEllipse(_r(size, 0.56, 0.54, 0.12, 0.1))
        for point in ((0.36, 0.38), (0.52, 0.34), (0.34, 0.58)):
            painter.drawEllipse(_p(size, *point), size * 0.018, size * 0.018)
        return
    if name == "message-circle":
        painter.drawEllipse(_r(size, 0.18, 0.2, 0.64, 0.5))
        _polyline(painter, size, ((0.36, 0.66), (0.26, 0.82), (0.48, 0.7)))
        return
    if name == "eye":
        path = QPainterPath()
        path.moveTo(_p(size, 0.14, 0.5))
        path.cubicTo(_p(size, 0.32, 0.26), _p(size, 0.68, 0.26), _p(size, 0.86, 0.5))
        path.cubicTo(_p(size, 0.68, 0.74), _p(size, 0.32, 0.74), _p(size, 0.14, 0.5))
        painter.drawPath(path)
        painter.drawEllipse(_r(size, 0.42, 0.42, 0.16, 0.16))
        return
    if name == "hand":
        _polyline(painter, size, ((0.3, 0.78), (0.3, 0.38), (0.38, 0.38), (0.38, 0.62), (0.44, 0.26), (0.52, 0.26), (0.52, 0.62), (0.58, 0.34), (0.66, 0.36), (0.62, 0.82)))
        return
    painter.drawEllipse(_r(size, 0.28, 0.22, 0.18, 0.28))
    painter.drawEllipse(_r(size, 0.56, 0.5, 0.18, 0.28))


def _draw_layout_icon(painter: QPainter, name: str, size: float) -> None:
    if name == "layout-grid":
        for x in (0.18, 0.52):
            for y in (0.18, 0.52):
                painter.drawRoundedRect(_r(size, x, y, 0.3, 0.3), size * 0.04, size * 0.04)
        return
    painter.drawRoundedRect(_r(size, 0.2, 0.22, 0.46, 0.34), size * 0.03, size * 0.03)
    painter.drawRoundedRect(_r(size, 0.34, 0.38, 0.46, 0.34), size * 0.03, size * 0.03)
    painter.drawRoundedRect(_r(size, 0.26, 0.54, 0.46, 0.26), size * 0.03, size * 0.03)


def _draw_ban_icon(painter: QPainter, size: float) -> None:
    painter.drawEllipse(_r(size, 0.18, 0.18, 0.64, 0.64))
    _line(painter, size, (0.28, 0.72), (0.72, 0.28))


def _draw_shirt_icon(painter: QPainter, size: float) -> None:
    path = QPainterPath()
    path.moveTo(_p(size, 0.34, 0.18))
    path.lineTo(_p(size, 0.2, 0.28))
    path.lineTo(_p(size, 0.14, 0.48))
    path.lineTo(_p(size, 0.3, 0.56))
    path.lineTo(_p(size, 0.3, 0.82))
    path.lineTo(_p(size, 0.7, 0.82))
    path.lineTo(_p(size, 0.7, 0.56))
    path.lineTo(_p(size, 0.86, 0.48))
    path.lineTo(_p(size, 0.8, 0.28))
    path.lineTo(_p(size, 0.66, 0.18))
    path.closeSubpath()
    painter.drawPath(path)


def _draw_corner_marks(painter: QPainter, size: float) -> None:
    for x1, y1, x2, y2 in (
        (0.14, 0.3, 0.14, 0.18),
        (0.14, 0.18, 0.26, 0.18),
        (0.86, 0.3, 0.86, 0.18),
        (0.86, 0.18, 0.74, 0.18),
        (0.14, 0.7, 0.14, 0.82),
        (0.14, 0.82, 0.26, 0.82),
        (0.86, 0.7, 0.86, 0.82),
        (0.86, 0.82, 0.74, 0.82),
    ):
        _line(painter, size, (x1, y1), (x2, y2))


def _draw_star(painter: QPainter, size: float, cx: float, cy: float, radius: float) -> None:
    _line(painter, size, (cx, cy - radius), (cx, cy + radius))
    _line(painter, size, (cx - radius, cy), (cx + radius, cy))
    _line(painter, size, (cx - radius * 0.65, cy - radius * 0.65), (cx + radius * 0.65, cy + radius * 0.65))
    _line(painter, size, (cx + radius * 0.65, cy - radius * 0.65), (cx - radius * 0.65, cy + radius * 0.65))
