# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio

import contextlib
import typing

from tagstudio.core.library.alchemy.fields import FieldID
from tagstudio.core.library.alchemy.library import Library
from tagstudio.qt.mixed.tag_search import TagSearchModal
from tagstudio.qt.views.preview_panel_view import PreviewPanelView

if typing.TYPE_CHECKING:
    from tagstudio.qt.ts_qt import QtDriver


class PreviewPanel(PreviewPanelView):
    def __init__(self, library: Library, driver: "QtDriver"):
        super().__init__(library, driver)

        self.__add_tag_modal = TagSearchModal(self.lib, is_tag_chooser=True)

    def _add_tag_button_callback(self):
        self.__add_tag_modal.show()

    def _set_selection_callback(self):
        with contextlib.suppress(RuntimeError, TypeError):
            self.__add_tag_modal.tsp.tag_chosen.disconnect()

        self.__add_tag_modal.tsp.tag_chosen.connect(self._add_tag_to_selected)

    def _edit_prompt_button_callback(self):
        self._fields.edit_or_add_field_to_selected(FieldID.DESCRIPTION)

    def _add_tag_to_selected(self, tag_id: int):
        self._fields.add_tags_to_selected(tag_id)
        if len(self._selected) == 1:
            self._fields.update_from_entry(self._selected[0])
