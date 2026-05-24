---
icon: material/script-text
---

# :material-script-text: Tools & Macros

Tools and macros provide extra actions for managing a PromptBook [library](libraries.md).

Some tools are intended for maintenance tasks, such as fixing missing files or handling duplicates. Other macros can create or update tags and fields based on existing library data.

Some features are still experimental or in development and may change in future versions.

## Tools

### Fix Unlinked Entries

This tool helps find and resolve unlinked [entries](entries.md).

An entry becomes unlinked when the file it points to has been moved, renamed, or deleted outside PromptBook.

Available actions:

- **Refresh**
    - Scans the library and updates the unlinked entry count.

- **Search & Relink**
    - Attempts to automatically find and reconnect missing files.

- **Delete Unlinked Entries**
    - Shows a confirmation prompt with the list of missing entries before deleting them from the library database.
    - This removes the entries from PromptBook, not the original files on disk.

### Fix Duplicate Files

This tool helps manage duplicate files in the library using a [DupeGuru](https://dupeguru.voltaicideas.net/) results file.

Available actions:

- **Load DupeGuru File**
    - Loads the results file created by a DupeGuru scan.

- **Mirror Entries**
    - Copies entry metadata across duplicate file entries.
    - This can help preserve tags and [field](fields.md) data before duplicate files are removed externally.

After duplicate files are deleted outside PromptBook, the [Fix Unlinked Entries](#fix-unlinked-entries) tool can be used to clean up entries that no longer have a file on disk.

### Create Collage

This tool is an experimental preview of a possible future feature.

When selected, PromptBook generates a collage from library contents.

The generated collage can be found inside the library folder:

```text
/your-library/.PromptBook/collages/
```

This feature is still in early development and does not currently offer many customization options.

## Macros

### Auto-fill [WIP]

This macro is in development and will be documented in a future update.

### Sort Fields [WIP]

This macro is in development.

It is planned to allow user-defined sorting of [fields](fields.md).

### Folders to Tags

This macro creates tags from the existing folder structure in the library.

PromptBook previews the folder structure as a hierarchy before applying the changes.

A tag is created for each folder and applied to all entries inside that folder. Subfolders are linked to their parent folders as [parent tags](tags.md#parent-tags).

The generated tags are initially named after the folders, but they can be edited and customized afterwards.