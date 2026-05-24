---
icon: material/code-braces
---

# :material-code-braces: Developing

This page explains how to set up a local development environment for PromptBook.

PromptBook is currently based on the TagStudio codebase, so some internal module names, file paths, scripts, and build files may still use the original `tagstudio` name. These names should only be changed when the corresponding code has also been updated.

!!! tip "Contributing"
    If you want to contribute to PromptBook, please read the repository's contribution guidelines first:

    [CONTRIBUTING.md](https://github.com/joolaszlo/PromptBook/blob/main/CONTRIBUTING.md)

## Installing Python

Python [3.12](https://www.python.org/downloads) is required to develop PromptBook. Any version matching `Python 3.12.x` should work.

Alternatively, you can use a tool such as [pyenv](https://github.com/pyenv/pyenv) to install this version of Python without affecting any existing Python installations on your system. Tools such as [uv](#installing-with-uv) can also install Python versions.

!!! info "Python Aliases"
    Depending on your system, Python may be called `python`, `py`, `python3`, or `py3`. These instructions use the alias `python` for consistency.

If you already have Python installed on your system, you can check the version by running the following command:

```sh
python --version
```

---

### Installing with pyenv

If you choose to install Python using pyenv, please refer to the following instructions:

1. Follow pyenv's [install instructions](https://github.com/pyenv/pyenv/?tab=readme-ov-file#installation) for your system.
2. Install the appropriate Python version with pyenv by running:

```sh
pyenv install 3.12
```

3. Navigate to the repository root folder in your terminal and run:

```sh
pyenv local 3.12
```

You could alternatively use `pyenv shell 3.12` or `pyenv global 3.12` to set the Python version for the current terminal session or for the entire system. Using `local` is recommended for development inside this repository.

---

## Cloning from GitHub

The repository can be cloned or downloaded via `git` in your terminal, or by downloading the zip file from the "Code" button on the [repository page](https://github.com/joolaszlo/PromptBook).

```sh
git clone https://github.com/joolaszlo/PromptBook.git
cd PromptBook
```

## Installing Dependencies

To install the required dependencies, you can use a dependency manager such as [uv](https://docs.astral.sh/uv) or [Poetry 2.0](https://python-poetry.org).

Alternatively, you can create a virtual environment and manually install the dependencies yourself.

### Installing with uv

If using [uv](https://docs.astral.sh/uv), you can install the dependencies for PromptBook with the following command:

```sh
uv pip install -e ".[dev]"
```

A reference `.envrc` is provided for use with [direnv](#direnv), see [`contrib/.envrc-uv`](https://github.com/joolaszlo/PromptBook/blob/main/contrib/.envrc-uv).

---

### Installing with Poetry

If using [Poetry](https://python-poetry.org), you can install the dependencies for PromptBook with the following command:

```sh
poetry install --with dev
```

---

### Manual Installation

If you choose to manually set up a virtual environment and install dependencies instead of using a dependency manager, please refer to the following instructions:

!!! tip "Virtual Environments"
    Learn more about setting up a virtual environment with Python's [official tutorial](https://docs.python.org/3/tutorial/venv.html).

1. In the root repository directory, create a Python virtual environment:

```sh
python -m venv .venv
```

2. Activate your environment:

- Windows with PowerShell: `.venv\Scripts\Activate.ps1`
- Windows with Command Prompt: `.venv\Scripts\activate.bat`
- Linux/macOS: `source .venv/bin/activate`

!!! info "Supported Shells"
    Depending on your system, the regular activation script may not work on alternative shells. In this case, refer to the table below for supported shells:

| Shell | Script |
| ---------: | :------------------------ |
| Bash/ZSH | `.venv/bin/activate` |
| Fish | `.venv/bin/activate.fish` |
| CSH/TCSH | `.venv/bin/activate.csh` |
| PowerShell | `.venv/bin/activate.ps1` |

3. Use the following pip command to create an editable installation and install the required development dependencies:

```sh
pip install -e ".[dev]"
```

## Nix(OS)

If using [Nix](https://nixos.org/), there is a development environment already provided in the [flake](https://wiki.nixos.org/wiki/Flakes) that is accessible with the following command:

```sh
nix develop
```

A reference `.envrc` is provided for use with [direnv](#direnv), see [`contrib/.envrc-nix`](https://github.com/joolaszlo/PromptBook/blob/main/contrib/.envrc-nix).

## Tooling

### Editor Integration

The current inherited entry point is `src/tagstudio/main.py`. You can target this file from your IDE to run or connect a debug session.

The example below shows a VS Code launch configuration. You can also use [launch arguments](./usage.md/#launch-arguments) to pass your own test [libraries](libraries.md) while developing.

You can find more editor configurations in [`contrib`](https://github.com/joolaszlo/PromptBook/tree/main/contrib).

=== "VS Code"

    ```json title=".vscode/launch.json"
    {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "PromptBook",
                "type": "python",
                "request": "launch",
                "program": "${workspaceRoot}/src/tagstudio/main.py",
                "console": "integratedTerminal",
                "justMyCode": true,
                "args": ["-o", "~/Documents/Example"]
            }
        ]
    }
    ```

!!! note
    The `src/tagstudio/main.py` path is an inherited internal path from the original TagStudio codebase. It may be renamed later as the PromptBook conversion continues.

### pre-commit

There is a [pre-commit](https://pre-commit.com/) configuration that will run checks before code is committed. Namely, mypy and the Ruff linter and formatter will check your code.

Once you have pre-commit installed, run:

```sh
pre-commit install
```

From there, Git will automatically run the hooks during commit actions.

### direnv

You can automatically enter this development shell with a tool like [direnv](https://direnv.net/).

Some reference `.envrc` files are provided in the repository at [`contrib`](https://github.com/joolaszlo/PromptBook/tree/main/contrib).

Two currently available variants are for [Nix](#nixos) and [uv](#installing-with-uv). To use one:

```sh
ln -s .envrc-$variant .envrc
```

You will have to allow usage of it.

!!! warning "direnv Security Framework"
    These files should be checked before allowing them, because they execute commands when the directory is loaded. direnv only runs `.envrc` files you have allowed, and it tracks whether they have changed. If an `.envrc` file changes, you may need to allow it again.

```sh
cat .envrc
direnv allow
```

## Building

To build your own executables of PromptBook, first follow the steps in [Installing Dependencies](#installing-dependencies).

The current inherited PyInstaller spec file is still named `tagstudio.spec`. Until this file is renamed in the codebase, use the following command:

```sh
pyinstaller tagstudio.spec
```

If you are on Windows or Linux and want to build a portable executable, pass the following flag:

```sh
pyinstaller tagstudio.spec -- --portable
```

The resulting executable file or files will be located in a new folder named `dist`.

!!! note
    The `tagstudio.spec` file name is inherited from the original TagStudio project. It should only be renamed after the build configuration has been updated and tested.

