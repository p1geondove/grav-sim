from __future__ import annotations

import pygame
from pygame.locals import *
from math import pi
from util import Vec2

import const
import random

class Ball:
    def __init__(self, radius:float = None, position:Vec2 = None, velocity:Vec2 = None):
        if radius is None:
            self.radius = float(random.uniform(5,50))
        else: self.radius = radius

        if position is None:
            self.pos = Vec2(random.uniform(0, 500), random.uniform(0, 500))
        else: self.pos = Vec2(position)

        if velocity is None:
            self.vel = Vec2(random.uniform(-1, 1), random.uniform(-1, 1))
        else: self.vel = Vec2(velocity)

        self.id = random.randint(1,1000)
        self.mass = pi*self.radius**2
        self.acc = Vec2(0)
        self.prev_pos = self.pos.copy()
        
        self.pressed_left = False
        self.pressed_right = False
        self.pressed_ctrl = False
        self.hover = False
        self._radius = self.radius
        self.surface = pygame.Surface(Vec2(self.radius*2+1).tuple(), SRCALPHA)
        self.color = pygame.Color.from_hsla(random.uniform(0,360), 100, 75, 100)
        pygame.draw.aacircle(self.surface, self.color, (self.radius, self.radius), self.radius, 2)

    def __repr__(self):
        return f'Ball r:{self.radius} pos:{self.pos.x:2f}|{self.pos.y:2f} vel:{self.vel.x:2f}|{self.vel.y:2f}'

    @property
    def radius(self) -> float:
        return self._radius
    
    @radius.setter
    def radius(self, val:float):
        self._radius = val
        self.mass = pi*val**2

    def collide(self, other: Ball): # die implementation hält die auseinander, aber paare fangen an sich immer schneller und schneller zu drehen
        impact_vector = other.pos - self.pos
        distance_squared = impact_vector.magnitude_squared()
        combined_radius = self.radius + other.radius

        if distance_squared > combined_radius ** 2: return

        distance = impact_vector.magnitude()
        overlap = combined_radius - distance
        if distance == 0:
            impact_vector = Vec2(1, 0)
            overlap = combined_radius
        else:
            impact_vector = impact_vector.normalize()

        self.pos -= impact_vector * overlap / 2
        other.pos += impact_vector * overlap / 2

        mass1 = self.radius ** 2 
        mass2 = other.radius ** 2

        v1 = self.vel
        v2 = other.vel
        self.vel = v1 - (2 * mass2 / (mass1 + mass2)) * (v1 - v2).dot(impact_vector) * impact_vector * .999
        other.vel = v2 - (2 * mass1 / (mass1 + mass2)) * (v2 - v1).dot(impact_vector) * impact_vector * .999

    def handle_event(self, event, grid_size:int, camera):
        calls = []

        if event.type == MOUSEBUTTONDOWN:
            if self.hover:
                if event.button == 1:
                    self.pressed_left = True
                elif event.button == 3:
                    self.pressed_right = True

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed_left = False
            elif event.button == 3:
                self.pressed_right = False

        elif event.type == MOUSEMOTION:
            self.hover = Vec2(camera.to_world_pos(event.pos) - self.pos).magnitude() < self.radius

            if self.pressed_left and self.pressed_right:
                calls.append('dragged_ball')
                old = self.radius
                if self.pressed_ctrl:
                    x, y = self.pos - camera.to_world_pos(event.pos)
                    x = x - x % grid_size
                    y = y - y % grid_size
                    self.radius = Vec2(x,y).magnitude()
                else:
                    self.radius += sum(Vec2(event.rel)*camera.zoom_val)

                self.radius = min(max(1,self.radius),10000)
                if old != self.radius:
                    self.draw()
                
            elif self.pressed_left:
                calls.append('dragged_ball')
                if self.pressed_ctrl:
                    x, y = camera.to_world_pos(event.pos) + Vec2(grid_size/2)
                    x = x - x % grid_size
                    y = y - y % grid_size
                    self.pos = Vec2(x,y)
                else:
                    self.pos += Vec2(event.rel) * camera.zoom_val

            elif self.pressed_right:
                calls.append('dragged_ball')
                if self.pressed_ctrl:
                    x, y = self.pos - camera.to_world_pos(event.pos)
                    x = x - x % grid_size
                    y = y - y % grid_size
                    self.vel = -Vec2(x,y) / 30
                else:
                    self.vel += Vec2(event.rel) * camera.zoom_val / 30

        elif event.type == KEYDOWN:
            if event.key == K_r and self.hover:
                self.vel = Vec2(0)
                calls.append('pressed_r')
            
            if event.key == K_LCTRL:
                self.pressed_ctrl = True

        elif event.type == KEYUP:
            if event.key == K_LCTRL:
                self.pressed_ctrl = False

        return calls

    def copy(self):
        b = Ball(self.radius, self.pos, self.vel)
        b.color = self.color
        return b

class Button:
    def __init__(self, pos:pygame.Rect, text:str = 'button', color:pygame.Color = None):
        self.pos = Vec2(pos)
        self.text = text
        if color:
            self.color = color
        else:
            self.color = 'white'
        self.font = const.Fonts.large
        self.surface = self.font.render(text, True, self.color)
        self.draw()

    def handle_event(self, event:pygame.Event):
        calls = []
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.surface.get_rect().move(self.pos.tuple()).collidepoint(event.pos):
                calls.append('pressed_button')
        return calls
    
    def draw(self):
        self.surface = self.font.render(self.text, True, self.color)

class Slider:
    def __init__(self, name:str, start:float, end:float, rect:pygame.Rect):
        self.name = name
        self.start = start
        self.end = end
        self.rect = pygame.FRect(rect)
        self.val = (end - start) / 2
        self.pressed = False
        self.size_hori = 2
        self.size_vert = 4
        self.surface = pygame.Surface(self.rect.size)
        self.draw()

    def draw(self):
        pos_x = (self.val - self.start) / (self.end - self.start) * (self.rect.width - self.size_vert*2)
        rect_hori = pygame.Rect(self.size_vert, self.rect.height/2-self.size_hori, self.rect.width-self.size_vert*2, self.size_hori*2)
        rect_vert = pygame.Rect(pos_x, 0, self.size_vert*2, self.rect.height)
        text = const.Fonts.small.render(f'{self.name}: {self.val:.4f}', True, const.Colors.text)
        self.surface = pygame.Surface((self.rect.size + Vec2(text.width,0)).tuple(), SRCALPHA)
        self.surface.blit(text,(self.rect.width, self.rect.height/2-text.height/2))
        pygame.draw.rect(self.surface, const.Colors.slider_hori, rect_hori, 0, self.size_hori)
        pygame.draw.rect(self.surface, const.Colors.slider_vert, rect_vert, 0, int(self.size_vert*0.7))
    
    def handle_event(self, event:pygame.Event):
        if event.type == MOUSEBUTTONDOWN:
            pos_x = (self.val - self.start) / (self.end - self.start) * (self.rect.width - self.size_vert*2)
            rect = pygame.Rect(pos_x, 0, self.size_vert*2, self.rect.height).move(self.rect.topleft)
            pygame.draw.rect(self.surface, 'red', rect, 1)
            if self.rect.collidepoint(event.pos):
                self.pressed = event.pos[0], self.val

        elif event.type == MOUSEBUTTONUP:
            self.pressed = False
        
        elif event.type == MOUSEMOTION and self.pressed:
            self.val = (self.end-self.start) / self.rect.width * (event.pos[0]-self.pressed[0]) + self.pressed[1]
            self.val = min(max(self.start, self.val), self.end)
            self.draw()
            return ['draw']

    def copy(self):
        slider = Slider(self.rect, self.start, self.end, self.name)
        slider.val = self.val
        return slider
