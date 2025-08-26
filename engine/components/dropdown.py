from .base import ComponentBase
from ..text import get_font
from .. import theme
import pygame
from ..window import Window


class Dropdown(ComponentBase):
    def __init__(self, parent, pos, size=(200, 34), options=None, selected=0, bg=None, text_color=None, border_color=None, font=(None, 20), on_select=None):
        self._size = size
        self._options = options or []
        self._selected_index = max(0, min(len(self._options) - 1, int(selected))) if self._options else -1
        self._ov_bg = bg
        self._ov_text = text_color
        self._ov_border = border_color
        self._open = False
        self.on_select = on_select if on_select is not None else (lambda i, v: ...)
        self._font = font if isinstance(font, pygame.font.Font) else get_font(*font)
        self._item_height = max(28, int(self._size[1]))
        super().__init__(parent, pos, self._size)

    @property
    def bg(self):
        return self._ov_bg if self._ov_bg is not None else theme.get('dropdown_bg')

    @property
    def text_color(self):
        return self._ov_text if self._ov_text is not None else theme.get('dropdown_text')

    @property
    def border_color(self):
        return self._ov_border if self._ov_border is not None else theme.get('dropdown_border')

    def _find_window(self):
        w = self.parent
        while w is not None and not isinstance(w, Window):
            w = getattr(w, 'parent', None)
        return w if isinstance(w, Window) else None

    def _event(self, event: pygame.event.Event) -> bool:
        handled = False
        if event.type == pygame.MOUSEMOTION:
            # update hovered state relative to expanded area when open
            mx, my = event.pos
            ax, ay = self.absolute_pos
            exp_h = self._size[1] + (self._item_height * len(self._options) if self._open else 0)
            hovered = pygame.Rect(ax, ay, self._size[0], exp_h).collidepoint((mx, my))
            changed = hovered != getattr(self, '_was_hovered', False)
            self._was_hovered = hovered
            if changed:
                self.render()
            if self._open and hovered:
                handled = True

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            ax, ay = self.absolute_pos
            exp_h = self._size[1] + (self._item_height * len(self._options) if self._open else 0)
            if pygame.Rect(ax, ay, self._size[0], exp_h).collidepoint((mx, my)):
                # local coords
                lx = mx - ax
                ly = my - ay
                if 0 <= ly <= self._size[1]:
                    # toggle
                    if self._open:
                        self._close()
                    else:
                        self._extracted_from__event_30()
                    handled = True
                else:
                    # clicked an option
                    idx = (ly - self._size[1]) // self._item_height
                    try:
                        idx = int(idx)
                        if 0 <= idx < len(self._options):
                            self._selected_index = idx
                            val = self._options[idx]
                            try:
                                self.on_select(idx, val)
                            except Exception:
                                pass
                            self.emit('select', idx, val)
                            handled = True
                    except Exception:
                        pass
                    self._close()
            elif self._open:
                self._close()
                handled = True

        elif event.type == pygame.KEYDOWN:
            key = event.key
            focused = getattr(self, '_was_hovered', False)
            if not self._open and focused and key in (pygame.K_SPACE, pygame.K_RETURN):
                self._extracted_from__event_30()
                handled = True
            elif self._open:
                if key == pygame.K_ESCAPE:
                    self._close()
                    handled = True
                elif key in (pygame.K_UP, pygame.K_w):
                    if self._options:
                        self._selected_index = (self._selected_index - 1) % len(self._options)
                        self.render()
                elif key in (pygame.K_DOWN, pygame.K_s):
                    if self._options:
                        self._selected_index = (self._selected_index + 1) % len(self._options)
                        self.render()
                elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if 0 <= self._selected_index < len(self._options):
                        val = self._options[self._selected_index]
                        try:
                            self.on_select(self._selected_index, val)
                        except Exception:
                            pass
                        self.emit('select', self._selected_index, val)
                    self._close()
                    handled = True

        return handled

    # TODO Rename this here and in `_event`
    def _extracted_from__event_30(self):
        self._open = True
        # claim overlay focus on window so events don't pass through
        w = self._find_window()
        if w is not None:
            setattr(w, '_overlay_focus', self)
        self.render()

    def _close(self):
        # remove popup from window overlay so it doesn't linger
        popup_h = self._item_height * len(self._options)
        popup_pos = (self.absolute_pos[0], self.absolute_pos[1] + self._size[1])
        w = self._find_window()
        if w and isinstance(w.blits, list) and len(w.blits) > 1 and isinstance(w.blits[1], list):
            if getattr(self, '_popup_gid', None) is not None:
                gid = self._popup_gid
                try:
                    w.remove_overlay(gid)
                except Exception:
                    # fallback to manual filter
                    w.blits[1] = [b for b in w.blits[1] if not (isinstance(b, tuple) and len(b) == 3 and b[0] == gid)]
                self._popup_gid = None
            else:
                w.blits[1] = [
                    b
                    for b in w.blits[1]
                    if b[1] != popup_pos or b[0].get_size() != (self._size[0], popup_h)
                ]

        self._open = False
        self.render()

    def render(self) -> None:
        # draw main
        self.surface.fill((0, 0, 0, 0))
        bg = self.bg
        txt_col = self.text_color
        border = self.border_color

        try:
            if self._open:
                pygame.draw.rect(
                    self.surface,
                    bg,
                    (0, 0, *self._size),
                    border_top_left_radius=6,
                    border_top_right_radius=6,
                    border_bottom_left_radius=0,
                    border_bottom_right_radius=0,
                )
            else:
                pygame.draw.rect(self.surface, bg, (0, 0, *self._size), border_radius=6)
        except Exception:
            pygame.draw.rect(self.surface, bg, (0, 0, *self._size))

        if border is not None:
            try:
                if self._open:
                    pygame.draw.rect(
                        self.surface,
                        border,
                        (0, 0, *self._size),
                        width=1,
                        border_top_left_radius=6,
                        border_top_right_radius=6,
                        border_bottom_left_radius=0,
                        border_bottom_right_radius=0,
                    )
                else:
                    pygame.draw.rect(self.surface, border, (0, 0, *self._size), width=1, border_radius=6)
            except Exception:
                pygame.draw.rect(self.surface, border, (0, 0, *self._size), width=1)

        sel_text = ''
        if 0 <= self._selected_index < len(self._options):
            sel_text = str(self._options[self._selected_index])

        txt_surf = self._font.render(sel_text, True, txt_col)
        self.surface.blit(txt_surf, (8, (self._size[1] // 2) - txt_surf.get_height() // 2))

        ax = self._size[0] - 18
        ay = self._size[1] // 2
        pts = [(ax - 6, ay - 3), (ax + 6, ay - 3), (ax, ay + 5)]
        pygame.draw.polygon(self.surface, txt_col, pts)

        # base blits for this component
        self.blits = [(self.surface, self.absolute_pos)]

        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

        # popup into window overlay
        if self._open and self._options:
            popup_h = self._item_height * len(self._options)
            popup = pygame.Surface((self._size[0], popup_h), pygame.SRCALPHA)
            # ensure opaque background so popup doesn't render transparently over other components
            try:
                popup.fill(theme.get('dropdown_bg'))
            except Exception:
                popup.fill((240, 240, 240))
            for i, opt in enumerate(self._options):
                rect = (0, i * self._item_height, self._size[0], self._item_height)
                mouse_pos = pygame.mouse.get_pos()
                ax, ay = self.absolute_pos
                if pygame.Rect(rect).move(ax, ay + self._size[1]).collidepoint(mouse_pos):
                    hover_col = theme.get('dropdown_hover')
                    if hover_col is not None:
                        pygame.draw.rect(popup, hover_col, rect)
                ts = self._font.render(str(opt), True, txt_col)
                popup.blit(ts, (8, rect[1] + (self._item_height // 2) - ts.get_height() // 2))
            if border is not None:
                try:
                    pygame.draw.rect(
                        popup,
                        border,
                        (0, 0, self._size[0], popup_h),
                        width=1,
                        border_top_left_radius=0,
                        border_top_right_radius=0,
                        border_bottom_left_radius=6,
                        border_bottom_right_radius=6,
                    )
                except Exception:
                    pygame.draw.rect(popup, border, (0, 0, self._size[0], popup_h), width=1)

            popup_pos = (self.absolute_pos[0], self.absolute_pos[1] + self._size[1])
            if w := self._find_window():
                # ensure layered structure
                if not (w.blits and isinstance(w.blits[0], list)):
                    base = w.blits if isinstance(w.blits, list) else []
                    w.blits = [base]
                if len(w.blits) < 2:
                    w.blits.append([])
                # let Window manage overlay gid allocation when possible
                try:
                    new_gid = w.add_overlay(popup, popup_pos, layer=1)
                    self._popup_gid = new_gid
                except Exception:
                    # fallback to manual behavior (position/size dedupe)
                    w.blits[1] = [
                        b
                        for b in w.blits[1]
                        if b[1] != popup_pos
                        or b[0].get_size() != (self._size[0], popup_h)
                    ]
                    w.blits[1].append((popup, popup_pos))
            else:
                self.blits.append((popup, popup_pos))


__all__ = ['Dropdown']

