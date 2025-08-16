from . import util
import pygame


class Window:
    __slots__ = [
        "_surface", "children", "pos", "clock", "dt",
        "_size", "_event_handlers", "blits", "frame",
        "debug", "mode"
    ]

    def __init__(self, size = (800, 600)) -> None:
        self._surface = pygame.display.set_mode(size)
        self._event_handlers = {}
        self.children = []
        self.pos = (0,0)
        self.clock = pygame.time.Clock()
        self._size = size
        self.frame = 0
        self.debug = False
        self.mode = 'hybrid'
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
            bg = theme.current_theme.get('window_bg', (0, 0, 0))
        except Exception:
            bg = (0, 0, 0)
        self.surface.fill(bg)

        if self._event_handlers:
            self._event_handlers.get('draw', lambda e: None)(self.frame)

        blits = []
        for child in self.children:
            blits += child.blits

        util.draw_performance_statistics(self.surface, self.clock)

        self.surface.blits(blits)

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
