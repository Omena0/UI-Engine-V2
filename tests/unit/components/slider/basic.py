"""Tests for Slider component."""

import pytest
import pygame
import engine as ui


class TestSlider:
    """Test suite for Slider component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def slider(self, window):
        """Create a basic slider for testing."""
        return ui.Slider(window, (10, 10), (200, 20))

    def test_creation(self, window):
        """Test basic slider creation."""
        slider = ui.Slider(window, (10, 10), (200, 20))
        assert slider.size == (200, 20)
        assert slider.value == 0.0
        assert slider.min_value == 0.0
        assert slider.max_value == 100.0

    def test_value_property(self, slider):
        """Test slider value property."""
        # Test setting value
        slider.value = 50.0
        assert slider.value == 50.0
        
        # Test clamping to max value
        slider.value = 150.0
        assert slider.value == 100.0
        
        # Test clamping to min value
        slider.value = -10.0
        assert slider.value == 0.0

    def test_rendering(self, slider):
        """Test slider rendering."""
        try:
            slider.render()
            if hasattr(slider, 'blits'):
                assert len(slider.blits) > 0
        except Exception as e:
            pytest.fail(f"Slider rendering failed: {e}")

    def test_different_ranges(self, window):
        """Test slider with different value ranges."""
        slider = ui.Slider(window, (10, 10), (200, 20))
        
        # Test custom range
        slider.min_value = 10.0
        slider.max_value = 50.0
        
        slider.value = 30.0
        assert slider.value == 30.0
        
        # Test value clamping with custom range
        slider.value = 5.0  # Below min
        assert slider.value == 10.0
        
        slider.value = 60.0  # Above max
        assert slider.value == 50.0
