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
def draw_performance_statistics(surface, clock:pygame.time.Clock) -> None:
    frame_time = clock.get_rawtime()

    surf = pygame.Surface((75, 50), pygame.SRCALPHA)
    pygame.draw.rect(surf, (50, 50, 50, 200), surf.get_rect(), border_top_left_radius=8)

    avg = get_average_fps()
    fps_text = font.render(f'{avg:.2f} fps', True, (245, 245, 246))
    frame_time_text = font.render(f'({frame_time} ms)', True, (245, 245, 246))

    i = min(1, avg / 2000)

    width = surf.get_width()

    pygame.draw.rect(surf, (200, 200, 200), (width - i * (width-7), 0, 100, 2))
    surf.blit(fps_text, (width - fps_text.get_width() - 5, 5))
    surf.blit(frame_time_text, (width - frame_time_text.get_width() - 3, 22))

    surface.blit(surf, (surface.get_width() - surf.get_width(), surface.get_height() - surf.get_height()))

