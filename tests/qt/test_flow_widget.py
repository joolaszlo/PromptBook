# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


from PySide6.QtCore import QRect
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from pytestqt.qtbot import QtBot

from tagstudio.qt.views.layouts.flow_layout import FlowLayout, FlowWidget


def test_flow_layout_happy_path(qtbot: QtBot):
    class Window(QWidget):
        def __init__(self):
            super().__init__()

            self.flow_layout = FlowLayout(self)
            self.flow_layout.enable_grid_optimizations(value=True)
            self.flow_layout.addWidget(QPushButton("Short"))

    window = Window()
    qtbot.addWidget(window)
    assert window.flow_layout.count()
    assert window.flow_layout._do_layout(QRect(0, 0, 0, 0), test_only=False)  # pyright: ignore[reportPrivateUsage]


def test_flow_widget_reflows_immediately_on_resize(qtbot: QtBot):
    window = QWidget()
    grid = QGridLayout(window)

    filter_layout = QVBoxLayout()
    filter_layout.setContentsMargins(0, 0, 0, 0)
    filter_layout.addWidget(QLabel("Pinned Tags"))

    flow_widget = FlowWidget()
    flow_layout = FlowLayout(flow_widget)
    flow_layout.setContentsMargins(0, 0, 0, 0)
    flow_layout.setSpacing(6)
    flow_widget.setLayout(flow_layout)
    filter_layout.addWidget(flow_widget)
    grid.addLayout(filter_layout, 0, 0)

    content = QWidget()
    content.setLayout(QVBoxLayout())
    content.layout().addWidget(QLabel("content"))
    grid.addWidget(content, 1, 0)
    grid.setRowStretch(1, 1)

    for index in range(30):
        chip = QLabel(f"pinned-tag-{index}")
        chip.setStyleSheet("border:1px solid white; padding:2px;")
        chip.setMinimumWidth(110)
        flow_layout.addWidget(chip)

    qtbot.addWidget(window)
    window.resize(1316, 740)
    window.show()
    qtbot.wait(0)
    compact_height = flow_widget.height()

    window.resize(600, 740)
    qtbot.wait(0)
    wrapped_height = flow_widget.height()

    assert wrapped_height > compact_height
    assert wrapped_height == flow_widget.sizeHint().height()

    window.resize(1316, 740)
    qtbot.wait(0)

    assert flow_widget.height() == compact_height
