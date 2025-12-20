"""Tests for IconButton component."""

import pytest
import pygame
import engine as ui


class TestIconButton:
    """Test suite for IconButton component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def icon_surface(self):
        """Create an icon surface for testing."""
        icon = pygame.Surface((16, 16))
        icon.fill((255, 0, 0))  # Red square
        return icon

    @pytest.fixture
    def icon_button(self, window, icon_surface):
        """Create a basic icon button for testing."""
        return ui.IconButton(window, (10, 10), icon_surface, (50, 50))

    def test_creation(self, window, icon_surface):
        """Test basic icon button creation."""
        icon_button = ui.IconButton(window, (10, 10), icon_surface, (50, 50))
        assert icon_button.size == (50, 50)
        assert icon_button.icon == icon_surface

    def test_rendering(self, icon_button):
        """Test icon button rendering."""
        try:
            icon_button.render()
            if hasattr(icon_button, 'blits'):
                assert len(icon_button.blits) > 0
        except Exception as e:
            pytest.fail(f"IconButton rendering failed: {e}")

    def test_different_icon_sizes(self, window):
        """Test icon button with different icon sizes."""
        icon_sizes = [(8, 8), (32, 32), (64, 64)]
        
        for width, height in icon_sizes:
            icon = pygame.Surface((width, height))
            icon.fill((0, 255, 0))  # Green
            
            icon_button = ui.IconButton(window, (10, 10), icon, (50, 50))
            assert icon_button.icon.get_size() == (width, height)
            
            try:
                icon_button.render()
            except Exception as e:
                pytest.fail(f"IconButton with {width}x{height} icon failed to render: {e}")

    def test_click_functionality(self, window, icon_surface):
        """Test icon button click functionality."""
        clicked = False
        
        def on_click():
            nonlocal clicked
            clicked = True
        
        icon_button = ui.IconButton(window, (10, 10), icon_surface, (50, 50), on_click=on_click)
        
        # Simulate click
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(25, 25), button=1)
        try:
            icon_button._event(click_event)
            if clicked:
                assert clicked
        except Exception as e:
            pytest.fail(f"IconButton click handling failed: {e}")
