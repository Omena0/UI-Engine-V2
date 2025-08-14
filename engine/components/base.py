import pygame

class ComponentBase:
    __slots__ = ["parent", "_surface", "children", "_size", "blits", "_pos"]
    def __init__(self, parent, pos) -> None:
        self.parent = parent
        self._surface = None
        self._pos = pos
        self.children = []
        self.blits = []

        parent.addChild(self)

    def addChild(self, child) -> None:
        self.children.append(child)
        self._build_blits()

    def _build_blits(self):
        """Recursively build the blits list for this component and its descendants."""
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            self.blits.extend(child.blits)

    def _clamp_size(self) -> tuple[int, int]:
        return (
            max(0, min(self._size[0], self.parent._size[0] - self.pos[0])),
            max(0, min(self._size[1], self.parent._size[1] - self.pos[1]))
        )

    @property
    def surface(self) -> pygame.Surface:
        if self._surface is None or self._surface.get_size() != self._clamp_size():
            self._surface = pygame.Surface(self._clamp_size(), pygame.SRCALPHA)

        return self._surface

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, value) -> None:
        self._pos = value
        self._build_blits()

    @property
    def size(self) -> tuple[int, int]:
        return self.surface.get_size()

    @size.setter
    def size(self, value) -> None:
        self._size = value
        self._build_blits()
        self._surface = pygame.Surface(self._clamp_size(), pygame.SRCALPHA)
        self.render()

    @property
    def absolute_pos(self) -> tuple[int, int]:
        return (self.pos[0] + self.parent.pos[0], self.pos[1] + self.parent.pos[1])

    # Placeholders, will be overwritten
    def render(self) -> None:
        ...

    def _event(self, event: pygame.event.Event) -> bool:
        for child in self.children:
            if child._event(event):
                return True
        return False

__all__ = ["ComponentBase"]
