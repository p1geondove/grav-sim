from __future__ import annotations

import pygame
from pygame.locals import *
from pygame import Vector2 as Vec2

import constants
import random

class Ball:
    def __init__(self, radius:float = None, position:Vec2 = None, velocity:Vec2 = None):
        if radius is None:
            self.radius = random.uniform(5,50)
        else: self.radius = radius

        if position is None:
            self.pos = Vec2(
                random.uniform(0, 500),
                random.uniform(0, 500))
        else: self.pos = Vec2(position)

        if velocity is None:
            self.vel = Vec2(random.uniform(-5, 5), random.uniform(-5, 5))
        else: self.vel = Vec2(velocity)

        self.surface = pygame.Surface(Vec2(self.radius*2), SRCALPHA)
        self.color = pygame.Color.from_hsla(random.uniform(0,360),100,75,100)
        self.acc = Vec2(0)
        self.pressed_left = False
        self.pressed_right = False
        self.pressed_ctrl = False
        self.touching = False

    def collide(self, other: Ball):
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

    def force(self, other: Ball):
        impact_vector = other.pos - self.pos
        if impact_vector.x + impact_vector.y == 0: return
        force = (self.radius**2 * other.radius**2) / self.pos.distance_to(other.pos)**2
        self.acc += impact_vector.normalize() * force / self.radius**2

    def update(self, dt=1):
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        self.acc = Vec2(0)

    def handle_event(self, event, grid_size:int):
        if event.type == MOUSEBUTTONDOWN:
            if Vec2(event.pos - self.pos).magnitude() < self.radius:
                if event.button == 1:
                    self.pressed_left = Vec2(event.pos)
                elif event.button == 3:
                    self.pressed_right = Vec2(event.pos)

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.pressed_left = False
            elif event.button == 3:
                self.pressed_right = False        
            self.pressed = False

        elif event.type == MOUSEMOTION:
            if self.pressed_left and self.pressed_right:
                if self.pressed_ctrl:
                    x, y = self.pos - event.pos + Vec2(grid_size/2)
                    x = x - x % grid_size
                    y = y - y % grid_size
                    self.radius = Vec2(x,y).magnitude()
                else:
                    self.radius += sum(Vec2(event.rel))
                self.radius = min(max(1,self.radius),10000)

            elif self.pressed_left:
                if self.pressed_ctrl:
                    x, y = event.pos + Vec2(grid_size/2)
                    x = x - x % grid_size
                    y = y - y % grid_size
                    self.pos = Vec2(x,y)
                else:
                    self.pos += Vec2(event.rel)

            elif self.pressed_right:
                if self.pressed_ctrl:
                    x, y = self.pos - event.pos + Vec2(grid_size/2)
                    x = x - x % grid_size
                    y = y - y % grid_size
                    self.vel = -Vec2(x,y) / 30
                else:
                    self.vel += Vec2(event.rel) / 30

        elif event.type == KEYDOWN:
            if (self.pressed_left or self.pressed_right) and event.key == K_r:
                self.vel = Vec2(0)
            
            if event.key == K_LCTRL:
                self.pressed_ctrl = True

        elif event.type == KEYUP:
            if event.key == K_LCTRL:
                self.pressed_ctrl = False

    def draw(self):
        surface = pygame.Surface(Vec2(self.radius*2), SRCALPHA)
        pygame.draw.aacircle(surface, self.color, (self.radius, self.radius), self.radius, 2)
        return surface

class Button:
    def __init__(self, pos:pygame.Rect, text:str = 'button'):
        self.pos = Vec2(pos)
        self.text = text
        self.color = 'white'
        self.font = constants.Fonts.large
        self.surface = self.font.render(text, True, self.color)

    def handle_event(self, event:pygame.Event):
        calls = []
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.surface.get_rect().move(self.pos).collidepoint(event.pos):
                calls.append('button_pressed')
        return calls

    def draw(self):
        self.surface = self.font.render(self.text, True, self.color)

class Slider:
    def __init__(self, rect:pygame.Rect, start:float, end:float):
        self.rect = pygame.Rect(rect)
        self.start = start
        self.end = end
        self.pos = (end - start) / 2
        self.pressed = False

    def draw(self):
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        pos_x = (self.end - self.pos) / (self.end - self.start) * self.rect.width
        rect_hori = pygame.Rect(0,self.rect.height/2-2,self.rect.width,4)
        rect_vert = pygame.Rect(pos_x-5, 0, 10, self.rect.height)
        pygame.draw.rect(self.surface, constants.Colors.slider_hori, rect_hori, 0, 2)
        pygame.draw.rect(self.surface, constants.Colors.slider_vert, rect_vert, 0, 4)
    
    def handle_event(self, event:pygame.Event):
        if event.type == MOUSEBUTTONDOWN:
            pos_x = (self.end - self.pos) / (self.end - self.start) * self.rect.width
            rect = pygame.Rect(pos_x-5, 0, 10, self.rect.height).move(self.rect.topleft)
            if rect.collidepoint(event.pos):
                self.pressed = True

        elif event.type == MOUSEBUTTONUP:
            self.pressed = False
        
        elif event.type == MOUSEMOTION and self.pressed:
            self.pos -= event.rel[0] * (self.end-self.start) / self.rect.width
            self.pos = min(max(self.start, self.pos), self.end)
            return ['draw']
