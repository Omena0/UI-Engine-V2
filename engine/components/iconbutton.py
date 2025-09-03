from .base import ComponentBase
from .base import ComponentBase
from .. import theme
import pygame


class IconButton(ComponentBase):
    __slots__ = [
        "_size",
        "_icon",
        "_ov_bg_color",
        "_ov_bg_hover_color",
        "_corner_radius",
        "on_click",
        "_composite_surface",
        "_composite_dirty",
        "_last_child_count",
    ]

    def __init__(
        self,
        parent,
        pos,
        icon_surf: pygame.Surface,
        size=(36, 36),
        bg_color=None,
        bg_hover_color=None,
        corner_radius=6,
        on_click=lambda x: None,
    ) -> None:
        self._icon = icon_surf
        self._ov_bg_color = bg_color
        self._ov_bg_hover_color = bg_hover_color
        self._corner_radius = corner_radius
        self._size = size
        self.on_click = on_click

        super().__init__(parent, pos, self._size)

    @property
    def icon(self) -> pygame.Surface:
        return self._icon

    @icon.setter
    def icon(self, surf: pygame.Surface) -> None:
        self._icon = surf
        self.render()

    # Resolved at render time so theme updates propagate immediately
    @property
    def bg_color(self):
        return self._ov_bg_color if self._ov_bg_color is not None else theme.get("button_bg")

    @property
    def bg_hover_color(self):
        return self._ov_bg_hover_color if self._ov_bg_hover_color is not None else theme.get("button_bg_hover")

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            # re-render on hover change so colors update
            if self._hovered(event.pos)[1]:
                self.render()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._hovered(event.pos)[0]:
                try:
                    self.on_click(self)
                except Exception:
                    pass
                return True  # Consume the event
        return False

    def render(self) -> None:
        # Skip transparent fill - background rect will overwrite

        is_hover = self._hovered()[0]
        bg = self.bg_hover_color if is_hover else self.bg_color

        # rounded rect background - this will overwrite the entire surface
        try:
            pygame.draw.rect(self.surface, bg, (0, 0, *self.size), border_radius=self._corner_radius)
        except Exception:
            self.surface.fill(bg)

        # draw centered icon
        if self._icon:
            try:
                iw, ih = self._icon.get_size()
                x = (self.size[0] - iw) // 2
                y = (self.size[1] - ih) // 2
                self.surface.blit(self._icon, (x, y))
            except Exception:
                pass

        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ["IconButton"]
