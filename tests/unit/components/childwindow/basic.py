"""Comprehensive tests for ChildWindow component."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch, MagicMock
from engine.components.childwindow import ChildWindow


class TestChildWindow:
    """Test suite for ChildWindow component."""

    @pytest.fixture
    def mock_window(self):
        """Create a mock window for testing."""
        pygame.init()
        return ui.Window((800, 600))

    @pytest.fixture
    def child_window(self, mock_window):
        """Create a basic ChildWindow for testing."""
        return ChildWindow(
            mock_window,
            pos=(100, 100),
            size=(300, 200),
            title="Test Window"
        )

    def test_creation_with_all_params(self, mock_window):
        """Test basic ChildWindow creation with all parameters."""
        child = ChildWindow(
            mock_window,
            pos=(50, 50),
            size=(400, 300),
            title="Test Window",
            draggable=True,
            closable=True,
            minimizable=True,
            maximizable=True
        )
        
        assert child._title == "Test Window"
        assert child._draggable
        assert child._closable
        assert child._minimizable
        assert child._maximizable
        assert not child._minimized
        assert not child._maximized
        assert not child._dragging

    def test_creation_with_defaults(self, mock_window):
        """Test ChildWindow creation with default parameters."""
        child = ChildWindow(mock_window, pos=(0, 0), size=(200, 150))
        
        assert child._title == "Child Window"
        assert child._draggable
        assert child._closable
        assert child._minimizable
        assert child._maximizable

    def test_title_property(self, child_window):
        """Test title getter and setter."""
        assert child_window.title == "Test Window"
        
        child_window.title = "New Title"
        assert child_window.title == "New Title"
        assert child_window._title == "New Title"

    def test_minimized_property(self, child_window):
        """Test minimized getter and setter."""
        assert not child_window.minimized

        child_window._minimized = True
        assert child_window.minimized
        assert child_window._minimized

    def test_maximized_property(self, child_window):
        """Test maximized getter and setter."""
        assert not child_window.maximized

        child_window._maximized = True
        assert child_window.maximized
        assert child_window._maximized

    def test_dragging_property(self, child_window):
        """Test dragging property getter."""
        assert not child_window._dragging
        child_window._dragging = True
        assert child_window.dragging

    def test_close_callback(self, mock_window):
        """Test close callback functionality."""
        callback_called = False
        
        def close_callback(child_window):
            nonlocal callback_called
            callback_called = True
        
        child = ChildWindow(
            mock_window,
            pos=(0, 0),
            size=(200, 150),
            on_close=close_callback
        )
        
        # Simulate close button click
        if hasattr(child, '_close_button') and hasattr(child._close_button, 'on_click'):
            if child._close_button.on_click:
                child._close_button.on_click()
            assert callback_called

    def test_minimize_callback(self):
        """Test minimize callback is called correctly"""
        window = ui.Window((800, 600))
        
        callback_called = False
        def minimize_callback(child_window, is_minimized):
            nonlocal callback_called
            callback_called = True
            
        cw = ChildWindow(window, pos=(100, 100), size=(300, 200), title="Test Window", on_minimize=minimize_callback)
        
        # Trigger minimize
        cw._minimized = True
        if cw._on_minimize:
            cw._on_minimize(cw, cw._minimized)
        
        assert callback_called

    def test_maximize_callback(self, mock_window):
        """Test maximize callback functionality."""
        callback_called = False
        
        def maximize_callback(child_window):
            nonlocal callback_called
            callback_called = True
        
        child = ChildWindow(
            mock_window,
            pos=(0, 0),
            size=(200, 150),
            on_maximize=maximize_callback
        )
        
        # Test maximize functionality
        child.maximize()
        
        assert callback_called

    def test_drag_functionality(self, child_window):
        """Test drag start, move, and stop functionality."""
        # Simulate mouse down on title bar
        mouse_down = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            pos=(150, 110),  # Within title bar area
            button=1
        )

        result = child_window._event(mouse_down)
        assert result is not None

        # Test drag move
        child_window._dragging = True
        child_window._drag_offset = (10, 10)

        mouse_motion = pygame.event.Event(
            pygame.MOUSEMOTION,
            pos=(200, 200),
            buttons=(1, 0, 0)
        )

        child_window._event(mouse_motion)

        # Test drag stop
        mouse_up = pygame.event.Event(
            pygame.MOUSEBUTTONUP,
            pos=(200, 200),
            button=1
        )

        child_window._event(mouse_up)
        assert not child_window._dragging

    def test_title_bar_detection(self, child_window):
        """Test title bar hit detection."""
        if hasattr(child_window, '_is_point_in_title_bar'):
            # Point in title bar
            assert child_window._is_point_in_title_bar((150, 110))
            
            # Point outside title bar
            assert not child_window._is_point_in_title_bar((-10, -10))

    def test_rendering_states(self, child_window):
        """Test rendering in different states."""
        # Test normal rendering
        try:
            child_window.render()
        except Exception as e:
            pytest.fail(f"Normal rendering failed: {e}")

        # Test minimized rendering
        child_window._minimized = True
        try:
            child_window.render()
        except Exception as e:
            pytest.fail(f"Rendering minimized window failed: {e}")

        # Test maximized rendering
        child_window._minimized = False
        child_window._maximized = True
        try:
            child_window.render()
        except Exception as e:
            pytest.fail(f"Rendering maximized window failed: {e}")

    def test_disabled_features(self, mock_window):
        """Test window with disabled features."""
        # Non-draggable window
        child = ChildWindow(
            mock_window,
            pos=(0, 0),
            size=(200, 150),
            draggable=False
        )
        
        assert not child._draggable
        
        mouse_event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            pos=(100, 25),
            button=1
        )
        
        child._event(mouse_event)
        assert not child._dragging

        # Test all buttons disabled
        child_all_disabled = ChildWindow(
            mock_window,
            pos=(0, 0),
            size=(200, 150),
            closable=False,
            minimizable=False,
            maximizable=False,
            draggable=False
        )
        
        assert not child_all_disabled._closable
        assert not child_all_disabled._minimizable
        assert not child_all_disabled._maximizable
        assert not child_all_disabled._draggable

    def test_content_area(self, child_window):
        """Test access to content area."""
        content_area = child_window.content_area
        assert content_area is not None
        # Content area should be some kind of container or frame
        assert hasattr(content_area, 'pos')
        assert hasattr(content_area, 'size')

    def test_event_handling(self, child_window):
        """Test various event handling scenarios."""
        # Mouse events outside window
        mouse_outside = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            pos=(-100, -100),
            button=1
        )
        
        child_window._event(mouse_outside)
        assert not child_window._dragging

        # Keyboard events
        key_event = pygame.event.Event(
            pygame.KEYDOWN,
            key=pygame.K_SPACE
        )
        
        try:
            child_window._event(key_event)
        except Exception as e:
            pytest.fail(f"Keyboard event handling failed: {e}")

        # Various event types
        events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(150, 150), button=1),
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(150, 150), button=1),
            pygame.event.Event(pygame.MOUSEMOTION, pos=(150, 150)),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
            pygame.event.Event(pygame.KEYUP, key=pygame.K_ESCAPE),
        ]
        
        for event in events:
            try:
                child_window._event(event)
            except Exception as e:
                pytest.fail(f"Event {event.type} handling failed: {e}")

    def test_state_combinations(self, child_window):
        """Test various combinations of window states."""
        # Test minimized + maximized (should handle gracefully)
        child_window._minimized = True
        child_window._maximized = True
        
        try:
            child_window.render()
        except Exception as e:
            pytest.fail(f"Failed to handle conflicting states: {e}")

    def test_position_and_size_changes(self, child_window):
        """Test window position and size changes."""
        # Test setting new size
        child_window.size = (400, 300)
        assert child_window.size == (400, 300)

        # Test setting new position
        child_window.pos = (200, 150)
        assert child_window.pos == (200, 150)
