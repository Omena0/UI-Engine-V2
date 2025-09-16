from typing import Optional, Tuple, Union, Any
from .base import ComponentBase
import pygame


class Image(ComponentBase):
    __slots__ = [
        '_image_source', '_original_surface', '_fit_mode', 
        '_size', '_rendered', '_scaling_filter', '_alpha', '_image_cache'
    ]

    def __init__(
        self, 
        parent, 
        pos: Tuple[int, int], 
        image: Union[str, pygame.Surface, Any] = None,
        size: Optional[Tuple[int, int]] = None,
        fit_mode: str = 'fit',  # 'fit', 'fill', 'stretch', 'center', 'tile'
        scaling_filter: str = 'smooth',  # 'smooth', 'nearest'
        alpha: int = 255
    ) -> None:
        """
        Create an Image component.
        
        Args:
            parent: Parent component
            pos: Position (x, y)
            image: Image source - can be:
                - str: Path to image file
                - pygame.Surface: Pygame surface
                - PIL.Image: PIL/Pillow image
                - Any pygame-compatible image object
            size: Size of the component (if None, uses image size or parent remaining space)
            fit_mode: How to fit the image:
                - 'fit': Scale to fit within bounds while maintaining aspect ratio
                - 'fill': Scale to fill bounds while maintaining aspect ratio (may crop)
                - 'stretch': Stretch to exact bounds (may distort)
                - 'center': Center image without scaling
                - 'tile': Tile image to fill bounds
            scaling_filter: Scaling filter ('smooth' or 'nearest')
            alpha: Alpha transparency (0-255)
        """
        self._image_source = image
        self._original_surface = None
        self._fit_mode = fit_mode
        self._rendered = False
        self._scaling_filter = scaling_filter
        self._alpha = alpha
        self._image_cache = {}

        # Load and convert the image
        if image is not None:
            self._original_surface = self._load_and_convert_image(image)
        else:
            self._original_surface = self._create_placeholder_surface()

        # Determine component size
        if size is not None:
            self._size = size
        elif self._original_surface:
            self._size = self._original_surface.get_size()
        else:
            try:
                self._size = (
                    max(0, parent._size[0] - pos[0]),
                    max(0, parent._size[1] - pos[1])
                )
            except Exception:
                self._size = (64, 64)  # fallback size

        super().__init__(parent, pos, self._size)

    def _load_and_convert_image(self, image_source: Union[str, pygame.Surface, Any]) -> pygame.Surface:
        """
        Load and convert various image types to pygame Surface.
        Implements caching for file-based images.
        """
        cache_key = None

        # Handle string (file path)
        if isinstance(image_source, str):
            cache_key = f"file:{image_source}"
            if cache_key in self._image_cache:
                return self._image_cache[cache_key].copy()

            try:
                surface = pygame.image.load(image_source).convert_alpha()
                self._image_cache[cache_key] = surface.copy()
                return surface
            except (pygame.error, FileNotFoundError) as e:
                print(f"Warning: Could not load image '{image_source}': {e}")
                return self._create_placeholder_surface()

        elif isinstance(image_source, pygame.Surface):
            return image_source.convert_alpha()

        else:
            try:
                if not hasattr(image_source, 'mode') or not hasattr(
                    image_source, 'size'
                ):
                    return pygame.image.load(image_source).convert_alpha()
                # Convert PIL Image to pygame Surface
                mode = image_source.mode
                size = image_source.size

                if mode == 'RGBA':
                    surface = pygame.image.fromstring(image_source.tobytes(), size, mode)
                elif mode == 'RGB':
                    surface = pygame.image.fromstring(image_source.tobytes(), size, mode)
                    surface = surface.convert_alpha()
                else:
                    # Convert to RGBA first
                    rgba_image = image_source.convert('RGBA')
                    surface = pygame.image.fromstring(rgba_image.tobytes(), size, 'RGBA')

                return surface.convert_alpha()

            except Exception as e:
                print(f"Warning: Could not convert image: {e}")
                return self._create_placeholder_surface()

    def _create_placeholder_surface(self) -> pygame.Surface:
        """Create a placeholder surface when image loading fails."""
        surface = pygame.Surface((64, 64), pygame.SRCALPHA)
        surface.fill((200, 200, 200, 128))
        pygame.draw.rect(surface, (160, 160, 160), surface.get_rect(), 2)
        # Draw an X to indicate missing image
        pygame.draw.line(surface, (160, 160, 160), (10, 10), (54, 54), 2)
        pygame.draw.line(surface, (160, 160, 160), (54, 10), (10, 54), 2)
        return surface

    @property
    def image(self) -> Union[str, pygame.Surface, Any]:
        """Get the current image source."""
        return self._image_source

    @image.setter
    def image(self, value: Union[str, pygame.Surface, Any]) -> None:
        """Set a new image source."""
        if self._image_source != value:
            self._image_source = value
            if value is not None:
                self._original_surface = self._load_and_convert_image(value)
                self._rendered = False
                self.render()

    @property
    def image_surface(self) -> Optional[pygame.Surface]:
        """Get the original pygame surface (for backward compatibility)."""
        return self._original_surface

    @image_surface.setter
    def image_surface(self, value: Optional[pygame.Surface]) -> None:
        if value is not None:
            self._original_surface = value.copy()
            self._rendered = False
            self.render()

    @property
    def fit_mode(self) -> str:
        return self._fit_mode

    @fit_mode.setter
    def fit_mode(self, value: str) -> None:
        if self._fit_mode != value:
            self._fit_mode = value
            self._rendered = False
            self.render()

    @property
    def alpha(self) -> int:
        return self._alpha

    @alpha.setter
    def alpha(self, value: int) -> None:
        value = max(0, min(255, value))
        if self._alpha != value:
            self._alpha = value
            self._rendered = False
            self.render()

    def _scale_image(self) -> pygame.Surface:
        """Scale the original image based on fit_mode and component size."""
        if not self._original_surface:
            return pygame.Surface(self.size, pygame.SRCALPHA)

        orig_w, orig_h = self._original_surface.get_size()
        comp_w, comp_h = self.size

        if self._fit_mode == 'stretch':
            # Stretch to exact bounds
            if self._scaling_filter == 'smooth':
                scaled = pygame.transform.smoothscale(self._original_surface, (comp_w, comp_h))
            else:
                scaled = pygame.transform.scale(self._original_surface, (comp_w, comp_h))

        elif self._fit_mode == 'fit':
            scaled = self._extracted_from__scale_image_18(comp_w, orig_w, comp_h, orig_h)
        elif self._fit_mode == 'fill':
            scaled = self._extracted_from__scale_image_32(comp_w, orig_w, comp_h, orig_h)
        elif self._fit_mode == 'center':
            # Center image without scaling
            scaled = self._original_surface.copy()

        elif self._fit_mode == 'tile':
            # Tile image to fill bounds
            scaled = pygame.Surface((comp_w, comp_h), pygame.SRCALPHA)
            for x in range(0, comp_w, orig_w):
                for y in range(0, comp_h, orig_h):
                    scaled.blit(self._original_surface, (x, y))
        else:
            # Default to 'fit'
            scaled = self._original_surface.copy()

        return scaled

    # TODO Rename this here and in `_scale_image`
    def _extracted_from__scale_image_32(self, comp_w, orig_w, comp_h, orig_h):
        # Scale to fill bounds while maintaining aspect ratio (may crop)
        scale_x = comp_w / orig_w
        scale_y = comp_h / orig_h
        scale = max(scale_x, scale_y)

        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        if self._scaling_filter == 'smooth':
            temp_scaled = pygame.transform.smoothscale(self._original_surface, (new_w, new_h))
        else:
            temp_scaled = pygame.transform.scale(self._original_surface, (new_w, new_h))

        # Crop to component size
        crop_x = (new_w - comp_w) // 2
        crop_y = (new_h - comp_h) // 2
        return temp_scaled.subsurface((crop_x, crop_y, comp_w, comp_h)).copy()

    # TODO Rename this here and in `_scale_image`
    def _extracted_from__scale_image_18(self, comp_w, orig_w, comp_h, orig_h):
        # Scale to fit within bounds while maintaining aspect ratio
        scale_x = comp_w / orig_w
        scale_y = comp_h / orig_h
        scale = min(scale_x, scale_y)

        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)

        return (
            pygame.transform.smoothscale(self._original_surface, (new_w, new_h))
            if self._scaling_filter == 'smooth'
            else pygame.transform.scale(self._original_surface, (new_w, new_h))
        )

    def render(self) -> None:
        if not self._rendered:
            surf = self.surface
            surf.fill((0, 0, 0, 0))  # Clear surface
            
            if self._original_surface:
                # Scale image according to fit mode
                scaled_image = self._scale_image()
                
                # Apply alpha if needed
                if self._alpha < 255:
                    scaled_image.set_alpha(self._alpha)
                
                # Position the image
                if self._fit_mode == 'center':
                    # Center the image
                    img_w, img_h = scaled_image.get_size()
                    comp_w, comp_h = self.size
                    x = (comp_w - img_w) // 2
                    y = (comp_h - img_h) // 2
                    surf.blit(scaled_image, (x, y))
                else:
                    # For other modes, image should already be sized correctly
                    surf.blit(scaled_image, (0, 0))
            
            self._rendered = True

        # Mark composite as dirty and build blits
        self._mark_composite_dirty()
        self._build_blits()

    def reload_image(self) -> None:
        """Reload the image from the current image source."""
        if not self._image_source:
            return
        try:
            # Clear cache for file-based images to force reload
            if isinstance(self._image_source, str):
                cache_key = f"file:{self._image_source}"
                if cache_key in self._image_cache:
                    del self._image_cache[cache_key]

            self._original_surface = self._load_and_convert_image(self._image_source)
            self._rendered = False
            self.render()
        except Exception as e:
            print(f"Warning: Could not reload image: {e}")


__all__ = ["Image"]
