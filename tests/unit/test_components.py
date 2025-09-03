"""Basic tests for the UI engine components."""

import pytest
import pygame
import engine as ui


def test_window_creation():
    """Test that we can create a basic window."""
    window = ui.Window((400, 300))
    assert window.size == (400, 300)
    assert window.surface is not None


def test_button_creation():
    """Test that we can create a button."""
    window = ui.Window((400, 300))
    button = ui.Button(window, (10, 10), "Test", (100, 30))
    assert button.text == "Test"
    assert button.size == (100, 30)


def test_frame_creation():
    """Test that we can create a frame."""
    window = ui.Window((400, 300))
    frame = ui.Frame(window, (0, 0), (200, 150))
    assert frame.size == (200, 150)


def test_label_creation():
    """Test that we can create a label."""
    window = ui.Window((400, 300))
    label = ui.Label(window, (10, 10), "Test Label", (None, 16))
    assert label.text == "Test Label"


def test_field_creation():
    """Test that we can create a text field."""
    window = ui.Window((400, 300))
    field = ui.Field(window, (10, 10), (None, 16), "Initial text")
    assert field.value == "Initial text"
