from __future__ import annotations
import pygame
from pygame import Vector2 as Vec2
from pygame.locals import *
from pygame import Surface, Event
from pygame import gfxdraw

from functools import reduce
from itertools import combinations, pairwise

import constants
import ui_elements
from util import points_on_grid, trajectories

class Playground:
    class Camera:
        def __init__(self, playground:Playground):
            self.window = playground.window
            self.surface = playground.window.copy()
            self.pos = Vec2(0,0)
            self.zoom_val:float = 1
            self.playground = playground

        def move(self, pixel_pos:Vec2):
            self.pos += Vec2(pixel_pos[0] * self.zoom_val, pixel_pos[1] * self.zoom_val)

        def zoom(self, zoom_amt):
            if zoom_amt < 0:
                self.pos += self.playground.mouse_pos * self.zoom_val
                self.zoom_val /= 2**zoom_amt
            if zoom_amt > 0:
                self.zoom_val /= 2**zoom_amt
                self.pos -= self.playground.mouse_pos * self.zoom_val

        def get_rect(self):
            return Rect(self.pos, Vec2(self.window.size)/self.zoom_val)

        def traj(self):
            if not self.playground.balls: return
            amt_steps = 100
            for slider in self.playground.sliders:
                if slider.name == 'len':
                    amt_steps = int(slider.val)

            for positions, distance in trajectories(self.playground.balls, self.playground.dt, amt_steps, self.zoom_val, self.zoom_val*100,self.playground.domain):
                for (p1, p2), dist in zip(pairwise(map(self.to_screen_pos, positions)), distance):
                    color = constants.Colors.trail.lerp(constants.Colors.background, dist)
                    pygame.draw.aaline(self.surface, color, p1, p2)

        def center(self):
            if not len(self.playground.balls): return
            mass = [b.radius**2 for b in self.playground.balls]
            pos = [b.pos.copy() for b in self.playground.balls]
            r = reduce(lambda x,y : x+y, (m*p for m,p in zip(mass,pos)))
            d = reduce(lambda x,y : x+y, mass)
            center = self.to_screen_pos(r/d)
            pygame.draw.aacircle(self.surface, constants.Colors.center2, center, 9, 0, True, False, True, False)
            pygame.draw.aacircle(self.surface, constants.Colors.center, center, 10, 1)

        def vel(self):
            for ball in self.playground.balls:
                start = self.to_screen_pos(ball.pos)
                end = self.to_screen_pos(ball.pos+ball.vel*30)
                pygame.draw.aaline(self.surface, constants.Colors.vel_vector, start, end)

        def grid(self, grid_radius:float = 100):
            grid_radius = grid_radius * self.zoom_val
            mouse_pos = self.to_world_pos(self.playground.mouse_pos)
            for point in points_on_grid(self.playground.grid_size, grid_radius, mouse_pos):
                lerp_val = (point - mouse_pos).magnitude() / grid_radius
                point = self.to_screen_pos(point)
                color = constants.Colors.grid.lerp(constants.Colors.background, lerp_val)
                gfxdraw.pixel(self.surface, int(point.x), int(point.y), color)

        def balls(self):
            for ball in self.playground.balls:
                pygame.draw.aacircle(self.surface, ball.color, self.to_screen_pos(ball.pos), ball.radius/self.zoom_val, 2)

        def debug_txt(self):
            amt_txt = constants.Fonts.medium.render(f'{len(self.playground.balls)} : amt balls',True,constants.Colors.text)
            pos = self.surface.width - amt_txt.width, 0
            self.surface.blit(amt_txt, pos)

        def ui(self):
            for button in self.playground.buttons:
                self.surface.blit(button.surface,button.pos)

            for slider in self.playground.sliders:
                slider.surface
                self.surface.blit(slider.surface, slider.rect.topleft)

            self.debug_txt()

        def draw(self):
            self.surface.fill('grey15')
            self.balls()

            for name, actve in self.playground.infos_states.items():
                if actve: self.functions[name](self)
            
            if self.playground.dragging or self.playground.pressed_ctrl:
                self.grid()

            self.ui()

            return self.surface

        def to_world_pos(self, screen_pos):
            return Vec2(screen_pos) * self.zoom_val - self.pos

        def to_screen_pos(self, world_pos):
            return (Vec2(world_pos) + self.pos) / self.zoom_val

        functions = {
            'trajectory':traj,
            'center':center,
            'velocity':vel,
        }

    def __init__(self, window:Surface):
        self.window = window
        self.domain = window.get_rect()

        self.dt = 1
        self.grid_size = 20
        self.trail_size = 300

        self.playing = False
        self.pressed_alt = False
        self.pressed_ctrl = False
        self.pressed_left = False
        self.pressed_right = False
        self.dragging = False
        self.show_grid = False
        self.domain = None

        self.mouse_pos = Vec2(0,0)
        self.infos_states = {n:False for n in self.Camera.functions}

        self.balls: list[ui_elements.Ball] = [ui_elements.Ball() for _ in range(3)]

        self.buttons:list[ui_elements.Button] = []
        for y, (name, state) in enumerate(self.infos_states.items()):
            color = constants.Colors.active if state else constants.Colors.inactive
            self.buttons.append(ui_elements.Button((5, 5 + y*30), name, color))

        self.sliders = [
            ui_elements.Slider((5, self.window.height-35, 100, 30), 0.005, 1, 'dt'),
            ui_elements.Slider((5, self.window.height-70, 100, 30), 10, 1000, 'len')
        ]

        self.camera = self.Camera(self)
        self.draw()

    def draw(self):
        if self.playing:
            self.update()

        surface_balls = self.camera.draw()
        surface_hud = self.window.copy()

        for slider in self.sliders:
            surface_hud.blit(slider.surface, slider.rect.topleft)
        
        for button in self.buttons:
            surface_hud.blit(button.surface, button.pos)
        
        self.window.blit(surface_hud, (0,0))
        self.window.blit(surface_balls, (0,0))

    def handle_event(self, event:Event):
        calls = []

        for ball in self.balls:
            if calls := ball.handle_event(event, self.grid_size, self.camera):
                if 'dragged_ball' in calls:
                    self.dragging = False
                calls.extend(calls)
                calls.append('draw')
        
        for button in self.buttons:
            if button.handle_event(event):
                self.infos_states[button.text] = not self.infos_states[button.text]
                button.color = constants.Colors.active if self.infos_states[button.text] else constants.Colors.inactive
                button.draw()
                calls.append('draw')

        if self.sliders[0].handle_event(event):
            self.dt = self.sliders[0].val
            calls.append('draw')
            self.dragging = False
        
        if self.sliders[1].handle_event(event):
            self.trail_size = int(self.sliders[1].val)
            calls.append('draw')
            self.dragging = False

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                self.playing = not self.playing

            elif event.key == K_LCTRL:
                self.pressed_ctrl = True

            elif event.key == K_LALT:
                self.pressed_alt = True
        
        elif event.type == KEYUP:
            if event.key == K_LCTRL:
                self.pressed_ctrl = False

            elif event.key == K_LALT:
                self.pressed_alt = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if not any((b.pressed for b in self.balls)):
                    self.dragging = True

            elif event.button == 2:
                for idx, ball in enumerate(self.balls):
                    if ball.pressed:
                    # if ball.pos.distance_to(event.pos) < ball.radius:
                        calls.append('draw')
                        del self.balls[idx]
                        break
                else:
                    self.balls.append(ui_elements.Ball(position=self.camera.to_world_pos(event.pos)))
                    calls.append('draw')
            
            elif event.button == 3:
                self.pressed_right = True

        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                self.pressed_left = False

            elif event.button == 3:
                self.pressed_right = False

        elif event.type == MOUSEWHEEL:
            if self.pressed_ctrl:
                self.grid_size /= 2**event.y
            else:
                self.grid_size /= 2**event.y
                self.camera.zoom(event.y)
                
        elif event.type == MOUSEMOTION:
            self.mouse_pos = Vec2(event.pos)
            if self.dragging:
                self.show_grid = True
                self.camera.move(event.rel)
                calls.append(['draw'])

        elif event.type == VIDEORESIZE:
            self.domain = Rect((0,0),event.size)
            self.surface = Surface(self.domain.size)

            for idx, slider in enumerate(self.sliders):
                slider.rect = Rect((5, self.surface.height-35*(idx+1), 100, 30))

            for ball in self.balls:
                ball.pos.x = ball.pos.x % self.surface.width
                ball.pos.y = ball.pos.y % self.surface.height
            
            calls.append('draw')

        self.show_grid = self.pressed_ctrl

        if 'draw' in calls:
            self.draw()
        
    def update(self):
        for b1, b2 in combinations(self.balls, 2):
            b1.collide(b2)
            b1.force(b2)
            b2.force(b1)
        
        if self.domain:
            for ball in self.balls:
                ball.update(self.dt)
                ball.pos.x = ball.pos.x % self.surface.width
                ball.pos.y = ball.pos.y % self.surface.height
        else:
            for ball in self.balls:
                ball.update(self.dt)
