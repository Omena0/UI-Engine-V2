"""Centralized theme defaults for the engine.

This module exposes a set of named color keys and simple theme maps.
Applications can change `applied_themes` or call `apply_themes()` to
select which theme overrides are active. `current_theme` is the merged
result of the base defaults plus applied themes (applied in order).
"""


from typing import Optional

# Base (light) defaults — every component-default color should exist here
LIGHT = {
    # Window and surfaces — light, soft, not pure-white
    'window_bg': (242, 247, 250),
    'surface_bg': (248, 250, 252),

    # Field / input
    'field_bg': (250, 252, 253),
    'field_text': (26, 30, 34),
    'field_placeholder': (120, 126, 132),
    'field_border': (200, 206, 212),

    # Buttons / controls
    'button_bg': (236, 242, 246),
    'button_bg_hover': (228, 236, 242),
    'button_text': (26, 30, 34),
    'button_text_hover': (20, 24, 28),

    # Labels / generic text
    'label_text': (28, 34, 40),
    'label_bg': None,

    # Frames and accents
    'frame_color': (190, 196, 202),
    'accent': (40, 110, 200),

    # Selection / caret / composition
    'selection': (180, 210, 245),
    'caret': (18, 20, 22),
    'composition': (100, 106, 112),

    # Misc
    'focus_glow': (40, 110, 200, 32),

    # Checkbox
    'checkbox_bg': (236, 242, 246),
    'checkbox_border': (196, 202, 208),
    'checkbox_bg_checked': (40, 110, 200),
    'checkbox_bg_hover': (230, 238, 244),
    'checkbox_text': (28, 34, 40),
    'checkbox_text_checked': (40, 110, 200),
    'checkbox_text_hover': (80, 140, 220),
    'checkbox_corner_radius': 6,
    'checkbox_inner': (200, 204, 208),
    'checkbox_inner_hover': (190, 194, 198),
    'checkbox_border_checked': (170, 176, 182),
    'checkbox_inner_border': (170, 176, 182),

    # Toggle
    'toggle_bg': (216, 222, 228),
    'toggle_bg_on': (40, 110, 200),
    'toggle_knob': (255, 255, 255),
    'toggle_border': (200, 206, 212),
    'toggle_hover': (208, 216, 230),

    # Dropdown
    'dropdown_bg': (250, 250, 252),
    'dropdown_text': (28, 34, 40),
    'dropdown_border': (200, 206, 212),
    'dropdown_hover': (236, 242, 246),
    # Radio
    'radio_bg': (255, 255, 255),
    'radio_border': (160, 160, 160),
    'radio_dot': (40, 110, 200),
    'radio_hover': (236, 242, 246),
    # Slider
    'slider_bg': (224, 228, 232),
    'slider_fg': (40, 110, 200),
    'slider_knob': (255, 255, 255),
    'slider_text': (28, 34, 40),

    # Progress
    'progress_bg': (230, 230, 230),
    'progress_fg': (40, 110, 200),
    'progress_knob': (255, 255, 255),
    # Segmented control
    'segmented_bg': (236, 242, 246),
    'segmented_selected': (40, 110, 200),
}

# Dark-mode overrides
DARK = {
    'window_bg': (18, 18, 20),
    'surface_bg': (24, 24, 26),

    # Field
    'field_bg': (30, 30, 34),
    'field_text': (230, 230, 235),
    'field_placeholder': (140, 140, 150),
    'field_border': (70, 70, 78),

    # Button
    'button_bg': (36, 36, 38),
    'button_bg_hover': (56, 56, 58),
    'button_text': (230, 230, 235),
    'button_text_hover': (230, 230, 235),

    # Label
    'label_text': (230, 230, 235),
    'label_bg': None,

    # Frame
    'frame_color': (90, 90, 94),
    'accent': (80, 150, 255),

    # Selection
    'selection': (50, 100, 200),
    'caret': (230, 230, 235),
    'composition': (200, 200, 200),

    # Misc
    'focus_glow': (80, 150, 255, 24),


    # Checkbox
    'checkbox_bg': (36, 36, 38),
    'checkbox_border': (70, 70, 78),
    'checkbox_bg_checked': (80, 150, 255),
    'checkbox_bg_hover': (56, 56, 58),
    'checkbox_text': (230, 230, 235),
    'checkbox_text_checked': (80, 150, 255),
    'checkbox_text_hover': (100, 170, 255),
    'checkbox_corner_radius': 6,
    'checkbox_inner': (110, 110, 110),
    'checkbox_inner_hover': (140, 140, 140),
    'checkbox_border_checked': (90, 90, 94),
    'checkbox_inner_border': (90, 90, 94),

    # Toggle
    'toggle_bg': (56, 56, 58),
    'toggle_bg_on': (80, 150, 255),
    'toggle_knob': (230, 230, 235),
    'toggle_border': (70, 70, 78),
    'toggle_hover': (72, 72, 76),

    # Dropdown
    'dropdown_bg': (36, 36, 38),
    'dropdown_text': (230, 230, 235),
    'dropdown_border': (70, 70, 78),
    'dropdown_hover': (56, 56, 58),

    # Radio
    'radio_bg': (36, 36, 38),
    'radio_border': (90, 90, 94),
    'radio_dot': (80, 150, 255),
    'radio_hover': (56, 56, 58),

    # Slider
    'slider_bg': (56, 56, 58),
    'slider_fg': (80, 150, 255),
    'slider_knob': (230, 230, 235),
    'slider_text': (230, 230, 235),

    # Progress
    'progress_bg': (48, 48, 50),
    'progress_fg': (80, 150, 255),
    'progress_knob': (230, 230, 235),
    # Segmented control
    'segmented_bg': (36, 36, 38),
    'segmented_selected': (80, 150, 255),
}

_current_themes: list[dict] = [LIGHT, DARK]

def swap_theme(window = None):
    _current_themes.reverse()
    compute_theme()
    if window:
        window.render()

def compute_theme() -> dict[str, tuple[int, ...]]:
    """Merge base LIGHT defaults with any applied themes (in order).

    Returns a new dict mapping keys to values.
    """
    global current

    merged = {}
    for current in _current_themes:
        merged |= current

    current = merged
    return merged

def apply_theme(theme:dict):
    _current_themes.append(theme)
    compute_theme()

def get(key:str) -> Optional[tuple[int, ...]]:
    return current.get(key)

current: dict[str, tuple[int, ...]] = {}

compute_theme()


__all__ = ['apply_theme', 'compute_theme', 'current', 'LIGHT', 'DARK']