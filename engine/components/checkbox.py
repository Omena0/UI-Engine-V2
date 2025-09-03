from .base import ComponentBase
from ..text import get_font
from .. import theme
import pygame

class CheckBox(ComponentBase):
    __slots__ = [
        "_size", "_text", "_font",
        "_ov_bg_color", "_ov_border_color", "_ov_bg_checked_color", "_ov_bg_hovered_color",
        "_ov_text_color", "_ov_text_checked_color", "_ov_text_hovered_color",
        "_ov_corner_radius",
        "_checked", "on_change",
        "_composite_surface", "_composite_dirty", "_last_child_count"
    ]

    def __init__(
            self, parent, pos,
            size = (50,50),
            text = 'X',
            bg_color = None,
            border_color = None,
            bg_checked_color = None,
            bg_hovered_color = None,
            text_color = None,
            text_checked_color = None,
            text_hovered_color = None
            , on_change=None
        ):
        # store overrides; actual theme resolution happens in render()
        self._size = size
        self._text = text
        self._font = get_font(None, size[1]-5)

        # keep the passed overrides (None means use theme)
        self._ov_bg_color = bg_color
        self._ov_border_color = border_color
        self._ov_bg_checked_color = bg_checked_color
        self._ov_bg_hovered_color = bg_hovered_color

        self._ov_text_color = text_color
        self._ov_text_checked_color = text_checked_color
        self._ov_text_hovered_color = text_hovered_color
        # allow corner radius override (optional theme key 'checkbox_corner_radius')
        self._ov_corner_radius = None

        # state and callback
        self._checked = False
        # public callback attribute; prefer passed callback otherwise noop
        self.on_change = on_change if on_change is not None else (lambda v: ...)

        super().__init__(parent, pos, self._size)

    def _resolve_theme(self):
        """Resolve theme values and apply any overrides passed to __init__.

        Returns a dict with keys: bg_color, border_color, bg_checked_color,
        bg_hovered_color, text_color, text_checked_color, text_hovered_color,
        corner_radius
        """
        t = theme.current

        # Resolve base values from theme unless an override was provided
        bg = self._ov_bg_color if self._ov_bg_color is not None else t.get('checkbox_bg')
        border = self._ov_border_color if self._ov_border_color is not None else t.get('checkbox_border')
        bg_checked = self._ov_bg_checked_color if self._ov_bg_checked_color is not None else t.get('checkbox_bg_checked')
        bg_hover = self._ov_bg_hovered_color if self._ov_bg_hovered_color is not None else t.get('checkbox_bg_hover')

        txt = self._ov_text_color if self._ov_text_color is not None else t.get('checkbox_text')
        txt_checked = self._ov_text_checked_color if self._ov_text_checked_color is not None else t.get('checkbox_text_checked')
        txt_hover = self._ov_text_hovered_color if self._ov_text_hovered_color is not None else t.get('checkbox_text_hover')

        corner = self._ov_corner_radius if self._ov_corner_radius is not None else t.get('checkbox_corner_radius')
        border_checked = t.get('checkbox_border_checked')
        inner_border = t.get('checkbox_inner_border')

        return {
            'bg_color': bg,
            'border_color': border,
            'bg_checked_color': bg_checked,
            'bg_hovered_color': bg_hover,
            'text_color': txt,
            'text_checked_color': txt_checked,
            'text_hovered_color': txt_hover,
            'inner_color': t.get('checkbox_inner'),
            'inner_hover_color': t.get('checkbox_inner_hover'),
            'border_color_checked': border_checked,
            'inner_border_color': inner_border,
            'corner_radius': corner,
        }

    @property
    def checked(self):
        return self._checked

    @checked.setter
    def checked(self, value: bool):
        self._checked = value
        self.render()

    def _event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self._hovered(event.pos)[1]:
                self.render()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._hovered(event.pos)[0]:
                # toggle
                self._checked = not self._checked
                # call callback
                try:
                    self.on_change(self._checked)
                except Exception:
                    pass
                # emit event for listeners
                self.emit('change', self._checked)
                self.render()
                return True  # Consume the event

        return False

    def render(self):
        # Skip transparent fill - background rect will overwrite

        hovered = self._hovered()[0]

        # Resolve theme values now so updates take effect immediately
        vals = self._resolve_theme()
        # background should remain the base bg; checked state is shown by the inner rect
        bg = vals['bg_color']
        if hovered and vals['bg_hovered_color'] is not None:
            bg = vals['bg_hovered_color']

        corner = int(vals['corner_radius']) if vals['corner_radius'] is not None else 0

        # clamp corner radius to half the smallest side so Pygame renders it correctly
        cw, ch = self.size
        corner_clamped = max(0, min(corner, cw // 2, ch // 2))

        # draw background with corner radius
        if bg is not None:
            pygame.draw.rect(self.surface, bg, (0, 0, *self.size), border_radius=corner_clamped)

        # draw border if provided (use checked-specific border when selected)
        outer_border_color = vals.get('border_color_checked') if self._checked else vals.get('border_color')
        # avoid a border color identical to the background (happens if theme set border to bg_checked)
        if outer_border_color is not None and outer_border_color == bg:
            # prefer explicit inner border color if available
            outer_border_color = vals.get('inner_border_color') or outer_border_color
        # final fallback: if still matches bg or is None, compute a neutral gray
        if outer_border_color is None or outer_border_color == bg:
            avg = int(sum(bg) / 3) if isinstance(bg, (list, tuple)) else 120
            gray = max(0, min(255, avg - 40))
            outer_border_color = (gray, gray, gray)

        if outer_border_color is not None:
            pygame.draw.rect(self.surface, outer_border_color, (0, 0, *self.size), width=2, border_radius=corner_clamped)

        # draw inner rect only when checked (slightly inset from background)
        if self._checked:
            # always prefer explicit inner color from theme for the checked fill
            fill_color = vals.get('inner_color')
            if hovered and vals.get('inner_hover_color') is not None:
                fill_color = vals.get('inner_hover_color')

            # padding is a fraction of the smallest dimension so the inner rect scales
            pad = max(2, int(min(self.size) * 0.12))
            inner_w = max(1, self.size[0] - 2 * pad)
            inner_h = max(1, self.size[1] - 2 * pad)
            inner_rect = (pad, pad, inner_w, inner_h)

            pygame.draw.rect(self.surface, fill_color, inner_rect, border_radius=corner_clamped//2)

            # draw a subtle inner border; prefer explicit inner_border_color then fall back to outer
            inner_border_color = vals.get('inner_border_color')
            if inner_border_color is None:
                inner_border_color = outer_border_color
            if inner_border_color is not None:
                try:
                    pygame.draw.rect(self.surface, inner_border_color, inner_rect, width=1, border_radius=corner_clamped//2)
                except Exception:
                    pass

        # rebuild blits and render children
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ["CheckBox"]
