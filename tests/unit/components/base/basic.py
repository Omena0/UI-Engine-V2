"""Tests for base component functionality."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


class TestBaseComponent:
    """Test suite for base component functionality."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def frame(self, window):
        """Create a frame component for testing base functionality."""
        return ui.Frame(window, (10, 10), (100, 100))

    def test_hover_detection(self, frame):
        """Test base component hover detection."""
        # Test hover detection with mock mouse position
        hovered, changed = frame._hovered((50, 50))
        assert hovered is True
        
        hovered, changed = frame._hovered((150, 150))
        assert hovered is False

    def test_event_system_registration(self, frame):
        """Test base component event system (on, off, emit)."""
        # Test event listener registration
        callback_called = False
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        frame.on('test_event', test_callback)
        frame.emit('test_event')
        assert callback_called

    def test_event_system_removal(self, frame):
        """Test removing event listeners."""
        callback_called = False
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        frame.on('test_event', test_callback)
        
        # Test removing specific event listener
        callback_called = False
        frame.off('test_event', test_callback)
        frame.emit('test_event')
        assert not callback_called

    def test_event_system_remove_all(self, frame):
        """Test removing all listeners for an event."""
        callback_called = False
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        frame.on('test_event', test_callback)
        
        # Test removing all listeners for an event
        frame.off('test_event')
        frame.emit('test_event')
        assert not callback_called
