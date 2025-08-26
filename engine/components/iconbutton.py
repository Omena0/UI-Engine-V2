from .base import ComponentBase
from .. import theme
import pygame

class IconButton(ComponentBase):
    def __init__(self, parent, pos, icon_surf: pygame.Surface, size=(36,36), on_click=None):
        self._size = size
        self.icon = icon_surf
        self.on_click = on_click
        super().__init__(parent, pos, self._size)

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.surface.get_rect().move(*self.absolute_pos).collidepoint((mx, my)):
                try:
                    if callable(self.on_click):
                        self.on_click(self)
                except Exception:
                    pass
                return True
        return super()._event(event)

    def render(self) -> None:
        bg = theme.get('button_bg')
        hover = theme.get('button_bg_hover')
        border = theme.get('button_border')
        self.surface.fill((0,0,0,0))
        rect = self.surface.get_rect()
        try:
            pygame.draw.rect(self.surface, bg or (236,236,236), rect, border_radius=6)
        except Exception:
            self.surface.fill(bg or (236,236,236))

        if self.icon:
            try:
                iw, ih = self.icon.get_size()
                x = (rect.width - iw)//2
                y = (rect.height - ih)//2
                self.surface.blit(self.icon, (x,y))
            except Exception:
                pass

        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

__all__ = ['IconButton']
