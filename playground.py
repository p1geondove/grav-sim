import pygame
from pygame import Vector2 as Vec2
from pygame.locals import *
from pygame import Surface, Event
from pygame import gfxdraw

from functools import reduce
from itertools import combinations, pairwise

import constants
import ui_elements
import camera
from util import points_on_grid, trajectories

class Camera:
    def __init__(self, playground):
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
        for line in trajectories(self.playground.balls, self.playground.dt, self.playground.sliders['len'], self.playground.domain):
            for p1, p2 in pairwise(line):
                color = constants.Colors.trail.lerp(constants.Colors.background, p2[1])
                pygame.draw.aaline(self.surface, color, p1[0], p2[0])

    def center(self):
        if not len(self.playground.balls): return
        mass = [b.radius**2 for b in self.playground.balls]
        pos = [b.pos.copy() for b in self.playground.balls]
        r = reduce(lambda x,y : x+y, (m*p for m,p in zip(mass,pos)))
        d = reduce(lambda x,y : x+y, mass)
        pygame.draw.aacircle(self.surface, constants.Colors.center2, r/d, 9, 0, True, False, True, False)
        pygame.draw.aacircle(self.surface, constants.Colors.center, r/d, 10, 1)

    def vel(self):
        for ball in self.playground.balls:
            pygame.draw.aaline(self.surface, constants.Colors.vel_vector, ball.pos, ball.pos + ball.vel*30)

    def grid(self, grid_radius:float = 100):
        grid_radius = grid_radius * self.zoom_val
        mouse_pos = self.to_world_pos(self.playground.mouse_pos)
        for point in points_on_grid(self.playground.grid_size, grid_radius, mouse_pos):
            lerp_val = (point - mouse_pos).magnitude() / grid_radius
            point = self.to_screen_pos(point)
            color = constants.Colors.grid.lerp(constants.Colors.background, lerp_val)
            gfxdraw.pixel(self.surface, int(point.x), int(point.y), color)

    def balls(self):
        rect = Rect(self.pos, Vec2(self.window.size)/self.zoom_val)
        for ball in self.playground.balls:
            size = Vec2(ball.surface.size) / self.zoom_val
            if not 1 < max(size) < min(self.window.size): continue
            screen_pos = (ball.pos + self.pos) / self.zoom_val
            rect = self.window.get_rect().move(-size)
            rect.size += size*2
            if not rect.collidepoint(screen_pos): continue
            surface = pygame.transform.scale(ball.surface, size)
            self.surface.blit(surface, screen_pos-size/2)

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
            if actve: self.functions[name]()
        
        if self.playground.show_grid:
            self.grid()

        self.ui()
        self.window.blit(self.surface, (0,0))

    def to_world_pos(self, screen_pos):
        return Vec2(screen_pos) * self.zoom_val - self.pos

    def to_screen_pos(self, world_pos):
        return (Vec2(world_pos) + self.pos) / self.zoom_val

    functions = {
        'trajectory':traj,
        'center':center,
        'velocity':vel,
    }

class Playground:
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
        self.infos_states = {n:False for n in Camera.functions}
        self.balls: list[ui_elements.Ball] = [ui_elements.Ball() for _ in range(3)]
        self.buttons = [ui_elements.Button((5, 5 + y*30), name) for y, name in enumerate(Camera.functions)]
        self.sliders = [
            ui_elements.Slider((5, self.window.height-35, 100, 30), 0.005, 1, 'dt'),
            ui_elements.Slider((5, self.window.height-70, 100, 30), 10, 1000, 'len')
        ]
        self.camera = Camera(self)
        self.draw()

    def draw(self):
        if self.playing:
            self.update()
        self.camera.draw()

    def handle_event(self, event:Event):
        calls = []
        if event.type == MOUSEMOTION:
            print(self.camera.to_world_pos(event.pos))

        for ball in self.balls:
            if calls := ball.handle_event(event, self.grid_size, self.camera):
                print(calls)
                if 'dragged_ball' in calls:
                    self.dragging = False
                calls.extend(calls)
                calls.append('draw')
        
        for button in self.buttons:
            if button.handle_event(event):
                self.infos_states[button.text] = not self.infos_states[button.text]
                calls.append('draw')

        if self.sliders[0].handle_event(event):
            self.dt = self.sliders[0].val
            calls.append('draw')
        
        if self.sliders[1].handle_event(event):
            self.trail_size = int(self.sliders[1].val)
            calls.append('draw')

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
                for ball in self.balls:
                    if ball.pos.distance_to(self.camera.to_world_pos(event.pos)) < ball.radius:
                        ball.pressed = True
                        self.dragging = False
                else:
                    self.dragging = True

            elif event.button == 2:
                for idx, ball in enumerate(self.balls):
                    if ball.pos.distance_to(event.pos) < ball.radius:
                        calls.append('draw')
                        del self.balls[idx]
                        break
                else:
                    self.balls.append(ui_elements.Ball(position=event.pos))
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
            self.camera.draw()
        
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
