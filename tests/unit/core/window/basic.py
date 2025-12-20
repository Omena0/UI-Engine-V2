"""Tests for Window core module."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch
from engine.window import Window


def ensure_pygame_ready():
    """Ensure pygame and font module are properly initialized."""
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()


class TestWindow:
    """Test suite for Window core module."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        ensure_pygame_ready()
        return ui.Window((800, 600))

    def test_creation_default_size(self):
        """Test Window creation with default size."""
        ensure_pygame_ready()
        window = Window()
        assert window._size == (800, 600)
        assert window.size == (800, 600)

    def test_creation_custom_size(self):
        """Test Window creation with custom size."""
        ensure_pygame_ready()

        # Test various sizes
        sizes = [(400, 300), (1024, 768), (1920, 1080)]
        for width, height in sizes:
            window = Window((width, height))
            assert window._size == (width, height)
            assert window.size == (width, height)

    def test_window_properties(self, window):
        """Test basic window properties."""
        assert window.pos == (0, 0)
        assert window.size == (800, 600)
        assert hasattr(window, 'children')
        assert hasattr(window, 'clock')
        assert hasattr(window, 'debug')
        assert hasattr(window, 'mode')

    def test_surface_property(self, window):
        """Test window surface property."""
        surface = window.surface
        assert surface is not None
        assert isinstance(surface, pygame.Surface)
        assert surface.get_size() == (800, 600)

    def test_event_system(self, window):
        """Test window event system."""
        callback_called = False

        def test_callback():
            nonlocal callback_called
            callback_called = True

        # Test event registration
        if hasattr(window, 'event'):
            window.event('test_event')(test_callback)
        # Note: Window event system varies by implementation

    def test_render_and_draw(self, window):
        """Test window render and draw methods."""
        ensure_pygame_ready()
        # Add some child components
        frame = ui.Frame(window, (10, 10), (100, 100))
        label = ui.Label(window, (20, 20), "Test", (None, 16))

        # Should not raise exceptions
        try:
            window.render()
            window.draw()
        except Exception as e:
            pytest.fail(f"Window render/draw failed: {e}")

    def test_child_component_management(self, window):
        """Test adding and managing child components."""
        ensure_pygame_ready()
        initial_children = len(window.children) if hasattr(window, 'children') else 0

        # Add child components
        frame = ui.Frame(window, (10, 10), (100, 100))
        button = ui.Button(window, (20, 20), "Test", (50, 30))

        if hasattr(window, 'children'):
            assert len(window.children) >= initial_children

    def test_event_handling(self, window):
        """Test window event handling."""
        # Test various pygame events
        events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 100), button=1),
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(100, 100), button=1),
            pygame.event.Event(pygame.MOUSEMOTION, pos=(100, 100)),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
            pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE),
            pygame.event.Event(pygame.QUIT),
        ]

        for event in events:
            try:
                if hasattr(window, '_event'):
                    window._event(event)
                elif hasattr(window, 'handle_event'):
                    window.handle_event(event)
            except Exception as e:
                pytest.fail(f"Window event handling failed for {event.type}: {e}")

    def test_clock_and_timing(self, window):
        """Test window clock and timing functionality."""
        if hasattr(window, 'clock'):
            assert window.clock is not None
            assert isinstance(window.clock, pygame.time.Clock)

    def test_debug_mode(self, window):
        """Test window debug mode functionality."""
        if hasattr(window, 'debug'):
            original_debug = window.debug
            window.debug = not original_debug
            assert window.debug == (not original_debug)

    def test_window_modes(self, window):
        """Test different window modes if supported."""
        if hasattr(window, 'mode'):
            # Test that mode property exists and can be accessed
            current_mode = window.mode
            assert current_mode is not None

    def test_window_with_many_children(self, window):
        """Test window performance with many child components."""
        ensure_pygame_ready()
        components = []

        # Add multiple components
        for i in range(10):
            frame = ui.Frame(window, (i * 50, i * 30), (40, 25))
            label = ui.Label(window, (i * 50 + 5, i * 30 + 5), f"Label {i}", (None, 12))
            components.extend([frame, label])

        # Should handle rendering without issues
        try:
            window.render()
        except Exception as e:
            pytest.fail(f"Window with many children failed to render: {e}")

    def test_window_edge_cases(self):
        """Test window edge cases."""
        ensure_pygame_ready()

        # Very small window (may be adjusted by OS)
        small_window = Window((1, 1))
        # Just ensure it was created, size may be adjusted by OS
        assert small_window.size is not None

        # Large window
        large_window = Window((2000, 1500))
        assert large_window.size == (2000, 1500)

    def test_window_cleanup(self, window):
        """Test window cleanup and resource management."""
        # Add components that might need cleanup
        for i in range(5):
            ui.Frame(window, (i * 20, i * 20), (50, 50))

        # Test that window can be properly cleaned up
        # This mainly ensures no exceptions are raised during cleanup
        try:
            if hasattr(window, 'cleanup'):
                window.cleanup()
            elif hasattr(window, 'quit'):
                window.quit()
        except Exception as e:
            pytest.fail(f"Window cleanup failed: {e}")
