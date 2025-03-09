from __future__ import annotations
import os
import sys
from mpmath import mp, mpf

mp.dps = 10

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def points_on_grid(grid:float, radius:float, pos:Vec2):
    near = lambda x : x - x % grid + grid
    left = near(pos.x - radius)
    right = near(pos.x + radius)
    while left < right:
        dx = abs(left - pos.x)
        height = (radius**2 - dx**2) ** 0.5
        bottom = near(pos.y - height)
        top = near(pos.y + height)
        while bottom < top:
            yield Vec2(left,bottom)
            bottom += grid
        left += grid

class Vec2:
    def __init__(self, x=0.0, y=None):
        if isinstance(x, tuple):
            self.x = mpf(x[0])
            self.y = mpf(x[1])
        elif isinstance(x, list):
            self.x = mpf(x[0])
            self.y = mpf(x[1])
        elif isinstance(x, Vec2):
            self.x = mpf(x.x)
            self.y = mpf(x.y)
        elif y is None:
            self.x = mpf(x)
            self.y = mpf(x)
        else:
            self.x = mpf(x)
            self.y = mpf(y)
        
    def __repr__(self):
        return f'<{self.x,self.y}>'
    
    def __add__(self, other:Vec2):
        if isinstance(other, tuple):
            return Vec2(self.x + other[0], self.y + other[1])
        elif isinstance(other, list):
            return Vec2(self.x + other[0], self.y + other[1])
        elif isinstance(other, int):
            return Vec2(self.x + other, self.y + other)
        elif isinstance(other, float):
            return Vec2(self.x + other, self.y + other)
        elif isinstance(other, Vec2):
            return Vec2(self.x + other.x, self.y + other.y)
        else:
            raise NotImplementedError
    
    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, tuple):
            return Vec2(self.x - other[0], self.y - other[1])
        elif isinstance(other, list):
            return Vec2(self.x - other[0], self.y - other[1])
        elif isinstance(other, int):
            return Vec2(self.x - other, self.y - other)
        elif isinstance(other, float):
            return Vec2(self.x - other, self.y - other)
        elif isinstance(other, Vec2):
            return Vec2(self.x - other.x, self.y - other.y)
        else:
            raise NotImplementedError

    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar):
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def dot(self, other:Vec2):
        return self.x * other.x + self.y * other.y
    
    def magnitude_squared(self):
        return self.x * self.x + self.y * self.y
    
    def magnitude(self):
        return self.magnitude_squared() ** 0.5
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return self / mag
        return Vec2(0, 0)

    def distance_to(self, other):
        if isinstance(other, Vec2):
            dx = other.x - self.x
            dy = other.y - self.y
            return (dx**2 + dy**2)**0.5

    def copy(self):
        return Vec2(self.x, self.y)
    
    def tuple(self):
        return float(self.x), float(self.y)
