"""Additional tests for input module missing coverage."""

import pytest
import pygame
import engine as ui
from engine.input import InputManager, _prev_word_index, _next_word_index
from unittest.mock import Mock, patch


def test_input_manager_comprehensive_coverage():
    """Test comprehensive InputManager coverage focusing on missing lines."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "hello world test example")
    field._focused = True
    input_manager = InputManager(field)
    
    # Test Select All (Ctrl+A)
    ctrl_a = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(ctrl_a)
    assert result is True
    assert field._sel_start == 0
    assert field._sel_end == len(field._value)
    assert field._caret == field._sel_end
    
    # Test Copy (Ctrl+C) with selection
    with patch('engine.input.clipboard.copy') as mock_copy:
        ctrl_c = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c, mod=pygame.KMOD_CTRL)
        result = input_manager.handle_event(ctrl_c)
        assert result is True
        mock_copy.assert_called_once_with(field._value)
    
    # Test Cut (Ctrl+X) with selection
    original_text = field._value
    field._sel_start = 6  # "world " part
    field._sel_end = 12
    
    with patch('engine.input.clipboard.copy') as mock_copy:
        ctrl_x = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x, mod=pygame.KMOD_CTRL)
        result = input_manager.handle_event(ctrl_x)
        assert result is True
        mock_copy.assert_called_once()
        assert len(field._value) < len(original_text)  # Text should be cut
        assert field._sel_start == field._sel_end  # Selection should be collapsed


def test_input_manager_paste_operations():
    """Test paste operations."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "hello world")
    field._focused = True
    input_manager = InputManager(field)
    
    # Test Paste (Ctrl+V)
    field._caret = 5  # After "hello"
    with patch('engine.input.clipboard.paste', return_value=' beautiful') as mock_paste:
        ctrl_v = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_v, mod=pygame.KMOD_CTRL)
        result = input_manager.handle_event(ctrl_v)
        assert result is True
        assert ' beautiful' in field._value
    
    # Test paste with selection (should replace selection)
    field._value = "hello world"
    field._sel_start = 6
    field._sel_end = 11  # Select "world"
    with patch('engine.input.clipboard.paste', return_value='universe') as mock_paste:
        ctrl_v = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_v, mod=pygame.KMOD_CTRL)
        result = input_manager.handle_event(ctrl_v)
        assert result is True
        assert 'universe' in field._value
        assert 'world' not in field._value


def test_input_manager_backspace_operations():
    """Test various backspace operations."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "hello world test")
    field._focused = True
    input_manager = InputManager(field)
    
    # Test backspace with selection (should delete selection)
    field._sel_start = 6
    field._sel_end = 11  # Select "world"
    backspace = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, mod=0)
    result = input_manager.handle_event(backspace)
    assert result is True
    assert 'world' not in field._value
    
    # Test Ctrl+Backspace (delete previous word)
    field._value = "hello world test"
    field._caret = 11  # After "world"
    ctrl_backspace = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(ctrl_backspace)
    assert result is True
    assert field._caret == 6  # Should be after "hello "
    
    # Test normal backspace
    field._value = "hello world"
    field._caret = 5  # After "hello"
    backspace = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE, mod=0)
    result = input_manager.handle_event(backspace)
    assert result is True
    assert field._value.startswith("hell")


def test_input_manager_delete_operations():
    """Test various delete operations."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "hello world test")
    field._focused = True
    input_manager = InputManager(field)
    
    # Test delete with selection
    field._sel_start = 6
    field._sel_end = 11  # Select "world"
    delete_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DELETE, mod=0)
    result = input_manager.handle_event(delete_key)
    assert result is True
    assert 'world' not in field._value
    
    # Test Ctrl+Delete (delete next word)
    field._value = "hello world test"
    field._caret = 5  # After "hello"
    ctrl_delete = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DELETE, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(ctrl_delete)
    assert result is True
    # Should delete " world"
    
    # Test normal delete
    field._value = "hello world"
    field._caret = 5  # After "hello"
    delete_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DELETE, mod=0)
    result = input_manager.handle_event(delete_key)
    assert result is True
    # Should delete the space


def test_input_manager_arrow_navigation():
    """Test comprehensive arrow key navigation."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "hello world test")
    field._focused = True
    input_manager = InputManager(field)
    
    # Test Left arrow
    field._caret = 5
    left_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, mod=0)
    result = input_manager.handle_event(left_key)
    assert result is True
    assert field._caret == 4
    
    # Test Right arrow
    right_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=0)
    result = input_manager.handle_event(right_key)
    assert result is True
    assert field._caret == 5
    
    # Test Shift+Left (select left)
    field._caret = 5
    field._sel_start = field._sel_end = field._caret
    shift_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, mod=pygame.KMOD_SHIFT)
    result = input_manager.handle_event(shift_left)
    assert result is True
    assert field._caret == 4
    assert field._sel_start != field._sel_end  # Should have selection
    
    # Test Shift+Right (select right)
    shift_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, mod=pygame.KMOD_SHIFT)
    result = input_manager.handle_event(shift_right)
    assert result is True


def test_input_manager_multiline_navigation():
    """Test multiline navigation."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "line1\nline2\nline3", multiline=True)
    field._focused = True
    input_manager = InputManager(field, multiline=True)
    
    # Test Up arrow
    field._caret = 12  # Middle of line2
    up_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP, mod=0)
    result = input_manager.handle_event(up_key)
    # Should move to line1
    
    # Test Down arrow
    field._caret = 3  # Middle of line1
    down_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN, mod=0)
    result = input_manager.handle_event(down_key)
    # Should move to line2
    
    # Test Home key (not implemented, should return False)
    field._caret = 8  # Middle of line2
    home_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_HOME, mod=0)
    result = input_manager.handle_event(home_key)
    assert result is False  # HOME key is not implemented
    
    # Test End key (not implemented, should return False)
    field._caret = 6  # Start of line2
    end_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_END, mod=0)
    result = input_manager.handle_event(end_key)
    assert result is False  # END key is not implemented
    
    # Test Enter key (should add newline in multiline)
    original_length = len(field._value)
    field._caret = 8
    enter_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0)
    result = input_manager.handle_event(enter_key)
    assert result is True
    assert len(field._value) > original_length  # Should have added newline


def test_input_manager_single_line_navigation():
    """Test navigation in single line mode."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "single line text", multiline=False)
    field._focused = True
    input_manager = InputManager(field, multiline=False)
    
    # Test Home key (not implemented, should return False)
    field._caret = 8
    home_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_HOME, mod=0)
    result = input_manager.handle_event(home_key)
    assert result is False
    assert field._caret == 8  # Caret should remain unchanged
    
    # Test End key (not implemented, should return False)
    end_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_END, mod=0)
    result = input_manager.handle_event(end_key)
    assert result is False
    assert field._caret == 8  # Caret should remain unchanged
    
    # Test Enter key (should trigger submit in single line)
    callback_called = []
    def test_submit(value):
        callback_called.append(value)
    
    field.emit('submit', field._value)  # Test emit
    
    enter_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0)
    result = input_manager.handle_event(enter_key)
    # In single line, enter might trigger submit


def test_input_manager_mouse_interaction():
    """Test mouse interaction with input field."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "clickable text")
    input_manager = InputManager(field)
    
    # Test mouse button down
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, 
                                    pos=(50, 25), button=1)
    result = input_manager.handle_event(click_event)
    # Should set focus and position caret
    
    # Test double click
    double_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, 
                                     pos=(50, 25), button=1)
    # Simulate quick succession for double click detection
    result1 = input_manager.handle_event(double_click)
    result2 = input_manager.handle_event(double_click)
    
    # Test drag selection
    drag_start = pygame.event.Event(pygame.MOUSEBUTTONDOWN, 
                                   pos=(30, 25), button=1)
    input_manager.handle_event(drag_start)
    
    drag_motion = pygame.event.Event(pygame.MOUSEMOTION, pos=(80, 25))
    input_manager.handle_event(drag_motion)
    
    drag_end = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(80, 25), button=1)
    input_manager.handle_event(drag_end)


def test_input_manager_text_input():
    """Test text input handling."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "")
    field._focused = True
    input_manager = InputManager(field)
    
    # Test text input event
    text_event = pygame.event.Event(pygame.TEXTINPUT, text='a')
    result = input_manager.handle_event(text_event)
    assert result is True
    assert 'a' in field._value
    
    # Test text input with selection (should replace)
    field._value = "hello"
    field._sel_start = 1
    field._sel_end = 4  # Select "ell"
    text_event = pygame.event.Event(pygame.TEXTINPUT, text='i')
    result = input_manager.handle_event(text_event)
    assert result is True
    assert field._value == "hio"  # "ell" replaced with "i"
    
    # Test empty text input
    empty_text_event = pygame.event.Event(pygame.TEXTINPUT, text='')
    result = input_manager.handle_event(empty_text_event)
    # Should handle gracefully


def test_input_manager_error_conditions():
    """Test error conditions and edge cases."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = InputManager(field)
    
    # Test with component not focused
    field._focused = False
    key_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=0)
    result = input_manager.handle_event(key_event)
    assert result is False
    
    text_event = pygame.event.Event(pygame.TEXTINPUT, text='a')
    result = input_manager.handle_event(text_event)
    assert result is False
    
    # Test clipboard operations with exceptions
    field._focused = True
    field._sel_start = 0
    field._sel_end = len(field._value)
    
    with patch('engine.input.clipboard.copy', side_effect=Exception("Clipboard error")):
        ctrl_c = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c, mod=pygame.KMOD_CTRL)
        result = input_manager.handle_event(ctrl_c)
        # Should not crash, just return True
        assert result is True
    
    with patch('engine.input.clipboard.paste', side_effect=Exception("Clipboard error")):
        ctrl_v = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_v, mod=pygame.KMOD_CTRL)
        result = input_manager.handle_event(ctrl_v)
        # Should handle gracefully