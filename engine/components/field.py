from ..text import get_font, render_line_with_caret, render_selection, measure_caret_x
from ..input import input_manager
from .base import ComponentBase
from .. import theme
import pygame
import time


class Field(ComponentBase):
    __slots__ = ['_value', '_font', '_color', '_bg_color', '_caret', '_sel_start', '_sel_end', '_placeholder', 'on_enter', '_caret_visible', '_last_blink', '_dragging', '_composition', '_focused', '_scroll_x', '_sel_anchor']

    def __init__(self, parent, pos, font, value='', color=(255,255,255), bg_color=None, placeholder='', on_enter=None, size=None):
        self._value = value
        self._font = font
        self._color = color
        self._bg_color = bg_color
        self._caret = len(value)
        self._sel_start = 0
        self._sel_end = 0
        self._placeholder = placeholder
        self.on_enter = on_enter

        # caret blink state
        self._caret_visible = True
        self._last_blink = time.time()

        # horizontal scroll offset so caret is always visible
        self._scroll_x = 0

        # focus state
        self._focused = False

        # dragging state for mouse selection
        self._dragging = False

        # IME composition text (if any)
        self._composition = ''

        # If no explicit size provided, pick a reasonable default based on font metrics
        if size is not None:
            self._size = size
        else:
            # resolve font to pygame.font.Font to measure heights
            if not isinstance(self._font, pygame.font.Font):
                try:
                    f = get_font(*self._font)
                except Exception:
                    f = None
            else:
                f = self._font
            if f:
                # width default 200, height based on font height + padding
                self._size = (200, f.size('Tg')[1] + 12)
            else:
                self._size = (200, 24)
        super().__init__(parent, pos, self._size)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self.render()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, f):
        self._font = f
        self.render()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, c):
        self._color = c
        self.render()

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, c):
        self._bg_color = c
        self.render()

    @property
    def placeholder(self):
        return self._placeholder

    @placeholder.setter
    def placeholder(self, p):
        self._placeholder = p
        self.render()

    def render(self):
        surf = self.surface
        surf.fill((0, 0, 0, 0))

        # modern visual style: subtle shadow, elevated background, focused accent
        bg = self._bg_color if self._bg_color is not None else (245, 245, 245, 0)
        radius = 8
        padding_x = 10
        padding_y = 8

        # drop shadow (subtle) — draw as slightly offset rect so it reads as elevation
        shadow_color = (0, 0, 0, 30)
        try:
            shadow_surf = pygame.Surface((self.size[0], self.size[1]), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, shadow_color, (0, 0, self.size[0], self.size[1]), border_radius=radius)
            # blit shadow slightly down-right for elevation
            surf.blit(shadow_surf, (2, 2))
        except Exception:
            pass

        bg_color_draw = theme.get('field_bg')
        effective_text_color = theme.get('field_text')
        border_col = theme.get('field_border')
        accent = theme.get('accent')

        pygame.draw.rect(surf, bg_color_draw, (0, 0, *self.size), border_radius=radius)

        # border: accent when focused
        focused = getattr(self, '_focused', False)
        if focused:
            border_col = accent if 'accent' in locals() else (80, 150, 255)
            border_width = 2
        else:
            border_col = border_col if 'border_col' in locals() else (200, 200, 200)
            border_width = 1
        pygame.draw.rect(surf, border_col, (0, 0, *self.size), width=border_width, border_radius=radius)

        # subtle focused glow (inner translucent accent)
        if focused:
            glow = pygame.Surface((self.size[0]-6, self.size[1]-6), pygame.SRCALPHA)
            glow.fill((0, 0, 0, 0))
            pygame.draw.rect(glow, (80, 150, 255, 24), (0, 0, glow.get_width(), glow.get_height()), border_radius=radius)
            surf.blit(glow, (3, 3))

        if not isinstance(self._font, pygame.font.Font):
            font = get_font(*self._font)
        else:
            font = self._font

        # determine text and color. Render placeholder separately so it does
        # not affect caret measurement/placement.
        is_empty = not self._value
        placeholder_text = self._placeholder
        value_text = self._value
        if self._bg_color is not None:
            value_color = self._color
            placeholder_color = (150, 150, 150)
        else:
            value_color = effective_text_color
            placeholder_color = (120, 120, 120)

        # choose caret color: accent when focused, else strong readable color
        if focused:
            caret_color = (80, 150, 255)
        else:
            caret_color = effective_text_color

        # If empty and not focused, draw placeholder and skip caret/selection
        if is_empty and not focused and placeholder_text:
            ph_surf = font.render(placeholder_text, True, placeholder_color)
            surf.blit(ph_surf, (padding_x, padding_y))
            # finalize blits
            self.blits = [(self._surface, self.absolute_pos)]
            for child in self.children:
                child.render()
                self.blits.extend(child.blits)
            return

        # prepare text and ensure caret is visible by adjusting horizontal scroll
        text = value_text

        # caret blink toggle
        if time.time() - self._last_blink > 0.5:
            self._caret_visible = not self._caret_visible
            self._last_blink = time.time()

        # compute caret x in text coordinates and update scroll so caret stays visible
        caret_x = measure_caret_x(text, font, self._caret)
        content_width = self.size[0] - padding_x * 2
        if caret_x - self._scroll_x < 0:
            self._scroll_x = max(0, caret_x - 8)
        elif caret_x - self._scroll_x > content_width:
            self._scroll_x = caret_x - content_width + 8

        # draw text shifted by scroll offset so caret is visible
        text_x = padding_x - int(self._scroll_x)

        # draw selection first (now using the same text_x offset as text)
        if self._sel_start != self._sel_end:
            render_selection(surf, text, self._sel_start, self._sel_end, font, (50, 100, 200), text_x, padding_y)

        # draw text and caret
        render_line_with_caret(surf, text, self._caret, font, value_color, self._bg_color, text_x, padding_y, caret_color=caret_color, caret_visible=self._caret_visible and focused)

        # draw IME composition (underlined) at caret position if present
        if getattr(self, '_composition', None):
            comp = self._composition
            comp_surf = font.render(comp, True, (80, 80, 80))
            cx = measure_caret_x(text, font, self._caret)
            # composition should be drawn using the same text_x offset
            surf.blit(comp_surf, (int(text_x + cx), padding_y))
            # underline
            underline_rect = pygame.Rect(int(text_x + cx), padding_y + font.size(text)[1] - 2, comp_surf.get_width(), 2)
            pygame.draw.rect(surf, (80, 80, 80), underline_rect)

        # finalize blits
        self.blits = [(self._surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

    def _event(self, event: pygame.event.Event) -> bool:
        # Delegate input handling to the centralized manager. The manager will
        # mutate component state and call render() as needed. If the manager
        # doesn't handle the event, fall back to the base implementation.
        handled = False
        try:
            handled = input_manager.handle_event(self, event)
        except Exception:
            handled = False
        if handled:
            return True
        return super()._event(event)


