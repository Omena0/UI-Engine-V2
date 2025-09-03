
# UI-Engine-V2

[![Build](https://github.com/Omena0/UI-Engine-V2/actions/workflows/publish.yml/badge.svg?event=push)](https://github.com/Omena0/UI-Engine-V2/actions/workflows/publish.yml)
[![Tests](https://github.com/Omena0/UI-Engine-V2/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/Omena0/UI-Engine-V2/actions/workflows/pytest.yml)
[![Coverage](https://codecov.io/gh/Omena0/UI-Engine-V2/branch/main/graph/badge.svg)](https://codecov.io/gh/Omena0/UI-Engine-V2)

[PyPI Package](https://pypi.org/project/ui-engine/)

High-performance pygame based UI framework with render-on-change architecture.

## Features

- **High Performance**: Hybrid-mode-rendering ensures no compute is wasted on re-rendering unchanged elements.
- **Easy to Use**: Intuitive API design makes it simple to create and manage UI components.
- **Events for everything**: Comprehensive event system for handling user interactions, components have their own events.
- **Immediate themes**: Style system allows immediate color palette changes across the entire application with one function call.
- **Text rendering**: Justified text rendering with minimal gaps.
- **Easily extensible**: You can easily make your own components by extending the base classes.
- **Maintainable**: Code quality is always in mind, never sacrificing readability for quick fixes.
- **Lightweight**: Minimal dependencies and a small footprint make it suitable for various projects.

## Install

```bash
pip install ui-engine
```

## QuickStart

```python
import engine as ui

# Create window
window = ui.Window((800, 600))

# Create a frame
frame = ui.Frame(window, (10, 10), (300, 200))

# Add components
label = ui.Label(
    frame,
    (10, 10),
    "Hello World!",
    (None, 18)
)

button = ui.Button(
    frame,
    (10, 50),       # Pos
    "Click Me",
    (100, 30),      # Size
    on_click=lambda b: print("Button clicked!")
)

field = ui.Field(
    frame,
    (10, 90),       # Pos
    (None, 14),     # Font
    "Type here...", # Text
    size=(200, 25)
)

# Run the application
window.mainloop()
```

## Components

- **Frame**: Basic rounded rectangle container
- **Button**: Interactive button with hover states and click handlers
- **Label**: Text display component with wrapping support
- **Field**: Text input component with multiline support and IME
- **CheckBox**: Toggle checkbox with customizable styling
- **Radio**: Radio button with easy group management
- **Toggle**: Switch-style toggle component
- **Slider**: Value slider with customizable range
- **ProgressBar**: Progress indicator with ultra-smooth animations
- **Dropdown**: Responsive dropdown menu
- **TabFrame**: Tab container for organizing content
- **SegmentedButton**: Multi-option button component
- **IconButton**: Button component for icon-based interactions


## License

This project is licensed under the PolyForm Noncommercial License 1.0.0 - see the [COPYING.md](COPYING.md) file for details.

Contact [Omena0](mailto:omena0mc@gmail.com) if you want an exception.
