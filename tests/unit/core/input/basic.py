"""Tests for Input core module."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


class TestInputManager:
    """Test suite for InputManager."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        pygame.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def field(self, window):
        """Create a field for testing."""
        return ui.Field(window, (10, 10), (None, 16), "Test")

    @pytest.fixture
    def input_manager(self, field):
        """Create an input manager for testing."""
        return ui.InputManager(field)

    def test_creation(self, field):
        """Test InputManager creation."""
        input_manager = ui.InputManager(field)
        assert input_manager is not None

    def test_creation_multiline(self, window):
        """Test InputManager with multiline field."""
        field = ui.Field(window, (10, 10), (None, 16), "Test", multiline=True)
        input_manager = ui.InputManager(field, multiline=True)
        assert input_manager is not None

    def test_text_input_handling(self, input_manager):
        """Test basic text input event handling."""
        # Test single character input
        text_event = pygame.event.Event(pygame.TEXTINPUT, text='a')
        result = input_manager.handle_event(text_event)
        assert result in [True, False]  # Should return a boolean

        # Test multiple characters
        chars_to_test = ['b', 'C', '1', '!', ' ']
        for char in chars_to_test:
            text_event = pygame.event.Event(pygame.TEXTINPUT, text=char)
            try:
                input_manager.handle_event(text_event)
            except Exception as e:
                pytest.fail(f"Text input handling failed for '{char}': {e}")

    def test_keyboard_events(self, input_manager):
        """Test keyboard event handling."""
        # Test common key events
        key_events = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DELETE),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_HOME),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_END),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB),
        ]
        
        for event in key_events:
            try:
                result = input_manager.handle_event(event)
                assert result in [True, False, None]
            except Exception as e:
                pytest.fail(f"Keyboard event handling failed for key {event.key}: {e}")

    def test_modifier_keys(self, input_manager):
        """Test modifier key combinations."""
        # Test Ctrl+key combinations
        ctrl_events = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=pygame.KMOD_CTRL),  # Select All
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c, mod=pygame.KMOD_CTRL),  # Copy
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_v, mod=pygame.KMOD_CTRL),  # Paste
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x, mod=pygame.KMOD_CTRL),  # Cut
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z, mod=pygame.KMOD_CTRL),  # Undo
        ]
        
        for event in ctrl_events:
            try:
                input_manager.handle_event(event)
            except Exception as e:
                pytest.fail(f"Ctrl+key event handling failed for key {event.key}: {e}")

    def test_arrow_key_navigation(self, input_manager):
        """Test arrow key navigation."""
        arrow_events = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN),
        ]
        
        for event in arrow_events:
            try:
                input_manager.handle_event(event)
            except Exception as e:
                pytest.fail(f"Arrow key navigation failed for key {event.key}: {e}")

    def test_multiline_input_manager(self, window):
        """Test multiline input manager functionality."""
        multiline_field = ui.Field(window, (10, 10), (None, 16), "Line 1\nLine 2", multiline=True)
        multiline_manager = ui.InputManager(multiline_field, multiline=True)
        
        # Test newline handling
        enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        try:
            multiline_manager.handle_event(enter_event)
        except Exception as e:
            pytest.fail(f"Multiline enter handling failed: {e}")

    def test_special_characters(self, input_manager):
        """Test special character input."""
        special_chars = ['@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=']
        
        for char in special_chars:
            text_event = pygame.event.Event(pygame.TEXTINPUT, text=char)
            try:
                input_manager.handle_event(text_event)
            except Exception as e:
                pytest.fail(f"Special character input failed for '{char}': {e}")

    def test_unicode_input(self, input_manager):
        """Test unicode character input."""
        unicode_chars = ['α', 'β', '中', '文', '🚀', 'ñ', 'é']
        
        for char in unicode_chars:
            text_event = pygame.event.Event(pygame.TEXTINPUT, text=char)
            try:
                input_manager.handle_event(text_event)
            except Exception as e:
                pytest.fail(f"Unicode input failed for '{char}': {e}")

    def test_empty_text_input(self, input_manager):
        """Test empty text input event."""
        empty_event = pygame.event.Event(pygame.TEXTINPUT, text='')
        try:
            result = input_manager.handle_event(empty_event)
            assert result in [True, False, None]
        except Exception as e:
            pytest.fail(f"Empty text input handling failed: {e}")

    def test_non_text_events(self, input_manager):
        """Test handling of non-text events."""
        non_text_events = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 100), button=1),
            pygame.event.Event(pygame.MOUSEMOTION, pos=(100, 100)),
            pygame.event.Event(pygame.QUIT),
        ]
        
        for event in non_text_events:
            try:
                result = input_manager.handle_event(event)
                # Should return False or None for non-text events
                assert result in [True, False, None]
            except Exception as e:
                pytest.fail(f"Non-text event handling failed for {event.type}: {e}")

    def test_input_manager_with_empty_field(self, window):
        """Test input manager with empty field."""
        empty_field = ui.Field(window, (10, 10), (None, 16), "")
        input_manager = ui.InputManager(empty_field)
        
        # Test text input on empty field
        text_event = pygame.event.Event(pygame.TEXTINPUT, text='hello')
        try:
            input_manager.handle_event(text_event)
        except Exception as e:
            pytest.fail(f"Input handling on empty field failed: {e}")

    def test_cursor_movement(self, input_manager):
        """Test cursor movement functionality."""
        # Test cursor positioning events
        cursor_events = [
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_HOME),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_END),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT),
        ]
        
        for event in cursor_events:
            try:
                input_manager.handle_event(event)
            except Exception as e:
                pytest.fail(f"Cursor movement failed for key {event.key}: {e}")
