import pygame
from util import resource_path
import numpy as np

pygame.font.init()
class Fonts:
    try:
        font_name = resource_path('assets/AgaveNerdFontMono-Regular.ttf')
        pygame.Font(font_name)
    except:
        font_name = pygame.font.get_default_font()

    small = pygame.Font(font_name, 16)
    medium = pygame.Font(font_name, 24)
    large = pygame.Font(font_name, 32)

class Colors:
    # Button
    active = pygame.Color('#4cb355')
    inactive = pygame.Color('#a74f4f')

    # Slider
    slider_hori = pygame.Color('grey50')
    slider_vert = pygame.Color('grey70')

    # Center of gravity
    center = pygame.Color('#7d2d8f')
    center2 = pygame.Color('#4e2158')

    # Energy graph colors
    kinetic_energy = pygame.Color('#2ecc71')
    total_energy = pygame.Color('#3498db')
    potential_energy = pygame.Color('#e74c3c')
    area_kinetik = pygame.Color('#008822')
    area_total = pygame.Color('#00437a')
    area_potential = pygame.Color('#880000')

    area_kinetik.a = 50
    area_total.a = 50
    area_potential.a = 50
    
    # Various
    background = pygame.Color('#292929')
    vel_vector = pygame.Color('#4e9c60')
    grid = pygame.Color('#5886bb')
    text = pygame.Color('#afafaf')

class Var:
    window_size = np.array((800, 800)) # standard window size in pixel
    slider_size = (100, 20) # x and y size of the sliders in pixel
    button_font = Fonts.large # font for the buttons
    framerate_limit = 150 # fps limit, because i feel like its a good idea idk...
    steps_per_draw = 20 # amt of physics steps. helps boost performance
    dtype = float # precision control hopefully
    G = 1 # universal gravitational standard
    cicrcle_lightness = 75 # l value from hsLa used for making circle a nice pastel color
    dampening = 0.999 # used in elastic collision only
    pad = 5 # 5 pixel padding for ui elements (except ball ofc)
    energy_graph_size = np.array((200, 150))
