from .base import ComponentBase
from .. import theme
import pygame


class Toggle(ComponentBase):
    __slots__ = [
        '_size', '_ov_bg', '_ov_knob', '_value', 'on_change', '_corner_radius', '_ov_bg_on',
        '_composite_surface', '_composite_dirty', '_last_child_count'
    ]

    def __init__(
        self,
        parent,
        pos,
        size=(40, 20),
        value: bool = False,
        bg=None,
        bg_on=None,
        knob_color=None,
        corner_radius: int = 10,
        on_change=None,
    ) -> None:
        self._size = size
        self._ov_bg = bg
        self._ov_bg_on = bg_on
        self._ov_knob = knob_color
        self._value = value
        self.on_change = on_change if on_change is not None else (lambda v: ...)
        self._corner_radius = corner_radius

        super().__init__(parent, pos, self._size)

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, v: bool):
        self._value = v
        self.render()

    # Resolve theme values at render time so updates apply live
    @property
    def bg(self):
        return self._ov_bg if self._ov_bg is not None else theme.get('toggle_bg')

    @property
    def bg_on(self):
        return self._ov_bg_on if self._ov_bg_on is not None else theme.get('toggle_bg_on')

    @property
    def knob_color(self):
        return self._ov_knob if self._ov_knob is not None else theme.get('toggle_knob')

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            if self._hovered(event.pos)[1]:
                self.render()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._hovered(event.pos)[0]:
                self._toggle()
                return True  # Consume the event
        elif event.type == pygame.KEYDOWN:
            # allow space/enter to toggle when focused
            if getattr(self, '_was_hovered', False) and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self._toggle()
                return True  # Consume the event

        return False

    def _toggle(self):
        self._value = not self._value
        try:
            self.on_change(self._value)
        except Exception:
            pass
        self.emit('change', self._value)
        self.render()

    def render(self) -> None:
        hovered = self._hovered()[0]

        bg = self.bg_on if self._value else self.bg
        # hover tweak
        if hovered:
            hover_col = theme.get('toggle_hover')
            if hover_col is not None and not self._value:
                bg = hover_col

        # Simplified: draw track and border in one call when possible
        border_col = theme.get('toggle_border')
        if border_col is not None:
            # Draw border first, then fill with background (one fewer draw call when border exists)
            try:
                pygame.draw.rect(self.surface, border_col, (0, 0, *self.size), border_radius=self._corner_radius)
                pygame.draw.rect(self.surface, bg, (1, 1, self.size[0]-2, self.size[1]-2), border_radius=self._corner_radius)
            except Exception:
                pygame.draw.rect(self.surface, border_col, (0, 0, *self.size))
                pygame.draw.rect(self.surface, bg, (1, 1, self.size[0]-2, self.size[1]-2))
        else:
            # No border - just draw background
            try:
                pygame.draw.rect(self.surface, bg, (0, 0, *self.size), border_radius=self._corner_radius)
            except Exception:
                pygame.draw.rect(self.surface, bg, (0, 0, *self.size))

        # knob
        kw = int(self.size[1] - 6)
        pad = 3
        kx = self.size[0] - kw - pad if self._value else pad
        kc = self.knob_color
        pygame.draw.ellipse(self.surface, kc, (kx, pad, kw, kw))

        # finalize blits
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ['Toggle']
