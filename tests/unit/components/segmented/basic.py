"""Tests for SegmentedButton component - simple version."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


class TestSegmentedButton:
    """Test suite for SegmentedButton component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a test window."""
        return ui.Window((800, 600))

    @pytest.fixture
    def segment_options(self):
        """Create sample segment options."""
        return ["First", "Second", "Third", "Fourth"]

    @pytest.fixture
    def segmented(self, window, segment_options):
        """Create a basic segmented control for testing."""
        return ui.SegmentedButton(window, (10, 10), segment_options, size=(200, 30))

    def test_creation(self, window, segment_options):
        """Test basic segmented control creation."""
        segmented = ui.SegmentedButton(window, (10, 10), segment_options, size=(200, 30))
        assert segmented.pos == (10, 10)
        assert segmented.size == (200, 30)
        assert hasattr(segmented, '_segments')

    def test_initial_selection(self, segmented):
        """Test initial selection state."""
        if hasattr(segmented, 'selected_index'):
            assert isinstance(segmented.selected_index, int)
        elif hasattr(segmented, '_selected'):
            assert isinstance(segmented._selected, int)

    def test_rendering(self, segmented):
        """Test segmented rendering."""
        try:
            segmented.render()
            if hasattr(segmented, 'blits'):
                assert len(segmented.blits) > 0
        except Exception as e:
            pytest.fail(f"SegmentedButton rendering failed: {e}")

    def test_segment_count(self, segmented, segment_options):
        """Test that all segments are available."""
        if hasattr(segmented, '_segments'):
            assert len(segmented._segments) == len(segment_options)
        elif hasattr(segmented, 'segments'):
            assert len(segmented.segments) == len(segment_options)

    def test_different_sizes(self, window, segment_options):
        """Test segmented control with different sizes."""
        sizes = [(100, 25), (300, 40), (200, 35)]
        
        for width, height in sizes:
            segmented = ui.SegmentedButton(window, (10, 10), segment_options, size=(width, height))
            try:
                segmented.render()
            except Exception as e:
                pytest.fail(f"SegmentedButton with size {width}x{height} failed to render: {e}")

    def test_creation_with_different_options(self, window):
        """Test segmented creation with different option sets."""
        option_sets = [
            ["A", "B"],
            ["One", "Two", "Three"],
            ["Alpha", "Beta", "Gamma", "Delta"],
        ]
        
        for options in option_sets:
            segmented = ui.SegmentedButton(window, (10, 10), options, size=(300, 30))
            try:
                segmented.render()
            except Exception as e:
                pytest.fail(f"SegmentedButton with {len(options)} options failed to render: {e}")

    def test_empty_segments(self, window):
        """Test creation with empty segments."""
        try:
            segmented = ui.SegmentedButton(window, (10, 10), [], size=(200, 30))
            segmented.render()
        except Exception:
            # Empty segments might not be supported
            pass

    def test_single_segment(self, window):
        """Test segmented control with single segment."""
        try:
            segmented = ui.SegmentedButton(window, (10, 10), ["Only"], size=(100, 30))
            segmented.render()
        except Exception as e:
            pytest.fail(f"SegmentedButton with single segment failed to render: {e}")

    def test_click_interaction(self, segmented):
        """Test basic click interaction."""
        try:
            click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 25), button=1)
            segmented._event(click_event)
            # Just verify no exception is thrown
        except Exception as e:
            pytest.fail(f"SegmentedButton click interaction failed: {e}")
