---
icon: material/magnify
---

# :material-magnify: Searching

PromptBook provides a simple search field together with tag filters and selectable search scopes.

The main search field is intended for quick text search. Tag selection is handled separately, so selected tags do not need to be written into the search field.

## Main Search Field

Use the search field at the top of the library view to search for text.

After typing a search term, press Enter or click the Search button to update the results.

Clearing the search field also clears the active text search.

## Search In

The "Search in" options control where the text from the main search field is searched.

Available options:

- **Tags**
- **Title**
- **Prompt**

By default:

- **Tags** is disabled
- **Title** is enabled
- **Prompt** is enabled

This means that a normal text search will search entry titles and prompt text by default, but not tag names unless the Tags option is enabled.

## Title Search

When **Title** is enabled, PromptBook searches the entry title field.

Use this when you want to find entries by their displayed title or manually added title metadata.

## Prompt Search

When **Prompt** is enabled, PromptBook searches the prompt or description text field.

Use this when you want to find entries by prompt text, generation notes, descriptions, or similar long-form text attached to entries.

!!! note
    Internally, the current implementation searches the description text field for the Prompt scope. This may be renamed or refined later as PromptBook's prompt-specific fields develop.

## Tag Text Search

When **Tags** is enabled under "Search in", the main search field can match tag information.

Tag text search can match:

- tag names
- tag shorthands
- tag aliases

This is different from selecting tags as filters. Tag text search finds entries whose attached tags match the text you typed.

## Search Scope Logic

If more than one "Search in" option is enabled, PromptBook uses OR logic between those text scopes.

For example, if **Title** and **Prompt** are enabled, an entry can match if the search text appears in either:

- the title field
- the prompt or description field

If **Tags** is also enabled, an entry can also match if one of its attached tags matches the search text.

## Selected Tag Filters

Tags can also be selected directly from the tag UI, pinned tags, favorite tags, or tag panels.

Selected tags act as filters separate from the main text search field.

This means you can combine:

- a text search
- one or more selected tags
- selected search scopes

For example, you can search for:

```text
red dress
```

while also selecting tags such as:

```text
character
portrait
```

This will narrow the results to entries that match the text search and also have the selected tags.

## Multiple Selected Tags

When multiple tags are selected as active filters, PromptBook uses AND logic.

This means an entry must contain all selected tags to appear in the results.

Example:

```text
Selected tags:
portrait
female
cyberpunk
```

The result list will only show entries that have all three selected tags.

## Excluded Tags

PromptBook also supports excluded tag filters.

An excluded tag removes entries from the results if they contain that tag.

Example:

```text
Included tag:
portrait

Excluded tag:
unfinished
```

This will show portrait entries, but hide entries tagged as unfinished.

## Resetting Tag Selection

Use **Reset Selection** to clear the currently selected tag filters.

This only resets the tag selection. It does not necessarily remove the text typed into the main search field.

## Combining Text Search and Tags

Text search and selected tag filters are combined.

In practice:

- selected tags narrow the library by tag
- excluded tags remove matching entries
- the search field narrows the remaining results by text
- active "Search in" options decide where the text is searched

Example:

```text
Search field:
castle

Search in:
Title enabled
Prompt enabled
Tags disabled

Selected tags:
fantasy
background
```

This searches for entries that:

- have the `fantasy` tag
- have the `background` tag
- contain `castle` in the title or prompt text

## Hidden Entries

Entries with hidden tags are hidden by default.

Use the **Show hidden entries** option if you want hidden entries to appear in search results.

## Advanced Search Syntax

Some inherited advanced query behavior may still exist internally, but the current PromptBook user interface is centered around:

- the main search field
- the Search in options
- selected tag filters
- excluded tag filters

Older TagStudio-style query examples such as manual `tag:`, `tag_id:`, `path:`, or `special:` searches should not be treated as the primary PromptBook search workflow unless they are reintroduced and tested in the current UI.