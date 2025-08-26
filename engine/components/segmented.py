from .base import ComponentBase
from .. import theme
import pygame

class SegmentedControl(ComponentBase):
    def __init__(self, parent, pos, segments:list[str], size=(200, 32), selected=0, on_change=None):
        self._size = size
        self.segments = list(segments)
        self.selected = int(selected) if segments else -1
        self.on_change = on_change
        super().__init__(parent, pos, self._size)

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            ax, ay = self.absolute_pos
            if pygame.Rect(ax, ay, *self._size).collidepoint((mx, my)):
                lx = mx - ax
                # clicked segment
                seg_w = self._size[0] // max(1, len(self.segments))
                idx = min(len(self.segments)-1, lx // seg_w)
                if idx != self.selected:
                    self.selected = idx
                    try:
                        if callable(self.on_change):
                            self.on_change(idx, self.segments[idx])
                    except Exception:
                        pass
                    self.emit('change', idx, self.segments[idx])
                    self.render()
                return True
        return super()._event(event)

    def render(self) -> None:
        self.surface.fill((0,0,0,0))
        bg = theme.get('button_bg')
        fg = theme.get('button_text')
        sel = theme.get('accent')
        border = theme.get('frame_color')

        rect = self.surface.get_rect()
        try:
            pygame.draw.rect(self.surface, bg or (236,236,236), rect, border_radius=6)
        except Exception:
            self.surface.fill(bg or (236,236,236))

        n = max(1, len(self.segments))
        base_w = rect.width // n
        for i, label in enumerate(self.segments):
            x = i * base_w
            # last segment takes remaining width
            sw = base_w if i < n - 1 else rect.width - base_w * (n - 1)
            seg_rect = (x, 0, sw, rect.height)
            if i == self.selected:
                # draw selection inset by 1px so outer rounded border remains visible
                sx = x + 1
                sy = 1
                ssw = max(1, sw - 2)
                sh = max(1, rect.height - 2)
                # per-corner radii so edge segments keep rounded corners
                tl = 6 if i == 0 else 0
                tr = 6 if i == n - 1 else 0
                bl = tl
                br = tr
                try:
                    pygame.draw.rect(
                        self.surface,
                        sel or (40, 110, 200),
                        (sx, sy, ssw, sh),
                        border_top_left_radius=bl,
                        border_top_right_radius=br,
                        border_bottom_left_radius=bl,
                        border_bottom_right_radius=br,
                    )
                except Exception:
                    try:
                        pygame.draw.rect(self.surface, sel or (40,110,200), (sx, sy, ssw, sh))
                    except Exception:
                        pass
            # label
            try:
                from ..text import get_font
                font = get_font(None, 16)
                ts = font.render(str(label), True, fg or (20,20,20))
                tw, th = ts.get_size()
                tx = x + (sw - tw)//2
                ty = (rect.height - th)//2
                self.surface.blit(ts, (tx, ty))
            except Exception:
                pass

        # border
        try:
            pygame.draw.rect(self.surface, border or (200,200,200), rect, width=1, border_radius=6)
        except Exception:
            pass

        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

__all__ = ['SegmentedControl']
