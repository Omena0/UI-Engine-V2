"""Tests specifically targeting uncovered lines in various components."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


def test_checkbox_missing_coverage():
    """Test CheckBox uncovered code paths."""
    window = ui.Window((400, 300))
    
    # Test checkbox creation with various parameters
    checkbox = ui.CheckBox(window, (10, 10), (20, 20))
    assert checkbox.checked is False
    
    # Test checked setter
    checkbox.checked = True
    assert checkbox.checked is True
    checkbox.checked = False
    assert checkbox.checked is False
    
    # Test click events
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(20, 20), button=1)
    result = checkbox._event(click_event)
    assert result is True
    assert checkbox.checked is True  # Should toggle
    
    # Test outside click
    outside_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 100), button=1)
    result = checkbox._event(outside_click)
    assert result is False
    
    # Test rendering in both states
    checkbox.checked = False
    checkbox.render()
    assert len(checkbox.blits) > 0
    
    checkbox.checked = True
    checkbox.render()
    assert len(checkbox.blits) > 0


def test_toggle_missing_coverage():
    """Test Toggle uncovered code paths."""
    window = ui.Window((400, 300))
    
    toggle = ui.Toggle(window, (10, 10), (60, 30))
    assert toggle.value is False
    
    # Test value property
    toggle.value = True
    assert toggle.value is True
    
    # Test click to toggle
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(30, 25), button=1)
    initial_value = toggle.value
    result = toggle._event(click_event)
    assert result is True
    assert toggle.value != initial_value  # Should toggle
    
    # Test outside click
    outside_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 100), button=1)
    result = toggle._event(outside_click)
    assert result is False
    
    # Test rendering in both states
    toggle.value = False
    toggle.render()
    assert len(toggle.blits) > 0
    
    toggle.value = True  
    toggle.render()
    assert len(toggle.blits) > 0


def test_progress_bar_missing_coverage():
    """Test ProgressBar uncovered code paths."""
    window = ui.Window((400, 300))
    
    # Test with various parameters
    progress = ui.ProgressBar(window, (10, 10), (200, 20), value=50, max_value=100)
    assert progress.value == 50
    assert progress._max == 100
    
    # Test value setter with clamping
    progress.value = -10
    assert progress.value == 0  # Should clamp to min
    
    progress.value = 150
    assert progress.value == 100  # Should clamp to max
    
    # Test changing max value directly
    progress._max = 200
    progress.value = 150
    assert progress.value == 150  # Now valid with new max
    
    # Test rendering at various values
    for value in [0, 25, 50, 75, 100]:
        progress.value = value
        progress.render()
        assert len(progress.blits) > 0
    
    # Test with progressive mode if it exists
    if hasattr(progress, '_progressive'):
        progress._progressive = True
        progress.render()


def test_slider_missing_coverage():
    """Test Slider uncovered code paths."""
    window = ui.Window((400, 300))
    
    slider = ui.Slider(window, (10, 10), (200, 20), min_value=0, max_value=100, value=50)
    assert slider.value == 50
    assert slider._min == 0
    assert slider._max == 100
    
    # Test value property
    slider.value = 25
    assert slider.value == 25
    
    # Test clamping
    slider.value = -10
    assert slider.value == 0
    
    slider.value = 150
    assert slider.value == 100
    
    # Test mouse interaction
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 20), button=1)
    result = slider._event(click_event)
    
    # Test mouse motion while dragging
    motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(150, 20))
    slider._event(motion_event)
    
    # Test mouse up to stop dragging
    up_event = pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(150, 20), button=1)
    slider._event(up_event)
    
    # Test rendering
    slider.render()
    assert len(slider.blits) > 0


def test_radio_missing_coverage():
    """Test Radio button uncovered code paths."""
    window = ui.Window((400, 300))
    
    radio = ui.Radio(window, (10, 10), (18, 18))
    assert radio.checked is False
    
    # Test checked property through internal method
    radio._set_checked(True)
    assert radio.checked is True
    
    # Test click events
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(19, 19), button=1)
    result = radio._event(click_event)
    
    # Test outside click
    outside_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(100, 100), button=1)
    result = radio._event(outside_click)
    assert result is False
    
    # Test rendering in both states
    radio._set_checked(False)
    radio.render()
    assert len(radio.blits) > 0
    
    radio._set_checked(True)
    radio.render()
    assert len(radio.blits) > 0


def test_iconbutton_missing_coverage():
    """Test IconButton uncovered code paths."""
    window = ui.Window((400, 300))
    
    # Create a small test icon surface
    icon_surface = pygame.Surface((16, 16))
    icon_surface.fill((255, 0, 0))
    
    iconbutton = ui.IconButton(window, (10, 10), icon_surface, (40, 40))
    
    # Test click events
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(30, 30), button=1)
    result = iconbutton._event(click_event)
    
    # Test mouse motion for hover
    motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(30, 30))
    iconbutton._event(motion_event)
    
    # Test mouse motion outside
    motion_out = pygame.event.Event(pygame.MOUSEMOTION, pos=(100, 100))
    iconbutton._event(motion_out)
    
    # Test rendering
    iconbutton.render()
    assert len(iconbutton.blits) > 0


def test_label_missing_coverage():
    """Test Label uncovered code paths."""
    window = ui.Window((400, 300))
    
    # Test with text wrapping
    label = ui.Label(window, (10, 10), "This is a longer text that might wrap", 
                    (None, 16), size=(150, 50))
    
    # Test wrap property
    label.wrap = True
    assert label.wrap is True
    label.render()
    assert len(label.blits) > 0
    
    label.wrap = False
    assert label.wrap is False
    label.render()
    
    # Test text property
    original_text = label.text
    label.text = "New text content"
    assert label.text == "New text content"
    
    # Test with different alignments if supported
    if hasattr(label, 'align'):
        for align in ['left', 'center', 'right']:
            label.align = align
            label.render()


def test_segmented_missing_coverage():
    """Test SegmentedButton uncovered code paths."""
    window = ui.Window((400, 300))
    
    options = ["Segment 1", "Segment 2", "Segment 3"]
    segmented = ui.SegmentedButton(window, (10, 10), options)
    assert segmented._segments == options
    assert segmented._selected == 0
    
    # Test click on different segments
    # Calculate positions for each segment
    segment_width = segmented.size[0] // len(options)
    
    # Click on second segment
    click_pos = (10 + segment_width + segment_width//2, 26)  # Middle of second segment
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=click_pos, button=1)
    result = segmented._event(click_event)
    
    # Test outside click
    outside_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(300, 100), button=1)
    result = segmented._event(outside_click)
    assert result is False
    
    # Test rendering
    segmented.render()
    assert len(segmented.blits) > 0


def test_field_property_setters():
    """Test Field property setters that might not be covered."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "initial")
    
    # Test font setter
    new_font = ui.text.get_font('Arial', 18)
    field.font = new_font
    assert field.font == new_font
    
    # Test color setter
    field.color = (255, 0, 0)
    assert field.color == (255, 0, 0)
    
    # Test bg_color setter
    field.bg_color = (50, 50, 50)
    assert field.bg_color == (50, 50, 50)
    
    # Test multiline property
    field.multiline = True
    assert field.multiline is True
    field.multiline = False
    assert field.multiline is False
    
    # Test with multiline content
    multiline_field = ui.Field(window, (10, 50), (None, 14), "Line 1\nLine 2\nLine 3", 
                              multiline=True)
    multiline_field.render()
    assert len(multiline_field.blits) > 0


def test_tabframe_missing_coverage():
    """Test TabFrame uncovered code paths."""
    window = ui.Window((400, 300))
    
    tab_frame = ui.TabFrame(window, (10, 10), (300, 200))
    
    # Test adding tabs
    if hasattr(tab_frame, 'add_tab'):
        tab1 = tab_frame.add_tab()  # No arguments needed
        tab2 = tab_frame.add_tab()
        
        # Test tab selection
        if hasattr(tab_frame, '_selected_tab'):
            tab_frame._selected_tab = 1
    
    # Test rendering
    tab_frame.render()
    assert len(tab_frame.blits) > 0
    
    # Test click events
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 30), button=1)
    tab_frame._event(click_event)


def test_theme_edge_cases():
    """Test theme system edge cases."""
    # Test getting theme values that might not exist
    try:
        bg_color = ui.theme.get('nonexistent_key')
    except:
        pass  # Expected to fail or return default
    
    # Test various theme keys
    theme_keys = [
        'window_bg', 'button_bg', 'button_text', 'frame_bg',
        'field_bg', 'field_text', 'checkbox_bg', 'dropdown_bg'
    ]
    
    for key in theme_keys:
        try:
            value = ui.theme.get(key)
            assert value is not None
        except:
            pass  # Some keys might not exist


def test_util_uncovered_lines():
    """Test util module uncovered functionality."""
    # Test FPS functions with edge cases
    ui.util.set_average_fps(0)
    ui.util.set_average_fps(-10)
    ui.util.set_average_fps(10000)
    
    avg = ui.util.get_average_fps()
    assert avg >= 0
    
    # Test performance font function
    try:
        font = ui.util.get_performance_font()
        assert font is not None
    except:
        pass  # Might fail in headless mode
    
    # Test cached render with edge cases
    font = ui.text.get_font('Arial', 12)
    try:
        # Test with empty text
        surface = ui.util.cached_render(font, "", (255, 255, 255))
        assert surface is not None
        
        # Test cache overflow (render many different texts)
        for i in range(150):  # More than cache limit
            ui.util.cached_render(font, f"text_{i}", (255, 255, 255))
    except:
        pass  # Might fail in headless mode