"""Tests for Text core module."""

import pytest
import pygame
from unittest.mock import Mock, patch
from engine import text


# Ensure pygame is initialized before any test class
def ensure_pygame_ready():
    """Ensure pygame and font module are properly initialized."""
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()


class TestTextModule:
    """Test suite for Text core module."""

    @pytest.fixture
    def setup_pygame(self):
        """Setup pygame for testing."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        yield
        # Don't quit pygame between tests to avoid font invalidation

    def test_get_font_basic(self, setup_pygame):
        """Test basic font creation."""
        ensure_pygame_ready()
        font = text.get_font("Arial", 16)
        assert font is not None
        assert isinstance(font, pygame.font.Font)

    def test_get_font_caching(self, setup_pygame):
        """Test font caching functionality."""
        ensure_pygame_ready()
        # Same parameters should return same object (cached)
        font1 = text.get_font("Arial", 16)
        font2 = text.get_font("Arial", 16)
        assert font1 is font2

    def test_get_font_different_sizes(self, setup_pygame):
        """Test different font sizes."""
        ensure_pygame_ready()
        font_16 = text.get_font("Arial", 16)
        font_24 = text.get_font("Arial", 24)
        font_12 = text.get_font("Arial", 12)
        
        assert font_16 is not font_24
        assert font_16 is not font_12
        assert font_24 is not font_12

    def test_get_font_styles(self, setup_pygame):
        """Test font styles (bold, italic)."""
        ensure_pygame_ready()
        font_normal = text.get_font("Arial", 16)
        font_bold = text.get_font("Arial", 16, bold=True)
        font_italic = text.get_font("Arial", 16, italic=True)
        font_bold_italic = text.get_font("Arial", 16, bold=True, italic=True)
        
        assert font_normal is not font_bold
        assert font_normal is not font_italic
        assert font_normal is not font_bold_italic
        assert font_bold is not font_italic
        assert font_bold is not font_bold_italic
        assert font_italic is not font_bold_italic

    def test_get_font_different_families(self, setup_pygame):
        """Test different font families."""
        ensure_pygame_ready()
        arial = text.get_font("Arial", 16)
        times = text.get_font("Times New Roman", 16)
        courier = text.get_font("Courier New", 16)
        
        # Different families should return different font objects
        assert arial is not times
        assert arial is not courier
        assert times is not courier

    def test_get_font_edge_cases(self, setup_pygame):
        """Test edge cases for font creation."""
        ensure_pygame_ready()
        # Very small font
        tiny_font = text.get_font("Arial", 6)
        assert tiny_font is not None
        
        # Large font
        large_font = text.get_font("Arial", 72)
        assert large_font is not None
        
        # Non-existent font family (should fallback)
        fallback_font = text.get_font("NonExistentFont", 16)
        assert fallback_font is not None

    def test_font_rendering_functionality(self, setup_pygame):
        """Test that fonts can actually render text."""
        ensure_pygame_ready()
        font = text.get_font("Arial", 16)
        
        # Test rendering simple text
        surface = font.render("Hello World", True, (0, 0, 0))
        assert surface is not None
        assert isinstance(surface, pygame.Surface)
        assert surface.get_width() > 0
        assert surface.get_height() > 0

    def test_font_rendering_different_text(self, setup_pygame):
        """Test rendering different types of text."""
        ensure_pygame_ready()
        font = text.get_font("Arial", 16)
        
        test_texts = [
            "",  # Empty string
            "A",  # Single character
            "Hello World",  # Normal text
            "1234567890",  # Numbers
            "!@#$%^&*()",  # Special characters
            "Unicode: αβγ 中文 🚀",  # Unicode
        ]
        
        for test_text in test_texts:
            try:
                surface = font.render(test_text, True, (0, 0, 0))
                assert surface is not None
                assert isinstance(surface, pygame.Surface)
            except Exception as e:
                pytest.fail(f"Font rendering failed for text '{test_text}': {e}")

    def test_font_rendering_colors(self, setup_pygame):
        """Test font rendering with different colors."""
        ensure_pygame_ready()
        font = text.get_font("Arial", 16)
        
        colors = [
            (0, 0, 0),      # Black
            (255, 255, 255), # White
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (128, 128, 128), # Gray
        ]
        
        for color in colors:
            try:
                surface = font.render("Test", True, color)
                assert surface is not None
                assert isinstance(surface, pygame.Surface)
            except Exception as e:
                pytest.fail(f"Font rendering failed for color {color}: {e}")

    def test_font_antialiasing(self, setup_pygame):
        """Test font rendering with and without antialiasing."""
        ensure_pygame_ready()
        font = text.get_font("Arial", 16)
        
        # Test with antialiasing
        surface_aa = font.render("Test", True, (0, 0, 0))
        assert surface_aa is not None
        
        # Test without antialiasing
        surface_no_aa = font.render("Test", False, (0, 0, 0))
        assert surface_no_aa is not None
        
        # Both should be valid surfaces
        assert isinstance(surface_aa, pygame.Surface)
        assert isinstance(surface_no_aa, pygame.Surface)

    def test_font_cache_size_limits(self, setup_pygame):
        """Test font cache behavior with many fonts."""
        ensure_pygame_ready()
        # Create many different font configurations
        fonts = []
        for size in range(8, 50, 2):  # Various sizes
            font = text.get_font("Arial", size)
            fonts.append(font)
            assert font is not None

        # All fonts should be valid
        for font in fonts:
            assert isinstance(font, pygame.font.Font)

    def test_font_metrics(self, setup_pygame):
        """Test font metrics and measurements."""
        ensure_pygame_ready()
        font = text.get_font("Arial", 16)
        
        # Test getting text size
        text_to_measure = "Hello World"
        width, height = font.size(text_to_measure)
        assert width > 0
        assert height > 0
        
        # Test font height
        font_height = font.get_height()
        assert font_height > 0
        
        # Test line spacing
        line_spacing = font.get_linesize()
        assert line_spacing > 0

    def test_font_performance(self, setup_pygame):
        """Test font caching performance."""
        ensure_pygame_ready()
        # First call should create the font
        font1 = text.get_font("Arial", 16)
        
        # Subsequent calls should be fast (cached)
        for _ in range(100):
            font_cached = text.get_font("Arial", 16)
            assert font_cached is font1  # Should be exact same object
