"""Tests for components that currently lack coverage."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch


def test_checkbox_creation():
    """Test basic checkbox creation."""
    window = ui.Window((400, 300))
    checkbox = ui.CheckBox(window, (10, 10), (50, 50), "Test checkbox")
    assert checkbox._text == "Test checkbox"
    assert checkbox._checked is False


def test_checkbox_value_property():
    """Test checkbox value getter and setter."""
    window = ui.Window((400, 300))
    checkbox = ui.CheckBox(window, (10, 10), (50, 50), "Test")
    
    # Test initial value
    assert checkbox.checked is False
    
    # Test setting value
    checkbox.checked = True
    assert checkbox.checked is True
    
    checkbox.checked = False
    assert checkbox.checked is False


def test_checkbox_toggle():
    """Test checkbox toggle functionality."""
    window = ui.Window((400, 300))
    checkbox = ui.CheckBox(window, (10, 10), (50, 50), "Test")
    
    initial_value = checkbox.checked
    
    # Simulate click event to toggle
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(25, 25), button=1)
    checkbox._event(click_event)
    
    # Value should change after click
    assert checkbox.checked == (not initial_value)


def test_checkbox_rendering():
    """Test checkbox rendering doesn't crash."""
    window = ui.Window((400, 300))
    checkbox = ui.CheckBox(window, (10, 10), (50, 50), "Test")
    
    # Should not raise any exceptions
    checkbox.render()
    assert len(checkbox.blits) > 0


def test_toggle_creation():
    """Test basic toggle creation."""
    window = ui.Window((400, 300))
    toggle = ui.Toggle(window, (10, 10), (60, 30))
    assert toggle.size == (60, 30)
    assert toggle.value is False


def test_toggle_value_property():
    """Test toggle value getter and setter."""
    window = ui.Window((400, 300))
    toggle = ui.Toggle(window, (10, 10), (60, 30))
    
    # Test initial value
    assert toggle.value is False
    
    # Test setting value
    toggle.value = True
    assert toggle.value is True


def test_toggle_toggle():
    """Test toggle toggle functionality."""
    window = ui.Window((400, 300))
    toggle = ui.Toggle(window, (10, 10), (60, 30))
    
    initial_value = toggle.value
    toggle._toggle()
    assert toggle.value == (not initial_value)


def test_toggle_rendering():
    """Test toggle rendering doesn't crash."""
    window = ui.Window((400, 300))
    toggle = ui.Toggle(window, (10, 10), (60, 30))
    
    # Should not raise any exceptions
    toggle.render()
    assert len(toggle.blits) > 0


def test_progress_creation():
    """Test basic progress bar creation."""
    window = ui.Window((400, 300))
    progress = ui.ProgressBar(window, (10, 10), (200, 20))
    assert progress.size == (200, 20)
    assert progress.value == 0.0
    assert progress._max == 100.0


def test_progress_value_property():
    """Test progress value getter and setter."""
    window = ui.Window((400, 300))
    progress = ui.ProgressBar(window, (10, 10), (200, 20))
    
    # Test setting value
    progress.value = 50.0
    assert progress.value == 50.0
    
    # Test clamping to max value
    progress.value = 150.0
    assert progress.value == 100.0  # Should be clamped to max_value
    
    # Test negative values
    progress.value = -10.0
    assert progress.value == 0.0  # Should be clamped to 0


def test_progress_max_value_property():
    """Test progress max_value property."""
    window = ui.Window((400, 300))
    progress = ui.ProgressBar(window, (10, 10), (200, 20))
    
    progress._max = 200.0
    assert progress._max == 200.0


def test_progress_rendering():
    """Test progress rendering doesn't crash."""
    window = ui.Window((400, 300))
    progress = ui.ProgressBar(window, (10, 10), (200, 20))
    progress.value = 50.0
    
    # Should not raise any exceptions
    progress.render()
    assert len(progress.blits) > 0


def test_slider_creation():
    """Test basic slider creation."""
    window = ui.Window((400, 300))
    slider = ui.Slider(window, (10, 10), (200, 20))
    assert slider.size == (200, 20)
    assert slider.value == 0.0
    assert slider.min_value == 0.0
    assert slider.max_value == 100.0


def test_slider_value_property():
    """Test slider value getter and setter."""
    window = ui.Window((400, 300))
    slider = ui.Slider(window, (10, 10), (200, 20))
    
    # Test setting value
    slider.value = 50.0
    assert slider.value == 50.0
    
    # Test clamping
    slider.value = 150.0
    assert slider.value == 100.0  # Should be clamped to max_value
    
    slider.value = -10.0
    assert slider.value == 0.0  # Should be clamped to min_value


def test_slider_rendering():
    """Test slider rendering doesn't crash."""
    window = ui.Window((400, 300))
    slider = ui.Slider(window, (10, 10), (200, 20))
    
    # Should not raise any exceptions
    slider.render()
    assert len(slider.blits) > 0


def test_iconbutton_creation():
    """Test basic icon button creation."""
    window = ui.Window((400, 300))
    # Create a simple surface for the icon
    icon_surface = pygame.Surface((16, 16))
    icon_surface.fill((255, 0, 0))  # Red square
    
    icon_button = ui.IconButton(window, (10, 10), icon_surface, (50, 50))
    assert icon_button.size == (50, 50)
    assert icon_button.icon == icon_surface


def test_iconbutton_rendering():
    """Test icon button rendering doesn't crash."""
    window = ui.Window((400, 300))
    icon_surface = pygame.Surface((16, 16))
    icon_surface.fill((255, 0, 0))
    
    icon_button = ui.IconButton(window, (10, 10), icon_surface, (50, 50))
    
    # Should not raise any exceptions
    icon_button.render()
    assert len(icon_button.blits) > 0


def test_dropdown_creation():
    """Test basic dropdown creation."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    assert dropdown.size == (150, 30)
    assert dropdown._options == options
    assert dropdown._selected_index == 0


def test_dropdown_properties():
    """Test dropdown property access."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Test selected_index property
    dropdown._selected_index = 1
    assert dropdown._selected_index == 1


def test_dropdown_rendering():
    """Test dropdown rendering doesn't crash."""
    window = ui.Window((400, 300))
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = ui.Dropdown(window, (10, 10), (150, 30), options)
    
    # Should not raise any exceptions
    dropdown.render()
    assert len(dropdown.blits) > 0


def test_radio_creation():
    """Test basic radio button creation."""
    window = ui.Window((400, 300))
    radio = ui.Radio(window, (10, 10), (18, 18))
    assert radio.size == (18, 18)
    assert radio.checked is False


def test_radio_value_property():
    """Test radio value property."""
    window = ui.Window((400, 300))
    radio = ui.Radio(window, (10, 10), (18, 18))
    
    radio._set_checked(True)
    assert radio.checked is True


def test_radio_rendering():
    """Test radio rendering doesn't crash."""
    window = ui.Window((400, 300))
    radio = ui.Radio(window, (10, 10), (18, 18))
    
    # Should not raise any exceptions
    radio.render()
    assert len(radio.blits) > 0


def test_segmented_creation():
    """Test basic segmented control creation."""
    window = ui.Window((400, 300))
    options = ["Segment 1", "Segment 2", "Segment 3"]
    segmented = ui.SegmentedButton(window, (10, 10), options)
    assert segmented.size == (200, 32)  # Default size
    assert segmented._segments == options
    assert segmented._selected == 0


def test_segmented_properties():
    """Test segmented control properties."""
    window = ui.Window((400, 300))
    options = ["Segment 1", "Segment 2", "Segment 3"]
    segmented = ui.SegmentedButton(window, (10, 10), options)
    
    # Test selected property
    segmented._selected = 1
    assert segmented._selected == 1


def test_segmented_rendering():
    """Test segmented control rendering doesn't crash."""
    window = ui.Window((400, 300))
    options = ["Segment 1", "Segment 2", "Segment 3"]
    segmented = ui.SegmentedButton(window, (10, 10), options)
    
    # Should not raise any exceptions
    segmented.render()
    assert len(segmented.blits) > 0


def test_tabframe_creation():
    """Test basic tab frame creation."""
    window = ui.Window((400, 300))
    tab_frame = ui.TabFrame(window, (10, 10), (300, 200))
    assert tab_frame.size == (300, 200)
    assert tab_frame.tab_count == 3  # Default value
    assert tab_frame.current == 0


def test_tabframe_properties():
    """Test tab frame properties."""
    window = ui.Window((400, 300))
    tab_frame = ui.TabFrame(window, (10, 10), (300, 200), tab_count=2)
    
    assert tab_frame.tab_count == 2
    
    # Test current tab property
    tab_frame.current = 1
    assert tab_frame.current == 1


def test_tabframe_indexing():
    """Test tab frame indexing access."""
    window = ui.Window((400, 300))
    tab_frame = ui.TabFrame(window, (10, 10), (300, 200), tab_count=3)
    
    # Should be able to access tabs by index
    tab0 = tab_frame[0]
    tab1 = tab_frame[1] 
    tab2 = tab_frame[2]
    
    assert tab0 is not None
    assert tab1 is not None
    assert tab2 is not None


def test_tabframe_add_tab():
    """Test adding tabs to tab frame."""
    window = ui.Window((400, 300))
    tab_frame = ui.TabFrame(window, (10, 10), (300, 200), tab_count=1)
    
    initial_count = tab_frame.tab_count
    new_tab = tab_frame.add_tab()
    
    assert tab_frame.tab_count == initial_count + 1
    assert new_tab is not None


def test_tabframe_rendering():
    """Test tab frame rendering doesn't crash."""
    window = ui.Window((400, 300))
    tab_frame = ui.TabFrame(window, (10, 10), (300, 200))
    
    # Should not raise any exceptions
    tab_frame.render()
    assert len(tab_frame.blits) > 0