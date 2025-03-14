from ui_elements import Ball
import numpy as np
from random import randint
from math import pi

SCALE = 12
VX = 0.3471128135672417 * SCALE
VY = 0.532726851767674 * SCALE
SCALE *= SCALE
ARRANGEMENTS = [
    [
        Ball(20, np.array([400, 300]), np.array([ 3, 0])),
        Ball(20, np.array([500, 400]), np.array([ 0, 3])),
        Ball(20, np.array([400, 500]), np.array([-3, 0])),
        Ball(20, np.array([300, 400]), np.array([ 0,-3])),
    ],[
        Ball(pi**0.5/pi*SCALE, np.array([400 - SCALE, 400]), np.array([   VX, -VY])),
        Ball(pi**0.5/pi*SCALE, np.array([400        , 400]), np.array([-2*VX,2*VY])),
        Ball(pi**0.5/pi*SCALE, np.array([400 + SCALE, 400]), np.array([   VX, -VY])),
    ]
]

def get_random(idx=None):
    """ ## Grow a pair

    get a random list of balls from `ARRANGEMENTS`
    """
    if idx is None:
        idx = randint(0, len(ARRANGEMENTS)-1)
    return [ball.copy() for ball in ARRANGEMENTS[idx]], idx