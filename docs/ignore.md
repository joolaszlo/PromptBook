---
title: Ignoring Files
icon: material/file-document-remove
---

# :material-file-document-remove: Ignoring Files & Directories

PromptBook can ignore specific files and directories through a `.ts_ignore` file located inside your [library's](libraries.md) `.PromptBook` folder.

This file uses glob-style pattern matching similar to the [`.gitignore`](https://git-scm.com/docs/gitignore) file used by Git™[^1].

The `.ts_ignore` file can be edited within PromptBook or opened in an external editor by going to the "Edit -> Ignore Files" option in the menu bar.

This file is only used when scanning directories for new files to add to your library. It does not apply to files that have already been added to your library.

!!! tip
    If you just want examples for common tasks, such as ignoring a single file type or ignoring a specific folder, jump to the [Use Cases](#use-cases) section.

=== "Example .ts_ignore file"

    ```toml title="My Library/.PromptBook/.ts_ignore"
    # PromptBook .ts_ignore file.

    # Code
    __pycache__
    .pytest_cache
    .venv
    .vs

    # Projects
    Minecraft/**/Metadata
    Minecraft/Website
    !Minecraft/Website/*.png
    !Minecraft/Website/*.css

    # Documents
    *.doc
    *.docx
    *.ppt
    *.pptx
    *.xls
    *.xlsx
    ```

## Pattern Format

!!! note ""
    This section is sourced and adapted from Git's[^1] `.gitignore` [documentation](https://git-scm.com/docs/gitignore).

### Internal Processes

When scanning your library directories, the `.ts_ignore` file is read by either the [`wcmatch`](https://facelessuser.github.io/wcmatch/glob/) library or [`ripgrep`](https://github.com/BurntSushi/ripgrep) in glob mode, depending on whether `ripgrep` is installed on your system and detected by PromptBook.

Ripgrep is the preferred method for scanning directories because of its improved performance and its pattern matching behavior.

This mixture of tools may lead to slight inconsistencies if `ripgrep` is not available.

---

### Comments (`#`)

A `#` symbol at the start of a line indicates that the line is a comment and matches no items.

Blank lines are used to improve readability and also match no items.

- A `#` symbol can be escaped by putting a backslash (`\`) in front of it.

=== "Example comment"

    ```toml
    # This is a comment.
    file_that_is_being_matched.txt

    # file_that_is_NOT_being_matched.png
    file_that_is_being_matched.png
    ```

=== "Organizing with comments"

    ```toml
    # PromptBook .ts_ignore file.

    # Minecraft Stuff
    Minecraft/**/Metadata
    Minecraft/Website
    !Minecraft/Website/*.png
    !Minecraft/Website/*.css

    # Microsoft Office
    *.doc
    *.docx
    *.ppt
    *.pptx
    *.xls
    *.xlsx
    ```

=== "Escape a # symbol"

    ```toml
    # To ensure a file named '#hashtag.jpg' is ignored:
    \#hashtag.jpg
    ```

---

### Directories (`/`)

The forward slash (`/`) is used as the directory separator.

Separators may occur at the beginning, middle, or end of the `.ts_ignore` search pattern.

- If there is a separator at the beginning or middle of the pattern, the pattern is relative to the library root.
- The library root is the folder that contains the `.PromptBook` folder.
- If there is no separator, the pattern may match at any level inside the library.
- If there is a separator at the end of the pattern, the pattern will only match directories.
- Otherwise, the pattern can match both files and directories.

=== "Example folder pattern"

    ```toml
    # Matches "frotz" and "a/frotz" if they are directories.
    frotz/
    ```

=== "Example nested folder pattern"

    ```toml
    # Matches "doc/frotz" but not "a/doc/frotz".
    doc/frotz/
    ```

---

### Negation (`!`)

A `!` prefix before a pattern negates the pattern, allowing files matched by previous patterns to be included again.

- Any matching file excluded by a previous pattern will become included again.
- It is not possible to re-include a file if a parent directory of that file is excluded.

=== "Example negation"

    ```toml
    # All .jpg files will be ignored, except any located in the "Photos" folder.
    *.jpg
    Photos/!*.jpg
    ```

=== "Escape a ! symbol"

    ```toml
    # To ensure a file named '!wowee.jpg' is ignored:
    \!wowee.jpg
    ```

---

### Wildcards

#### Single Asterisks (`*`)

An asterisk (`*`) matches anything except a slash.

=== "File examples"

    ```toml
    # Matches all .png files in the "Images" folder.
    Images/*.png

    # Matches all .png files in all folders.
    *.png
    ```

=== "Folder examples"

    ```toml
    # Matches any files or folders directly in "Images/" but not deeper levels.
    # Matches file "Images/mario.jpg"
    # Matches folder "Images/Mario"
    # Does not match file "Images/Mario/cat.jpg"
    Images/*
    ```

#### Question Marks (`?`)

The character `?` matches any one character except `/`.

=== "File examples"

    ```toml
    # Matches any .png file starting with "IMG_" and ending in any four characters.
    # Matches "IMG_0001.png"
    # Matches "Photos/IMG_1234.png"
    # Does not match "IMG_1.png"
    IMG_????.png

    # Same as above, except matches any file extension instead of only .png.
    IMG_????.*
    ```

=== "Folder examples"

    ```toml
    # Matches all files in any direct subfolder of "Photos" beginning with "20".
    # Matches "Photos/2000"
    # Matches "Photos/2024"
    # Matches "Photos/2099"
    # Does not match "Photos/1995"
    Photos/20??/
    ```

#### Double Asterisks (`**`)

Two consecutive asterisks (`**`) in patterns matched against a full pathname may have special meaning:

- A leading `**` followed by a slash matches in all directories.
- A trailing `/**` matches everything inside.
- A slash followed by `**` followed by another slash matches zero or more directories.
- Other consecutive asterisks are considered regular asterisks and will match according to the previous rules.

=== "Leading **"

    ```toml
    # Both match file or directory "foo" anywhere.
    **/foo
    foo

    # Matches file or directory "bar" anywhere that is directly under directory "foo".
    **/foo/bar
    ```

=== "Trailing /**"

    ```toml
    # Matches all files inside directory "abc" with infinite depth.
    abc/**
    ```

=== "Middle /**/"

    ```toml
    # Matches "a/b", "a/x/b", "a/x/y/b", and so on.
    a/**/b
    ```

#### Square Brackets (`[a-z]`)

Character sets and ranges use characters inside brackets (`[]`) for more specific matching.

The range notation, such as `[a-zA-Z]`, can be used to match one character from a range.

!!! tip
    For more detailed examples and explanations, see the [`glob`](https://man7.org/linux/man-pages/man7/glob.7.html) man page.

=== "Range examples"

    ```toml
    # Matches all files that start with "IMG_" and end in a single numeric character.
    # Matches "IMG_0.jpg"
    # Matches "IMG_7.png"
    # Does not match "IMG_10.jpg"
    # Does not match "IMG_A.jpg"
    IMG_[0-9]

    # Matches all files that start with "IMG_" and end in a single alphabetic character.
    IMG_[a-z]
    ```

=== "Set examples"

    ```toml
    # Matches all files that start with "draft_" and end in one character from the set.
    # Matches "draft_a.docx"
    # Matches "draft_b.docx"
    # Matches "draft_c.docx"
    # Does not match "draft_d.docx"
    draft_[abc]
    ```

---

## Use Cases

### Ignoring Files by Extension

=== "Ignore all .jpg files"

    ```toml
    *.jpg
    ```

=== "Ignore all files except .jpg files"

    ```toml
    *
    !*.jpg
    ```

=== "Ignore all .jpg files in specific folders"

    ```toml
    ./Photos/Worst Vacation/*.jpg
    Music/Artwork
    Art/*.jpg
    ```

!!! tip "Ensuring Complete Extension Matches"
    For some file types, it may be necessary to specify different casing and alternative spellings in order to match all possible variations of an extension in your library.

```toml title="Ignore most possible JPEG file extensions"
# The JPEG Cinematic Universe
*.jpg
*.jpeg
*.jfif
*.jpeg_large
*.JPG
*.JPEG
*.JFIF
*.JPEG_LARGE
```

### Ignoring a Folder

=== "Ignore all folders named Cache"

    ```toml
    # Matches any folder called "Cache" no matter where it is in your library.
    Cache/
    cache/
    ```

=== "Ignore a Downloads folder in the library root"

    ```toml
    # "Downloads" must be a folder in the library root.
    # It must be on the same level as the ".PromptBook" folder.
    # Does not match folders named "Downloads" elsewhere in your library.
    # Does not match a file called "Downloads".
    /Downloads/
    ```

=== "Ignore .jpg files in specific folders"

    ```toml
    Photos/Worst Vacation/*.jpg
    /Music/Artwork
    Art/*.jpg
    ```

[^1]: The term "Git" is a licensed trademark of "The Git Project", a member of the Software Freedom Conservancy. Git is released under the [GNU General Public License version 2.0](https://opensource.org/license/GPL-2.0), an open source license.

PromptBook is not associated with the Git Project. It only includes ignore pattern behavior based on similar concepts.