---
icon: material/download
---

# :material-download: Installation

PromptBook is currently in early development.

Executable releases are planned to be distributed through the PromptBook GitHub repository. Until public release builds are available, the recommended way to run PromptBook is from source.

## Executable Releases

When executable builds are available, they will be published on the PromptBook GitHub Releases page:

[PromptBook Releases](https://github.com/joolaszlo/PromptBook/releases)

Download the latest release for your operating system from the "Assets" section of the release page.

Planned release targets may include:

- :fontawesome-brands-windows: **Windows**
- :fontawesome-brands-apple: **macOS**
- :material-penguin: **Linux**

!!! info "Third-Party Dependencies"
    You may need to install [third-party dependencies](#third-party-dependencies), such as FFmpeg, to use the full preview and playback feature set.

!!! warning ":fontawesome-brands-apple: macOS Privacy & Security Popup"
    On macOS, unsigned or unnotarized application builds may be blocked the first time they are opened.

    If this happens, open the macOS "Settings" app, go to "Privacy & Security", find the blocked application message, and choose "Open Anyway".

    You should only have to do this once after downloading the application.

---

## Package Managers

!!! danger "Unofficial Releases"
    PromptBook is not currently published to remote package repositories.

    Any PromptBook distributions outside of the official GitHub repository are unofficial and are not maintained by this project.

Use unofficial packages at your own risk.

---

## Running from Source

PromptBook can be installed and run from source with Python.

Make sure you have Python 3.12 installed.

### Clone the Repository

```sh
git clone https://github.com/joolaszlo/PromptBook.git
cd PromptBook
```

### Create a Virtual Environment

```sh
python -m venv .venv
```

Activate the virtual environment:

=== "Windows PowerShell"

    ```sh
    .venv\Scripts\Activate.ps1
    ```

=== "Windows Command Prompt"

    ```sh
    .venv\Scripts\activate.bat
    ```

=== "Linux/macOS"

    ```sh
    source .venv/bin/activate
    ```

### Install PromptBook

```sh
pip install .
```

### Launch PromptBook

The current inherited source entry point is:

```sh
python src/tagstudio/main.py
```

If installed as a package, the current inherited command may also be available:

```sh
tagstudio
```

!!! note
    The `src/tagstudio/main.py` path and `tagstudio` command name are inherited from the original TagStudio codebase.

    They may be renamed later as the PromptBook conversion continues.

For development setup, see the [Developing](developing.md) page.

---

## Linux Dependencies

Some external dependencies may be required on Linux.

| Package | Reason |
| --------------- | --------------- |
| [dbus](https://repology.org/project/dbus) | required for Qt and opening desktop applications |
| [ffmpeg](https://repology.org/project/ffmpeg) | audio/video thumbnails and playback |
| libstdc++ | required for Qt |
| [libva](https://repology.org/project/libva) | hardware rendering with VAAPI |
| [libvdpau](https://repology.org/project/libvdpau) | hardware rendering with VDPAU |
| [libx11](https://repology.org/project/libx11) | required for Qt |
| libxcb-cursor OR [xcb-util-cursor](https://repology.org/project/xcb-util-cursor) | required for Qt |
| [libxkbcommon](https://repology.org/project/libxkbcommon) | required for Qt |
| [libxrandr](https://repology.org/project/libxrandr) | hardware rendering |
| [pipewire](https://repology.org/project/pipewire) | PipeWire audio support |
| [qt](https://repology.org/project/qt) | required |
| [qt-multimedia](https://repology.org/project/qt) | required |
| [qt-wayland](https://repology.org/project/qt) | Wayland support |

---

## Third-Party Dependencies

!!! tip
    You can check whether these dependencies are correctly detected by launching PromptBook and opening the About window from the menu bar.

### FFmpeg/FFprobe

For audio and video thumbnails and playback, install [FFmpeg](https://ffmpeg.org/download.html).

If you encounter issues with FFmpeg, see the [FFmpeg Help](./help/ffmpeg.md) guide.

### RAR Extractor

To generate thumbnails for RAR-based files, such as `.cbr` comic book archives, you need an extractor capable of handling RAR files.

- :material-penguin: On Linux, install either `unrar` or `unrar-free` from your package manager.
- :fontawesome-brands-apple: On macOS, `unrar` can be installed through Homebrew's [`rar`](https://formulae.brew.sh/cask/rar) formula.
- :fontawesome-brands-windows: On Windows, install either [`WinRAR`](https://www.rarlab.com/download.htm) or [`7-Zip`](https://www.7-zip.org/) and add its folder to your `PATH`.

!!! tip "WinRAR License"
    Both `unrar` and `WinRAR` require a license, but the evaluation copy has no time limit. You can dismiss the prompt.

### ripgrep

[`ripgrep`](https://github.com/BurntSushi/ripgrep) is recommended to improve directory scanning performance.

PromptBook can use ripgrep with the [`.ts_ignore`](ignore.md) pattern matching system to exclude files and directories during scans.

Ripgrep is already pre-installed on some Linux distributions and is also available from several package managers.