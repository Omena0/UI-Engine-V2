"""Tests for Label component."""

import pytest
import pygame
import engine as ui


class TestLabel:
    """Test suite for Label component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def label(self, window):
        """Create a basic label for testing."""
        return ui.Label(window, (10, 10), "Test Label", (None, 16))

    def test_creation(self, window):
        """Test basic label creation."""
        label = ui.Label(window, (10, 10), "Test Label", (None, 16))
        assert label.text == "Test Label"
        assert label.pos == (10, 10)

    def test_text_property(self, label):
        """Test label text property."""
        assert label.text == "Test Label"
        label.text = "Updated Label"
        assert label.text == "Updated Label"

    def test_theme_properties(self, label):
        """Test theme-resolved properties."""
        # Color property should be available and not None
        assert label.color is not None

    def test_rendering_default_font(self, label):
        """Test label rendering with default font."""
        try:
            label.render()
        except Exception as e:
            pytest.fail(f"Label rendering with default font failed: {e}")

    def test_rendering_different_sizes(self, window):
        """Test label rendering with different font sizes."""
        font_sizes = [12, 16, 20, 24]
        
        for size in font_sizes:
            label = ui.Label(window, (10, 10), f"Size {size}", (None, size))
            try:
                label.render()
            except Exception as e:
                pytest.fail(f"Label rendering with font size {size} failed: {e}")

    def test_empty_text(self, window):
        """Test label with empty text."""
        label = ui.Label(window, (10, 10), "", (None, 16))
        assert label.text == ""
        
        try:
            label.render()
        except Exception as e:
            pytest.fail(f"Label rendering with empty text failed: {e}")

    def test_long_text(self, window):
        """Test label with long text."""
        long_text = "This is a very long text that might exceed normal label boundaries"
        label = ui.Label(window, (10, 10), long_text, (None, 16))
        assert label.text == long_text
        
        try:
            label.render()
        except Exception as e:
            pytest.fail(f"Label rendering with long text failed: {e}")

    def test_special_characters(self, window):
        """Test label with special characters."""
        special_text = "Special: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        label = ui.Label(window, (10, 10), special_text, (None, 16))
        assert label.text == special_text
        
        try:
            label.render()
        except Exception as e:
            pytest.fail(f"Label rendering with special characters failed: {e}")

    def test_positioning(self, window):
        """Test label positioning."""
        positions = [(0, 0), (50, 100), (200, 150)]
        
        for x, y in positions:
            label = ui.Label(window, (x, y), f"Pos {x},{y}", (None, 16))
            assert label.pos == (x, y)

    def test_unicode_text(self, window):
        """Test label with unicode text."""
        unicode_text = "Unicode: αβγδε ñáéíóú 中文 🚀"
        label = ui.Label(window, (10, 10), unicode_text, (None, 16))
        assert label.text == unicode_text
        
        try:
            label.render()
        except Exception as e:
            pytest.fail(f"Label rendering with unicode text failed: {e}")

    def test_newline_text(self, window):
        """Test label with newline characters."""
        newline_text = "Line 1\nLine 2\nLine 3"
        label = ui.Label(window, (10, 10), newline_text, (None, 16))
        assert label.text == newline_text
        
        try:
            label.render()
        except Exception as e:
            pytest.fail(f"Label rendering with newline text failed: {e}")
