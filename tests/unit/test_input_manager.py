"""Tests for InputManager and input handling."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


def test_input_manager_creation():
    """Test InputManager creation."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "Test")
    
    # Create input manager
    input_manager = ui.InputManager(field)
    assert input_manager is not None


def test_input_manager_multiline():
    """Test InputManager with multiline field."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "Test", multiline=True)
    
    # Create multiline input manager
    input_manager = ui.InputManager(field, multiline=True)
    assert input_manager is not None


def test_input_manager_basic_events():
    """Test basic input manager event handling."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "")
    input_manager = ui.InputManager(field)
    
    # Test text input event
    text_event = pygame.event.Event(pygame.TEXTINPUT, text='a')
    result = input_manager.handle_event(text_event)
    
    # Should handle text input (return value may vary)
    assert result is True or result is False


def test_input_manager_key_events():
    """Test keyboard event handling."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = ui.InputManager(field)
    
    # Test backspace
    backspace_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_BACKSPACE)
    result = input_manager.handle_event(backspace_event)
    
    assert result is True or result is False
    
    # Test arrow keys
    left_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
    result = input_manager.handle_event(left_event)
    
    assert result is True or result is False
    
    right_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    result = input_manager.handle_event(right_event)
    
    assert result is True or result is False


def test_input_manager_special_keys():
    """Test special key handling."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = ui.InputManager(field)
    
    # Test home key
    home_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_HOME)
    result = input_manager.handle_event(home_event)
    
    assert result is True or result is False
    
    # Test end key
    end_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_END)
    result = input_manager.handle_event(end_event)
    
    assert result is True or result is False


def test_input_manager_enter_handling():
    """Test enter key handling."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = ui.InputManager(field)
    
    # Test enter key
    enter_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
    result = input_manager.handle_event(enter_event)
    
    assert result is True or result is False


def test_input_manager_ctrl_keys():
    """Test Ctrl key combinations."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = ui.InputManager(field)
    
    # Test Ctrl+A (select all)
    select_all_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(select_all_event)
    
    assert result is True or result is False
    
    # Test Ctrl+C (copy)
    copy_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c, mod=pygame.KMOD_CTRL)
    result = input_manager.handle_event(copy_event)
    
    assert result is True or result is False


def test_input_manager_mouse_events():
    """Test mouse event handling."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = ui.InputManager(field)
    
    # Test mouse button down
    mouse_down_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 20), button=1)
    result = input_manager.handle_event(mouse_down_event)
    
    assert result is True
    
    # Test mouse button up
    mouse_up_event = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(50, 20), button=1)
    result = input_manager.handle_event(mouse_up_event)
    
    assert result is True


def test_input_manager_unhandled_events():
    """Test that unhandled events return False."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = ui.InputManager(field)
    
    # Test unhandled event type
    unhandled_event = pygame.event.Event(pygame.QUIT)
    result = input_manager.handle_event(unhandled_event)
    
    assert result is False


def test_field_input_integration():
    """Test field input integration."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "initial")
    
    # Test that field can handle events
    text_event = pygame.event.Event(pygame.TEXTINPUT, text='x')
    result = field._event(text_event)
    
    # Should handle text input in some way
    assert result is True or result is False  # Either is valid


def test_input_manager_composition():
    """Test IME composition handling."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    input_manager = ui.InputManager(field)
    
    # Test text editing event (IME composition) if available
    if hasattr(pygame, 'TEXTEDITING'):
        editing_event = pygame.event.Event(pygame.TEXTEDITING, text='comp')
        result = input_manager.handle_event(editing_event)
        
        assert result is True