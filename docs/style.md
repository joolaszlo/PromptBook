---
icon: material/sign-text
---

# :material-sign-text: Style Guide

This page describes general code style expectations for PromptBook development.

PromptBook is still based on the original TagStudio codebase, so older files may not follow every guideline listed here. When editing existing code, prefer small, focused cleanup over broad unrelated refactors.

## Formatting

Most formatting and linting rules can be checked, fixed, or enforced with Ruff.

General guidelines:

- Write clear, concise, and modular code.
- Prefer private methods by default, for example `__method()`.
- Use protected methods, for example `_method()`, only when subclass access is needed.
- Use public methods, for example `method()`, only when they are part of the intended external API.
- Keep the maximum line width at **100** characters.
- Use comments to explain code that cannot clearly explain itself.
- Use [Google style](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings) docstrings for new classes and functions.
- When modifying an existing function without docstrings, add docstrings only if they improve clarity.
- Keep imports ordered alphabetically.
- Keep lists of values ordered using their [natural sort order](https://en.wikipedia.org/wiki/Natural_sort_order), where appropriate.
- If a file already follows a clear method ordering pattern, preserve that pattern unless there is a good reason to change it.
- If a rule is not covered here, follow [PEP 8](https://peps.python.org/pep-0008/).

## Qt

The Qt frontend still contains inherited structure from the original codebase. Some files mix view setup, event handling, and controller logic.

When adding or restructuring Qt code, prefer separating view code from controller logic.

A useful structure is:

```text
qt/
├── controllers/
│   ├── widgets/
│   │   └── preview_panel_controller.py
│   └── main_window_controller.py
├── views/
│   ├── widgets/
│   │   └── preview_panel_view.py
│   └── main_window_view.py
├── ts_qt.py
└── mixed.py
```

In this structure:

- `views` contain UI construction and UI-only behavior.
- `controllers` contain application logic and event handling.
- For every `_view.py` file, there should usually be a matching `_controller.py` file.
- The controller class is usually named after the widget itself, not `SomethingController`, because it is the class used by other code.

Example view:

```py
# my_cool_widget_view.py

class MyCoolWidgetView(QWidget):
    def __init__(self):
        super().__init__()

        self.__button = QPushButton()
        self.__color_dropdown = QComboBox()

        self.__connect_callbacks()

    def __connect_callbacks(self):
        self.__button.clicked.connect(self._button_click_callback)
        self.__color_dropdown.currentIndexChanged.connect(
            lambda idx: self._color_dropdown_callback(
                self.__color_dropdown.itemData(idx)
            )
        )

    def _button_click_callback(self):
        raise NotImplementedError()

    def _color_dropdown_callback(self, color: Color):
        raise NotImplementedError()
```

Example controller:

```py
# my_cool_widget_controller.py

class MyCoolWidget(MyCoolWidgetView):
    def __init__(self):
        super().__init__()

    def _button_click_callback(self):
        print("Button was clicked!")

    def _color_dropdown_callback(self, color: Color):
        print(f"The selected color is now: {color}")
```

Key points:

- UI elements should usually be private variables inside the view.
- Controllers should not directly access private UI elements.
- Views should expose a protected API when the controller needs to read or update UI state.
- Callback methods should be protected methods defined by the view and implemented by the controller.
- If code requires non-UI imports, it usually does not belong in a `*_view.py` file.

## Scope of Cleanup

Avoid large formatting-only rewrites unless the file is already being actively refactored.

When changing existing code:

- keep the change focused
- avoid unrelated renaming
- avoid large movement of code unless needed
- preserve existing behavior unless the change intentionally modifies it
- document important behavior changes in comments, docs, or release notes where appropriate

## References

For an explanation of the Model-View-Controller pattern, see:

[MVC Framework Introduction](https://www.geeksforgeeks.org/mvc-framework-introduction/)