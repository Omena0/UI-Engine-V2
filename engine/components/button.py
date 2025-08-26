from pygame.event import Event
from .base import ComponentBase
from ..text import get_font
from typing import Any
from .. import theme
import pygame


class Button(ComponentBase):
    __slots__ = [
        "_size",
        "_ov_bg_color",
        "_ov_text_color",
        "_corner_radius",
        "_text",
        "_font",
        "_ov_bg_hover_color",
        "_ov_text_hover_color",
        "on_click",
    ]

    def __init__(
        self,
        parent,
        pos,
        text,
        size,
        bg_color=None,
        bg_hover_color=None,
        text_color=None,
        text_hover_color=None,
        corner_radius=8,
        font=(None, 38),
        on_click=lambda x: None,
    ) -> None:
        self._text = text

        # store overrides; resolve actual colors in render() so theme updates apply
        self._ov_bg_color = bg_color
        self._ov_text_color = text_color
        self._corner_radius = corner_radius
        self._size = size
        self._font = get_font(*font)
        self._ov_bg_hover_color = bg_hover_color
        self._ov_text_hover_color = text_hover_color
        self.on_click = on_click

        super().__init__(parent, pos, self._size)

    @property
    def text(self) -> Any:
        return self._text

    @text.setter
    def text(self, value) -> None:
        self._text = value
        self.render()

    # Resolved at render time so theme updates propagate immediately
    @property
    def bg_color(self):
        return self._ov_bg_color if self._ov_bg_color is not None else theme.get("button_bg")

    @property
    def text_color(self):
        return self._ov_text_color if self._ov_text_color is not None else theme.get("button_text")

    @property
    def bg_hover_color(self):
        return self._ov_bg_hover_color if self._ov_bg_hover_color is not None else theme.get("button_bg_hover")

    @property
    def text_hover_color(self):
        return self._ov_text_hover_color if self._ov_text_hover_color is not None else theme.get("button_text_hover")

    def _event(self, event: Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            # re-render on hover change so colors update
            if self._hovered(event.pos)[1]:
                self.render()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._hovered(event.pos)[0]:
                try:
                    self.on_click(self.text)
                except Exception:
                    pass
        return False

    def render(self) -> None:
        self.surface.fill((0, 0, 0, 0))

        is_hover = self._hovered()[0]
        bg = self.bg_hover_color if is_hover else self.bg_color
        txt_col = self.text_hover_color if is_hover else self.text_color

        # rounded rect background
        pygame.draw.rect(self.surface, bg, (0, 0, *self.size), border_radius=self._corner_radius)

        # render text and mask to the rounded bounds
        text_surf = self._font.render(self.text, True, txt_col)
        tmp = pygame.Surface(self.size, pygame.SRCALPHA)
        # center text
        pos = (self.size[0] // 2 - text_surf.get_width() // 2, self.size[1] // 2 - text_surf.get_height() // 2)
        tmp.blit(text_surf, pos)

        # mask with rounded rect
        mask = pygame.Surface(self.size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (254, 254, 254, 255), (0, 0, *self.size), border_radius=self._corner_radius)
        tmp.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        self.surface.blit(tmp, (0, 0))

        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ["Button"]
