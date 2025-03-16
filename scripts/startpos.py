import numpy as np
import random
from math import pi
from scripts.ui_elements import Ball
from scripts.const import Var

def get_figure_8(scale:float): # figure 8 orbit (∞). Thanks to Faustino Palmero Ramos (https://www.maths.ed.ac.uk/~ateckent/vacation_reports/Report_Faustino.pdf)
    vx = 0.3471128135672417 * scale # these values are copy pasted from the paper
    vy = 0.532726851767674 * scale  # and scaled up to match the default 800,800 winsize
    scale *= scale                  # the positions scale needs to be squared to the velocity
    mass = pi**0.5/pi * scale       # pi**0.5/pi is the mass of radius 1

    return [
        Ball(mass, np.array([400 - scale, 400]), np.array([   vx, -vy])),
        Ball(mass, np.array([400        , 400]), np.array([-2*vx,2*vy])),
        Ball(mass, np.array([400 + scale, 400]), np.array([   vx, -vy])),
    ]

def get_ngon(amount:int):
    """
    Create a regular n-gon orbit with n balls using NumPy vectorization.
    """
    if amount < 2: return []
    mass = 50
    radius = 250
    center = Var.window_size/2
    velocity_scale = amount * 1.25
    angles = 2 * pi * np.arange(amount) / amount
    positions = center + radius * np.column_stack((np.cos(angles), np.sin(angles)))
    velocities = velocity_scale * np.column_stack((-np.sin(angles), np.cos(angles)))
    return [Ball(mass, pos, vel) for pos, vel in zip(positions, velocities)]

def get_random():
    """ ## Grow a pair

    Get a list of balls in a random orbit
    """
    arrangements = [get_figure_8(13)] + [get_ngon(x) for x in range(2,10)]
    return random.choice(arrangements)