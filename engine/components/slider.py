from typing import Optional, Callable
from .base import ComponentBase
from ..text import get_font
from .. import theme
import pygame


class Slider(ComponentBase):
    __slots__ = [
        "_size",
        "_min",
        "_max",
        "_value",
        "_font",
        "_dragging",
        "_ov_bg_color",
        "_ov_fg_color",
        "_ov_knob_color",
        "_corner_radius",
        "on_change",
        "_composite_surface",
        "_composite_dirty",
        "_last_child_count",
    ]

    def __init__(
        self,
        parent,
        pos,
        size=(200, 28),
        min_value=0,
        max_value=100,
        value=0,
        bg_color=None,
        fg_color=None,
        knob_color=None,
        corner_radius=6,
        on_change: Optional[Callable] = None,
    ) -> None:
        self._size = size
        self._min = int(min_value)
        self._max = int(max_value)

        # clamp initial value
        try:
            v = int(value)
        except Exception:
            v = self._min
        v = max(v, self._min)
        v = min(v, self._max)
        self._value = v

        self._ov_bg_color = bg_color
        self._ov_fg_color = fg_color
        self._ov_knob_color = knob_color

        self.on_change = on_change or (lambda v: None)
        self._dragging = False
        self._font = get_font(None, 14)
        self._corner_radius = corner_radius

        super().__init__(parent, pos, self._size)

    @property
    def min_value(self) -> int:
        return self._min

    @min_value.setter
    def min_value(self, v: int) -> None:
        self._min = v
        self._value = max(self._min, self._value)
        self.render()

    @property
    def max_value(self) -> int:
        return self._max

    @max_value.setter
    def max_value(self, v: int) -> None:
        self._max = v
        self._value = min(self._max, self._value)
        self.render()

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, v: int) -> None:
        self._set_value(v)

    # theme-resolved colors
    @property
    def bg_color(self):
        return self._ov_bg_color if self._ov_bg_color is not None else theme.get("slider_bg")

    @property
    def fg_color(self):
        return self._ov_fg_color if self._ov_fg_color is not None else theme.get("slider_fg")

    @property
    def knob_color(self):
        return self._ov_knob_color if self._ov_knob_color is not None else theme.get("slider_knob")

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            ax, ay = self.absolute_pos
            if pygame.Rect(ax, ay, *self._size).collidepoint((mx, my)):
                self._dragging = True
                self._set_from_mouse(mx)
                return True

        if event.type == pygame.MOUSEBUTTONUP and self._dragging:
            self._dragging = False
            return True

        if event.type == pygame.MOUSEMOTION:
            if self._dragging:
                mx, my = event.pos
                self._set_from_mouse(mx)
                return True
            # re-render on hover changes
            if self._hovered(event.pos)[1]:
                self.render()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._set_value(self._value - 1)
                return True
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                self._set_value(self._value + 1)
                return True

        return False

    def _set_from_mouse(self, mx):
        ax, ay = self.absolute_pos
        rel = (mx - ax) / max(1, self._size[0])
        val = int(self._min + rel * (self._max - self._min))
        self._set_value(val)

    def _set_value(self, val):
        val = max(self._min, min(self._max, int(val)))
        if val != self._value:
            self._value = val
            try:
                self.on_change(self._value)
            except Exception:
                pass
            self.emit("change", self._value)
            self.render()

    def render(self) -> None:
        bg = self.bg_color or (220, 220, 220)
        fg = self.fg_color or (120, 160, 220)
        knob = self.knob_color or (255, 255, 255)

        rect = pygame.Rect(0, 0, *self.size)
        track_h = max(6, rect.height // 4)
        track_y = rect.height // 2 - track_h // 2

        try:
            pygame.draw.rect(self.surface, bg, (0, track_y, rect.width, track_h), border_radius=self._corner_radius)
        except Exception:
            self.surface.fill(bg)

        if self._max > self._min:
            frac = (self._value - self._min) / (self._max - self._min)
        else:
            frac = 0.0
        filled_w = max(4, int(frac * rect.width))

        try:
            pygame.draw.rect(self.surface, fg, (0, track_y, filled_w, track_h), border_radius=self._corner_radius)
        except Exception:
            pass

        knob_x = max(8, min(rect.width - 8, int(frac * rect.width)))
        try:
            pygame.draw.circle(self.surface, knob, (knob_x, rect.height // 2), 8)
        except Exception:
            pass

        # build blits
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ["Slider"]
