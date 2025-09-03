from .base import ComponentBase
from .. import theme
from ..text import get_font
import pygame
from typing import List, Callable, Optional


class SegmentedButton(ComponentBase):
    __slots__ = [
        "_size",
        "_segments",
        "_selected",
        "_corner_radius",
        "_ov_bg_color",
        "_ov_text_color",
        "_ov_sel_color",
        "_font",
        "on_change",
        "_composite_surface",
        "_composite_dirty",
        "_last_child_count",
    ]

    def __init__(
        self,
        parent,
        pos,
        segments: List[str],
        size=(200, 32),
        selected: int = 0,
        bg_color=None,
        text_color=None,
        sel_color=None,
        corner_radius=6,
        on_change: Optional[Callable] = None,
    ) -> None:
        self._size = size
        self._segments = list(segments)
        self._selected = selected if segments else -1
        self._ov_bg_color = bg_color
        self._ov_text_color = text_color
        self._ov_sel_color = sel_color
        self._corner_radius = corner_radius
        self._font = get_font(None, 16)
        self.on_change = on_change or (lambda *a, **k: None)

        super().__init__(parent, pos, self._size)

    @property
    def segments(self) -> List[str]:
        return self._segments

    @segments.setter
    def segments(self, v: List[str]) -> None:
        self._segments = list(v)
        # ensure selected index remains valid
        if not self._segments:
            self._selected = -1
        else:
            self._selected = max(0, min(self._selected, len(self._segments) - 1))
        self.render()

    @property
    def selected(self) -> int:
        return self._selected

    @selected.setter
    def selected(self, idx: int) -> None:
        if idx == self._selected:
            return
        self._selected = idx
        self.emit("change", idx, self._segments[idx] if 0 <= idx < len(self._segments) else None)
        self.render()

    # Resolved at render time so theme updates propagate immediately
    @property
    def bg_color(self):
        return self._ov_bg_color if self._ov_bg_color is not None else theme.get("button_bg")

    @property
    def text_color(self):
        return self._ov_text_color if self._ov_text_color is not None else theme.get("button_text")

    @property
    def sel_color(self):
        return self._ov_sel_color if self._ov_sel_color is not None else theme.get("accent")

    def _event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            # re-render on hover change
            if self._hovered(event.pos)[1]:
                self.render()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self._hovered(event.pos)[0]:
                mx, my = event.pos
                ax, ay = self.absolute_pos
                lx = mx - ax
                n = max(1, len(self._segments))
                seg_w = self._size[0] // n
                idx = min(len(self._segments) - 1, lx // seg_w)
                if idx != self._selected:
                    self._selected = idx
                    try:
                        if callable(self.on_change):
                            self.on_change(idx, self._segments[idx])
                    except Exception:
                        pass
                    self.emit("change", idx, self._segments[idx])
                    self.render()
                return True
        return False

    def render(self) -> None:
        surf = self.surface  # Cache surface reference
        bg = self.bg_color
        fg = self.text_color
        sel = self.sel_color
        border = theme.get("frame_color")

        rect = pygame.Rect(0, 0, *self.size)
        n = max(1, len(self._segments))
        base_w = rect.width // n
        
        # Draw background with full corner radius
        try:
            pygame.draw.rect(surf, bg or (236, 236, 236), rect, border_radius=self._corner_radius)
        except Exception:
            surf.fill(bg or (236, 236, 236))

        # Draw selected segment with proper corner radius handling
        if 0 <= self._selected < n:
            i = self._selected
            x = i * base_w
            sw = base_w if i < n - 1 else rect.width - base_w * (n - 1)
            sx = x + 1
            sy = 1
            ssw = max(1, sw - 2)
            sh = max(1, rect.height - 2)
            
            # Proper corner radius for selected segment
            try:
                # Only apply corner radius to the ends of the segmented control
                tl = self._corner_radius - 1 if i == 0 else 0
                tr = self._corner_radius - 1 if i == n - 1 else 0
                bl = self._corner_radius - 1 if i == 0 else 0
                br = self._corner_radius - 1 if i == n - 1 else 0
                
                pygame.draw.rect(
                    surf,
                    sel or (40, 110, 200),
                    (sx, sy, ssw, sh),
                    border_top_left_radius=max(0, tl),
                    border_top_right_radius=max(0, tr),
                    border_bottom_left_radius=max(0, bl),
                    border_bottom_right_radius=max(0, br),
                )
            except Exception:
                # Fallback to simple rect
                pygame.draw.rect(surf, sel or (40, 110, 200), (sx, sy, ssw, sh))

        # Render all text in one pass
        for i, label in enumerate(self._segments):
            x = i * base_w
            sw = base_w if i < n - 1 else rect.width - base_w * (n - 1)
            
            try:
                from .. import util
                try:
                    ts = util.cached_render(self._font, str(label), fg or (20, 20, 20))
                except Exception:
                    ts = self._font.render(str(label), True, fg or (20, 20, 20))
                tw, th = ts.get_size()
                tx = x + (sw - tw) // 2
                ty = (rect.height - th) // 2
                surf.blit(ts, (tx, ty))
            except Exception:
                pass

        # Single border draw at the end
        if border:
            try:
                pygame.draw.rect(surf, border or (200, 200, 200), rect, width=1, border_radius=self._corner_radius)
            except Exception:
                pygame.draw.rect(surf, border or (200, 200, 200), rect, width=1)

            sw = base_w if i < n - 1 else rect.width - base_w * (n - 1)
            
            # label
            try:
                from .. import util
                try:
                    ts = util.cached_render(self._font, str(label), fg or (20, 20, 20))
                except Exception:
                    # Fall back to direct rendering if caching fails
                    ts = self._font.render(str(label), True, fg or (20, 20, 20))
                tw, th = ts.get_size()
                tx = x + (sw - tw) // 2
                ty = (rect.height - th) // 2
                surf.blit(ts, (tx, ty))
            except Exception:
                pass

        # Draw border last (single rect draw)
        try:
            pygame.draw.rect(surf, border or (200, 200, 200), rect, width=1, border_radius=self._corner_radius)
        except Exception:
            pass

        # Mark composite as dirty since we updated our surface and build blits
        self._mark_composite_dirty()
        self._build_blits()


__all__ = ["SegmentedButton"]
