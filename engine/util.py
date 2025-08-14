import pygame

fontCache = {}
def get_font(font_name, size, bold=False, italic=False):
    key = (font_name, size, bold, italic)
    if key not in fontCache:
        font = pygame.font.SysFont(font_name, size, bold=bold, italic=italic)
        fontCache[key] = font
    return fontCache[key]

