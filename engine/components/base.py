from ..window import Window
import pygame


class ComponentBase:
    __slots__ = [
        "parent", "window", "_surface", "children", "_size", "blits", "_pos", 
        "_was_hovered", "events", "_cached_size", "_composite_surface", 
        "_composite_dirty", "_last_child_count"
    ]
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
        self._cached_size = None  # Cache the clamped size
        
        # Intermediate surface system
        self._composite_surface = None
        self._composite_dirty = True
        self._last_child_count = 0

        # simple event listeners: mapping event_name -> list[callable]
        self.events = {}

        parent.addChild(self)

        p = self.parent
        while not isinstance(p, Window):
            p = p.parent
        self.window = p

    def addChild(self, child) -> None:
        self.children.append(child)
        self._mark_composite_dirty()

    def _mark_composite_dirty(self) -> None:
        """Mark this component's composite surface as dirty and propagate up the parent chain."""
        self._composite_dirty = True
        self._composite_surface = None
        # Propagate up to parent
        if hasattr(self.parent, '_mark_composite_dirty'):
            self.parent._mark_composite_dirty()

    def _build_blits(self) -> None:
        """Build blits using simple direct approach (no composite surfaces)."""
        # Always use direct approach for maximum performance
        self.blits = [(self.surface, self.absolute_pos)]
        for child in self.children:
            child.render()
            self.blits.extend(child.blits)

    def _rebuild_composite(self) -> None:
        """Rebuild the composite surface containing this component and all children."""
        if not self.children:
            return
            
        # Calculate size needed for composite
        min_x = 0
        min_y = 0
        max_x = self.size[0]
        max_y = self.size[1]
        
        for child in self.children:
            child_right = child.pos[0] + child.size[0]
            child_bottom = child.pos[1] + child.size[1]
            max_x = max(max_x, child_right)
            max_y = max(max_y, child_bottom)
            
        # Create composite surface
        comp_width = max(1, max_x - min_x)
        comp_height = max(1, max_y - min_y)
        try:
            # Use standard surface creation for speed
            self._composite_surface = pygame.Surface((comp_width, comp_height), pygame.SRCALPHA)
            
            # Blit this component's surface first (background)
            if self.surface:
                self._composite_surface.blit(self.surface, (0, 0))
            
            # Blit all children on top
            for child in self.children:
                child.render()  # Ensure child is up to date
                if child.children and hasattr(child, '_composite_surface') and child._composite_surface:
                    # Child has its own composite - use that
                    self._composite_surface.blit(child._composite_surface, child.pos)
                elif child.surface:
                    # Child has no children or no composite - use regular surface
                    self._composite_surface.blit(child.surface, child.pos)
                    
            # Mark as clean
            self._composite_dirty = False
            self._last_child_count = len(self.children)
        except Exception as e:
            # Fall back to no composite if there's an error
            self._composite_surface = None
            self._composite_dirty = True

    def _clamp_size(self) -> tuple[int, int]:
        return (
            max(0, min(self._size[0], self.parent._size[0] - self.pos[0])),
            max(0, min(self._size[1], self.parent._size[1] - self.pos[1]))
        )

    def _hovered(self, mouse_pos=None) -> tuple[bool, bool]:
        if not mouse_pos:
            mouse_pos = pygame.mouse.get_pos()

        # Cache rect calculation since absolute_pos is now cached
        abs_pos = self.absolute_pos  # This is now cached
        rect = pygame.Rect(abs_pos[0], abs_pos[1], *self.size)
        hovered = rect.collidepoint(mouse_pos)
        changed = hovered != self._was_hovered
        if changed:
            self._was_hovered = hovered
        return hovered, changed

    @property
    def surface(self) -> pygame.Surface:
        # Use cached size to avoid repeated _clamp_size() calls
        if self._cached_size is None:
            self._cached_size = self._clamp_size()
            
        size = self._cached_size
        if self._surface is None or self._surface.get_size() != size:
            # Create surface - prioritize speed over premultiplied alpha for now
            self._surface = pygame.Surface(size, pygame.SRCALPHA)
            try:
                self._surface = self._surface.convert_alpha()
            except Exception:
                pass
                
        return self._surface

    @property
    def pos(self) -> tuple[int, int]:
        return self._pos

    @pos.setter
    def pos(self, value) -> None:
        if self._pos != value:
            self._pos = value
            self._cached_size = None  # Invalidate size cache
            self._mark_composite_dirty()
            self._build_blits()

    @property
    def size(self) -> tuple[int, int]:
        # Use cached size to avoid accessing surface property
        if self._cached_size is None:
            self._cached_size = self._clamp_size()
        return self._cached_size

    @size.setter
    def size(self, value) -> None:
        if self._size != value:
            self._size = value
            self._cached_size = None  # Invalidate size cache
            self._mark_composite_dirty()
            self._build_blits()
            self._surface = None  # Force recreation on next access
            self.render()

    @property
    def absolute_pos(self) -> tuple[int, int]:
        return (self.pos[0] + self.parent.pos[0], self.pos[1] + self.parent.pos[1])

    # Placeholders, will be overwritten
    def render(self) -> None:
        ...

    def _event(self, event: pygame.event.Event) -> bool:
        return any(
            self.children[i]._event(event)
            for i in range(len(self.children) - 1, -1, -1)
        )

    # Lightweight event emitter for components
    def on(self, event_name: str, callback):
        # Insert at beginning so newest handlers get processed first
        if event_name not in self.events:
            self.events[event_name] = [callback]
        else:
            self.events[event_name].insert(0, callback)

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
