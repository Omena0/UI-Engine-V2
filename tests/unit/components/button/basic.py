"""Tests for Button component."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock


class TestButton:
    """Test suite for Button component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def button(self, window):
        """Create a basic button for testing."""
        return ui.Button(window, (10, 10), "Test", (100, 30))

    def test_creation(self, window):
        """Test basic button creation."""
        button = ui.Button(window, (10, 10), "Test", (100, 30))
        assert button.text == "Test"
        assert button.size == (100, 30)
        assert button.pos == (10, 10)

    def test_text_property(self, button):
        """Test button text property getters and setters."""
        assert button.text == "Test"
        button.text = "Updated"
        assert button.text == "Updated"

    def test_theme_properties(self, button):
        """Test theme-resolved properties."""
        # These properties should be available and not None
        assert button.bg_color is not None
        assert button.text_color is not None
        assert button.bg_hover_color is not None
        assert button.text_hover_color is not None

    def test_click_event_handling(self, window):
        """Test button click event handling."""
        clicked = False
        click_data = None
        
        def on_click(text):
            nonlocal clicked, click_data
            clicked = True
            click_data = text
        
        button = ui.Button(window, (10, 10), "Click me", (100, 30), on_click=on_click)
        
        # Simulate mouse click event within button bounds
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 25), button=1)
        result = button._event(click_event)
        
        assert result is True  # Event should be consumed
        assert clicked
        assert click_data == "Click me"

    def test_click_outside_bounds(self, window):
        """Test that clicks outside button bounds don't trigger events."""
        clicked = False
        
        def on_click(text):
            nonlocal clicked
            clicked = True
        
        button = ui.Button(window, (10, 10), "Click me", (100, 30), on_click=on_click)
        
        # Simulate mouse click event outside button bounds
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(200, 200), button=1)
        result = button._event(click_event)
        
        # Event should not be consumed and callback should not be called
        assert not clicked

    def test_hover_state(self, button):
        """Test button hover state changes."""
        # Simulate mouse motion event within button bounds
        motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(50, 25))
        button._event(motion_event)
        
        # Should not raise exceptions
        try:
            button.render()
        except Exception as e:
            pytest.fail(f"Button rendering after hover failed: {e}")

    def test_rendering(self, button):
        """Test button rendering."""
        try:
            button.render()
        except Exception as e:
            pytest.fail(f"Button rendering failed: {e}")

    def test_button_without_callback(self, window):
        """Test button creation without click callback."""
        button = ui.Button(window, (10, 10), "No Callback", (100, 30))
        
        # Should not crash when clicking
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 25), button=1)
        try:
            button._event(click_event)
        except Exception as e:
            pytest.fail(f"Button without callback crashed: {e}")

    def test_button_with_different_sizes(self, window):
        """Test button creation with different sizes."""
        sizes_to_test = [(50, 25), (200, 40), (100, 50)]
        
        for width, height in sizes_to_test:
            button = ui.Button(window, (10, 10), f"Size {width}x{height}", (width, height))
            assert button.size == (width, height)
            
            # Should render without issues
            try:
                button.render()
            except Exception as e:
                pytest.fail(f"Button with size {width}x{height} failed to render: {e}")

    def test_button_positioning(self, window):
        """Test button positioning."""
        positions = [(0, 0), (50, 100), (200, 150)]
        
        for x, y in positions:
            button = ui.Button(window, (x, y), f"Pos {x},{y}", (100, 30))
            assert button.pos == (x, y)
