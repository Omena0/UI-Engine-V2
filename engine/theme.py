"""Centralized theme defaults for the engine.

This module exposes a set of named color keys and simple theme maps.
Applications can change `applied_themes` or call `apply_themes()` to
select which theme overrides are active. `current_theme` is the merged
result of the base defaults plus applied themes (applied in order).
"""

from typing import Any, Optional

# Base (light) defaults — every component-default color should exist here
LIGHT = {
    'window_bg': (245, 245, 246),
    'surface_bg': (255, 255, 255),

    # Field / input
    'field_bg': (255, 255, 255),
    'field_text': (28, 28, 30),
    'field_placeholder': (120, 120, 120),
    'field_border': (200, 200, 200),

    # Buttons / controls
    'button_bg': (240, 240, 240),
    'button_bg_hover': (220, 220, 220),
    'button_text': (28, 28, 30),
    'button_text_hover': (28, 28, 30),

    # Labels / generic text
    'label_text': (28, 28, 30),
    'label_bg': (0, 0, 0, 0),

    # Frames and accents
    'frame_color': (200, 200, 200),
    'accent': (80, 150, 255),

    # Selection / caret / composition
    'selection': (50, 100, 200),
    'caret': (28, 28, 30),
    'composition': (80, 80, 80),

    # Misc
    'focus_glow': (80, 150, 255, 24),
}


# Dark-mode overrides
DARK = {
    'window_bg': (18, 18, 20),
    'surface_bg': (24, 24, 26),
    'field_bg': (30, 30, 34),
    'field_text': (230, 230, 235),
    'field_placeholder': (140, 140, 150),
    'field_border': (70, 70, 78),
    'accent': (80, 150, 255),
    'selection': (50, 100, 200),
    'caret': (230, 230, 235),
    'composition': (200, 200, 200),
    'focus_glow': (80, 150, 255, 24),
    'button_bg': (36, 36, 38),
    'button_bg_hover': (56, 56, 58),
    'button_text': (230, 230, 235),
    'button_text_hover': (230, 230, 235),
    'label_text': (230, 230, 235),
    'label_bg': (0, 0, 0, 0),
    'frame_color': (90, 90, 94),
}

_current_themes: list[dict] = [LIGHT, DARK]

def compute_theme() -> dict[str, tuple[int, ...]]:
    """Merge base LIGHT defaults with any applied themes (in order).

    Returns a new dict mapping keys to values.
    """
    global current

    merged = {}
    for current in _current_themes:
        merged.update(current)

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