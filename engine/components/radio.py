from .base import ComponentBase
from .. import theme
import pygame


class Radio(ComponentBase):
    # class-level group registry: list of lists, each index is a group
    _groups: list[list] = []

    # instance slots to match ComponentBase pattern and reduce per-instance memory
    __slots__ = ["_size", "_checked", "on_change", "_gid", "_composite_surface", "_composite_dirty", "_last_child_count"]

    def __init__(self, parent, pos, size=(18, 18), checked=False, group_gid: int | None = None, on_change=None):
        self._size = size
        self._checked = checked
        self.on_change = on_change
        super().__init__(parent, pos, self._size)

        # group_gid is either None or an index into Radio._groups
        if group_gid is None:
            self._gid = None
        else:
            gid = int(group_gid)
            # ensure groups list has that index
            if gid < 0:
                raise ValueError('group_gid must be >= 0 or None')
            while len(Radio._groups) <= gid:
                Radio._groups.append([])
            Radio._groups[gid].append(self)
            self._gid = gid

    @property
    def gid(self) -> int | None:
        return self._gid

    @property
    def checked(self):
        return self._checked

    def _set_checked(self, value: bool, emit=True):
        if value == self._checked:
            return
        self._checked = value
        try:
            if callable(self.on_change):
                self.on_change(self._checked)
        except Exception:
            pass
        if emit:
            self.emit('change', self._checked)
        self.render()

    def _select_self_and_unselect_others(self):
        if self._gid is None:
            # behave like a toggle when not in a group
            self._set_checked(not self._checked)
            return

        members = Radio._groups[self._gid]
        for r in members:
            # uncheck others, check this one
            r._set_checked(r is self, emit=(r is self))

        try:
            index = members.index(self)
            self.emit('group_select', index, self)
        except Exception:
            pass

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            rect = pygame.Rect(0, 0, *self.size).move(*self.absolute_pos)
            if rect.collidepoint((mx, my)):
                self._select_self_and_unselect_others()
                return True
        return super()._event(event)

    def render(self) -> None:
        # Draw radio circle
        bg = theme.get('radio_bg')
        border = theme.get('radio_border')
        dot = theme.get('radio_dot')

        rect = pygame.Rect(0, 0, *self.size)

        try:
            pygame.draw.ellipse(self.surface, bg, rect)
        except Exception:
            self.surface.fill(bg or (255, 255, 255))

        try:
            pygame.draw.ellipse(self.surface, border or (120, 120, 120), rect, width=1)
        except Exception:
            pass

        if self._checked:
            # inner dot: choose a larger, even size so it remains visible
            base = min(rect.width, rect.height) // 2
            iw = max(6, base)
            ih = iw
            # prefer increasing odd sizes to keep dot from shrinking
            if iw % 2 != 0:
                iw += 1
                ih = iw
            ir = pygame.Rect(0, 0, iw, ih)
            # center using integer center coordinates
            ir.center = (rect.width // 2, rect.height // 2)
            try:
                pygame.draw.ellipse(self.surface, dot or (40, 110, 200), ir)
            except Exception:
                pass

        # expose blits
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)


__all__ = ['Radio']
