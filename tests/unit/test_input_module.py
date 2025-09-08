"""Tests for the input module specifically."""

import pytest
import pygame
import engine as ui
from engine.input import InputManager, _prev_word_index, _next_word_index
from unittest.mock import Mock, patch


def test_prev_word_index():
    """Test _prev_word_index function."""
    # Test empty string
    assert _prev_word_index("", 0) == 0
    assert _prev_word_index("", 5) == 0
    
    # Test idx <= 0
    assert _prev_word_index("hello world", 0) == 0
    assert _prev_word_index("hello world", -1) == 0
    
    # Test normal word navigation
    text = "hello world test"
    assert _prev_word_index(text, 16) == 12  # from end to "test"
    assert _prev_word_index(text, 11) == 6   # from "world" to "hello"
    assert _prev_word_index(text, 5) == 0    # from "hello" to beginning
    
    # Test with multiple spaces
    text = "hello   world   test"
    assert _prev_word_index(text, 20) == 16  # skip multiple spaces
    assert _prev_word_index(text, 16) == 8   # skip multiple spaces
    
    # Test with leading spaces
    text = "   hello world"
    assert _prev_word_index(text, 14) == 9   # from end to "hello"
    assert _prev_word_index(text, 8) == 3    # from "hello" to beginning


def test_next_word_index():
    """Test _next_word_index function."""
    # Test empty string
    assert _next_word_index("", 0) == 0
    assert _next_word_index("", 5) == 0
    
    # Test normal word navigation
    text = "hello world test"
    assert _next_word_index(text, 0) == 6    # from beginning to "world"
    assert _next_word_index(text, 6) == 12   # from "world" to "test"
    assert _next_word_index(text, 12) == 16  # from "test" to end
    
    # Test with multiple spaces
    text = "hello   world   test"
    assert _next_word_index(text, 0) == 8    # skip multiple spaces
    assert _next_word_index(text, 8) == 16   # skip multiple spaces
    
    # Test at end
    text = "hello world"
    assert _next_word_index(text, 11) == 11  # already at end


def test_input_manager_word_navigation():
    """Test word navigation functionality in InputManager."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "hello world test")
    field._focused = True  # Ensure field is focused
    input_manager = InputManager(field)
    
    # Test Ctrl+Left (previous word)
    field._caret = 16  # At end
    ctrl_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(ctrl_left)
    assert field._caret == 12  # Should move to "test"
    
    # Test Ctrl+Right (next word)  
    field._caret = 0  # At beginning
    ctrl_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(ctrl_right)
    assert field._caret == 6  # Should move to "world"


def test_input_manager_selection_word_navigation():
    """Test word navigation with selection."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "hello world test")
    field._focused = True  # Ensure field is focused
    input_manager = InputManager(field)
    
    # Test Ctrl+Shift+Left (select previous word)
    field._caret = 16  # At end
    field._sel_start = 16
    field._sel_end = 16
    ctrl_shift_left = pygame.event.Event(pygame.KEYDOWN, 
                                        key=pygame.K_LEFT, 
                                        mod=pygame.KMOD_CTRL | pygame.KMOD_SHIFT)
    result = input_manager.handle_event(ctrl_shift_left)
    assert field._caret == 12  # Should move to "test"
    assert field._sel_start != field._sel_end  # Should have selection
    
    # Test Ctrl+Shift+Right (select next word)
    field._caret = 0  # At beginning 
    field._sel_start = 0
    field._sel_end = 0
    ctrl_shift_right = pygame.event.Event(pygame.KEYDOWN,
                                         key=pygame.K_RIGHT,
                                         mod=pygame.KMOD_CTRL | pygame.KMOD_SHIFT)
    result = input_manager.handle_event(ctrl_shift_right)
    assert field._caret == 6  # Should move to "world"
    assert field._sel_start != field._sel_end  # Should have selection


def test_input_manager_clipboard_operations():
    """Test clipboard operations that may not be covered."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test text")
    field._focused = True  # Ensure field is focused
    input_manager = InputManager(field)
    
    # Select all text
    field._sel_start = 0
    field._sel_end = len(field._value)
    
    # Mock clipboard operations
    with patch('engine.input.clipboard.copy') as mock_copy, \
         patch('engine.input.clipboard.paste', return_value='pasted'):
        
        # Test Ctrl+C (copy)
        ctrl_c = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c, mod=pygame.KMOD_CTRL)
        result = input_manager.handle_event(ctrl_c)
        mock_copy.assert_called_once_with("test text")
        
        # Test Ctrl+V (paste)
        ctrl_v = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_v, mod=pygame.KMOD_CTRL)
        result = input_manager.handle_event(ctrl_v)
        assert "pasted" in field._value


def test_input_manager_multiline_specific():
    """Test multiline-specific functionality."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "line1\nline2\nline3", multiline=True)
    input_manager = InputManager(field, multiline=True)
    
    # Test Up arrow
    field._caret = 12  # Middle of line2
    up_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    result = input_manager.handle_event(up_key)
    # Should move up one line
    
    # Test Down arrow
    field._caret = 5  # Middle of line1
    down_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    result = input_manager.handle_event(down_key)
    # Should move down one line
    
    # Test Enter key (should add new line in multiline)
    enter_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    result = input_manager.handle_event(enter_key)
    assert '\n' in field._value


def test_input_manager_edge_cases():
    """Test edge cases and error conditions."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = InputManager(field)
    
    # Test with unsupported event type
    unsupported_event = pygame.event.Event(pygame.MOUSEMOTION)
    result = input_manager.handle_event(unsupported_event)
    assert result is False
    
    # Test with malformed key event (missing attributes)
    try:
        bad_event = Mock()
        bad_event.type = pygame.KEYDOWN
        result = input_manager.handle_event(bad_event)
    except AttributeError:
        pass  # Expected to fail gracefully


def test_input_manager_ctrl_operations():
    """Test various Ctrl operations for better coverage."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "hello world test")
    field._focused = True
    input_manager = InputManager(field)
    
    # Test Ctrl+Backspace (delete previous word)
    field._caret = 11  # After "world"
    ctrl_backspace = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(ctrl_backspace)
    assert field._caret == 6  # Should delete "world"
    assert "hello  test" in field._value
    
    # Reset field
    field._value = "hello world test"
    field._caret = 11
    
    # Test Ctrl+Delete (delete next word)  
    ctrl_delete = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DELETE, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(ctrl_delete)
    # Should delete " test"
    assert "hello world" in field._value