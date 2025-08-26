from . import util
import pygame


class Window:
    __slots__ = [
        "_surface", "children", "pos", "clock", "dt",
        "_size", "_event_handlers", "blits", "frame",
        "debug", "mode", "_overlay_focus"
    ]

    def __init__(self, size = (800, 600)) -> None:
        self._surface = pygame.display.set_mode(size)
        self._event_handlers = {}
        self.children = []
        self.pos = (0,0)
        self.clock = pygame.time.Clock()
        self._size = size
        # which overlay component currently has claimed focus (can consume events)
        self._overlay_focus = None
        self.frame = 0
        self.debug = False
        self.mode = 'hybrid'
        # blits will be a list of layers, each layer is a list of (surface, pos) tuples
        # layer 0 is the base layer (children), subsequent layers are overlays
        self.blits = []
        try:
            # enable key repeat: (delay ms, interval ms)
            pygame.key.set_repeat(400, 35)
        except Exception:
            pass

    def addChild(self, child) -> None:
        self.children.append(child)

    @property
    def surface(self) -> pygame.Surface:
        return self._surface

    @property
    def title(self) -> str:
        return pygame.display.get_caption()[0]

    @title.setter
    def title(self, title: str) -> None:
        pygame.display.set_caption(title)

    @property
    def size(self) -> tuple[int, int]:
        return self.surface.get_size()

    @size.setter
    def size(self, size) -> None:
        self._surface = pygame.display.set_mode(size)
        self.render()

    def event(self, event_type:int|str):
        def decorator(func):
            self._event_handlers[event_type] = func
            return func
        return decorator

    def _event(self, event: pygame.event.Event) -> None:
        # If an overlay has claimed focus, give it the first chance to handle the event
        overlay = getattr(self, '_overlay_focus', None)
        if overlay is not None:
            try:
                if overlay._event(event):
                    # if overlay handled a closing action, and it's now closed, clear focus
                    if not getattr(overlay, '_open', False):
                        setattr(self, '_overlay_focus', None)
                    return
            except Exception:
                # swallow overlay errors and fall back to normal dispatch
                pass

        for child in self.children:
            if child._event(event):
                return

        self._event_handlers.get(event.type, lambda e: None)(event)

    def render(self) -> None:
        for child in self.children:
            child.render()

    def draw(self) -> None:
        self.frame += 1
        # use theme background if available (dark-mode by default)
        try:
            from . import theme
            bg = theme.get('window_bg')
        except Exception:
            bg = (0, 0, 0)
        self.surface.fill(bg)

        if self._event_handlers:
            self._event_handlers.get('draw', lambda e: None)(self.frame)

        # Compose base layer from children
        base_blits = []
        for child in self.children:
            # each child provides a flat list of (surface, pos) tuples
            base_blits += child.blits

        # If self.blits already contains overlay layers (list of lists), preserve them.
        # Detect whether self.blits is already a list-of-lists; if not, treat it as empty overlays.
        overlays = []
        if self.blits and isinstance(self.blits[0], list):
            overlays = self.blits[1:]

        # Build final layered structure: base followed by overlays
        layers = [base_blits] + overlays

        # expose as window.blits (list of lists)
        self.blits = layers

        # Flatten for pygame blit call
        flat = []
        for layer in layers:
            flat.extend(layer)

        # batch blit
        if flat:
            self.surface.blits(flat)

        util.draw_performance_statistics(self.surface, self.clock)

        pygame.display.flip()

    def mainloop(self) -> None:
        self.render()
        if self.debug:
            # Window.every was implemented in un-pushed commit
            # self.every(100)(lambda: util.draw_performance_statistics(self.surface, self.clock))
            ...

        while True:
            self.dt = self.clock.tick()
            util.set_average_fps(self.clock.get_fps())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                self._event(event)

            # Always render each loop so time-based visuals (caret blink, IME
            # composition underline, animations) update. The 'mode' flag can
            # still be used to reduce work if desired.
            self.render()

            self.draw()
