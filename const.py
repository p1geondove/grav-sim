import os
import sys
import pygame

pygame.font.init()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class Sizes:
    slider = pygame.Vector2(100, 20)
    
class Fonts:
    try:
        font_name = resource_path('AgaveNerdFontMono-Regular.ttf')
        pygame.Font(font_name)
    except:
        font_name = pygame.font.get_default_font()

    small = pygame.Font(font_name, 16)
    medium = pygame.Font(font_name, 24)
    large = pygame.Font(font_name, 32)

class Colors:
    background = pygame.Color('#292929')
    active = pygame.Color('#4cb355')
    inactive = pygame.Color('#a74f4f')
    trail = pygame.Color('#5e94d1')
    vel_vector = pygame.Color('#4e9c60')
    grid = pygame.Color('#5886bb')
    text = pygame.Color('#afafaf')

    slider_hori = pygame.Color('grey50')
    slider_vert = pygame.Color('grey70')

    center = pygame.Color('#7d2d8f')
    center2 = pygame.Color('#4e2158')
