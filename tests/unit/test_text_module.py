"""Tests for the text module specifically."""

import pytest
import pygame
import engine as ui
from engine.text import (
    get_font, get_caret_index_at_x, measure_caret_x, render_line_with_caret,
    render_selection, draw, draw_justified, split_text, get_total_size,
    measure_word_width, measure_line_words_width, render_word_per_char,
    _font_id_key, _font_cache_key
)
from unittest.mock import Mock, patch


def test_get_caret_index_at_x():
    """Test get_caret_index_at_x function."""
    font = get_font('Arial', 16)
    text = "hello world"
    
    # Test x <= 0
    assert get_caret_index_at_x(text, font, -5) == 0
    assert get_caret_index_at_x(text, font, 0) == 0
    
    # Test normal case - should find closest caret position
    # Test middle position
    mid_x = font.size(text[:6])[0]  # After "hello "
    result = get_caret_index_at_x(text, font, mid_x)
    assert 0 <= result <= len(text)
    
    # Test beyond end
    end_x = font.size(text)[0] + 100
    assert get_caret_index_at_x(text, font, end_x) == len(text)


def test_render_line_with_caret():
    """Test render_line_with_caret function."""
    # Create a surface to render on
    surface = pygame.Surface((200, 50))
    font = get_font('Arial', 16)
    text = "test text"
    
    # Test normal rendering with visible caret
    render_line_with_caret(
        surface, text, 5, font, 
        color=(255, 255, 255), bg_color=(0, 0, 0), 
        x=10, y=10, caret_visible=True
    )
    
    # Test with invisible caret
    render_line_with_caret(
        surface, text, 5, font, 
        color=(255, 255, 255), bg_color=(0, 0, 0), 
        x=10, y=10, caret_visible=False
    )
    
    # Test with None caret_index
    render_line_with_caret(
        surface, text, None, font, 
        color=(255, 255, 255), bg_color=(0, 0, 0), 
        x=10, y=10, caret_visible=True
    )
    
    # Test with out-of-range caret_index
    render_line_with_caret(
        surface, text, -1, font, 
        color=(255, 255, 255), bg_color=(0, 0, 0), 
        x=10, y=10, caret_visible=True
    )
    
    render_line_with_caret(
        surface, text, 100, font, 
        color=(255, 255, 255), bg_color=(0, 0, 0), 
        x=10, y=10, caret_visible=True
    )


def test_render_selection():
    """Test render_selection function."""
    surface = pygame.Surface((200, 50))
    font = get_font('Arial', 16)
    
    # Test no selection (sel_start == sel_end)
    render_selection(surface, "test", 0, 0, font, (100, 100, 255), 10, 10)
    
    # Test normal selection
    render_selection(surface, "test", 1, 3, font, (100, 100, 255), 10, 10)
    
    # Test reversed selection (sel_start > sel_end)
    render_selection(surface, "test", 3, 1, font, (100, 100, 255), 10, 10)
    
    # Test multiline selection
    multiline_text = "line1\nline2\nline3"
    render_selection(surface, multiline_text, 2, 8, font, (100, 100, 255), 10, 10)


def test_draw_function():
    """Test draw function with various parameters."""
    font = get_font('Arial', 16)
    text = "This is test text for drawing"
    
    # Test basic draw - returns a surface
    surface = draw(text, font, (255, 255, 255))
    assert isinstance(surface, pygame.Surface)
    assert surface.get_width() > 0
    assert surface.get_height() > 0
    
    # Test with background color
    surface_bg = draw(text, font, (255, 255, 255), bg_color=(50, 50, 50))
    assert isinstance(surface_bg, pygame.Surface)
    
    # Test with custom dimensions
    surface_custom = draw(text, font, (255, 255, 255), width=400, height=100)
    assert surface_custom.get_width() == 400
    assert surface_custom.get_height() == 100
    
    # Test multiline text
    multiline = "Line one\nLine two\nLine three"
    surface_multi = draw(multiline, font, (255, 255, 255))
    assert isinstance(surface_multi, pygame.Surface)


def test_draw_justified():
    """Test draw_justified function."""
    font = get_font('Arial', 16)
    text = "This is a longer text that should be justified when drawn on multiple lines"
    
    # Test basic justified drawing - returns a surface
    surface = draw_justified(text, font, (255, 255, 255), width=200, height=150)
    assert isinstance(surface, pygame.Surface)
    assert surface.get_width() == 200
    # Height may be adjusted based on content, just check it's positive
    assert surface.get_height() > 0
    
    # Test with background color
    surface_bg = draw_justified(text, font, (255, 255, 255), bg_color=(50, 50, 50), 
                               width=200, height=100)
    assert isinstance(surface_bg, pygame.Surface)
    
    # Test with specific line spacing
    surface_spaced = draw_justified(text, font, (255, 255, 255), 
                                   width=200, height=100, line_spacing=1.5)
    assert isinstance(surface_spaced, pygame.Surface)


def test_split_text():
    """Test split_text function."""
    font = get_font('Arial', 16)
    text = "This is a longer text that should be split into multiple lines"
    
    # Test basic split - returns list of tuples (line, space_info, letter_spacings)
    lines = split_text(text, font, 200)
    assert isinstance(lines, list)
    assert len(lines) > 0
    # Each line should be a tuple with 3 elements
    for line_data in lines:
        assert isinstance(line_data, tuple)
        assert len(line_data) == 3
        line_text, space_info, letter_spacings = line_data
        assert isinstance(line_text, str)
    
    # Test with very narrow width (should split words)
    lines_narrow = split_text(text, font, 50)
    assert len(lines_narrow) >= len(lines)
    
    # Test with very wide width (should be single line)
    lines_wide = split_text(text, font, 1000)
    assert len(lines_wide) <= len(lines)
    
    # Test with justify=False
    lines_no_justify = split_text(text, font, 200, justify=False)
    assert isinstance(lines_no_justify, list)


def test_get_total_size():
    """Test get_total_size function."""
    font = get_font('Arial', 16)
    
    # First create some line data using split_text
    text = "Single line text"
    lines = split_text(text, font, 300)
    
    # Test with these lines
    width, height = get_total_size(lines, font, 1.2)
    assert width > 0
    assert height > 0
    
    # Test multiline
    multiline_text = "Line one\nLine two\nLine three"
    lines_multi = split_text(multiline_text, font, 300)
    width_multi, height_multi = get_total_size(lines_multi, font, 1.2)
    assert width_multi > 0
    assert height_multi >= height  # Should be at least as tall
    
    # Test with narrow width (forces wrapping)
    long_text = "This is a really long line that should wrap"
    lines_wrapped = split_text(long_text, font, 100)
    width_narrow, height_narrow = get_total_size(lines_wrapped, font, 1.2)
    assert height_narrow >= height  # Should be at least as tall as single line


def test_measure_word_width():
    """Test measure_word_width function."""
    font = get_font('Arial', 16)
    
    # Test normal word
    width = measure_word_width("hello", font)
    assert width > 0
    
    # Test empty string
    width_empty = measure_word_width("", font)
    assert width_empty >= 0
    
    # Test longer word
    width_long = measure_word_width("hello world", font)
    assert width_long > width


def test_measure_line_words_width():
    """Test measure_line_words_width function."""
    font = get_font('Arial', 16)
    words = ["hello", "world", "test"]
    
    # Test basic measure
    width = measure_line_words_width(words, font)
    assert width > 0
    
    # Test empty list
    width_empty = measure_line_words_width([], font)
    assert width_empty == 0
    
    # Test single word
    width_single = measure_line_words_width(["hello"], font)
    assert width_single > 0


def test_render_word_per_char():
    """Test render_word_per_char function."""
    surface = pygame.Surface((200, 50))
    font = get_font('Arial', 16)
    
    # Test normal word rendering (note: bg_color is required)
    end_x = render_word_per_char(surface, "hello", 10, 10, font, (255, 255, 255), None)
    assert end_x > 10  # Should return x position after rendering
    
    # Test with background color
    end_x_bg = render_word_per_char(surface, "hello", 10, 30, font, (255, 255, 255), (50, 50, 50))
    assert end_x_bg > 10
    
    # Test with extras (letter spacing)
    end_x_spaced = render_word_per_char(surface, "hello", 10, 30, font, (255, 255, 255), None, 
                                       extras=[1, 2, 1, 1])  # Extra spacing between letters
    assert end_x_spaced >= end_x  # Should be at least as wide


def test_font_cache_functions():
    """Test font caching helper functions."""
    font = get_font('Arial', 16)
    
    # Test _font_id_key
    key1 = _font_id_key(font)
    assert key1 is not None
    
    # Test with tuple (font spec)
    font_spec = ('Arial', 16, False, False)  
    key2 = _font_id_key(font_spec)
    assert key2 == font_spec
    
    # Test _font_cache_key  
    cache_key = _font_cache_key(font, "test", (255, 255, 255))
    assert cache_key is not None
    assert isinstance(cache_key, tuple)


def test_cache_functionality():
    """Test text rendering cache functionality."""
    # Import cache globals
    from engine.text import LINE_RENDER_CACHE, WORD_RENDER_CACHE, CACHE_ENABLED
    
    # Clear caches first
    LINE_RENDER_CACHE.clear()
    WORD_RENDER_CACHE.clear()
    
    font = get_font('Arial', 16)
    
    # Enable caching
    original_cache_enabled = CACHE_ENABLED
    try:
        import engine.text
        engine.text.CACHE_ENABLED = True
        
        # Test that repeated draws use cache
        surface1 = draw("cached text", font, (255, 255, 255))
        cache_size_1 = len(LINE_RENDER_CACHE)
        
        # Second draw should potentially use cache
        surface2 = draw("cached text", font, (255, 255, 255))
        cache_size_2 = len(LINE_RENDER_CACHE)
        
        # Cache should not shrink
        assert cache_size_2 >= cache_size_1
        
    finally:
        # Restore original cache setting
        engine.text.CACHE_ENABLED = original_cache_enabled


def test_edge_cases():
    """Test edge cases and error conditions."""
    font = get_font('Arial', 16)
    surface = pygame.Surface((100, 50))
    
    # Test with empty text
    surface_empty = draw("", font, (255, 255, 255))
    assert isinstance(surface_empty, pygame.Surface)
    
    lines_empty = split_text("", font, 100)
    width_empty, height_empty = get_total_size(lines_empty, font, 1.2)
    assert width_empty >= 0 and height_empty >= 0
    
    # Test render_line_with_caret with None caret_index
    render_line_with_caret(surface, "test", None, font, (255, 255, 255), None, 10, 10)
    
    # Test very small dimensions
    surface_small = draw("test", font, (255, 255, 255), width=10, height=10)
    assert isinstance(surface_small, pygame.Surface)
    assert surface_small.get_width() == 10
    assert surface_small.get_height() == 10
    
    # Test with special characters
    special_text = "Special: àáâãäå ñ ç €"
    surface_special = draw(special_text, font, (255, 255, 255))
    assert isinstance(surface_special, pygame.Surface)