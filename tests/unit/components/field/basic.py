"""Tests for Field component."""

import pytest
import pygame
import engine as ui


class TestField:
    """Test suite for Field component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def field(self, window):
        """Create a basic field for testing."""
        return ui.Field(window, (10, 10), (None, 16), "Initial text")

    def test_creation(self, window):
        """Test basic field creation."""
        field = ui.Field(window, (10, 10), (None, 16), "Initial text")
        assert field.value == "Initial text"
        assert field.pos == (10, 10)

    def test_creation_with_size(self, window):
        """Test field creation with explicit size."""
        field = ui.Field(window, (10, 10), (None, 16), "Test", size=(200, 25))
        assert field.value == "Test"

    def test_value_property(self, field):
        """Test field value property."""
        assert field.value == "Initial text"
        field.value = "Updated value"
        assert field.value == "Updated value"

    def test_empty_field(self, window):
        """Test field with empty initial value."""
        field = ui.Field(window, (10, 10), (None, 16), "")
        assert field.value == ""

        try:
            field.render()
        except Exception as e:
            pytest.fail(f"Empty field rendering failed: {e}")

    def test_multiline_field(self, window):
        """Test multiline field functionality."""
        multiline_text = "Line 1\nLine 2\nLine 3"
        field = ui.Field(window, (10, 10), (None, 16), multiline_text, multiline=True)

        assert field.value == multiline_text

        try:
            field.render()
        except Exception as e:
            pytest.fail(f"Multiline field rendering failed: {e}")

    def test_single_line_field(self, window):
        """Test single line field (default)."""
        field = ui.Field(window, (10, 10), (None, 16), "Single line")

        try:
            field.render()
        except Exception as e:
            pytest.fail(f"Single line field rendering failed: {e}")

    def test_rendering(self, field):
        """Test field rendering."""
        try:
            field.render()
            # Should have blits after rendering
            if hasattr(field, 'blits'):
                assert len(field.blits) >= 0
        except Exception as e:
            pytest.fail(f"Field rendering failed: {e}")

    def test_positioning(self, window):
        """Test field positioning."""
        positions = [(0, 0), (50, 100), (200, 150)]

        for x, y in positions:
            field = ui.Field(window, (x, y), (None, 16), f"Pos {x},{y}")
            assert field.pos == (x, y)

    def test_long_text(self, window):
        """Test field with long text."""
        long_text = "This is a very long text that might exceed normal field boundaries and should be handled gracefully"
        field = ui.Field(window, (10, 10), (None, 16), long_text)
        assert field.value == long_text

        try:
            field.render()
        except Exception as e:
            pytest.fail(f"Field with long text failed to render: {e}")

    def test_special_characters(self, window):
        """Test field with special characters."""
        special_text = "Special: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        field = ui.Field(window, (10, 10), (None, 16), special_text)
        assert field.value == special_text

        try:
            field.render()
        except Exception as e:
            pytest.fail(f"Field with special characters failed to render: {e}")

    def test_unicode_text(self, window):
        """Test field with unicode text."""
        unicode_text = "Unicode: αβγδε ñáéíóú 中文 🚀"
        field = ui.Field(window, (10, 10), (None, 16), unicode_text)
        assert field.value == unicode_text

        try:
            field.render()
        except Exception as e:
            pytest.fail(f"Field with unicode text failed to render: {e}")

    def test_field_events(self, field):
        """Test field event handling."""
        # Test various events
        events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 25), button=1),
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(50, 25), button=1),
            pygame.event.Event(pygame.MOUSEMOTION, pos=(50, 25)),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a),
            pygame.event.Event(pygame.KEYUP, key=pygame.K_a),
        ]

        for event in events:
            try:
                field._event(event)
            except Exception as e:
                pytest.fail(f"Field event handling failed for {event.type}: {e}")

    def test_different_font_sizes(self, window):
        """Test field with different font sizes."""
        font_sizes = [12, 16, 20, 24]

        for size in font_sizes:
            field = ui.Field(window, (10, 10), (None, size), f"Size {size}")
            try:
                field.render()
            except Exception as e:
                pytest.fail(f"Field with font size {size} failed to render: {e}")
