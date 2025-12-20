"""Tests for Toggle component."""

import pytest
import pygame
import engine as ui


class TestToggle:
    """Test suite for Toggle component."""

    @pytest.fixture(scope='class')
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def toggle(self, window):
        """Create a basic toggle for testing."""
        return ui.Toggle(window, (10, 10), (60, 30))

    def test_creation(self, window):
        """Test basic toggle creation."""
        toggle = ui.Toggle(window, (10, 10), (60, 30))
        assert toggle.size == (60, 30)
        assert not toggle.value
        assert toggle.pos == (10, 10)

    def test_value_property(self, toggle):
        """Test toggle value property getter and setter."""
        # Test initial value
        assert not toggle.value
        
        # Test setting value
        toggle.value = True
        assert toggle.value
        
        toggle.value = False
        assert not toggle.value

    def test_toggle_method(self, toggle):
        """Test toggle method functionality."""
        initial_value = toggle.value
        toggle._toggle()
        assert toggle.value == (not initial_value)
        
        # Toggle again
        toggle._toggle()
        assert toggle.value == initial_value

    def test_rendering(self, toggle):
        """Test toggle rendering in different states."""
        # Test off state rendering
        toggle.value = False
        try:
            toggle.render()
            if hasattr(toggle, 'blits'):
                assert len(toggle.blits) > 0
        except Exception as e:
            pytest.fail(f"Toggle off state rendering failed: {e}")
        
        # Test on state rendering
        toggle.value = True
        try:
            toggle.render()
            if hasattr(toggle, 'blits'):
                assert len(toggle.blits) > 0
        except Exception as e:
            pytest.fail(f"Toggle on state rendering failed: {e}")

    def test_click_interaction(self, toggle):
        """Test toggle click interaction."""
        initial_value = toggle.value
        
        # Simulate click event
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(30, 15), button=1)
        toggle._event(click_event)
        
        # Value should toggle
        assert toggle.value == (not initial_value)

    def test_click_outside_bounds(self, toggle):
        """Test that clicks outside toggle bounds don't affect state."""
        initial_value = toggle.value
        
        # Click outside toggle bounds
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(200, 200), button=1)
        toggle._event(click_event)
        
        # Value should not change
        assert toggle.value == initial_value

    def test_different_sizes(self, window):
        """Test toggle with different sizes."""
        sizes = [(40, 20), (80, 40), (100, 50)]
        
        for width, height in sizes:
            toggle = ui.Toggle(window, (10, 10), (width, height))
            assert toggle.size == (width, height)
            
            try:
                toggle.render()
            except Exception as e:
                pytest.fail(f"Toggle with size {width}x{height} failed to render: {e}")

    def test_positioning(self, window):
        """Test toggle positioning."""
        positions = [(0, 0), (50, 100), (200, 150)]
        
        for x, y in positions:
            toggle = ui.Toggle(window, (x, y), (60, 30))
            assert toggle.pos == (x, y)

    def test_state_transitions(self, toggle):
        """Test multiple state transitions."""
        # Test multiple toggles
        for _ in range(5):
            initial_value = toggle.value
            toggle._toggle()
            assert toggle.value == (not initial_value)

    def test_event_handling(self, toggle):
        """Test various event handling."""
        events = [
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(30, 15), button=1),
            pygame.event.Event(pygame.MOUSEMOTION, pos=(30, 15)),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
        ]
        
        for event in events:
            try:
                toggle._event(event)
            except Exception as e:
                pytest.fail(f"Toggle event handling failed for {event.type}: {e}")

    def test_minimal_size_toggle(self, window):
        """Test toggle with minimal size."""
        toggle = ui.Toggle(window, (10, 10), (20, 10))
        assert toggle.size == (20, 10)
        
        try:
            toggle.render()
        except Exception as e:
            pytest.fail(f"Minimal size toggle rendering failed: {e}")

    def test_large_size_toggle(self, window):
        """Test toggle with large size."""
        toggle = ui.Toggle(window, (10, 10), (200, 100))
        assert toggle.size == (200, 100)
        
        try:
            toggle.render()
        except Exception as e:
            pytest.fail(f"Large size toggle rendering failed: {e}")
