from collections import deque
from . import text
import pygame

fps = 0
fps_history = deque(maxlen=200)
def set_average_fps(fps_sample: float):
    global fps
    fps_history.append(fps_sample)
    fps = sum(fps_history) / len(fps_history) if fps_history else 0

def draw_performance_statistics(surface, clock:pygame.time.Clock) -> None:
    frame_time = clock.get_rawtime()
    font = text.get_font('Arial', 15, bold=True)

    surf = pygame.Surface((75, 50), pygame.SRCALPHA)
    pygame.draw.rect(surf, (50, 50, 50, 200), surf.get_rect(), border_top_left_radius=8)

    fps_text = font.render(f'{fps:.2f} fps', True, (255, 255, 255))
    frame_time_text = font.render(f'({frame_time} ms)', True, (255, 255, 255))

    i = min(1, fps / 2000)

    width = surf.get_width()

    pygame.draw.rect(surf, (200, 200, 200), (width - i * (width-7), 0, 100, 2))
    surf.blit(fps_text, (width - fps_text.get_width() - 5, 5))
    surf.blit(frame_time_text, (width - frame_time_text.get_width() - 3, 22))

    surface.blit(surf, (surface.get_width() - surf.get_width(), surface.get_height() - surf.get_height()))
