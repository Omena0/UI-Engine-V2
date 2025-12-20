from .base import ComponentBase
from .base import ComponentBase
from typing import Any
from .. import theme
import pygame


class Frame(ComponentBase):
    __slots__ = ["_size", "_ov_color", "_corner_radius", "_rendered"]

    def __init__(
        self, parent, pos, size, color=None, corner_radius=8
    ) -> None:
        # store override; resolve in render() so theme changes apply
        self._ov_color = color
        self._corner_radius = corner_radius
        self._size = size
        self._rendered = False  # Track if we've rendered this frame
        super().__init__(parent, pos, self._size)

    @property
    def color(self) -> Any:
        return self._ov_color if self._ov_color is not None else theme.get("frame_color")

    @color.setter
    def color(self, value) -> None:
        # treat setter as override
        if self._ov_color != value:
            self._ov_color = value
            self._rendered = False  # Mark for re-render
            self.render()

    @property
    def corner_radius(self) -> Any:
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, value) -> None:
        self._corner_radius = value
        self._rendered = False  # Mark for re-render
        self.render()

    def render(self) -> None:
        # Only render if we haven't rendered yet or something changed
        if not self._rendered:
            surf = self.surface  # Cache surface reference
            # Clear the surface first
            surf.fill((0, 0, 0, 0))
            # Draw background directly using pygame primitives
            pygame.draw.rect(
                surf,
                self.color,
                (0, 0, *self.size),
                border_radius=self.corner_radius,
            )
            self._rendered = True

        # Mark composite as dirty since we updated our surface and build blits
        self._mark_composite_dirty()
        self._build_blits()


__all__ = ["Frame"]
__all__ = ["Frame"]
