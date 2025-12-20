from .base import ComponentBase
from .frame import Frame
from .label import Label
from .iconbutton import IconButton
from .. import theme
import pygame
from typing import Callable, Optional, Tuple, Any


class ChildWindow(ComponentBase):
    __slots__ = [
        '_title', '_size', '_toolbar_height', '_resizable', '_draggable',
        '_minimized', '_maximized', '_closable', '_minimizable', '_maximizable',
        '_drag_offset', '_dragging', '_border_width', '_corner_radius',
        '_on_close', '_on_minimize', '_on_maximize', '_on_restore', '_on_move',
        '_content_area', '_toolbar', '_title_label', '_close_button', 
        '_minimize_button', '_maximize_button', '_last_normal_pos', '_last_normal_size',
        '_rendered', '_window_frame', '_min_size'
    ]

    def __init__(
        self,
        parent,
        pos: Tuple[int, int],
        size: Tuple[int, int],
        title: str = "Child Window",
        toolbar_height: int = 30,
        resizable: bool = True,
        draggable: bool = True,
        closable: bool = True,
        minimizable: bool = True,
        maximizable: bool = True,
        border_width: int = 2,
        corner_radius: int = 8,
        min_size: Tuple[int, int] = (200, 150),
        on_close: Optional[Callable] = None,
        on_minimize: Optional[Callable] = None,
        on_maximize: Optional[Callable] = None,
        on_restore: Optional[Callable] = None,
        on_move: Optional[Callable] = None
    ) -> None:
        """
        Create a ChildWindow component that acts as a container with window controls.
        
        Args:
            parent: Parent component
            pos: Position (x, y)
            size: Size (width, height)
            title: Window title
            toolbar_height: Height of the toolbar/title bar
            resizable: Whether the window can be resized
            draggable: Whether the window can be dragged
            closable: Whether the window can be closed
            minimizable: Whether the window can be minimized
            maximizable: Whether the window can be maximized
            border_width: Width of the window border
            corner_radius: Corner radius for the window
            min_size: Minimum size when resizing
            on_close: Callback when window is closed
            on_minimize: Callback when window is minimized
            on_maximize: Callback when window is maximized
            on_restore: Callback when window is restored
            on_move: Callback when window is moved
        """
        self._title = title
        self._size = size
        self._toolbar_height = toolbar_height
        self._resizable = resizable
        self._draggable = draggable
        self._minimized = False
        self._maximized = False
        self._closable = closable
        self._minimizable = minimizable
        self._maximizable = maximizable
        self._border_width = border_width
        self._corner_radius = corner_radius
        self._min_size = min_size
        
        # Dragging state
        self._drag_offset = None
        self._dragging = False
        
        # Store normal position/size for maximize/restore
        self._last_normal_pos = pos
        self._last_normal_size = size
        
        # Callbacks
        self._on_close = on_close
        self._on_minimize = on_minimize
        self._on_maximize = on_maximize
        self._on_restore = on_restore
        self._on_move = on_move
        
        self._rendered = False
        
        super().__init__(parent, pos, self._size)
        
        # Create UI components
        self._create_ui_components()

    def _create_text_icon(self, text: str, size: int, color: Any) -> pygame.Surface:
        """Create a text surface to use as an icon."""
        try:
            font = pygame.font.Font(None, size)
        except:
            font = pygame.font.Font(None, 16)
        
        return font.render(text, True, color)

    def _create_ui_components(self) -> None:
        """Create the internal UI components (toolbar, buttons, content area)."""
        # Main window frame
        self._window_frame = Frame(
            self, (0, 0), self._size, 
            color=theme.get('window_bg'),
            corner_radius=self._corner_radius
        )
        
        # Toolbar background
        self._toolbar = Frame(
            self._window_frame, 
            (self._border_width, self._border_width), 
            (self._size[0] - 2 * self._border_width, self._toolbar_height),
            color=theme.get('frame_color'),
            corner_radius=self._corner_radius
        )
        
        # Title label
        try:
            from .. import text
            font = text.get_font(None, 14)
        except:
            font = pygame.font.Font(None, 16)
            
        self._title_label = Label(
            self._toolbar,
            (8, (self._toolbar_height - 16) // 2),
            self._title,
            font,
            color=theme.get('label_text')
        )
        
        # Calculate button positions
        button_size = self._toolbar_height - 8
        button_y = 4
        button_spacing = 4
        buttons_width = 0
        
        # Close button (rightmost)
        if self._closable:
            close_x = self._toolbar.size[0] - button_size - 4
            close_icon = self._create_text_icon("×", button_size - 4, theme.get('button_text'))
            self._close_button = IconButton(
                self._toolbar,
                (close_x, button_y),
                close_icon,
                (button_size, button_size),
                bg_color=theme.get('button_bg'),
                bg_hover_color=(220, 80, 80),
                on_click=self._handle_close
            )
            buttons_width += button_size + button_spacing
        
        # Maximize button
        if self._maximizable:
            max_x = self._toolbar.size[0] - buttons_width - button_size - 4
            max_icon_text = "🗗" if self._maximized else "⬜"  # Different icons for max/restore
            max_icon = self._create_text_icon(max_icon_text, button_size - 6, theme.get('button_text'))
            self._maximize_button = IconButton(
                self._toolbar,
                (max_x, button_y),
                max_icon,
                (button_size, button_size),
                bg_color=theme.get('button_bg'),
                bg_hover_color=theme.get('button_bg_hover'),
                on_click=self._handle_maximize
            )
            buttons_width += button_size + button_spacing
        
        # Minimize button
        if self._minimizable:
            min_x = self._toolbar.size[0] - buttons_width - button_size - 4
            min_icon = self._create_text_icon("—", button_size - 4, theme.get('button_text'))
            self._minimize_button = IconButton(
                self._toolbar,
                (min_x, button_y),
                min_icon,
                (button_size, button_size),
                bg_color=theme.get('button_bg'),
                bg_hover_color=theme.get('button_bg_hover'),
                on_click=self._handle_minimize
            )
            buttons_width += button_size + button_spacing
        
        # Content area (below toolbar)
        content_y = self._toolbar_height + 2 * self._border_width
        content_height = self._size[1] - content_y - self._border_width
        if not self._minimized and content_height > 0:
            self._content_area = Frame(
                self._window_frame,
                (self._border_width, content_y),
                (self._size[0] - 2 * self._border_width, content_height),
                color=theme.get('surface_bg'),
                corner_radius=max(0, self._corner_radius - 2)
            )

    def _handle_close(self) -> None:
        """Handle close button click."""
        if self._on_close:
            self._on_close(self)
        self.emit('close', self)
        # Optionally remove from parent
        if hasattr(self.parent, 'children') and self in self.parent.children:
            self.parent.children.remove(self)
            if hasattr(self.parent, '_mark_composite_dirty'):
                self.parent._mark_composite_dirty()

    def _handle_minimize(self) -> None:
        """Handle minimize button click."""
        self._minimized = not self._minimized
        if self._on_minimize:
            self._on_minimize(self, self._minimized)
        self.emit('minimize', self, self._minimized)
        self._recreate_ui()

    def _store_normal_state(self) -> None:
        """Store the current position and size as normal state."""
        self._last_normal_pos = self.pos
        self._last_normal_size = self.size

    def _handle_maximize(self) -> None:  # sourcery skip: extract-method
        """Handle maximize/restore button click."""
        if self._maximized:
            # Restore
            self._maximized = False
            self.pos = self._last_normal_pos
            self.size = self._last_normal_size
            if self._on_restore:
                self._on_restore(self)
            self.emit('restore', self)
        else:
            # Maximize
            self._store_normal_state()
            self._maximized = True
            # Maximize to parent's full size
            self.pos = (0, 0)
            self.size = self.parent.size
            if self._on_maximize:
                self._on_maximize(self)
            self.emit('maximize', self)
        
        self._recreate_ui()

    def _recreate_ui(self) -> None:
        """Recreate UI components after size/state changes."""
        # Clear children and recreate
        self.children.clear()
        self._create_ui_components()
        self._rendered = False
        self.render()

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if self._title != value:
            self._title = value
            if hasattr(self, '_title_label'):
                self._title_label.text = value

    @property
    def minimized(self) -> bool:
        return self._minimized

    @property
    def maximized(self) -> bool:
        return self._maximized

    @property
    def dragging(self) -> bool:
        return self._dragging

    @property
    def content_area(self) -> Optional[ComponentBase]:
        """Get the content area where child components should be added."""
        return getattr(self, '_content_area', None)

    def add_content(self, component: ComponentBase) -> None:
        """Add a component to the content area."""
        if self._content_area:
            # Update the component's parent to be the content area
            component.parent = self._content_area
            self._content_area.addChild(component)
        else:
            # Fallback to adding to window frame
            component.parent = self._window_frame
            self._window_frame.addChild(component)

    def _event(self, event: pygame.event.Event) -> bool:
        # Handle window dragging
        if self._draggable and not self._maximized:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if click is in toolbar area
                    toolbar_rect = pygame.Rect(
                        self.absolute_pos[0] + self._border_width,
                        self.absolute_pos[1] + self._border_width,
                        self._size[0] - 2 * self._border_width,
                        self._toolbar_height
                    )
                    if toolbar_rect.collidepoint(mouse_pos):
                        # Check if click is on a window control button (not title label)
                        button_clicked = False
                        for child in self._toolbar.children:
                            # Only check IconButton components, not Labels
                            if hasattr(child, 'absolute_pos') and child.__class__.__name__ == 'IconButton':
                                child_rect = pygame.Rect(
                                    child.absolute_pos[0], child.absolute_pos[1],
                                    child.size[0], child.size[1]
                                )
                                if child_rect.collidepoint(mouse_pos):
                                    button_clicked = True
                                    break
                        
                        if not button_clicked:
                            # Start dragging
                            self._dragging = True
                            self._drag_offset = (
                                mouse_pos[0] - self.absolute_pos[0],
                                mouse_pos[1] - self.absolute_pos[1]
                            )
                            return True
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self._dragging:
                    self._dragging = False
                    self._drag_offset = None
                    return True
            
            elif event.type == pygame.MOUSEMOTION:
                if self._dragging and self._drag_offset:
                    mouse_pos = pygame.mouse.get_pos()
                    new_pos = (
                        mouse_pos[0] - self._drag_offset[0],
                        mouse_pos[1] - self._drag_offset[1]
                    )
                    # Constrain to parent bounds
                    max_x = self.parent.size[0] - self._size[0]
                    max_y = self.parent.size[1] - self._size[1]
                    new_pos = (
                        max(0, min(new_pos[0], max_x)),
                        max(0, min(new_pos[1], max_y))
                    )
                    if new_pos != self.pos:
                        self.pos = new_pos
                        if self._on_move:
                            self._on_move(self, new_pos)
                        self.emit('move', self, new_pos)
                    return True

        # Let children handle the event first
        return super()._event(event)

    def render(self) -> None:
        if not self._rendered:
            # The window frame and its children will handle rendering
            if hasattr(self, '_window_frame'):
                self._window_frame.render()
            self._rendered = True

        # Mark composite as dirty and build blits
        self._mark_composite_dirty()
        self._build_blits()

    def close(self) -> None:
        """Programmatically close the window."""
        self._handle_close()

    def minimize(self) -> None:
        """Programmatically minimize the window."""
        if not self._minimized:
            self._handle_minimize()

    def maximize(self) -> None:
        """Programmatically maximize the window."""
        if not self._maximized:
            self._handle_maximize()

    def restore(self) -> None:
        """Programmatically restore the window."""
        if self._maximized:
            self._handle_maximize()


__all__ = ["ChildWindow"]
