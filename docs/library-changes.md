---
icon: material/database-edit
---

# :material-database-edit: Library Format

This page gives a high-level overview of the PromptBook library format.

For the current developer-facing database layout, see the [Database Schema](database-schema.md) page.

## Current Format

PromptBook stores each library's metadata in a local SQLite database.

The current library data path is:

```text
.PromptBook/ts_library.sqlite
```

The `.PromptBook` folder name is the current PromptBook library folder name. The `ts_library.sqlite` database filename is still inherited from the original codebase and is kept for compatibility.

## What Is Stored

The library database stores PromptBook metadata such as:

- file entries
- tags
- tag relationships
- custom field definitions
- field values
- tag colors
- internal version information
- per-library settings

PromptBook does not write this metadata into your original files.

## Versioning

PromptBook libraries use internal database versioning.

The database version is separate from the application version. This allows the application to update the internal library structure when needed without tying every schema change directly to a public release number.

The current schema details are implementation details and may change between versions.

## Legacy History

PromptBook is based on the TagStudio codebase, so some inherited migration code and historical database concepts may still exist internally.

Older TagStudio library formats, including legacy JSON libraries and earlier SQLite schema versions, are part of the inherited project history. They are not the recommended format for new PromptBook libraries.

New PromptBook libraries should use the current SQLite format.

## Developer Notes

Developers should treat the database schema as an implementation detail.

Before changing the schema, check the current SQLAlchemy models, migration logic, default data initialization, and the [Database Schema](database-schema.md) documentation.

Relevant source areas include:

```text
src/tagstudio/core/library/alchemy/
src/tagstudio/core/library/
```