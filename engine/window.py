from threading import Thread
from . import util
import time as t
import pygame


class Window:
    __slots__ = [
        "_surface", "children", "pos", "clock", "dt", "_size", "_event_handlers",
        "_blits", "frame", "debug", "_interval_events"
    ]

    def __init__(self, size = (800, 600)) -> None:
        self._surface = pygame.display.set_mode(size)
        self._event_handlers  = {}
        self._interval_events = {}
        self.children = []
        self.pos = (0,0)
        self.clock = pygame.time.Clock()
        self._size = size
        self.frame = 0
        self.debug = False
        self._blits = []

    def addChild(self, child) -> None:
        self.children.append(child)

    def event(self, event_type:int|str):
        def decorator(func):
            self._event_handlers[event_type] = func
            return func
        return decorator

    def every(self, duration: int):
        """
            Request the event loop to call a function every `duration` ms.
        """
        if not duration in self._interval_events:
            self._interval_events[duration] = []
        def decorator(func):
            self._interval_events[duration].append((t.time()*1000, func))
            return func
        return decorator

    def blit(self, surface: pygame.Surface, pos: tuple[int, int]) -> None:
        self._blits.append((surface, pos))

    def blits(self, blits: list[tuple[pygame.Surface, tuple[int, int]]]) -> None:
        self._blits.extend(blits)

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
        self.surface.fill((0, 0, 0))

        self._event_handlers.get('draw', lambda e: None)(self.frame)

        blits = []
        for child in self.children:
            blits.extend(child.blits)

        blits.extend(self._blits)

        self.surface.blits(blits)

        # Performance statistics
        if self.debug:
            util.draw_performance_statistics(self.surface, self.clock)

        pygame.display.flip()

    def mainloop(self) -> None:
        # Pre-render all components
        self.render()

        while True:
            self.dt = self.clock.tick()
            util.set_average_fps(self.clock.get_fps())

            # Normal events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                self._event(event)

            # Interval events
            for freq, events in self._interval_events.items():
                for (timer, callback) in events:
                    if t.time()*1000-timer > freq:
                        timer = t.time()*1000
                        self._interval_events[freq] = [(timer, callback)]
                        callback()

            self.draw()

