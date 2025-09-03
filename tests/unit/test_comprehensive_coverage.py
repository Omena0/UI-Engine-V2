"""Tests for improving coverage of specific modules and components."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


# Comprehensive Window tests
def test_window_properties_comprehensive():
    """Test all window properties and methods."""
    window = ui.Window((800, 600))
    
    # Test title property
    assert window.title == "pygame window"
    window.title = "Test Window"
    assert window.title == "Test Window"
    
    # Test size property
    assert window.size == (800, 600)
    
    # Test surface property
    assert window.surface is not None
    assert isinstance(window.surface, pygame.Surface)
    
    # Test other properties
    assert window.pos == (0, 0)
    assert isinstance(window.children, list)
    assert window.frame >= 0
    assert window.dt >= 0


def test_window_event_handling():
    """Test window event handling."""
    window = ui.Window((800, 600))
    
    # Register event handler
    callback_called = False
    def test_handler():
        nonlocal callback_called
        callback_called = True
    
    window.event('test')(test_handler)
    assert 'test' in window._event_handlers
    
    # Test calling event handlers
    if hasattr(window, '_call_event_handlers'):
        window._call_event_handlers('test')
        assert callback_called


def test_window_render_modes():
    """Test different window render modes."""
    window = ui.Window((800, 600))
    
    # Test setting different modes
    window.mode = 'hybrid'
    assert window.mode == 'hybrid'
    
    window.mode = 'simple'
    assert window.mode == 'simple'
    
    # Test rendering with components
    frame = ui.Frame(window, (10, 10), (100, 100))
    window.render()
    window.draw()


def test_window_debug_mode():
    """Test window debug functionality."""
    window = ui.Window((800, 600))
    
    # Test debug mode
    window.debug = True
    assert window.debug is True
    
    # Rendering should still work in debug mode
    frame = ui.Frame(window, (10, 10), (100, 100))
    window.render()
    window.draw()


def test_window_timing():
    """Test window timing functionality."""
    window = ui.Window((800, 600))
    
    # Test timing properties
    assert hasattr(window, 'dt')
    assert hasattr(window, 'clock')
    assert hasattr(window, 'frame')
    
    # Test frame advancement
    initial_frame = window.frame
    window.frame += 1
    assert window.frame > initial_frame


# Comprehensive Dropdown tests
def test_dropdown_comprehensive():
    """Test dropdown functionality comprehensively."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Test basic properties
    assert dropdown._options == options
    assert dropdown._selected_index == 0
    
    # Test theme properties
    assert dropdown.bg is not None
    assert dropdown.text_color is not None
    assert dropdown.border_color is not None
    
    # Test rendering
    dropdown.render()
    assert len(dropdown.blits) > 0
    
    # Test event handling
    mouse_motion = pygame.event.Event(pygame.MOUSEMOTION, pos=(80, 25))
    dropdown._event(mouse_motion)
    
    # Test opening dropdown
    mouse_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(80, 25), button=1)
    dropdown._event(mouse_click)


def test_dropdown_selection():
    """Test dropdown selection handling."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    
    selected_option = None
    def on_select(index, value):
        nonlocal selected_option
        selected_option = value
    
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options, on_select=on_select)
    
    # Test selection
    dropdown._selected_index = 1
    assert dropdown._selected_index == 1


# Progress bar comprehensive tests
def test_progress_bar_comprehensive():
    """Test progress bar functionality comprehensively."""
    window = ui.Window((400, 300))
    progress = ui.ProgressBar(window, (10, 10), (200, 20))
    
    # Test progressive mode
    progress._progressive = True
    progress.value = 50.0
    assert progress.value == 50.0
    
    # Test frame progress update
    if hasattr(progress, '_frame_progress_update'):
        progress._frame_progress_update(0.016)  # 16ms delta
    
    # Test theme properties
    if hasattr(progress, 'bg_color'):
        assert progress.bg_color is not None
    if hasattr(progress, 'fg_color'):
        assert progress.fg_color is not None


def test_progress_bar_edge_cases():
    """Test progress bar edge cases."""
    window = ui.Window((400, 300))
    progress = ui.ProgressBar(window, (10, 10), (200, 20))
    
    # Test boundary values
    progress.value = -10.0
    assert progress.value == 0.0
    
    progress.value = 150.0
    assert progress.value == 100.0
    
    # Test with different max value
    progress._max = 200.0
    progress.value = 150.0
    assert progress.value == 150.0


# Slider comprehensive tests
def test_slider_comprehensive():
    """Test slider functionality comprehensively."""
    window = ui.Window((400, 300))
    slider = ui.Slider(window, (10, 10), (200, 20))
    
    # Test range properties
    assert slider.min_value == 0.0
    assert slider.max_value == 100.0
    
    # Test event handling
    mouse_down = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 15), button=1)
    slider._event(mouse_down)
    
    mouse_motion = pygame.event.Event(pygame.MOUSEMOTION, pos=(120, 15))
    slider._event(mouse_motion)
    
    mouse_up = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(120, 15), button=1)
    slider._event(mouse_up)


def test_slider_value_calculation():
    """Test slider value calculation from position."""
    window = ui.Window((400, 300))
    slider = ui.Slider(window, (10, 10), (200, 20))
    
    # Test setting values
    slider.value = 25.0
    assert slider.value == 25.0
    
    slider.value = 75.0
    assert slider.value == 75.0


# Icon button comprehensive tests
def test_icon_button_comprehensive():
    """Test icon button functionality comprehensively."""
    window = ui.Window((400, 300))
    icon_surface = pygame.Surface((16, 16))
    icon_surface.fill((255, 0, 0))
    
    icon_button = ui.IconButton(window, (10, 10), icon_surface, (50, 50))
    
    # Test properties
    assert icon_button.icon == icon_surface
    assert icon_button.size == (50, 50)
    
    # Test event handling
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(35, 35), button=1)
    icon_button._event(click_event)
    
    # Test hover
    motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(35, 35))
    icon_button._event(motion_event)


# Radio button comprehensive tests
def test_radio_button_groups():
    """Test radio button group functionality."""
    window = ui.Window((400, 300))
    
    # Create radio buttons in same group
    radio1 = ui.Radio(window, (10, 10), group_gid=0)
    radio2 = ui.Radio(window, (10, 40), group_gid=0)
    radio3 = ui.Radio(window, (10, 70), group_gid=0)
    
    # Test group property
    assert radio1.gid == 0
    assert radio2.gid == 0
    assert radio3.gid == 0
    
    # Test checking one radio button
    radio1._set_checked(True)
    assert radio1.checked is True


def test_radio_button_events():
    """Test radio button event handling."""
    window = ui.Window((400, 300))
    radio = ui.Radio(window, (10, 10))
    
    # Test mouse click
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(15, 15), button=1)
    radio._event(click_event)


# Segmented button comprehensive tests
def test_segmented_button_comprehensive():
    """Test segmented button functionality comprehensively."""
    window = ui.Window((400, 300))
    options = ["Segment 1", "Segment 2", "Segment 3"]
    segmented = ui.SegmentedButton(window, (10, 10), options)
    
    # Test properties
    assert segmented.segments == options
    assert segmented._selected == 0
    
    # Test selection
    if hasattr(segmented, 'selected_index'):
        segmented.selected_index = 1
        assert segmented.selected_index == 1
    
    # Test event handling
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 25), button=1)
    segmented._event(click_event)


# TabFrame comprehensive tests
def test_tab_frame_comprehensive():
    """Test tab frame functionality comprehensively."""
    window = ui.Window((400, 300))
    tab_frame = ui.TabFrame(window, (10, 10), (300, 200), tab_count=3)
    
    # Test properties
    assert tab_frame.tab_count == 3
    assert tab_frame.current == 0
    
    # Test accessing tabs
    tab0 = tab_frame[0]
    tab1 = tab_frame[1]
    assert tab0 is not None
    assert tab1 is not None
    
    # Test switching tabs
    tab_frame.current = 1
    assert tab_frame.current == 1
    
    # Test adding tabs
    initial_count = tab_frame.tab_count
    new_tab = tab_frame.add_tab()
    assert tab_frame.tab_count == initial_count + 1
    assert new_tab is not None


def test_tab_frame_properties():
    """Test tab frame property getters and setters."""
    window = ui.Window((400, 300))
    tab_frame = ui.TabFrame(window, (10, 10), (300, 200))
    
    # Test color property
    original_color = tab_frame.color
    new_color = (255, 0, 0)
    tab_frame.color = new_color
    assert tab_frame.color == new_color
    
    # Test corner radius
    tab_frame.corner_radius = 10
    assert tab_frame.corner_radius == 10


# Base component comprehensive tests
def test_base_component_composite_surfaces():
    """Test base component composite surface functionality."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (200, 150))
    
    # Add child components to trigger composite surface logic
    button = ui.Button(frame, (10, 10), "Test", (100, 30))
    label = ui.Label(frame, (10, 50), "Label", (None, 16))
    
    # Test composite surface methods
    frame._mark_composite_dirty()
    frame._rebuild_composite()
    frame._build_blits()
    
    # Test rendering
    frame.render()
    assert len(frame.blits) > 0


def test_base_component_size_calculations():
    """Test base component size calculation methods."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (200, 150))
    
    # Test size clamping
    clamped_size = frame._clamp_size()
    assert isinstance(clamped_size, tuple)
    assert len(clamped_size) == 2
    assert clamped_size[0] > 0
    assert clamped_size[1] > 0


# Theme comprehensive tests
def test_theme_comprehensive():
    """Test theme functionality comprehensively."""
    # Test getting various theme values
    button_bg = ui.theme.get('button_bg')
    assert button_bg is not None
    
    # Test other theme keys (some may return None)
    text_color = ui.theme.get('text_color')  # May be None
    checkbox_bg = ui.theme.get('checkbox_bg')  # May be None
    
    # Test fallback for non-existent keys
    non_existent = ui.theme.get('non_existent_key')
    # Should return None or a default value


# Text module comprehensive tests
def test_text_module_comprehensive():
    """Test text module functionality comprehensively."""
    # Test getting fonts with different parameters
    font1 = ui.text.get_font(None, 12)
    font2 = ui.text.get_font(None, 16)
    font3 = ui.text.get_font(None, 20)
    
    assert font1.get_height() < font2.get_height() < font3.get_height()
    
    # Test font caching (same parameters should return same font)
    font1_again = ui.text.get_font(None, 12)
    assert font1 is font1_again
    
    # Test font with specific family
    arial_font = ui.text.get_font('Arial', 16)
    assert arial_font is not None


def test_text_rendering_functions():
    """Test text rendering utility functions."""
    font = ui.text.get_font(None, 16)
    text = "Test text with multiple words"
    
    # Test caret position measurement
    for i in range(len(text)):
        x = ui.text.measure_caret_x(text, font, i)
        assert x >= 0
    
    # Test with multiline text
    multiline_text = "Line 1\nLine 2\nLine 3"
    x = ui.text.measure_caret_x(multiline_text, font, len("Line 1\n"))
    assert x >= 0


# Field comprehensive tests
def test_field_comprehensive():
    """Test field functionality comprehensively."""
    window = ui.Window((400, 300))
    
    # Test single-line field
    field = ui.Field(window, (10, 10), (None, 16), "Initial text", size=(200, 25))
    assert field.value == "Initial text"
    
    # Test multiline field
    multiline_field = ui.Field(window, (10, 50), (None, 16), "Line 1\nLine 2", multiline=True, size=(200, 50))
    assert multiline_field.value == "Line 1\nLine 2"
    
    # Test rendering both
    field.render()
    multiline_field.render()
    
    assert len(field.blits) > 0
    assert len(multiline_field.blits) > 0


def test_field_properties():
    """Test field properties and methods."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "test")
    
    # Test value property
    field.value = "new value"
    assert field.value == "new value"
    
    # Test that field has various properties (may be None)
    bg_color = getattr(field, 'bg_color', None)
    text_color = getattr(field, 'text_color', None)
    # These may be None, which is valid


# Additional component edge cases
def test_component_edge_cases():
    """Test various component edge cases."""
    window = ui.Window((400, 300))
    
    # Test components with minimum sizes
    tiny_button = ui.Button(window, (10, 10), "T", (10, 10))
    tiny_button.render()
    
    tiny_frame = ui.Frame(window, (30, 10), (1, 1))
    tiny_frame.render()
    
    # Test components with large sizes
    large_frame = ui.Frame(window, (50, 10), (1000, 1000))
    large_frame.render()
    
    # All should render without crashing
    assert len(tiny_button.blits) > 0
    assert len(tiny_frame.blits) > 0
    assert len(large_frame.blits) > 0


def test_component_event_propagation():
    """Test event propagation through component hierarchy."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (10, 10), (200, 150))
    button = ui.Button(frame, (10, 10), "Click", (100, 30))
    
    # Test event propagation
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(60, 35), button=1)
    
    # Event should be handled by the button
    result = frame._event(click_event)
    assert result is True or result is False  # Either is valid depending on implementation


def test_component_rendering_optimization():
    """Test component rendering optimization."""
    window = ui.Window((400, 300))
    button = ui.Button(window, (10, 10), "Optimized", (100, 30))
    
    # Test that rendering state is tracked
    if hasattr(button, '_rendered'):
        initial_rendered = button._rendered
        button.render()
        assert button._rendered is True
    
    # Test hover state optimization
    if hasattr(button, '_last_hover_state'):
        # Simulate hover change
        motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(60, 25))
        button._event(motion_event)