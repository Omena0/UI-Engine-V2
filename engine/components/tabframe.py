from typing import Any, List
from .base import ComponentBase
from .frame import Frame
from .. import theme
import pygame


class TabFrame(ComponentBase):
    __slots__ = ["_size", "_tab_frames", "_current", "_ov_color", "_corner_radius", "_header_height", "_composite_surface", "_composite_dirty", "_last_child_count"]

    def __init__(
        self,
        parent,
        pos,
        size,
        tab_count: int = 3,
        current: int = 0,
        color=None,
        corner_radius: int = 8,
        header_height: int = 48,
    ) -> None:
        # store overrides and initial state
        self._size = size
        self._ov_color = color
        self._corner_radius = corner_radius
        self._header_height = header_height
        self._current = 0
        self._tab_frames: List[Frame] = []

        super().__init__(parent, pos, self._size)

        # Create frames for each tab
        self._create_tab_frames(tab_count)
        self.current = current

    def _create_tab_frames(self, count: int) -> None:
        """Create Frame objects for each tab."""
        self._tab_frames = []

        # Calculate the content area (below the header)
        content_y = self._header_height
        content_width = self._size[0] - 16  # 8px margin on each side
        content_height = self._size[1] - content_y - 8  # Header height + bottom margin

        for _ in range(count):
            frame = Frame(
                self,
                (8, content_y),
                (content_width, content_height),
                color=self._ov_color,
                corner_radius=self._corner_radius
            )
            self._tab_frames.append(frame)

        # Set the first frame as active
        self.children = [self._tab_frames[0]] if self._tab_frames else []

    def __getitem__(self, index: int) -> Frame:
        """Allow access to tab frames using tabframe[index] syntax."""
        if 0 <= index < len(self._tab_frames):
            return self._tab_frames[index]
        raise IndexError(f"Tab index {index} out of range (0-{len(self._tab_frames)-1})")

    def add_tab(self) -> Frame:
        """Add a new tab and return its frame."""
        content_y = self._header_height
        content_width = self._size[0] - 16
        content_height = self._size[1] - content_y - 8
        
        frame = Frame(
            self,
            (8, content_y),
            (content_width, content_height),
            color=self._ov_color,
            corner_radius=self._corner_radius
        )
        self._tab_frames.append(frame)
        return frame

    @property
    def tab_count(self) -> int:
        return len(self._tab_frames)

    @property
    def color(self) -> Any:
        return self._ov_color if self._ov_color is not None else theme.get("frame_color")

    @color.setter
    def color(self, v) -> None:
        self._ov_color = v
        # Update all tab frame colors
        for frame in self._tab_frames:
            frame.color = v
        self.render()

    @property
    def corner_radius(self) -> int:
        return self._corner_radius

    @corner_radius.setter
    def corner_radius(self, v: int) -> None:
        self._corner_radius = v
        # Update all tab frame corner radius
        for frame in self._tab_frames:
            frame.corner_radius = v
        self.render()

    @property
    def current(self) -> int:
        return self._current

    @current.setter
    def current(self, idx: int) -> None:
        if not self._tab_frames:
            self._current = 0
            self.children = []
            self.render()
            return

        idx = max(0, min(idx, len(self._tab_frames) - 1))
        if idx == self._current:
            return

        self._current = idx
        # Switch to the selected tab frame
        self.children = [self._tab_frames[self._current]]
        self.emit("tabchange", idx)
        self.render()

    def render(self) -> None:
        # draw frame background
        try:
            pygame.draw.rect(
                self.surface,
                self.color,
                (0, 0, *self.size),
                border_radius=self.corner_radius,
            )
        except Exception:
            # fallback
            self.surface.fill(self.color)

        # render only the current tab's frame
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            try:
                child.render()
                self.blits.extend(child.blits)
            except Exception:
                pass


__all__ = ["TabFrame"]
