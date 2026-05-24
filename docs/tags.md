---
icon: material/tag-text
---

# :material-tag-text: Tags

Tags are reusable labels that describe something about an entry.

In PromptBook, tags can be used for people, characters, places, styles, models, projects, prompt types, generated media types, workflow states, and any other information that helps organize your library.

Unlike simple hashtag-based systems, PromptBook tags can have additional properties, aliases, colors, and relationships with other tags.

## Naming Tags

PromptBook tags are flexible.

Tag names:

- do **not** have to be unique
- are **not** limited to specific characters
- can have aliases
- can have a shorthand name
- can be connected to parent tags

### Name

The main display name of the tag.

This can be any text you want.

Examples:

```text
portrait
cyberpunk
Midjourney
character reference
blue dress
```

### Shorthand

A shorthand is a shorter version of the tag name.

It is useful when the full tag name is long or when a shorter display name is easier to read.

Example:

```text
Name:
Stable Diffusion

Shorthand:
SD
```

Tag shorthands can also be used when searching for tags.

### Aliases

Aliases are alternate names for the same tag.

They are useful for:

- alternate spellings
- translated names
- common abbreviations
- old names
- related search terms

Example:

```text
Name:
science fiction

Aliases:
sci-fi
scifi
sf
```

When searching for tags, aliases can help find the correct tag even if you do not type the main tag name.

## Disambiguation

Different tags can have the same or similar names.

Disambiguation helps make those tags easier to tell apart by displaying a parent tag name next to the tag.

For example, you might have several tags named:

```text
Jinx
```

One could be a character name, another could be part of a project, and another could be used in a different context.

A disambiguating parent tag can make the displayed name clearer:

```text
Jinx (Arcane)
Jinx (Project Name)
```

![Tag Disambiguation Example](assets/tag_disambiguation_example.png)

The base tag name remains unchanged. PromptBook only uses the selected parent tag to make the displayed name clearer.

## Parent Tags

Tags can have parent tags.

A parent tag describes a broader category or relationship.

Example:

```text
Child tag:
portrait

Parent tag:
image type
```

Another example:

```text
Child tag:
cyberpunk

Parent tag:
style
```

Parent tags can help organize related tags and make broader tag relationships easier to understand.

## Why Parent Tags Are Useful

### Simpler Tagging

Instead of adding every broad category manually to every entry, you can create useful relationships between tags.

Example:

```text
cyberpunk
└── style
```

If `cyberpunk` has `style` as a parent tag, then the relationship is stored once on the tag instead of being manually repeated everywhere.

### Better Organization

Parent tags can help keep large tag collections understandable.

For prompt and media workflows, this can be useful for groups such as:

```text
style
character
location
project
model
generator
workflow status
reference type
```

### Easier Rediscovery

Parent relationships can help you rediscover entries through broader categories.

For example, if several specific style tags are connected to a broader `style` tag, it becomes easier to browse or reason about those tags later.

![Shrek Tag Details](assets/built_tag_shrek.png)

## Tag Appearance

### Color

Tags can use built-in colors or custom colors.

Colors make tags easier to recognize in lists, panels, and entry metadata.

![Tag Color Selection](assets/tag_color_selection.png)

Custom palettes and colors can be created with the [Tag Color Manager](colors.md).

![Custom Tag Color Selection](assets/custom_tag_color_selection.png)

### Icon

Tags currently have an internal icon field, but icon support should be treated as unfinished unless it is fully exposed in the current user interface.

Do not rely on tag icons as a stable user-facing feature yet.

## Tag Properties

Tags can have properties that change how they behave or how they are shown.

### Is Category

The **Is Category** property marks a tag as a category.

Category tags can be used to organize other tags into visible groups.

Example:

```text
Category tag:
Character

Tags under that category:
main character
side character
villain
npc
```

If a tag inherits from a category tag through parent tags, it can appear under that category in the UI.

A tag can inherit from more than one category. In that case, it may appear in more than one category group.

![Tag Category Example](assets/tag_categories_example.png)

### Is Hidden

The **Is Hidden** property marks a tag as hidden.

Entries with hidden tags are hidden by default in normal browsing and search results.

Use the **Show hidden entries** option if you want entries with hidden tags to appear.

The built-in `Archived` tag uses hidden behavior.

### Pinned

Pinned tags are shown in a more accessible place in the interface.

Use pinned tags for tags you apply or filter by often.

Examples:

```text
favorite style tags
common workflow status tags
frequently used project tags
important prompt categories
```

### Favorite

Favorite tags are another way to mark important tags.

Depending on the current UI, favorite tags may be shown separately or made easier to access.

## Built-in Tags

PromptBook includes built-in tags used for common metadata behavior.

Current built-in examples include:

```text
Favorite
Archived
Meta Tags
```

These can be used as part of normal organization, but they may also have special default behavior.

For example, `Archived` is hidden by default.

## Tags and Search

Tags can be used in two main ways during search:

1. text search in tag names, shorthands, or aliases
2. selected tag filters

For current search behavior, see [Searching](search.md).

## PromptBook Tagging Examples

For AI-generated media workflows, useful tag groups may include:

### Content Type

```text
image
video
prompt
reference
character sheet
background
variation
```

### Style

```text
cyberpunk
watercolor
anime
old photo
90s sitcom
vintage newspaper
```

### Subject

```text
portrait
cat
spaceship
medieval town
city street
bedroom
```

### Workflow Status

```text
favorite
archived
unfinished
needs edit
final
reference only
```

### Generator or Model

```text
Midjourney
Stable Diffusion
DALL-E
Runway
Kling
Sora
```

Use whatever structure fits your own library. PromptBook does not require a fixed tag system.