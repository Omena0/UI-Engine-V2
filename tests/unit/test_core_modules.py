"""Tests for core modules and additional component functionality."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


# Base component tests
def test_component_base_hover():
    """Test base component hover detection."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (100, 100))
    
    # Test hover detection with mock mouse position
    hovered, changed = frame._hovered((50, 50))
    assert hovered is True
    
    hovered, changed = frame._hovered((150, 150))
    assert hovered is False


def test_component_base_event_system():
    """Test base component event system (on, off, emit)."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (100, 100))
    
    # Test event listener registration
    callback_called = False
    def test_callback():
        nonlocal callback_called
        callback_called = True
    
    frame.on('test_event', test_callback)
    frame.emit('test_event')
    assert callback_called is True
    
    # Test removing event listener
    callback_called = False
    frame.off('test_event', test_callback)
    frame.emit('test_event')
    assert callback_called is False
    
    # Test removing all listeners for an event
    frame.on('test_event', test_callback)
    frame.off('test_event')
    frame.emit('test_event')
    assert callback_called is False


def test_component_base_size_property():
    """Test base component size property."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (100, 100))
    
    original_size = frame.size
    assert original_size == (100, 100)
    
    # Test setting size
    frame.size = (200, 150)
    assert frame.size == (200, 150)


def test_component_base_pos_property():
    """Test base component position property."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (100, 100))
    
    assert frame.pos == (10, 10)
    
    # Test setting position
    frame.pos = (20, 30)
    assert frame.pos == (20, 30)


def test_component_base_absolute_pos():
    """Test absolute position calculation."""
    window = ui.Window((400, 300))
    frame1 = ui.Frame(window, (10, 10), (100, 100))
    frame2 = ui.Frame(frame1, (5, 5), (50, 50))
    
    assert frame2.absolute_pos == (15, 15)  # 10+5, 10+5


def test_component_base_add_child():
    """Test adding children to components."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (100, 100))
    
    initial_children = len(frame.children)
    button = ui.Button(frame, (5, 5), "Test", (50, 30))
    
    assert len(frame.children) == initial_children + 1
    assert button in frame.children


# Window tests
def test_window_event_system():
    """Test window event system."""
    window = ui.Window((400, 300))
    
    callback_called = False
    def test_callback():
        nonlocal callback_called
        callback_called = True
    
    window.event('test_event')(test_callback)
    # Note: Window doesn't have emit method, this test focuses on event registration


def test_window_properties():
    """Test window properties."""
    window = ui.Window((400, 300))
    
    assert window.size == (400, 300)
    assert window.surface is not None
    assert isinstance(window.surface, pygame.Surface)


def test_window_render_and_draw():
    """Test window render and draw methods."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (100, 100))
    
    # Should not raise exceptions
    window.render()
    window.draw()


# Button tests (additional coverage)
def test_button_properties():
    """Test button property getters and setters."""
    window = ui.Window((400, 300))
    button = ui.Button(window, (10, 10), "Initial", (100, 30))
    
    # Test text property
    assert button.text == "Initial"
    button.text = "Updated"
    assert button.text == "Updated"
    
    # Test theme-resolved properties
    assert button.bg_color is not None
    assert button.text_color is not None
    assert button.bg_hover_color is not None
    assert button.text_hover_color is not None


def test_button_event_handling():
    """Test button event handling."""
    window = ui.Window((400, 300))
    
    clicked = False
    def on_click(text):
        nonlocal clicked
        clicked = True
    
    button = ui.Button(window, (10, 10), "Click me", (100, 30), on_click=on_click)
    
    # Simulate mouse click event
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 25), button=1)
    result = button._event(click_event)
    
    assert result is True  # Event should be consumed
    assert clicked is True


def test_button_hover_state():
    """Test button hover state changes."""
    window = ui.Window((400, 300))
    button = ui.Button(window, (10, 10), "Hover me", (100, 30))
    
    # Simulate mouse motion event
    motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(50, 25))
    button._event(motion_event)
    
    # Should not raise exceptions and button should be re-rendered


# Label tests (additional coverage)
def test_label_properties():
    """Test label properties."""
    window = ui.Window((400, 300))
    label = ui.Label(window, (10, 10), "Test Label", (None, 16))
    
    # Test text property
    assert label.text == "Test Label"
    label.text = "Updated Label"
    assert label.text == "Updated Label"
    
    # Test theme-resolved properties
    assert label.color is not None


def test_label_rendering():
    """Test label rendering with different configurations."""
    window = ui.Window((400, 300))
    
    # Test with default font
    label1 = ui.Label(window, (10, 10), "Label 1", (None, 16))
    label1.render()
    assert len(label1.blits) > 0
    
    # Test with explicit size
    label2 = ui.Label(window, (10, 40), "Label 2", (None, 20), size=(100, 25))
    label2.render()
    assert len(label2.blits) > 0


# Field tests (additional coverage)
def test_field_properties():
    """Test field properties."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "Initial value")
    
    # Test value property
    assert field.value == "Initial value"
    field.value = "Updated value"
    assert field.value == "Updated value"


def test_field_multiline():
    """Test multiline field."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "Line 1\nLine 2", multiline=True)
    
    assert field.value == "Line 1\nLine 2"
    field.render()
    assert len(field.blits) > 0


# Frame tests (additional coverage)
def test_frame_background_color():
    """Test frame background color."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (100, 100))
    
    # Test default color
    assert frame.color is not None
    
    # Test setting color
    new_color = (255, 0, 0)
    frame.color = new_color
    assert frame.color == new_color


# Toggle tests (additional coverage)
def test_toggle_properties():
    """Test toggle additional properties."""
    window = ui.Window((400, 300))
    toggle = ui.Toggle(window, (10, 10), (60, 30))
    
    # Test theme-resolved properties
    assert toggle.bg is not None
    assert toggle.bg_on is not None
    assert toggle.knob_color is not None


def test_toggle_event_handling():
    """Test toggle event handling."""
    window = ui.Window((400, 300))
    
    changed = False
    def on_change(value):
        nonlocal changed
        changed = True
    
    toggle = ui.Toggle(window, (10, 10), (60, 30), on_change=on_change)
    
    # Simulate mouse click event
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(30, 15), button=1)
    result = toggle._event(click_event)
    
    assert result is True  # Event should be consumed
    assert changed is True


# Theme tests
def test_theme_get():
    """Test theme.get functionality."""
    # Test getting a theme value
    value = ui.theme.get('button_bg')
    assert value is not None


def test_theme_current():
    """Test theme.current access."""
    current_theme = ui.theme.current
    assert current_theme is not None
    assert hasattr(current_theme, 'get')


# Util tests
def test_util_cached_render():
    """Test util.cached_render functionality."""
    font = ui.text.get_font(None, 16)
    text = "Test Text"
    color = (255, 255, 255)
    
    # Should not raise exceptions
    surface = ui.util.cached_render(font, text, color)
    assert surface is not None
    assert isinstance(surface, pygame.Surface)


def test_util_functions():
    """Test util module functions."""
    # Test get_average_fps
    avg_fps = ui.util.get_average_fps()
    assert avg_fps >= 0
    
    # Test set_average_fps
    ui.util.set_average_fps(60.0)
    assert ui.util.get_average_fps() > 0


# Text module tests
def test_text_get_font():
    """Test text.get_font functionality."""
    # Test default font
    font = ui.text.get_font(None, 16)
    assert font is not None
    assert isinstance(font, pygame.font.Font)
    
    # Test different sizes
    font_small = ui.text.get_font(None, 12)
    font_large = ui.text.get_font(None, 24)
    assert font_small.get_height() < font_large.get_height()


def test_text_measure_functions():
    """Test text measurement functions."""
    font = ui.text.get_font(None, 16)
    text = "Test Text"
    
    # Test measure_caret_x
    x = ui.text.measure_caret_x(text, font, len(text))
    assert x >= 0
    
    # Test render_selection (requires x, y coordinates)
    selection_surface = ui.text.render_selection(text, font, 0, 4, (255, 255, 255), (0, 0, 255), 0, 0)
    assert selection_surface is not None


# Error handling tests
def test_component_exception_handling():
    """Test that components handle exceptions gracefully."""
    window = ui.Window((400, 300))
    
    # Test with invalid event handlers
    def bad_handler():
        raise Exception("Test exception")
    
    button = ui.Button(window, (10, 10), "Test", (100, 30), on_click=bad_handler)
    
    # Should not raise exception even with bad handler
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 25), button=1)
    button._event(click_event)
    

def test_emit_exception_handling():
    """Test event emission handles exceptions in listeners."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (100, 100))
    
    def bad_listener():
        raise Exception("Test exception")
    
    frame.on('test', bad_listener)
    
    # Should not raise exception
    frame.emit('test')


# Integration tests for rendering
def test_complex_component_hierarchy():
    """Test rendering with complex component hierarchy."""
    window = ui.Window((800, 600))
    
    # Create nested structure
    main_frame = ui.Frame(window, (10, 10), (780, 580))
    
    # Add various components
    ui.Label(main_frame, (10, 10), "Complex UI Test", (None, 20))
    ui.Button(main_frame, (10, 40), "Button 1", (100, 30))
    ui.Button(main_frame, (120, 40), "Button 2", (100, 30))
    
    sub_frame = ui.Frame(main_frame, (10, 80), (300, 200))
    ui.Field(sub_frame, (10, 10), (None, 16), "Text field", size=(280, 25))
    ui.CheckBox(sub_frame, (10, 45), (20, 20), "✓")
    ui.Toggle(sub_frame, (40, 45), (60, 20))
    
    # Test that everything renders without exceptions
    window.render()
    window.draw()
    
    # Verify component structure
    assert len(window.children) == 1
    assert len(main_frame.children) >= 4
    assert len(sub_frame.children) >= 3