"""Comprehensive tests for the dropdown component."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


def test_dropdown_creation_and_properties():
    """Test dropdown creation with various parameters."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    # Test basic creation
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    assert dropdown._options == options
    assert dropdown._selected_index == 0
    assert dropdown.size == (150, 30)
    assert dropdown._open is False
    
    # Test with custom selected index
    dropdown2 = ui.Dropdown(window, (10, 50), (150, 30), options, selected=1)
    assert dropdown2._selected_index == 1
    
    # Test with out-of-range selected index
    dropdown3 = ui.Dropdown(window, (10, 90), (150, 30), options, selected=10)
    assert dropdown3._selected_index == len(options) - 1  # Should clamp to max
    
    # Test with empty options
    dropdown4 = ui.Dropdown(window, (10, 130), (150, 30), [])
    assert dropdown4._selected_index == -1
    
    # Test with None options
    dropdown5 = ui.Dropdown(window, (10, 170), (150, 30), None)
    assert dropdown5._options == []
    assert dropdown5._selected_index == -1


def test_dropdown_properties():
    """Test dropdown property access."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    # Test with custom colors
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options,
                          bg=(100, 100, 100),
                          text_color=(255, 255, 255),
                          border_color=(200, 200, 200))
    
    assert dropdown.bg == (100, 100, 100)
    assert dropdown.text_color == (255, 255, 255)
    assert dropdown.border_color == (200, 200, 200)
    
    # Test with default theme colors
    dropdown2 = ui.Dropdown(window, (10, 50), (150, 30), options)
    # These should get values from theme
    assert dropdown2.bg is not None
    assert dropdown2.text_color is not None 
    assert dropdown2.border_color is not None


def test_dropdown_font_handling():
    """Test dropdown font handling."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    # Test with font tuple
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options, 
                          font=('Arial', 16))
    assert isinstance(dropdown._font, pygame.font.Font)
    
    # Test with pygame Font object
    font = ui.text.get_font('Arial', 18)
    dropdown2 = ui.Dropdown(window, (10, 50), (150, 30), options, font=font)
    assert dropdown2._font == font


def test_dropdown_callback():
    """Test dropdown callback functionality."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    # Test with custom callback
    callback_called = []
    def test_callback(index, value):
        callback_called.append((index, value))
    
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options, 
                          on_select=test_callback)
    assert dropdown.on_select == test_callback
    
    # Test default callback (should be a lambda that does nothing)
    dropdown2 = ui.Dropdown(window, (10, 50), (150, 30), options)
    # Should not raise an exception
    dropdown2.on_select(0, "test")


def test_dropdown_rendering():
    """Test dropdown rendering doesn't crash."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Test closed rendering
    dropdown.render()
    assert len(dropdown.blits) > 0
    
    # Test open rendering
    dropdown._open = True
    dropdown.render() 
    assert len(dropdown.blits) > 0


def test_dropdown_find_window():
    """Test _find_window method."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (50, 50), (200, 150))
    options = ["Option 1", "Option 2", "Option 3"]
    
    # Test direct child of window
    dropdown1 = ui.Dropdown(window, (10, 10), (150, 30), options)
    found_window = dropdown1._find_window()
    assert found_window == window
    
    # Test nested in frame
    dropdown2 = ui.Dropdown(frame, (10, 10), (150, 30), options)
    found_window2 = dropdown2._find_window()
    assert found_window2 == window


def test_dropdown_mouse_motion():
    """Test dropdown mouse motion handling."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Test mouse motion when closed
    motion_outside = pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0))
    result = dropdown._event(motion_outside)
    assert result is False
    
    motion_inside = pygame.event.Event(pygame.MOUSEMOTION, pos=(80, 25))
    result = dropdown._event(motion_inside)
    assert result is False
    
    # Test mouse motion when open
    dropdown._open = True
    motion_inside_open = pygame.event.Event(pygame.MOUSEMOTION, pos=(80, 25))
    result = dropdown._event(motion_inside_open)
    assert result is True  # Should swallow event when open and hovered
    
    motion_outside_open = pygame.event.Event(pygame.MOUSEMOTION, pos=(0, 0))
    result = dropdown._event(motion_outside_open)
    assert result is False


def test_dropdown_click_toggle():
    """Test dropdown click to toggle open/closed."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Test clicking header when closed (should open)
    click_header = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(80, 25), button=1)
    result = dropdown._event(click_header)
    assert result is True
    assert dropdown._open is True
    
    # Test clicking header when open (should close)
    result = dropdown._event(click_header)
    assert result is True
    assert dropdown._open is False


def test_dropdown_click_outside():
    """Test clicking outside dropdown when open."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Open dropdown first
    dropdown._open = True
    
    # Test clicking outside (should close)
    click_outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(200, 200), button=1)
    result = dropdown._event(click_outside)
    assert result is True
    assert dropdown._open is False


def test_dropdown_option_selection():
    """Test selecting dropdown options by clicking."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    callback_calls = []
    def on_select(index, value):
        callback_calls.append((index, value))
    
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options, on_select=on_select)
    
    # Open dropdown
    dropdown._open = True
    
    # Calculate click position for second option
    # Options start at y = dropdown.pos[1] + dropdown.size[1] 
    option_y = 25 + 30 + (dropdown._item_height * 1)  # Second option (index 1)
    click_option = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(80, option_y), button=1)
    
    result = dropdown._event(click_option)
    assert result is True
    assert dropdown._selected_index == 1
    assert dropdown._open is False  # Should close after selection
    assert len(callback_calls) == 1
    assert callback_calls[0] == (1, "Option 2")


def test_dropdown_keyboard_navigation():
    """Test keyboard navigation in dropdown."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Simulate hover state for focus
    dropdown._was_hovered = True
    
    # Test opening with space key
    space_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    result = dropdown._event(space_key)
    assert result is True
    assert dropdown._open is True
    
    # Test navigation with arrow keys
    down_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    result = dropdown._event(down_key)
    assert result is True
    assert dropdown._selected_index == 1
    
    up_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    result = dropdown._event(up_key)
    assert result is True
    assert dropdown._selected_index == 0
    
    # Test wrapping with up key at index 0
    result = dropdown._event(up_key)
    assert result is True
    assert dropdown._selected_index == 2  # Should wrap to last
    
    # Test escape to close
    escape_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    result = dropdown._event(escape_key)
    assert result is True
    assert dropdown._open is False


def test_dropdown_keyboard_selection():
    """Test keyboard selection with Enter."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    callback_calls = []
    def on_select(index, value):
        callback_calls.append((index, value))
    
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options, on_select=on_select)
    
    # Open and navigate to option 1
    dropdown._open = True
    dropdown._selected_index = 1
    
    # Test selection with enter
    enter_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    result = dropdown._event(enter_key)
    assert result is True
    assert dropdown._open is False  # Should close after selection
    assert len(callback_calls) == 1
    assert callback_calls[0] == (1, "Option 2")


def test_dropdown_error_handling():
    """Test dropdown error handling in callbacks."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    # Test callback that raises exception
    def bad_callback(index, value):
        raise Exception("Test exception")
    
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options, on_select=bad_callback)
    
    # Open and select - should not crash despite exception
    dropdown._open = True
    dropdown._selected_index = 1
    
    enter_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    result = dropdown._event(enter_key)
    assert result is True  # Should still return True even with exception
    assert dropdown._open is False  # Should still close


def test_dropdown_edge_cases():
    """Test dropdown edge cases and boundary conditions."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Test with empty options list
    empty_dropdown = ui.Dropdown(window, (10, 50), (150, 30), [])
    
    # Keyboard navigation with empty options
    empty_dropdown._was_hovered = True
    empty_dropdown._open = True
    
    down_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    result = empty_dropdown._event(down_key)
    assert result is False  # Should not handle when no options
    
    # Test unhandled event types
    unsupported_event = pygame.event.Event(pygame.KEYUP, key=pygame.K_a)
    result = dropdown._event(unsupported_event)
    assert result is False
    
    # Test keyboard events when not focused
    dropdown._was_hovered = False
    dropdown._open = False
    space_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
    result = dropdown._event(space_key)
    assert result is False


def test_dropdown_close_functionality():
    """Test dropdown close functionality."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Test _close method
    dropdown._open = True
    dropdown._close()
    assert dropdown._open is False
    
    # Test _set_dropdown_closed method (if accessible)
    if hasattr(dropdown, '_set_dropdown_closed'):
        dropdown._open = True
        dropdown._set_dropdown_closed()
        assert dropdown._open is False


def test_dropdown_w_key_navigation():
    """Test navigation with W and S keys."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    dropdown._open = True
    dropdown._selected_index = 1
    
    # Test W key (up)
    w_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_w)
    result = dropdown._event(w_key)
    assert result is True
    assert dropdown._selected_index == 0
    
    # Test S key (down)
    s_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s)
    result = dropdown._event(s_key)
    assert result is True
    assert dropdown._selected_index == 1


def test_dropdown_enter_key_variants():
    """Test different Enter key variants."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    callback_calls = []
    def on_select(index, value):
        callback_calls.append((index, value))
    
    # Test opening with return key
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options, on_select=on_select)
    dropdown._was_hovered = True
    
    return_key = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    result = dropdown._event(return_key)
    assert result is True
    assert dropdown._open is True
    
    # Test selection with keypad enter
    dropdown._selected_index = 2
    kp_enter = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_KP_ENTER)
    result = dropdown._event(kp_enter)
    assert result is True
    assert dropdown._open is False
    assert len(callback_calls) == 1
    assert callback_calls[0] == (2, "Option 3")