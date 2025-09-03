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
        # MOUSEMOTION: update hover and optionally swallow
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            ax, ay = self.absolute_pos
            exp_h = self._size[1] + (self._item_height * len(self._options) if self._open else 0)
            hovered = pygame.Rect(ax, ay, self._size[0], exp_h).collidepoint((mx, my))
            if hovered != getattr(self, '_was_hovered', False):
                self._was_hovered = hovered
                self.render()
            return bool(self._open and hovered)

        # MOUSEBUTTONDOWN: handle toggle / option click / close on outside
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            ax, ay = self.absolute_pos
            exp_h = self._size[1] + (self._item_height * len(self._options) if self._open else 0)
            rect = pygame.Rect(ax, ay, self._size[0], exp_h)
            if not rect.collidepoint((mx, my)):
                if self._open:
                    self._close()
                    return True
                return False

            lx = mx - ax
            ly = my - ay
            if 0 <= ly <= self._size[1]:
                # click on header -> toggle
                if self._open:
                    self._close()
                else:
                    self._handle_dropdown_open()
                return True

            # click on option
            idx = int((ly - self._size[1]) // self._item_height)
            if 0 <= idx < len(self._options):
                self._selected_index = idx
                val = self._options[idx]
                try:
                    self.on_select(idx, val)
                except Exception:
                    pass
                self.emit('select', idx, val)
            self._close()
            return True

        # KEYDOWN: space/enter opens, arrows navigate, escape/enter close
        if event.type == pygame.KEYDOWN:
            key = event.key
            focused = getattr(self, '_was_hovered', False)
            if not self._open and focused and key in (pygame.K_SPACE, pygame.K_RETURN):
                self._handle_dropdown_open()
                return True

            if not self._open:
                return False

            if key == pygame.K_ESCAPE:
                self._close()
                return True

            if key in (pygame.K_UP, pygame.K_w) and self._options:
                self._selected_index = (self._selected_index - 1) % len(self._options)
                self.render()
                return True

            if key in (pygame.K_DOWN, pygame.K_s) and self._options:
                self._selected_index = (self._selected_index + 1) % len(self._options)
                self.render()
                return True

            if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if 0 <= self._selected_index < len(self._options):
                    val = self._options[self._selected_index]
                    try:
                        self.on_select(self._selected_index, val)
                    except Exception:
                        pass
                    self.emit('select', self._selected_index, val)
                self._close()
                return True

        return False

    def _handle_dropdown_open(self):
        self._open = True
        w = self._find_window()
        if w is not None:
            setattr(w, '_overlay_focus', self)
            try:
                if getattr(w, 'debug', False):
                    print(f"[Dropdown] open: popup will be requested; popup_gid(before)={getattr(self,'_popup_gid',None)}; window.blits.layers={len(getattr(w,'blits',[]))}")
            except Exception:
                pass
        self.render()

    def _close(self):
        popup_h = self._item_height * len(self._options)
        popup_pos = (self.absolute_pos[0], self.absolute_pos[1] + self._size[1])
        w = self._find_window()
        if (
            not w
            or not isinstance(w.blits, list)
            or len(w.blits) <= 1
            or not isinstance(w.blits[1], list)
        ):
            return self._set_dropdown_closed()

        # remove by stored gid when available
        gid = getattr(self, '_popup_gid', None)
        if gid is not None:
            try:
                if getattr(w, 'debug', False):
                    print(f"[Dropdown] closing: attempting remove_overlay gid={gid}; pre-layer-count={len(w.blits[1]) if len(w.blits)>1 else 0}")
                removed = w.remove_overlay(gid)
                if getattr(w, 'debug', False):
                    print(f"[Dropdown] remove_overlay returned {removed}; post-layer-count={len(w.blits[1]) if len(w.blits)>1 else 0}")
            except Exception:
                try:
                    w.blits[1] = [b for b in w.blits[1] if not (isinstance(b, tuple) and len(b) == 3 and b[0] == gid)]
                except Exception:
                    pass
            self._popup_gid = None
            # clear overlay focus if this dropdown had claimed it
            try:
                if getattr(w, '_overlay_focus', None) is self:
                    setattr(w, '_overlay_focus', None)
            except Exception:
                pass
            return self._set_dropdown_closed()
        # fallback: remove entries that match popup pos+size (handle (surf,pos) and (gid,surf,pos))
        new_overlay = []
        for entry in w.blits[1]:
            try:
                if isinstance(entry, tuple) and len(entry) == 3:
                    _g, surf, pos = entry
                elif isinstance(entry, tuple) and len(entry) == 2:
                    surf, pos = entry
                else:
                    new_overlay.append(entry)
                    continue

                if pos == popup_pos and getattr(surf, 'get_size', lambda: None)() == (self._size[0], popup_h):
                    # drop
                    continue
                new_overlay.append(entry)
            except Exception:
                new_overlay.append(entry)

        w.blits[1] = new_overlay
        try:
            if getattr(w, '_overlay_focus', None) is self:
                setattr(w, '_overlay_focus', None)
        except Exception:
            pass

        self._open = False
        self.render()

    def _set_dropdown_closed(self):
        self._open = False
        self.render()
        return

    def render(self) -> None:
        # Simplified dropdown rendering
        bg = self.bg
        txt_col = self.text_color
        border = self.border_color

        # Single draw call: background with border
        if border is not None:
            # Draw border first, then background (reduces from 2 rect calls to 2)
            pygame.draw.rect(self.surface, border, (0, 0, *self._size), border_radius=6)
            pygame.draw.rect(self.surface, bg, (1, 1, self._size[0]-2, self._size[1]-2), border_radius=5)
        else:
            # No border case
            pygame.draw.rect(self.surface, bg, (0, 0, *self._size), border_radius=6)

        # Selected text
        sel_text = ''
        if 0 <= self._selected_index < len(self._options):
            sel_text = str(self._options[self._selected_index])

        from .. import util
        try:
            txt_surf = util.cached_render(self._font, sel_text, txt_col)
        except Exception:
            txt_surf = self._font.render(sel_text, True, txt_col)
        self.surface.blit(txt_surf, (8, (self._size[1] // 2) - txt_surf.get_height() // 2))

        # Simplified arrow - use triangle instead of polygon 
        ax = self._size[0] - 18
        ay = self._size[1] // 2
        pts = [(ax - 6, ay - 3), (ax + 6, ay - 3), (ax, ay + 5)]
        pygame.draw.polygon(self.surface, txt_col, pts)

        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

        if not (self._open and self._options):
            return

        # Simplified popup rendering
        popup_h = self._item_height * len(self._options)
        popup = pygame.Surface((self._size[0], popup_h), pygame.SRCALPHA)
        popup_bg = theme.get('dropdown_bg') or (240, 240, 240)
        popup.fill(popup_bg)

        # Draw all options without individual hover rects (reduces draw calls significantly)
        for i, opt in enumerate(self._options):
            y_pos = i * self._item_height
            from .. import util
            try:
                ts = util.cached_render(self._font, str(opt), txt_col)
            except Exception:
                ts = self._font.render(str(opt), True, txt_col)
            popup.blit(ts, (8, y_pos + (self._item_height // 2) - ts.get_height() // 2))

        # Single border for popup
        if border is not None:
            pygame.draw.rect(popup, border, (0, 0, self._size[0], popup_h), width=1)

        popup_pos = (self.absolute_pos[0], self.absolute_pos[1] + self._size[1])
        if w := self._find_window():
            if not (w.blits and isinstance(w.blits[0], list)):
                base = w.blits if isinstance(w.blits, list) else []
                w.blits = [base]
            if len(w.blits) < 2:
                w.blits.append([])
            try:
                existing_gid = getattr(self, '_popup_gid', None)
                if existing_gid is not None:
                    # try to update existing overlay entry instead of appending a new one
                    updated = False
                    try:
                        for i, entry in enumerate(w.blits[1]):
                            if isinstance(entry, tuple) and len(entry) == 3 and entry[0] == existing_gid:
                                w.blits[1][i] = (existing_gid, popup, popup_pos)
                                updated = True
                                break
                    except Exception:
                        updated = False

                    if updated:
                        if getattr(w, 'debug', False):
                            print(f"[Dropdown] updated overlay gid={existing_gid}; layer1-count={len(w.blits[1])}")
                    else:
                        new_gid = w.add_overlay(popup, popup_pos, layer=1)
                        if getattr(w, 'debug', False):
                            print(f"[Dropdown] add_overlay returned gid={new_gid}; layer1-count={len(w.blits[1])}")
                        self._popup_gid = new_gid
                else:
                    new_gid = w.add_overlay(popup, popup_pos, layer=1)
                    if getattr(w, 'debug', False):
                        print(f"[Dropdown] add_overlay returned gid={new_gid}; layer1-count={len(w.blits[1])}")
                    self._popup_gid = new_gid
            except Exception:
                try:
                    gid = getattr(w, '_next_gid', 1)
                    try:
                        w._next_gid = gid + 1
                    except Exception:
                        pass
                    new_layer = []
                    for entry in w.blits[1]:
                        try:
                            if isinstance(entry, tuple) and len(entry) == 3:
                                _g, s, p = entry
                            elif isinstance(entry, tuple) and len(entry) == 2:
                                s, p = entry
                            else:
                                new_layer.append(entry)
                                continue
                            if p == popup_pos and getattr(s, 'get_size', lambda: None)() == (self._size[0], popup_h):
                                continue
                            new_layer.append(entry)
                        except Exception:
                            new_layer.append(entry)
                    new_layer.append((gid, popup, popup_pos))
                    w.blits[1] = new_layer
                    if getattr(w, 'debug', False):
                        print(f"[Dropdown] fallback inserted overlay as gid={gid}; layer1-count={len(w.blits[1])}")
                    self._popup_gid = gid
                except Exception:
                    w.blits[1].append((popup, popup_pos))
                    try:
                        if getattr(w, 'debug', False):
                            print(f"[Dropdown] fallback append without gid; layer1-count={len(w.blits[1])}")
                    except Exception:
                        pass
        else:
            self.blits.append((popup, popup_pos))


__all__ = ['Dropdown']

