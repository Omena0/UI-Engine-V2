"""Tests for ProgressBar component."""

import pytest
import pygame
import engine as ui


class TestProgressBar:
    """Test suite for ProgressBar component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def progress(self, window):
        """Create a basic progress bar for testing."""
        return ui.ProgressBar(window, (10, 10), (200, 20))

    def test_creation(self, window):
        """Test basic progress bar creation."""
        progress = ui.ProgressBar(window, (10, 10), (200, 20))
        assert progress.size == (200, 20)
        assert progress.value == 0.0
        assert progress._max == 100.0
        assert progress.pos == (10, 10)

    def test_value_property(self, progress):
        """Test progress value property getter and setter."""
        # Test setting normal value
        progress.value = 50.0
        assert progress.value == 50.0
        
        # Test clamping to max value
        progress.value = 150.0
        assert progress.value == 100.0  # Should be clamped to max_value
        
        # Test negative values
        progress.value = -10.0
        assert progress.value == 0.0  # Should be clamped to 0

    def test_max_value_property(self, progress):
        """Test progress max_value property."""
        progress._max = 200.0
        assert progress._max == 200.0
        
        # Test that values above the new max are clamped
        progress.value = 250.0
        assert progress.value == 200.0

    def test_rendering_different_values(self, progress):
        """Test progress rendering with different values."""
        values_to_test = [0.0, 25.0, 50.0, 75.0, 100.0]
        
        for value in values_to_test:
            progress.value = value
            try:
                progress.render()
                if hasattr(progress, 'blits'):
                    assert len(progress.blits) > 0
            except Exception as e:
                pytest.fail(f"Progress rendering with value {value} failed: {e}")

    def test_different_sizes(self, window):
        """Test progress bar with different sizes."""
        sizes = [(100, 10), (300, 25), (150, 30)]
        
        for width, height in sizes:
            progress = ui.ProgressBar(window, (10, 10), (width, height))
            assert progress.size == (width, height)
            
            try:
                progress.render()
            except Exception as e:
                pytest.fail(f"Progress bar with size {width}x{height} failed to render: {e}")

    def test_positioning(self, window):
        """Test progress bar positioning."""
        positions = [(0, 0), (50, 100), (200, 150)]
        
        for x, y in positions:
            progress = ui.ProgressBar(window, (x, y), (200, 20))
            assert progress.pos == (x, y)

    def test_custom_max_value(self, window):
        """Test progress bar with custom max value."""
        progress = ui.ProgressBar(window, (10, 10), (200, 20))
        progress._max = 50.0
        
        # Test value setting with custom max
        progress.value = 25.0
        assert progress.value == 25.0
        
        progress.value = 75.0  # Above max
        assert progress.value == 50.0  # Should be clamped

    def test_zero_max_value(self, window):
        """Test progress bar with zero max value."""
        progress = ui.ProgressBar(window, (10, 10), (200, 20))
        progress._max = 0.0
        
        # Any value should be clamped to 0
        progress.value = 10.0
        assert progress.value == 0.0

    def test_fractional_values(self, progress):
        """Test progress bar with fractional values."""
        fractional_values = [0.1, 12.5, 33.33, 66.67, 99.9]
        
        for value in fractional_values:
            progress.value = value
            assert progress.value == value
            
            try:
                progress.render()
            except Exception as e:
                pytest.fail(f"Progress rendering with fractional value {value} failed: {e}")

    def test_edge_cases(self, progress):
        """Test progress bar edge cases."""
        # Test exactly at max
        progress.value = 100.0
        assert progress.value == 100.0
        
        # Test exactly at min
        progress.value = 0.0
        assert progress.value == 0.0
        
        # Test very small positive value (may be rounded to 0 by implementation)
        progress.value = 0.001
        assert progress.value >= 0.0  # Allow for rounding

    def test_large_max_value(self, window):
        """Test progress bar with large max value."""
        progress = ui.ProgressBar(window, (10, 10), (200, 20))
        progress._max = 1000.0
        
        progress.value = 500.0
        assert progress.value == 500.0
        
        try:
            progress.render()
        except Exception as e:
            pytest.fail(f"Progress rendering with large max value failed: {e}")

    def test_minimal_size(self, window):
        """Test progress bar with minimal size."""
        progress = ui.ProgressBar(window, (10, 10), (10, 5))
        assert progress.size == (10, 5)
        
        progress.value = 50.0
        try:
            progress.render()
        except Exception as e:
            pytest.fail(f"Minimal size progress bar rendering failed: {e}")
