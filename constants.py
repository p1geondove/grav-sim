import pygame
import os

pygame.font.init()

class Fonts:
    try:
        pygame.Font('AgaveNerdFontMono-Regular.ttf')
        font_name = 'AgaveNerdFontMono-Regular.ttf'
    except:
        font_name = pygame.font.get_default_font()

    small = pygame.Font(font_name, 16)
    medium = pygame.Font(font_name, 24)
    large = pygame.Font(font_name, 32)

class Colors:
    background = pygame.Color('#292929')
    active = pygame.Color('#4cb355')
    inactive = pygame.Color('#a74f4f')
    trail = pygame.Color('#967e1e')
    grid = pygame.Color('#87ddff')
    debug_txt = pygame.Color('#afafaf')

    slider_hori = pygame.Color('grey50')
    slider_vert = pygame.Color('grey70')

    center = pygame.Color('#7d2d8f')
    center2 = pygame.Color('#4e2158')