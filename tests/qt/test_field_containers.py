# Copyright (C) 2025
# Licensed under the GPL-3.0 License.
# Created for TagStudio: https://github.com/CyanVoxel/TagStudio


from unittest.mock import Mock

from tagstudio.core.library.alchemy.fields import FieldID
from tagstudio.core.library.alchemy.library import Library
from tagstudio.core.library.alchemy.models import Entry, Tag
from tagstudio.core.utils.types import unwrap
from tagstudio.qt.controllers.preview_panel_controller import PreviewPanel
from tagstudio.qt.ts_qt import QtDriver


def test_update_selection_empty(qt_driver: QtDriver, library: Library):
    panel = PreviewPanel(library, qt_driver)

    # Clear the library selection (selecting 1 then unselecting 1)
    qt_driver.toggle_item_selection(1, append=False, bridge=False)
    qt_driver.toggle_item_selection(1, append=True, bridge=False)
    panel.set_selection(qt_driver.selected)

    # FieldContainer should hide all containers
    for container in panel.field_containers_widget.containers:
        assert container.isHidden()


def test_update_selection_single(qt_driver: QtDriver, library: Library, entry_full: Entry):
    panel = PreviewPanel(library, qt_driver)

    # Select the single entry
    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)

    # FieldContainer should show all applicable tags and field containers
    for container in panel.field_containers_widget.containers:
        assert not container.isHidden()


def test_title_container_requires_meaningful_content(
    qt_driver: QtDriver, library: Library, entry_full: Entry
):
    panel = PreviewPanel(library, qt_driver)

    library.upsert_entry_field(entry_full.id, FieldID.TITLE, "   ")
    panel.set_selection([entry_full.id])

    visible_titles = [
        container.title
        for container in panel.field_containers_widget.containers
        if not container.isHidden()
    ]
    assert "<h4>Title</h4>" not in visible_titles

    library.set_entry_title(entry_full.id, "  Visible Title  ")
    panel.set_selection([entry_full.id])

    visible_titles = [
        container.title
        for container in panel.field_containers_widget.containers
        if not container.isHidden()
    ]
    assert "<h4>Title</h4>" in visible_titles


def test_text_only_title_cannot_be_cleared_from_field_container(
    qt_driver: QtDriver, library: Library
):
    panel = PreviewPanel(library, qt_driver)
    entry = Entry(
        id=101,
        folder=unwrap(library.folder),
        path=None,
        fields=[],
    )
    assert library.add_entries([entry])
    assert library.set_entry_title(entry.id, "Required Title")
    qt_driver.show_error_message = Mock()

    panel.set_selection([entry.id])
    title_field = next(
        field
        for field in panel.field_containers_widget.cached_entries[0].fields
        if field.type.key == FieldID.TITLE.name
    )

    panel.field_containers_widget.update_field(title_field, "   ")
    entry = unwrap(library.get_entry_full(entry.id))
    assert library.get_entry_field_value(entry, FieldID.TITLE) == "Required Title"
    qt_driver.show_error_message.assert_called_once()

    qt_driver.show_error_message.reset_mock()
    panel.field_containers_widget.remove_field(title_field)
    entry = unwrap(library.get_entry_full(entry.id))
    assert library.get_entry_field_value(entry, FieldID.TITLE) == "Required Title"
    qt_driver.show_error_message.assert_called_once()


def test_media_title_can_be_cleared_from_field_container(
    qt_driver: QtDriver, library: Library, entry_full: Entry
):
    panel = PreviewPanel(library, qt_driver)
    assert library.set_entry_title(entry_full.id, "Optional Title")

    panel.set_selection([entry_full.id])
    title_field = next(
        field
        for field in panel.field_containers_widget.cached_entries[0].fields
        if field.type.key == FieldID.TITLE.name
    )

    panel.field_containers_widget.update_field(title_field, "   ")
    entry = unwrap(library.get_entry_full(entry_full.id))
    assert not any(field.type.key == FieldID.TITLE.name for field in entry.fields)


def test_add_missing_title_from_field_container_does_not_store_empty_title(
    qt_driver: QtDriver, library: Library, entry_full: Entry
):
    panel = PreviewPanel(library, qt_driver)
    assert library.set_entry_title(entry_full.id, "")

    panel.set_selection([entry_full.id])
    panel.field_containers_widget.edit_or_add_field_to_selected(FieldID.TITLE)

    entry = unwrap(library.get_entry_full(entry_full.id))
    assert not any(field.type.key == FieldID.TITLE.name for field in entry.fields)


def test_update_selection_multiple(qt_driver: QtDriver, library: Library):
    # TODO: Implement mixed field editing. Currently these containers will be hidden,
    # same as the empty selection behavior.
    panel = PreviewPanel(library, qt_driver)

    # Select the multiple entries
    qt_driver.toggle_item_selection(1, append=False, bridge=False)
    qt_driver.toggle_item_selection(2, append=True, bridge=False)
    panel.set_selection(qt_driver.selected)

    # FieldContainer should show mixed field editing
    for container in panel.field_containers_widget.containers:
        assert container.isHidden()


def test_add_tag_to_selection_single(qt_driver: QtDriver, library: Library, entry_full: Entry):
    panel = PreviewPanel(library, qt_driver)

    assert {t.id for t in entry_full.tags} == {1000}

    # Select the single entry
    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)

    # Add new tag
    panel.field_containers_widget.add_tags_to_selected(2000)

    # Then reload entry
    refreshed_entry: Entry = next(library.all_entries(with_joins=True))
    assert {t.id for t in refreshed_entry.tags} == {1000, 2000}


def test_add_same_tag_to_selection_single(qt_driver: QtDriver, library: Library, entry_full: Entry):
    panel = PreviewPanel(library, qt_driver)

    assert {t.id for t in entry_full.tags} == {1000}

    # Select the single entry
    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)

    # Add an existing tag
    panel.field_containers_widget.add_tags_to_selected(1000)

    # Then reload entry
    refreshed_entry = next(library.all_entries(with_joins=True))
    assert {t.id for t in refreshed_entry.tags} == {1000}


def test_add_tag_to_selection_multiple(qt_driver: QtDriver, library: Library):
    panel = PreviewPanel(library, qt_driver)
    all_entries = library.all_entries(with_joins=True)

    # We want to verify that tag 1000 is on some, but not all entries already.
    tag_present_on_some: bool = False
    tag_absent_on_some: bool = False

    for e in all_entries:
        if 1000 in [t.id for t in e.tags]:
            tag_present_on_some = True
        else:
            tag_absent_on_some = True

    assert tag_present_on_some
    assert tag_absent_on_some

    # Select the multiple entries
    for i, e in enumerate(library.all_entries(with_joins=True), start=0):
        qt_driver.toggle_item_selection(e.id, append=(True if i == 0 else False), bridge=False)  # noqa: SIM210
    panel.set_selection(qt_driver.selected)

    # Add new tag
    panel.field_containers_widget.add_tags_to_selected(1000)

    # Then reload all entries and recheck the presence of tag 1000
    refreshed_entries = library.all_entries(with_joins=True)
    tag_present_on_some = False
    tag_absent_on_some = False

    for e in refreshed_entries:
        if 1000 in [t.id for t in e.tags]:
            tag_present_on_some = True
        else:
            tag_absent_on_some = True

    assert tag_present_on_some
    assert not tag_absent_on_some


def test_meta_tag_category(qt_driver: QtDriver, library: Library, entry_full: Entry):
    panel = PreviewPanel(library, qt_driver)

    # Ensure the Favorite tag is on entry_full
    library.add_tags_to_entries(1, entry_full.id)

    # Select the single entry
    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)

    # FieldContainer should hide all containers
    assert len(panel.field_containers_widget.containers) == 3
    for i, container in enumerate(panel.field_containers_widget.containers):
        match i:
            case 0:
                # Check if the container is the Meta Tags category
                tag: Tag = unwrap(library.get_tag(2))
                assert container.title == f"<h4>{tag.name}</h4>"
            case 1:
                # Check if the container is the Tags category
                assert container.title == "<h4>Tags</h4>"
            case 2:
                # Make sure the container isn't a duplicate Tags category
                assert container.title != "<h4>Tags</h4>"
            case _:
                pass


def test_custom_tag_category(qt_driver: QtDriver, library: Library, entry_full: Entry):
    panel = PreviewPanel(library, qt_driver)

    # Set tag 1000 (foo) as a category
    tag: Tag = unwrap(library.get_tag(1000))
    tag.is_category = True
    library.update_tag(
        tag,
    )

    # Ensure the Favorite tag is on entry_full
    library.add_tags_to_entries(1, entry_full.id)

    # Select the single entry
    qt_driver.toggle_item_selection(entry_full.id, append=False, bridge=False)
    panel.set_selection(qt_driver.selected)

    # FieldContainer should hide all containers
    assert len(panel.field_containers_widget.containers) == 3
    for i, container in enumerate(panel.field_containers_widget.containers):
        match i:
            case 0:
                # Check if the container is the Meta Tags category
                tag_2: Tag = unwrap(library.get_tag(2))
                assert container.title == f"<h4>{tag_2.name}</h4>"
            case 1:
                # Check if the container is the custom "foo" category
                assert container.title == f"<h4>{tag.name}</h4>"
            case 2:
                # Make sure the container isn't a plain Tags category
                assert container.title != "<h4>Tags</h4>"
            case _:
                pass
