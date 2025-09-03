import pygame

# Ensure pygame-ce is being used
if not hasattr(pygame, 'IS_CE') or not pygame.IS_CE:
    raise ImportError(
        "This UI engine requires pygame-ce (Community Edition). "
        "Please install it with: pip install pygame-ce"
    )

pygame.init()

from .window import Window
from .components import *
from . import text
from . import util
from . import theme

