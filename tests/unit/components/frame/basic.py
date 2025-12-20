"""Tests for Frame component."""

import pytest
import pygame
import engine as ui


class TestFrame:
    """Test suite for Frame component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def frame(self, window):
        """Create a basic frame for testing."""
        return ui.Frame(window, (0, 0), (200, 150))

    def test_creation(self, window):
        """Test basic frame creation."""
        frame = ui.Frame(window, (0, 0), (200, 150))
        assert frame.size == (200, 150)
        assert frame.pos == (0, 0)

    def test_sizing(self, window):
        """Test frame with different sizes."""
        sizes = [(100, 100), (300, 200), (50, 75)]
        
        for width, height in sizes:
            frame = ui.Frame(window, (10, 10), (width, height))
            assert frame.size == (width, height)

    def test_positioning(self, window):
        """Test frame positioning."""
        positions = [(0, 0), (50, 100), (200, 150)]
        
        for x, y in positions:
            frame = ui.Frame(window, (x, y), (100, 100))
            assert frame.pos == (x, y)

    def test_background_color(self, window):
        """Test frame background color property."""
        frame = ui.Frame(window, (10, 10), (100, 100))
        
        # Should have a background color property (check attribute exists)
        # Note: Different implementations may use 'color', 'bg_color', or '_color'
        has_color_attr = (hasattr(frame, 'bg_color') or 
                         hasattr(frame, 'color') or 
                         hasattr(frame, '_color'))
        assert has_color_attr

    def test_rendering(self, frame):
        """Test frame rendering."""
        try:
            frame.render()
        except Exception as e:
            pytest.fail(f"Frame rendering failed: {e}")

    def test_child_components(self, window):
        """Test adding child components to frame."""
        frame = ui.Frame(window, (10, 10), (200, 150))
        
        # Add child components
        label = ui.Label(frame, (10, 10), "Child Label", (None, 16))
        button = ui.Button(frame, (10, 40), "Child Button", (100, 30))
        
        # Should render without issues
        try:
            frame.render()
            label.render()
            button.render()
        except Exception as e:
            pytest.fail(f"Frame with child components failed to render: {e}")

    def test_nested_frames(self, window):
        """Test nested frame structures."""
        parent_frame = ui.Frame(window, (10, 10), (300, 200))
        child_frame = ui.Frame(parent_frame, (20, 20), (100, 100))
        
        assert parent_frame.size == (300, 200)
        assert child_frame.size == (100, 100)
        
        try:
            parent_frame.render()
            child_frame.render()
        except Exception as e:
            pytest.fail(f"Nested frames failed to render: {e}")

    def test_zero_size_frame(self, window):
        """Test frame with zero or minimal size."""
        # Zero size
        frame_zero = ui.Frame(window, (0, 0), (0, 0))
        assert frame_zero.size == (0, 0)
        
        # Minimal size
        frame_minimal = ui.Frame(window, (0, 0), (1, 1))
        assert frame_minimal.size == (1, 1)
        
        try:
            frame_zero.render()
            frame_minimal.render()
        except Exception as e:
            pytest.fail(f"Zero/minimal size frame rendering failed: {e}")

    def test_large_frame(self, window):
        """Test frame with large dimensions."""
        # Note: Some implementations may limit frame size to parent window size
        large_frame = ui.Frame(window, (0, 0), (1000, 800))
        # Just ensure it was created successfully, size may be clamped
        assert large_frame.size is not None
        
        try:
            large_frame.render()
        except Exception as e:
            pytest.fail(f"Large frame rendering failed: {e}")

    def test_frame_events(self, frame):
        """Test frame event handling."""
        # Test various events
        events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 75), button=1),
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(100, 75), button=1),
            pygame.event.Event(pygame.MOUSEMOTION, pos=(100, 75)),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
        ]
        
        for event in events:
            try:
                frame._event(event)
            except Exception as e:
                pytest.fail(f"Frame event handling failed for {event.type}: {e}")
