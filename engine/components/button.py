from pygame.event import Event
from .base import ComponentBase
from ..text import get_font
from typing import Any
import pygame

class Button(ComponentBase):
    __slots__ = ["_size", "_bg_color", "_corner_radius", "_text", "_font", "_text_color",
                 "_bg_hover_color", "_text_hover_color", "on_click"]
    def __init__(
            self, parent, pos, text, size,
            bg_color = (255, 255, 255),
            bg_hover_color = (200, 200, 200),
            text_color = (0, 0, 0),
            text_hover_color = (0, 0, 0),
            corner_radius = 8,
            font = (None, 38),
            on_click = lambda x: ...
    ) -> None:
        self._text = text
        self._bg_color = bg_color
        self._text_color = text_color
        self._corner_radius = corner_radius
        self._size = size
        self._font = get_font(*font)
        self._bg_hover_color = bg_hover_color
        self._text_hover_color = text_hover_color
        self.on_click = on_click

        super().__init__(parent, pos)

    @property
    def text(self) -> Any:
        return self._text

    @text.setter
    def text(self, value) -> None:
        self._text = value
        self.render()

    @property
    def bg_color(self) -> Any:
        return self._bg_color

    @bg_color.setter
    def bg_color(self, value) -> None:
        self._bg_color = value
        self.render()

    @property
    def text_color(self) -> Any:
        return self._text_color

    @text_color.setter
    def text_color(self, value) -> None:
        self._text_color = value
        self.render()

    @property
    def corner_radius(self) -> Any:
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, value) -> None:
        self._corner_radius = value
        self.render()

    @property
    def font(self) -> pygame.font.Font:
        return self._font

    @font.setter
    def font(self, value) -> None:
        self._font = get_font(*value)
        self.render()

    @property
    def bg_hover_color(self) -> Any:
        return self._bg_hover_color

    @bg_hover_color.setter
    def bg_hover_color(self, value) -> None:
        self._bg_hover_color = value
        self.render()

    @property
    def text_hover_color(self) -> Any:
        return self._text_hover_color

    @text_hover_color.setter
    def text_hover_color(self, value) -> None:
        self._text_hover_color = value
        self.render()

    def _event(self, event: Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            if self._hovered(event.pos)[1]:
                self.render()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._hovered(event.pos)[0]:
                self.on_click(self.text)
        return False

    def render(self) -> None:
        self.surface.fill((0, 0, 0, 0))
        # Draw the rounded rectangle background
        pygame.draw.rect(
            self.surface,
            self.bg_hover_color if self._hovered()[0] else self.bg_color,
            (0, 0, *self.size),
            border_radius=self.corner_radius
        )

        # Render the text to a temporary surface with per-pixel alpha
        text = self.font.render(self.text, True, self.text_hover_color if self._hovered()[0] else self.text_color)
        text_surf = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        text_surf.blit(text, (0, 0))

        # Create a mask surface with the same size as the button
        mask = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(
            mask,
            (255, 255, 255, 255),
            (0, 0, *self.size),
            border_radius=self.corner_radius
        )

        # Position to center the text
        text_pos = (
            self.size[0] // 2 - text.get_width() // 2,
            self.size[1] // 2 - text.get_height() // 2
        )

        # Blit the text onto the button surface using the mask
        # 1. Blit text onto a temp surface the size of the button
        temp = pygame.Surface(self.size, pygame.SRCALPHA)
        temp.blit(text_surf, text_pos)
        # 2. Use the mask to keep only the text inside the rounded rect
        temp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        # 3. Blit the masked text onto the button surface
        self.surface.blit(temp, (0, 0))

        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ["Button"]
