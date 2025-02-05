from __future__ import annotations

import pygame
from pygame.locals import *
from pygame import gfxdraw
from pygame import Vector2 as Vec2

import sys
from itertools import combinations ,pairwise
from functools import reduce
from util import points_on_grid, trajectories

import constants
import ui_elements


class Draw:
    def __init__(self, playground:Playground):
        self.window = playground.window
        self.surface = playground.window.copy()
        self.pos = Vec2(0,0)
        self.zoom:float = 1
        self.playground = playground

    def move(self, pixel_pos:Vec2):
        self.pos += Vec2(pixel_pos[0] * self.zoom, pixel_pos[1] * self.zoom)

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
        for point in points_on_grid(self.playground.grid_size, grid_radius, self.playground.mouse_pos - self.pos):
            lerp_val = (point - self.playground.mouse_pos + self.pos).magnitude() / grid_radius
            # print(lerp_val)
            point = (point / self.zoom) + self.pos
            color = constants.Colors.grid.lerp(constants.Colors.background, lerp_val)
            gfxdraw.pixel(self.surface, int(point.x), int(point.y), color)

    def balls(self):
        rect = pygame.Rect(self.pos, Vec2(self.window.size)/self.zoom)
        for ball in self.playground.balls:
            size = Vec2(ball.surface.size) / self.zoom
            if not 1 < max(size) < min(self.window.size): continue
            screen_pos = (ball.pos + self.pos) / self.zoom
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

    functions = {
        'trajectory':traj,
        'center':center,
        'velocity':vel,
    }

    def draw(self):
        self.surface.fill('grey15')
        self.balls()

        for name, actve in self.playground.infos_states.items():
            if actve: self.functions[name]()
        
        if self.playground.show_grid:
            self.grid()

        self.ui()
        self.window.blit(self.surface, (0,0))

class Playground:
    def __init__(self, window:pygame.Surface):
        pygame.font.init()
        self.window = window
        self.domain = window.get_rect()

        self.amt_balls = 3
        self.dt = 1
        self.grid_size = 20
        self.trail_size = 300
        self.playing = False
        self.pressed_alt = False
        self.pressed_ctrl = False
        self.pressed_left = False
        self.pressed_right = False
        self.show_grid = False
        self.mouse_pos = None
        self.domain = None
        self.infos_states = {n:False for n in Draw.functions}
        self.balls: list[ui_elements.Ball] = [ui_elements.Ball() for _ in range(self.amt_balls)]
        self.buttons = [ui_elements.Button((5, 5 + y*30), name) for y, name in enumerate(Draw.functions)]
        self.sliders = [
            ui_elements.Slider((5, self.window.height-35, 100, 30), 0.005, 1, 'dt'),
            ui_elements.Slider((5, self.window.height-70, 100, 30), 10, 1000, 'len')
        ]
        self.camera = Draw(self)
        self.draw()

    def draw(self):
        if self.playing:
            self.update()
        self.camera.draw()

    def handle_event(self, event:pygame.Event):
        calls = []

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                self.playing = not self.playing

            elif event.key == K_LCTRL:
                self.show_grid = True
                self.pressed_ctrl = True

            elif event.key == K_LALT:
                self.pressed_alt = True
        
        elif event.type == KEYUP:
            if event.key == K_LCTRL:
                self.show_grid = False
                self.pressed_ctrl = False

            elif event.key == K_LALT:
                self.pressed_alt = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.pressed_left = True
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
                self.pressed_left = False

            elif event.button == 3:
                self.pressed_right = False

        elif event.type == MOUSEWHEEL:
            if self.pressed_ctrl:
                self.grid_size *= 2**event.y
            else:
                self.camera.zoom /= 2**event.y
                
        elif event.type == MOUSEMOTION:
            self.mouse_pos = Vec2(event.pos)
            pressed = self.pressed_left or self.pressed_right
            balls_pressed = [ball.pressed_left or ball.pressed_right for ball in self.balls]
            if pressed and not any(balls_pressed):
                self.show_grid = True
                self.camera.move(event.rel)
                calls.extend(['draw'])

        elif event.type == VIDEORESIZE:
            self.domain = pygame.Rect((0,0),event.size)
            self.surface = pygame.Surface(self.domain.size)

            for idx, slider in enumerate(self.sliders):
                slider.rect = pygame.Rect((5, self.surface.height-35*(idx+1), 100, 30))

            for ball in self.balls:
                ball.pos.x = ball.pos.x % self.surface.width
                ball.pos.y = ball.pos.y % self.surface.height
            
            calls.append('draw')

        for ball in self.balls:
            if ball.handle_event(event, self.grid_size):
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

def main():
    # random.seed(0)
    winsize = pygame.Vector2(800, 800)
    window = pygame.display.set_mode(winsize, RESIZABLE)
    playground = Playground(window)
    clock = pygame.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            playground.handle_event(event)

        playground.draw()
        pygame.display.flip()
        clock.tick(150)
        print(f'fps: {clock.get_fps():.0f}', end=f'{" "*10}\r')

if __name__ == '__main__':
    main()