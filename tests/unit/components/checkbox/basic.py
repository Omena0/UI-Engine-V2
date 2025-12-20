"""Tests for CheckBox component."""

import pytest
import pygame
import engine as ui


class TestCheckBox:
    """Test suite for CheckBox component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def checkbox(self, window):
        """Create a basic checkbox for testing."""
        return ui.CheckBox(window, (10, 10), (50, 50), "Test checkbox")

    def test_creation(self, window):
        """Test basic checkbox creation."""
        checkbox = ui.CheckBox(window, (10, 10), (50, 50), "Test checkbox")
        assert checkbox._text == "Test checkbox"
        assert not checkbox._checked
        assert checkbox.size == (50, 50)
        assert checkbox.pos == (10, 10)

    def test_checked_property(self, checkbox):
        """Test checkbox checked property getter and setter."""
        # Test initial value
        assert not checkbox.checked
        
        # Test setting value
        checkbox.checked = True
        assert checkbox.checked
        
        checkbox.checked = False
        assert not checkbox.checked

    def test_toggle_functionality(self, checkbox):
        """Test checkbox toggle functionality."""
        initial_value = checkbox.checked
        
        # Simulate click event to toggle
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(25, 25), button=1)
        checkbox._event(click_event)
        
        # Value should change after click
        assert checkbox.checked == (not initial_value)

    def test_toggle_multiple_times(self, checkbox):
        """Test checkbox multiple toggles."""
        initial_value = checkbox.checked
        
        # Click multiple times
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(25, 25), button=1)
        checkbox._event(click_event)
        checkbox._event(click_event)
        
        # Should be back to initial value
        assert checkbox.checked == initial_value

    def test_rendering(self, checkbox):
        """Test checkbox rendering."""
        # Test unchecked rendering
        try:
            checkbox.render()
            if hasattr(checkbox, 'blits'):
                assert len(checkbox.blits) > 0
        except Exception as e:
            pytest.fail(f"Unchecked checkbox rendering failed: {e}")
        
        # Test checked rendering
        checkbox.checked = True
        try:
            checkbox.render()
            if hasattr(checkbox, 'blits'):
                assert len(checkbox.blits) > 0
        except Exception as e:
            pytest.fail(f"Checked checkbox rendering failed: {e}")

    def test_click_outside_bounds(self, checkbox):
        """Test that clicks outside checkbox bounds don't toggle."""
        initial_value = checkbox.checked
        
        # Click outside checkbox bounds
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(200, 200), button=1)
        checkbox._event(click_event)
        
        # Value should not change
        assert checkbox.checked == initial_value

    def test_different_sizes(self, window):
        """Test checkbox with different sizes."""
        sizes = [(20, 20), (30, 30), (40, 40)]
        
        for width, height in sizes:
            checkbox = ui.CheckBox(window, (10, 10), (width, height), f"Size {width}x{height}")
            assert checkbox.size == (width, height)
            
            try:
                checkbox.render()
            except Exception as e:
                pytest.fail(f"Checkbox with size {width}x{height} failed to render: {e}")

    def test_different_text_labels(self, window):
        """Test checkbox with different text labels."""
        labels = ["", "Short", "Very long checkbox label text", "Unicode: αβγ 中文"]
        
        for label in labels:
            checkbox = ui.CheckBox(window, (10, 10), (50, 50), label)
            assert checkbox._text == label
            
            try:
                checkbox.render()
            except Exception as e:
                pytest.fail(f"Checkbox with label '{label}' failed to render: {e}")

    def test_positioning(self, window):
        """Test checkbox positioning."""
        positions = [(0, 0), (50, 100), (200, 150)]
        
        for x, y in positions:
            checkbox = ui.CheckBox(window, (x, y), (50, 50), f"Pos {x},{y}")
            assert checkbox.pos == (x, y)

    def test_event_handling(self, checkbox):
        """Test various event handling."""
        events = [
            pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(25, 25), button=1),
            pygame.event.Event(pygame.MOUSEMOTION, pos=(25, 25)),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
        ]
        
        for event in events:
            try:
                checkbox._event(event)
            except Exception as e:
                pytest.fail(f"Checkbox event handling failed for {event.type}: {e}")
