---
icon: material/file
---

# :material-file: Entries

Entries are the individual representations of your files inside a PromptBook [library](./index.md). Each one corresponds one-to-one to a file on disk, and tracks all of the additional [tags](tags.md) and metadata that you attach to it inside PromptBook.

## Storage

File entry data is stored within the `ts_library.sqlite` file inside each library's `.PromptBook` folder. No modifications are made to your actual files on disk, and nothing like sidecar files are generated for your files.

The internal database schema is an implementation detail and may change between versions. Developers who need the current model layout can refer to the [database schema](database-schema.md) notes.

## Appearance

File entries appear as thumbnails inside the grid display. The preview panel shows a more detailed preview of the file, along with extra file stats and all attached PromptBook tags and fields.

## Unlinked Entries

If the file that an entry is referencing has been moved, renamed, or deleted on disk, then PromptBook will display its unlinked status with a red chain-link icon instead of its thumbnail image. Certain uncached stats such as the file size and image dimensions will also be unavailable to see in the preview panel.

To fix file entries that have become unlinked, select the "Fix Unlinked Entries" option from the Tools menu. From there, refresh the unlinked entry count and choose whether to search and relink your files, and/or delete the file entries from your library. This will NOT delete or modify any files on disk.
