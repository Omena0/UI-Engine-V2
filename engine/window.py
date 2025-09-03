from . import util
import pygame
import time


class Window:
    __slots__ = [
        "_surface", "children", "pos", "clock", "dt",
        "_size", "_event_handlers", "blits", "frame",
        "debug", "mode", "_overlay_focus", "_next_gid",
        "_last_frame_time"
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
        # numeric id allocator for overlay groups
        self._next_gid = 1
        self.frame = 0
        self.debug = False
        self.mode = 'hybrid'
        # blits will be a list of layers, each layer is a list of (surface, pos) tuples
        # layer 0 is the base layer (children), subsequent layers are overlays
        self.blits = []
        
        # High precision timing
        self._last_frame_time = time.perf_counter()
        
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

        # Build flat list for pygame-ce fblits with viewport culling
        flat = []
        window_rect = pygame.Rect(0, 0, *self.size)
        
        for layer in layers:
            for entry in layer:
                if not entry:
                    continue
                    
                surf, pos = None, None
                if isinstance(entry, tuple) and len(entry) == 2:
                    surf, pos = entry
                elif isinstance(entry, tuple) and len(entry) == 3:
                    # (gid, surface, pos)
                    _, surf, pos = entry
                else:
                    continue
                
                # Viewport culling - only render surfaces that intersect with window
                if surf and pos:
                    surf_rect = pygame.Rect(pos[0], pos[1], surf.get_width(), surf.get_height())
                    if window_rect.colliderect(surf_rect):
                        flat.append((surf, pos))

        # Direct pygame-ce fblits for maximum performance
        if flat:
            self.surface.fblits(flat)

        util.draw_performance_statistics(self.surface, self.dt)

        pygame.display.flip()

    def add_overlay(self, surface: pygame.Surface, pos: tuple[int,int], layer:int=1) -> int:
        """Add an overlay surface to a given layer and return a numeric GID.

        The overlay entry is stored as (gid, surface, pos).
        """
        # ensure layered structure
        if not (self.blits and isinstance(self.blits[0], list)):
            base = self.blits if isinstance(self.blits, list) else []
            self.blits = [base]
        # ensure requested layer exists
        while len(self.blits) <= layer:
            self.blits.append([])
        gid = getattr(self, '_next_gid', 1)
        try:
            self._next_gid = gid + 1
        except Exception:
            # best-effort; if _next_gid can't be set, continue without increment
            pass
        self.blits[layer].append((gid, surface, pos))
        return gid

    def remove_overlay(self, gid: int) -> bool:
        """Remove overlay entries with the given gid. Returns True if any removed."""
        removed = False
        if not (self.blits and isinstance(self.blits[0], list)):
            return False
        for i in range(1, len(self.blits)):
            before = len(self.blits[i])
            self.blits[i] = [b for b in self.blits[i] if not (isinstance(b, tuple) and len(b) == 3 and b[0] == gid)]
            if len(self.blits[i]) != before:
                removed = True
        return removed

    def mainloop(self) -> None:
        self.render()

        while True:
            # Calculate high precision deltatime
            current_time = time.perf_counter()
            self.dt = (current_time - self._last_frame_time) * 1000
            self._last_frame_time = current_time

            # Still use pygame clock for FPS calculation
            self.clock.tick()
            util.set_average_fps(self.clock.get_fps())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                self._event(event)

            # Only render every frame if in immediate mode
            # You should never enable this unless something breaks.
            # Immediate mode will give 10x worse performance.
            if self.mode == 'immediate':
                self.render()

            self.draw()

