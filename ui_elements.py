from __future__ import annotations

import pygame
from pygame.locals import *
from math import pi
import numpy as np
import random
from const import Var, Fonts, Colors

class Ball:
    def __init__(self, radius=None, position=None, velocity=None, id=None):
        if id is None:
            self.id = random.randint(1, 999)
        else:
            self.id = id
        
        if radius is None:
            self.radius = float(random.uniform(5, 50))
        else: 
            self.radius = radius

        if position is None:
            self.pos = np.array([random.uniform(0, Var.window_size[0]), random.uniform(0, Var.window_size[1])], dtype=np.float64)
        else: 
            self.pos = np.array(position, dtype=np.float64)

        if velocity is None:
            self.vel = np.array([random.uniform(-1, 1), random.uniform(-1, 1)], dtype=np.float64)
        else: 
            self.vel = np.array(velocity, dtype=np.float64)

        self.mass = pi * self.radius**2
        self.acc = np.zeros(2, dtype=np.float64)
        self.prev_pos = self.pos.copy()
        
        self.pressed_left = False
        self.pressed_right = False
        self.pressed_ctrl = False
        self.hover = False
        self._radius = self.radius
        self.surface = pygame.Surface((int(self.radius*2+1), int(self.radius*2+1)), SRCALPHA)
        self.color = pygame.Color.from_hsla(random.uniform(0, 360), 100, 75, 100)
        pygame.draw.aacircle(self.surface, self.color, (self.radius, self.radius), self.radius, 2)

    def __repr__(self):
        return f'Ball r:{self.radius} pos:{self.pos[0]:.2f}|{self.pos[1]:.2f} vel:{self.vel[0]:.2f}|{self.vel[1]:.2f}'

    @property
    def radius(self) -> float:
        return self._radius
    
    @radius.setter
    def radius(self, val: float):
        self._radius = val
        self.mass = pi * val**2

    def distance_to(self, other):
        """Calculate distance to another ball"""
        return np.linalg.norm(self.pos - other.pos)

    def handle_event(self, event, grid_size, camera):
        """Handle all pygame events"""
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
            mouse_world_pos = camera.to_world_pos(np.array(event.pos))
            # Calculate distance using numpy
            self.hover = np.linalg.norm(mouse_world_pos - self.pos) < self.radius

            if self.pressed_left and self.pressed_right:
                calls.append('dragged_ball')
                old = self.radius
                if self.pressed_ctrl:
                    diff = self.pos - mouse_world_pos
                    # Snap to grid
                    diff[0] = diff[0] - diff[0] % grid_size
                    diff[1] = diff[1] - diff[1] % grid_size
                    self.radius = np.linalg.norm(diff)
                else:
                    # Convert event.rel to numpy array
                    rel = np.array(event.rel) * camera.zoom_val
                    self.radius += np.sum(rel)

                self.radius = min(max(1, self.radius), 10000)
                if old != self.radius:
                    self.draw()
                
            elif self.pressed_left:
                calls.append('dragged_ball')
                if self.pressed_ctrl:
                    # Snap to grid
                    mouse_pos = camera.to_world_pos(np.array(event.pos)) + np.array([grid_size/2, grid_size/2])
                    mouse_pos[0] = mouse_pos[0] - mouse_pos[0] % grid_size
                    mouse_pos[1] = mouse_pos[1] - mouse_pos[1] % grid_size
                    self.pos = mouse_pos
                else:
                    # Move freely
                    self.pos += np.array(event.rel) * camera.zoom_val

            elif self.pressed_right:
                calls.append('dragged_ball')
                if self.pressed_ctrl:
                    # Snap velocity
                    diff = self.pos - camera.to_world_pos(np.array(event.pos))
                    diff[0] = diff[0] - diff[0] % grid_size
                    diff[1] = diff[1] - diff[1] % grid_size
                    self.vel = -diff / 30
                else:
                    # Free velocity adjustment
                    self.vel += np.array(event.rel) * camera.zoom_val / 30

        elif event.type == KEYDOWN:
            if event.key == K_r and self.hover:
                # reset velocity
                self.vel = np.zeros(2)
                calls.append('pressed_r')
            
            if event.key == K_LCTRL:
                self.pressed_ctrl = True

        elif event.type == KEYUP:
            if event.key == K_LCTRL:
                self.pressed_ctrl = False

        return calls

    def copy(self):
        b = Ball(self.radius, self.pos.copy(), self.vel.copy(), self.id)
        b.color = self.color
        return b
        
    def draw(self):
        """Update the ball's surface"""
        self.surface = pygame.Surface((int(self.radius*2+1), int(self.radius*2+1)), SRCALPHA)
        pygame.draw.aacircle(self.surface, self.color, (self.radius, self.radius), self.radius, 2)

class Button:
    def __init__(self, pos, text='button', color=None):
        self.pos = np.array(pos, dtype=np.int32)
        self.text = text
        if color:
            self.color = color
        else:
            self.color = 'white'
        self.font = Fonts.large
        self.surface = self.font.render(text, True, self.color)
        self.hover = False
        self.draw()

    def handle_event(self, event):
        calls = []
        rect = self.surface.get_rect().move(int(self.pos[0]), int(self.pos[1]))
        if event.type == MOUSEMOTION:
            self.hover = rect.collidepoint(event.pos)

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1 and self.hover:
                    calls.append('pressed_button')

        return calls
    
    def draw(self):
        self.surface = self.font.render(self.text, True, self.color)

class Slider:
    def __init__(self, name, start, end, rect):
        self.name = name
        self.start = start
        self.end = end
        self.rect = pygame.Rect(rect)
        self.val = (end - start) / 2
        self.pressed = False
        self.hover = False
        self.size_hori = 2
        self.size_vert = 4
        self.surface = pygame.Surface(self.rect.size)
        self.draw()

    def draw(self):
        pos_x = (self.val - self.start) / (self.end - self.start) * (self.rect.width - self.size_vert*2)
        rect_hori = pygame.Rect(self.size_vert, self.rect.height/2-self.size_hori, self.rect.width-self.size_vert*2, self.size_hori*2)
        rect_vert = pygame.Rect(pos_x, 0, self.size_vert*2, self.rect.height)
        text = Fonts.small.render(f'{self.name}: {self.val:.2f}', True, Colors.text)
        
        width = self.rect.width + text.get_width()
        self.surface = pygame.Surface((width, self.rect.height), SRCALPHA)
        self.surface.blit(text, (self.rect.width, self.rect.height/2-text.get_height()/2))
        pygame.draw.rect(self.surface, Colors.slider_hori, rect_hori, 0, self.size_hori)
        pygame.draw.rect(self.surface, Colors.slider_vert, rect_vert, 0, int(self.size_vert*0.7))
    
    def handle_event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            pos_x = (self.val - self.start) / (self.end - self.start) * (self.rect.width - self.size_vert*2)
            rect = pygame.Rect(pos_x, 0, self.size_vert*2, self.rect.height).move(self.rect.topleft)
            pygame.draw.rect(self.surface, 'red', rect, 1)
            if self.rect.collidepoint(event.pos):
                self.pressed = event.pos[0], self.val

        elif event.type == MOUSEBUTTONUP:
            self.pressed = False
        
        elif event.type == MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            if self.pressed:
                self.val = (self.end-self.start) / self.rect.width * (event.pos[0]-self.pressed[0]) + self.pressed[1]
                self.val = min(max(self.start, self.val), self.end)
                self.draw()
                return ['draw']

    def copy(self):
        slider = Slider(self.name, self.start, self.end, self.rect)
        slider.val = self.val
        return slider
