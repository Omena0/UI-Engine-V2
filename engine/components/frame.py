from .base import ComponentBase
from .base import ComponentBase
from typing import Any
from .. import theme
import pygame


class Frame(ComponentBase):
    __slots__ = ["_size", "_ov_color", "_corner_radius"]

    def __init__(
        self, parent, pos, size, color=None, corner_radius=8
    ) -> None:
        # store override; resolve in render() so theme changes apply
        self._ov_color = color
        self._corner_radius = corner_radius
        self._size = size
        super().__init__(parent, pos, self._size)

    @property
    def color(self) -> Any:
        return self._ov_color if self._ov_color is not None else theme.get("frame_color")

    @color.setter
    def color(self, value) -> None:
        # treat setter as override
        self._ov_color = value
        self.render()

    @property
    def corner_radius(self) -> Any:
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, value) -> None:
        self._corner_radius = value
        self.render()

    def render(self) -> None:
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self.surface,
            self.color,
            (0, 0, *self.size),
            border_radius=self.corner_radius,
        )

        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ["Frame"]
__all__ = ["Frame"]
