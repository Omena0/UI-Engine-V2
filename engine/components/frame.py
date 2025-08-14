from .base import ComponentBase
from typing import Any
import pygame

class Frame(ComponentBase):
    __slots__ = ["_size", "_color", "_corner_radius"]
    def __init__(
            self, parent, pos, size,
            color = (255, 255, 255),
            corner_radius = 8,
    ) -> None:
        self._color = color
        self._corner_radius = corner_radius
        self._size = size
        super().__init__(parent, pos)

    @property
    def color(self) -> Any:
        return self._color

    @color.setter
    def color(self, value) -> None:
        self._color = value
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
            border_radius=self.corner_radius
        )

        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

__all__ = ["Frame"]
