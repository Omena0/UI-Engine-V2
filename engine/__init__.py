import pygame

pygame.init()
pygame.threads.init(8)

from .window import Window
from .components import *
from . import text
from . import util
from . import theme



