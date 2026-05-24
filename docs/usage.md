---
icon: material/mouse
---

# :material-mouse: Basic Usage

This page covers the basic PromptBook workflow: creating a library, adding metadata, searching, and maintaining entries.

## Creating or Opening a Library

With PromptBook open, create a new library or open an existing one from the menu bar:

```text
File -> Open/Create Library
```

If the selected folder does not already contain a PromptBook library, PromptBook will create one.

PromptBook will scan the selected folder and add supported files as entries in the library.

!!! note
    PromptBook does not move your files during this process.

    It stores library metadata separately inside the library's `.PromptBook` folder.

## Refreshing the Library

PromptBook can scan the library folder for new or changed files.

To manually refresh the library, use:

```text
File -> Refresh Directories
```

Refreshing the library checks the folder contents and updates PromptBook's entry list.

## Browsing Entries

Entries are shown in the main grid view.

Selecting an entry shows more information in the preview panel, including:

- file preview
- tags
- fields
- metadata
- file status

For more information, see [Entries](entries.md).

## Adding Tags to Entries

To add tags to selected entries, open the Add Tag dialog.

You can do this by:

- clicking the **Add Tag** button in the preview panel
- using the **Add Tags to Selected** option from the File menu
- pressing `Ctrl` + `Shift` + `T`

From the Add Tag dialog, you can search for existing tags or create a new tag if it does not already exist.

Click the `+` button next to a tag to add it to the selected entries.

You can also press `Enter` or `Return` to quickly add the top result.

## Removing Tags from Entries

To remove a tag from an entry:

1. Select the entry.
2. Find the tag in the preview panel.
3. Hover over the tag.
4. Click the remove icon.

This removes the tag from that entry. It does not delete the tag from the library.

## Creating Tags

To create a new tag, use:

```text
Edit -> New Tag
```

Or press:

```text
Ctrl + T
```

When creating or editing a tag, you can set:

- name
- shorthand
- aliases
- parent tags
- color
- category behavior
- hidden behavior
- pinned or favorite state, if available in the current UI

For more information, see [Tags](tags.md).

## Managing Tags

Open the Tag Manager from:

```text
Edit -> Manage Tags
```

From the Tag Manager, you can create, search, edit, and delete tags in the current library.

!!! warning
    Deleting a tag removes it from the library and from entries that used it.

## Adding Fields to Entries

Fields are custom metadata values attached to entries.

To add a field:

1. Select an entry.
2. Click **Add Field** in the preview panel.
3. Choose the field type.
4. Enter the field value.

Common field uses include:

- title
- prompt text
- source URL
- description
- notes
- date

For more information, see [Fields](fields.md).

## Editing Fields

To edit a field:

1. Select an entry.
2. Find the field in the preview panel.
3. Hover over the field.
4. Click the pencil icon.
5. Edit the value in the dialog.

## Searching

Use the main search field to search your library.

PromptBook search can work together with:

- text search
- Search in options
- selected tag filters
- excluded tag filters
- hidden entry visibility

For the current search behavior, see [Searching](search.md).

## Handling Unlinked Entries

An entry becomes unlinked when its file has been moved, renamed, or deleted outside PromptBook.

Unlinked entries are shown with a broken chain-link style indicator instead of a normal thumbnail.

To manage them, use:

```text
Tools -> Fix Unlinked Entries
```

Available actions may include:

- refresh the unlinked entry count
- search for missing files and relink entries
- delete unlinked entries from the library database

!!! note
    Deleting an unlinked entry removes the PromptBook entry from the library database.

    It does not delete a file from disk, because the file is already missing from its original location.

## Duplicate File Workflow

PromptBook includes duplicate-file tooling based on DupeGuru result files.

To use this workflow:

1. Scan your files with [DupeGuru](https://dupeguru.voltaicideas.net/).
2. Save or export the DupeGuru results.
3. Open the duplicate file tool in PromptBook.
4. Load the DupeGuru result file.
5. Use the available actions to mirror metadata across duplicate entries where appropriate.

After removing duplicate files outside PromptBook, use the unlinked entry tool to clean up entries whose files no longer exist.

For more information, see [Tools & Macros](macros.md).

## Saving and Backups

PromptBook saves normal library metadata changes during use.

For backups, copy the library folder together with its `.PromptBook` folder.

Example:

```text
My Library/
├─ .PromptBook/
├─ Images/
├─ Videos/
└─ Prompts/
```

The `.PromptBook` folder contains the local library database and must stay with the library files.

## Launch Arguments

PromptBook supports a small set of launch arguments when started from the command line.

Because some inherited internal names still exist, the current source entry point may still be:

```sh
python src/tagstudio/main.py
```

Supported arguments:

| Argument | Short | Description |
| -------- | ----- | ----------- |
| `--open <path>` | `-o` | Opens a PromptBook library folder on startup. |
| `--settings-file <path>` | `-s` | Uses a specific PromptBook `.toml` global settings file. |
| `--cache-file <path>` | `-c` | Uses a specific PromptBook `.ini` or `.plist` cache file. |
| `--debug` | | Reveals additional internal data useful for debugging. |
| `--version` | `-v` | Displays PromptBook version information. |

Example:

```sh
python src/tagstudio/main.py --open "/path/to/my/library"
```

!!! note
    The `src/tagstudio/main.py` path is inherited from the original codebase and may be renamed later.