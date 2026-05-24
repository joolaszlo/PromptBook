---
icon: material/database-cog
---

# :material-database-cog: Database Schema

This page summarizes the current SQLAlchemy model layout used by PromptBook libraries. It is intended for developers working on the repository, not as a stable public database contract. The schema is an implementation detail and may change with migrations.

The source of truth is the code under `src/tagstudio/core/library/alchemy/`, especially:

-   `models.py`
-   `fields.py`
-   `joins.py`
-   `db.py`
-   `library.py`

Some internal Python package paths still use the inherited `tagstudio` name. The current library folder name is `.PromptBook`, and the current SQLite filename is `ts_library.sqlite`.

## Storage and Initialization

Libraries are opened through `Library.open_library()`. For regular file-backed libraries, the SQLite database path is:

```text
<Library Folder>/.PromptBook/ts_library.sqlite
```

`Library.open_sqlite_library()` creates a SQLite engine for that path and calls `make_tables()`, which runs `Base.metadata.create_all(engine)` for the SQLAlchemy declarative metadata. `db.py` also exposes `make_engine()` as a thin `create_engine()` wrapper and `drop_tables()` as a metadata-level drop helper.

New libraries are also initialized with default color namespaces, default color groups, built-in tags, version rows, deprecated preference rows, default field type rows, a `folders` row for the library root, and a generated `.ts_ignore` file. The current database version constant is `106`.

Tag IDs below `1000` are reserved for built-in tags. During table creation, `make_tables()` bumps the SQLite autoincrement sequence for `tags` by inserting and deleting a temporary row with ID `999` when needed.

## Tables

### Entries and Folders

`entries` stores library items. An entry may reference media on disk, but `path` is nullable so an entry can exist without linked media.

| Table | Columns |
| ----- | ------- |
| `entries` | `id` primary key; nullable `folder_id` foreign key to `folders.id`; nullable unique `path`; `filename`; `suffix`; nullable `date_created`; nullable `date_modified`; nullable `date_added` |
| `folders` | `id` primary key; unique `path`; unique `uuid` |

`Entry.path` and `Folder.path` use `PathType`, which stores `pathlib.Path` values as POSIX-style strings in SQLite and converts them back to `Path` objects when loaded.

`Entry.tags` is a many-to-many relationship through `tag_entries`. `Entry.text_fields` and `Entry.datetime_fields` are one-to-many relationships with delete cascade. The `Entry.fields` property combines text and datetime fields sorted by their field type position.

### Tags

| Table | Columns |
| ----- | ------- |
| `tags` | `id` autoincrementing primary key; `name`; nullable `shorthand`; nullable `color_namespace`; nullable `color_slug`; `is_category`; `is_hidden`; `pinned`; `favorite`; nullable `icon`; nullable `disambiguation_id` |
| `tag_aliases` | `id` primary key; `name`; `tag_id` foreign key to `tags.id` |
| `tag_entries` | composite primary key of `tag_id` and `entry_id`; foreign keys to `tags.id` and `entries.id` |
| `tag_parents` | composite primary key of `parent_id` and `child_id`; both foreign keys to `tags.id` |

`tags.color_namespace` and `tags.color_slug` form a composite foreign key to `tag_colors.namespace` and `tag_colors.slug`. Parent-child tag relationships are represented by `tag_parents`, where `parent_id` points to the parent tag and `child_id` points to the child tag.

### Tag Colors

| Table | Columns |
| ----- | ------- |
| `namespaces` | `namespace` primary key; `name` |
| `tag_colors` | composite primary key of `slug` and `namespace`; `name`; `primary`; nullable `secondary`; `color_border` |

`tag_colors.namespace` is a foreign key to `namespaces.namespace`. Some seeded color namespaces still use inherited names such as `tagstudio-standard`; those values are current database data and should not be renamed without a migration.

### Fields

Field definitions live in `value_type`. Entry-specific field values live in separate tables by storage type.

| Table | Columns |
| ----- | ------- |
| `value_type` | `key` primary key; `name`; `type`; `is_default`; `position` |
| `text_fields` | `id` primary key; `type_key` foreign key to `value_type.key`; `entry_id` foreign key to `entries.id`; `position`; nullable `value` |
| `datetime_fields` | `id` primary key; `type_key` foreign key to `value_type.key`; `entry_id` foreign key to `entries.id`; `position`; nullable `value` |
| `boolean_fields` | `id` primary key; `type_key` foreign key to `value_type.key`; `entry_id` foreign key to `entries.id`; `position`; `value` |

The current field type enum includes `TEXT_LINE`, `TEXT_BOX`, `TAGS`, `DATETIME`, and `BOOLEAN`. `FieldID` currently seeds default `value_type` rows for:

```text
TITLE, AUTHOR, ARTIST, URL, DESCRIPTION, NOTES, COLLATION,
DATE, DATE_CREATED, DATE_MODIFIED, DATE_TAKEN, DATE_PUBLISHED,
BOOK, COMIC, SERIES, MANGA, SOURCE, DATE_UPLOADED, DATE_RELEASED,
VOLUME, ANTHOLOGY, MAGAZINE, PUBLISHER, GUEST_ARTIST, COMPOSER, COMMENTS
```

`Library.add_field_to_entry()` currently creates `TextField` rows for `TEXT_LINE` and `TEXT_BOX` value types, and `DatetimeField` rows for `DATETIME` value types. `BooleanField` is mapped in SQLAlchemy, but entry creation and `Entry.fields` currently handle text and datetime fields.

### Settings and Versions

| Table | Columns |
| ----- | ------- |
| `versions` | `key` primary key; `value` integer |
| `preferences` | `key` primary key; `value` JSON |
| `category_sidebar_settings` | `id` primary key; `collapsed`; `groups` JSON |

`versions` stores the database version keys, including `CURRENT` and `INITIAL`. `preferences` is deprecated and retained for compatibility until it is removed from the codebase.
