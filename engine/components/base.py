import pygame

class ComponentBase:
    __slots__ = ["parent", "_surface", "children", "_size", "blits", "_pos", "_was_hovered", "events"]
    def __init__(self, parent, pos, size=None) -> None:
        self.parent = parent
        self._surface = None
        self._pos = pos
        # initialize _size: if provided, use it; otherwise default to parent's remaining space
        if size is not None:
            self._size = size
        else:
            try:
                # default to fill remaining area inside parent
                self._size = (
                    max(0, parent._size[0] - pos[0]),
                    max(0, parent._size[1] - pos[1])
                )
            except Exception:
                # parent may not have _size set during construction; fallback to zero-size
                self._size = (0, 0)

        self.children = []
        self.blits = []

        self._was_hovered = False
        # simple event listeners: mapping event_name -> list[callable]
        self.events = {}

        parent.addChild(self)

    def addChild(self, child) -> None:
        self.children.append(child)
        self._build_blits()

    def _build_blits(self) -> None:
        """Recursively build the blits list for this component and its descendants."""
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            self.blits.extend(child.blits)

    def _clamp_size(self) -> tuple[int, int]:
        return (
            max(0, min(self._size[0], self.parent._size[0] - self.pos[0])),
            max(0, min(self._size[1], self.parent._size[1] - self.pos[1]))
        )

    def _hovered(self, mouse_pos=None) -> tuple[bool, bool]:
        if not mouse_pos:
            mouse_pos = pygame.mouse.get_pos()

        hovered = self.surface.get_rect().move(*self.absolute_pos).collidepoint(mouse_pos)
        changed = hovered != self._was_hovered
        self._was_hovered = hovered
        return hovered, changed

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

    # Lightweight event emitter for components
    def on(self, event_name: str, callback):
        self.events.setdefault(event_name, []).append(callback)

    def off(self, event_name: str, callback=None):
        if event_name not in self.events:
            return
        if callback is None:
            self.events.pop(event_name, None)
        else:
            try:
                self.events[event_name].remove(callback)
            except ValueError:
                pass

    def emit(self, event_name: str, *args, **kwargs):
        for cb in list(self.events.get(event_name, [])):
            try:
                cb(*args, **kwargs)
            except Exception:
                # swallow exceptions from listeners to avoid breaking UI loop
                pass

__all__ = ["ComponentBase"]
