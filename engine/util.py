from collections import deque
from .text import get_font
import pygame

average_fps = 0

def get_average_fps() -> float:
    global average_fps
    average_fps = sum(fps_history) / len(fps_history) if fps_history else 1.0
    return average_fps

fps_history = deque(maxlen=100)
def set_average_fps(fps: float):
    fps_history.append(fps)

font = get_font('Arial', 15, bold=True)
# Cache for performance statistics
_cached_stats_surface = None
_last_stats_update = 0
_text_cache = {}  # Cache for rendered text (for #7: text rendering optimization)

def cached_render(font, text, color):
    """Cache rendered text to avoid redundant rendering operations."""
    cache_key = (id(font), text, tuple(color))
    if cache_key not in _text_cache:
        _text_cache[cache_key] = font.render(text, True, color)

        # Prevent unlimited growth of the cache
        if len(_text_cache) > 100:
            # Remove oldest entry
            try:
                _text_cache.pop(next(iter(_text_cache)))
            except Exception:
                # Just continue if there's an issue clearing cache
                pass

    return _text_cache[cache_key]

def draw_performance_statistics(surface, dt) -> None:
    global _cached_stats_surface, _last_stats_update

    current_time = pygame.time.get_ticks()

    # Only update stats every 40ms (25Hz)
    if _cached_stats_surface is None or (current_time - _last_stats_update) > 40:
        _last_stats_update = current_time

        surf = pygame.Surface((75, 50), pygame.SRCALPHA)
        pygame.draw.rect(surf, (50, 50, 50, 200), surf.get_rect(), border_top_left_radius=8)

        avg = get_average_fps()
        # Use cached text rendering
        fps_text = cached_render(font, f'{avg:.2f} fps', (245, 245, 246))
        frame_time_text = cached_render(font, f'({dt:.2f} ms)', (245, 245, 246))

        i = min(1, avg / 2000)

        width = surf.get_width()

        pygame.draw.rect(surf, (200, 200, 200), (width - i * (width-7), 0, 100, 2))
        surf.blit(fps_text, (width - fps_text.get_width() - 5, 5))
        surf.blit(frame_time_text, (width - frame_time_text.get_width() - 3, 22))
        
        # Convert surface for faster blitting
        try:
            _cached_stats_surface = surf.convert_alpha()
        except Exception:
            _cached_stats_surface = surf

    # Always blit the cached surface
    surface.blit(_cached_stats_surface, (surface.get_width() - _cached_stats_surface.get_width(), surface.get_height() - _cached_stats_surface.get_height()))

