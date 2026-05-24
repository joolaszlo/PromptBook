---
icon: material/database
---

# :material-database: Libraries

A library is the folder that PromptBook uses as the root of an organized collection.

Every supported file inside the library can be represented as a [file entry](entries.md). PromptBook stores the tags, fields, and metadata for those entries in a local library database.

You can create and use multiple libraries. Each library has its own separate tags, fields, entries, and settings.

## Library Folder

PromptBook stores library data inside a `.PromptBook` folder at the root of the selected library directory.

Example:

```text
My Library/
├─ .PromptBook/
│  └─ ts_library.sqlite
├─ Images/
├─ Videos/
└─ Prompts/
```

The `.PromptBook` folder contains PromptBook's local data for that library.

## Library Database

The main library database is stored as:

```text
.PromptBook/ts_library.sqlite
```

This database stores information such as:

- file entries
- tags
- tag relationships
- custom fields
- field values
- internal library metadata

PromptBook does not write this metadata into your original files.

## Per-Library Tags

Tags are currently stored per library.

This means that tags created in one library do not automatically appear in another library.

For example, if you create a `portrait` tag in one library, a different library will not automatically have that same tag unless you create it there too.

## Moving or Copying a Library

If you move or copy a library, keep the `.PromptBook` folder together with the files it belongs to.

The `.PromptBook` folder contains the database that connects PromptBook entries, tags, and fields to the files in that library.

## Notes

- The database file is still named `ts_library.sqlite` for compatibility with the inherited codebase.
- Older TagStudio legacy formats are not relevant for new PromptBook libraries.
- Internal storage details may change between PromptBook versions.
- Developers who need the current database structure should refer to the [Database Schema](database-schema.md) page.