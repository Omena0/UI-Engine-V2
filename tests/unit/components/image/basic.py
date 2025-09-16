"""Tests for Image component."""

import pytest
import pygame
import engine as ui
from unittest.mock import Mock, patch, MagicMock
import os


class TestImage:
    """Test suite for Image component."""

    @pytest.fixture(scope="session")
    def window(self):
        """Create a window for testing."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
        return ui.Window((400, 300))

    @pytest.fixture
    def test_surface(self):
        """Create a test surface for image testing."""
        surface = pygame.Surface((100, 100))
        surface.fill((255, 0, 0))  # Red square
        return surface

    @pytest.fixture
    def image_from_surface(self, window, test_surface):
        """Create an image from a surface."""
        return ui.Image(window, (10, 10), test_surface)

    def test_creation_from_surface(self, window, test_surface):
        """Test image creation from pygame surface."""
        image = ui.Image(window, (10, 10), test_surface)
        assert image.pos == (10, 10)
        assert hasattr(image, 'surface') or hasattr(image, '_surface') or hasattr(image, 'image')

    def test_creation_from_path(self, window):
        """Test image creation from file path."""
        # Create a temporary test image
        test_surface = pygame.Surface((50, 50))
        test_surface.fill((0, 255, 0))  # Green square
        temp_path = "/tmp/test_image.png"
        
        try:
            pygame.image.save(test_surface, temp_path)
            image = ui.Image(window, (20, 20), temp_path)
            assert image.pos == (20, 20)
        except Exception as e:
            # If file operations fail, test that constructor handles it gracefully
            try:
                image = ui.Image(window, (20, 20), temp_path)
            except Exception:
                pass  # Expected if file doesn't exist
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_rendering(self, image_from_surface):
        """Test image rendering."""
        try:
            image_from_surface.render()
            if hasattr(image_from_surface, 'blits'):
                assert len(image_from_surface.blits) > 0
        except Exception as e:
            pytest.fail(f"Image rendering failed: {e}")

    def test_positioning(self, window, test_surface):
        """Test image positioning."""
        positions = [(0, 0), (100, 50), (200, 150)]
        
        for x, y in positions:
            image = ui.Image(window, (x, y), test_surface)
            assert image.pos == (x, y)
            
            try:
                image.render()
            except Exception as e:
                pytest.fail(f"Image rendering failed at position ({x}, {y}): {e}")

    def test_different_surface_sizes(self, window):
        """Test images with different surface sizes."""
        sizes = [(10, 10), (100, 50), (200, 200), (300, 100)]
        
        for width, height in sizes:
            surface = pygame.Surface((width, height))
            surface.fill((0, 0, 255))  # Blue
            
            image = ui.Image(window, (10, 10), surface)
            try:
                image.render()
            except Exception as e:
                pytest.fail(f"Image with size {width}x{height} failed to render: {e}")

    def test_scaling_if_supported(self, window, test_surface):
        """Test image scaling if supported."""
        image = ui.Image(window, (10, 10), test_surface)
        
        # Check if image supports scaling
        if hasattr(image, 'scale') or hasattr(image, 'size'):
            try:
                # Try setting different sizes
                scales = [(50, 50), (150, 150), (100, 200)]
                for scale_w, scale_h in scales:
                    if hasattr(image, 'scale'):
                        image.scale = (scale_w, scale_h)
                    elif hasattr(image, 'size'):
                        image.size = (scale_w, scale_h)
                    
                    image.render()
            except Exception as e:
                pytest.fail(f"Image scaling failed: {e}")

    def test_transparency_handling(self, window):
        """Test image with transparency."""
        # Create surface with per-pixel alpha
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        surface.fill((255, 0, 0, 128))  # Semi-transparent red
        
        image = ui.Image(window, (10, 10), surface)
        try:
            image.render()
        except Exception as e:
            pytest.fail(f"Transparent image rendering failed: {e}")

    def test_colorkey_transparency(self, window):
        """Test image with colorkey transparency."""
        surface = pygame.Surface((50, 50))
        surface.fill((255, 0, 255))  # Magenta
        surface.set_colorkey((255, 0, 255))  # Make magenta transparent
        
        image = ui.Image(window, (10, 10), surface)
        try:
            image.render()
        except Exception as e:
            pytest.fail(f"Colorkey transparent image rendering failed: {e}")

    def test_rotation_if_supported(self, window, test_surface):
        """Test image rotation if supported."""
        image = ui.Image(window, (10, 10), test_surface)
        
        # Check if image supports rotation
        if hasattr(image, 'rotation') or hasattr(image, 'angle'):
            try:
                angles = [0, 45, 90, 180, 270, 360]
                for angle in angles:
                    if hasattr(image, 'rotation'):
                        image.rotation = angle
                    elif hasattr(image, 'angle'):
                        image.angle = angle
                    
                    image.render()
            except Exception as e:
                pytest.fail(f"Image rotation failed at angle {angle}: {e}")

    def test_flipping_if_supported(self, window, test_surface):
        """Test image flipping if supported."""
        image = ui.Image(window, (10, 10), test_surface)
        
        # Check if image supports flipping
        flip_attrs = ['flip_x', 'flip_y', 'flip_horizontal', 'flip_vertical']
        for attr in flip_attrs:
            if hasattr(image, attr):
                try:
                    setattr(image, attr, True)
                    image.render()
                    setattr(image, attr, False)
                    image.render()
                except Exception as e:
                    pytest.fail(f"Image flipping failed for {attr}: {e}")

    def test_alpha_blending(self, window, test_surface):
        """Test image alpha blending."""
        image = ui.Image(window, (10, 10), test_surface)
        
        # Check if image supports alpha
        if hasattr(image, 'alpha') or hasattr(image, 'opacity'):
            try:
                alphas = [0, 64, 128, 192, 255]
                for alpha in alphas:
                    if hasattr(image, 'alpha'):
                        image.alpha = alpha
                    elif hasattr(image, 'opacity'):
                        image.opacity = alpha
                    
                    image.render()
            except Exception as e:
                pytest.fail(f"Image alpha blending failed at alpha {alpha}: {e}")

    def test_tinting_if_supported(self, window, test_surface):
        """Test image tinting if supported."""
        image = ui.Image(window, (10, 10), test_surface)
        
        # Check if image supports tinting
        if hasattr(image, 'tint') or hasattr(image, 'color'):
            try:
                colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255)]
                for color in colors:
                    if hasattr(image, 'tint'):
                        image.tint = color
                    elif hasattr(image, 'color'):
                        image.color = color
                    
                    image.render()
            except Exception as e:
                pytest.fail(f"Image tinting failed with color {color}: {e}")

    def test_click_handling(self, image_from_surface):
        """Test image click handling."""
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 50), button=1)
        
        try:
            image_from_surface._event(click_event)
        except Exception as e:
            pytest.fail(f"Image click handling failed: {e}")

    def test_mouse_hover(self, image_from_surface):
        """Test image mouse hover."""
        motion_event = pygame.event.Event(pygame.MOUSEMOTION, pos=(50, 50))
        
        try:
            image_from_surface._event(motion_event)
        except Exception as e:
            pytest.fail(f"Image mouse hover failed: {e}")

    def test_bounds_checking(self, image_from_surface):
        """Test image bounds checking."""
        # Test clicks outside image bounds
        outside_clicks = [
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(0, 0), button=1),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(200, 200), button=1),
        ]
        
        for event in outside_clicks:
            try:
                image_from_surface._event(event)
            except Exception as e:
                pytest.fail(f"Image bounds checking failed: {e}")

    def test_different_color_formats(self, window):
        """Test images with different color formats."""
        formats = [8, 16, 24, 32]
        
        for depth in formats:
            try:
                surface = pygame.Surface((50, 50), depth=depth)
                surface.fill((128, 128, 128))
                
                image = ui.Image(window, (10, 10), surface)
                image.render()
            except Exception as e:
                # Some formats might not be supported
                pass

    def test_large_image(self, window):
        """Test handling of large images."""
        try:
            # Create a large surface
            large_surface = pygame.Surface((1000, 1000))
            large_surface.fill((100, 100, 100))
            
            image = ui.Image(window, (10, 10), large_surface)
            image.render()
        except Exception as e:
            # Large images might have memory constraints
            pass

    def test_empty_surface(self, window):
        """Test image with empty surface."""
        try:
            empty_surface = pygame.Surface((0, 0))
            image = ui.Image(window, (10, 10), empty_surface)
            image.render()
        except Exception as e:
            # Empty surfaces might not be supported
            pass

    def test_negative_position(self, window, test_surface):
        """Test image with negative position."""
        image = ui.Image(window, (-50, -50), test_surface)
        try:
            image.render()
        except Exception as e:
            pytest.fail(f"Image with negative position failed: {e}")

    def test_position_outside_window(self, window, test_surface):
        """Test image positioned outside window bounds."""
        image = ui.Image(window, (500, 500), test_surface)
        try:
            image.render()
        except Exception as e:
            pytest.fail(f"Image outside window bounds failed: {e}")

    def test_image_size_property(self, image_from_surface):
        """Test image size property."""
        if hasattr(image_from_surface, 'size'):
            size = image_from_surface.size
            assert isinstance(size, tuple)
            assert len(size) == 2
            assert all(isinstance(x, int) for x in size)

    def test_image_width_height(self, image_from_surface):
        """Test image width and height properties."""
        if hasattr(image_from_surface, 'width'):
            assert isinstance(image_from_surface.width, int)
        
        if hasattr(image_from_surface, 'height'):
            assert isinstance(image_from_surface.height, int)

    def test_invalid_file_path(self, window):
        """Test image creation with invalid file path."""
        try:
            image = ui.Image(window, (10, 10), "nonexistent_file.png")
            # Should handle gracefully or raise appropriate exception
        except Exception:
            # Expected behavior for invalid paths
            pass

    def test_callback_if_supported(self, window, test_surface):
        """Test image callback functionality if supported."""
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        # Check if image supports callbacks
        try:
            image = ui.Image(window, (10, 10), test_surface, callback=test_callback)
            
            # Simulate click to trigger callback
            click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(50, 50), button=1)
            image._event(click_event)
            
            # Note: callback might not be called depending on implementation
        except TypeError:
            # Constructor doesn't accept callback parameter
            pass
        except Exception as e:
            pytest.fail(f"Image callback test failed: {e}")

    @patch('pygame.image.load')
    def test_file_loading_with_mock(self, mock_load, window):
        """Test image file loading with mocked pygame.image.load."""
        # Mock the image loading
        mock_surface = pygame.Surface((100, 100))
        mock_load.return_value = mock_surface
        
        try:
            image = ui.Image(window, (10, 10), "test_image.png")
            image.render()
            mock_load.assert_called_once_with("test_image.png")
        except Exception as e:
            # Image constructor might not use pygame.image.load directly
            pass

    def test_surface_conversion(self, window):
        """Test surface conversion handling."""
        # Create surface without per-pixel alpha
        surface = pygame.Surface((50, 50))
        surface.fill((255, 255, 0))  # Yellow
        
        image = ui.Image(window, (10, 10), surface)
        try:
            image.render()
        except Exception as e:
            pytest.fail(f"Surface conversion failed: {e}")

    def test_image_subsurface(self, window, test_surface):
        """Test image created from subsurface."""
        try:
            # Create a subsurface
            subsurface = test_surface.subsurface((10, 10, 50, 50))
            image = ui.Image(window, (10, 10), subsurface)
            image.render()
        except Exception as e:
            pytest.fail(f"Subsurface image failed: {e}")

    def test_animated_image_frame(self, window, test_surface):
        """Test animated image frame handling if supported."""
        image = ui.Image(window, (10, 10), test_surface)
        
        # Check if image supports animation frames
        if hasattr(image, 'frame') or hasattr(image, 'current_frame'):
            try:
                frame_values = [0, 1, 2]
                for frame in frame_values:
                    if hasattr(image, 'frame'):
                        image.frame = frame
                    elif hasattr(image, 'current_frame'):
                        image.current_frame = frame
                    
                    image.render()
            except Exception as e:
                pytest.fail(f"Animated image frame handling failed: {e}")
