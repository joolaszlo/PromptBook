---
icon: material/movie-open-cog
---

# :material-movie-open-cog: Installing FFmpeg

FFmpeg is required for thumbnail previews and playback features on audio and video files.

FFmpeg is a free open source project for handling multimedia files, including video and audio files.

For more information, see the official FFmpeg website:

[ffmpeg.org](https://www.ffmpeg.org/)

## Installation on Windows

### Prebuilt Binaries

Prebuilt binaries from trusted sources are available from the FFmpeg download page:

[FFmpeg Downloads](https://www.ffmpeg.org/download.html)

Under "More downloading options", click the Windows section, then under "Windows EXE Files", select a source to download a build from.

Follow the download instructions from the build website you choose.

![Windows Download Location](../assets/ffmpeg_windows_download.png)

!!! warning
    Do **not** download the source code by mistake.

To install FFmpeg manually on Windows:

1. Download the `.7z` or `.zip` file.
2. Extract it.
3. Move the extracted contents to a dedicated folder, for example:

```text
C:\ffmpeg
```

or:

```text
C:\Program Files\ffmpeg
```

4. Add FFmpeg's `bin` folder to your system PATH.

Example PATH entry:

```text
C:\ffmpeg\bin
```

or:

```text
C:\Program Files\ffmpeg\bin
```

To edit PATH on Windows:

1. Search for "Edit the system environment variables".
2. Open it from Control Panel.
3. Click "Environment Variables".
4. Under "User variables", select "Path".
5. Click "Edit".
6. Click "New".
7. Add the FFmpeg `bin` path.
8. Click "OK".

### Package Managers

FFmpeg is also available through Windows package managers:

```sh
winget install ffmpeg
```

```sh
scoop install main/ffmpeg
```

```sh
choco install ffmpeg-full
```

## Installation on macOS

### Homebrew

FFmpeg can be installed with [Homebrew](https://brew.sh/):

```sh
brew install ffmpeg
```

FFmpeg downloads for macOS are also listed on the official FFmpeg download page:

[FFmpeg Downloads](https://www.ffmpeg.org/download.html)

## Installation on Linux

FFmpeg may already be installed on some Linux distributions.

If it is not installed, use your distribution's package manager.

### Debian / Ubuntu

```sh
sudo apt install ffmpeg
```

### Fedora

```sh
sudo dnf install ffmpeg-free
```

### Arch Linux

```sh
sudo pacman -S ffmpeg
```

## Checking the Installation

After installing FFmpeg, open a terminal and run:

```sh
ffmpeg -version
```

You can also check FFprobe:

```sh
ffprobe -version
```

If both commands return version information, FFmpeg is available on your system PATH.

## Help

If FFmpeg is installed but PromptBook still cannot detect it, restart PromptBook first.

If the problem remains, check that the FFmpeg `bin` folder is available on your system PATH.