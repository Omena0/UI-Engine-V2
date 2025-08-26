from .base import ComponentBase
from .. import theme
import pygame


class ProgressBar(ComponentBase):
    __slots__ = [
        "_size",
        "_value",
        "_max",
        "_ov_bg_color",
        "_ov_fg_color",
        "_ov_knob_color",
        "_corner_radius",
    ]

    def __init__(
        self,
        parent,
        pos,
        size=(200, 18),
        value=0,
        max_value=100,
        bg_color=None,
        fg_color=None,
        knob_color=None,
        corner_radius=4,
    ):
        # store overrides; resolve actual colors in render() so theme updates apply
        self._size = size
        self._value = float(value)
        self._max = float(max_value)
        self._ov_bg_color = bg_color
        self._ov_fg_color = fg_color
        self._ov_knob_color = knob_color
        self._corner_radius = corner_radius

        super().__init__(parent, pos, self._size)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v: float):
        v = max(0.0, min(round(v,2), self._max))
        if v == self._value:
            return
        self._value = v
        self.emit("change", self._value)
        self.render()

    # convenience method for callers that prefer a function
    def set_value(self, v: float):
        self.value = v

    # Resolved at render time so theme updates propagate immediately
    @property
    def bg_color(self):
        return self._ov_bg_color if self._ov_bg_color is not None else theme.get("progress_bg")

    @property
    def fg_color(self):
        return self._ov_fg_color if self._ov_fg_color is not None else theme.get("progress_fg")

    @property
    def knob_color(self):
        return self._ov_knob_color if self._ov_knob_color is not None else theme.get("progress_knob")

    @property
    def corner_radius(self):
        return self._corner_radius

    def render(self) -> None:
        bg = self.bg_color or (230, 230, 230)
        fg = self.fg_color or (40, 110, 200)
        knob = self.knob_color or (255, 255, 255)

        rect = self.surface.get_rect()
        w, h = rect.width, rect.height

        self.surface.fill((0, 0, 0, 0))
        try:
            pygame.draw.rect(self.surface, bg, (0, 0, w, h), border_radius=self.corner_radius)
        except Exception:
            self.surface.fill(bg)

        frac = (self._value / self._max)
        try:
            fill_w = max(0, int(frac * w))
            if fill_w > 0:
                pygame.draw.rect(self.surface, fg, (0, 0, fill_w, h), border_radius=self.corner_radius)
        except Exception:
            pass

        # build blits consistently with other components
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ["ProgressBar"]
