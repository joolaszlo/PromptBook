---
icon: material/text-box
---

# :material-text-box: Fields

Fields are additional types of metadata that you can attach to [file entries](./entries.md).

Like [tags](tags.md), fields are not stored inside the original files themselves and are not written to sidecar files. They are stored inside the PromptBook [library](./libraries.md) database.

Fields are useful for information that belongs to an entry but does not work well as a tag, such as a title, author, source URL, description, notes, or date.

## Field Types

### Text Line

A short text value displayed as a single line.

Examples:

- Title
- Author
- Artist
- URL
- Source
- Publisher

### Text Box

A longer text value displayed as a larger text area.

Examples:

- Description
- Notes
- Comments
- Prompt text
- Generation notes

### Datetime

A date and time value.

Examples:

- Date
- Date Created
- Date Modified
- Date Published
- Date Released
- Date Uploaded

## Storage

Field data is stored in the PromptBook library database.

The exact internal database structure is an implementation detail and may change between versions. Developers who need schema details should refer to the current [Database Schema](./database-schema.md) documentation and the SQLAlchemy models in the source code.