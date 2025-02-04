from __future__ import annotations

import pygame
from pygame.locals import *
from pygame import gfxdraw
from pygame import Vector2 as Vec2

import sys
from itertools import combinations, pairwise
from functools import reduce

import constants
import ui_elements

class Playground:
    class draw_infos:
        def draw_traj(self:Playground):
            if not self.balls: return
            for line in self.trajectories(self.trail_size):
                for p1, p2 in pairwise(line):
                    color = constants.Colors.trail.lerp(constants.Colors.background, p2[1])
                    pygame.draw.aaline(self.surface, color, p1[0], p2[0])

        def draw_center(self:Playground):
            if not self.amt_balls: return
            mass = [b.radius**2 for b in self.balls]
            pos = [b.pos.copy() for b in self.balls]
            r = reduce(lambda x,y : x+y, (m*p for m,p in zip(mass,pos)))
            d = reduce(lambda x,y : x+y, mass)
            pygame.draw.aacircle(self.surface, constants.Colors.center2, r/d, 9, 0, True, False, True, False)
            pygame.draw.aacircle(self.surface, constants.Colors.center, r/d, 10, 1)

        def draw_vel(self:Playground):
            for ball in self.balls:
                pygame.draw.aaline(self.surface, constants.Colors.vel_vector, ball.pos, ball.pos + ball.vel*30)

        def draw_grid(self:Playground):
            if self.mouse_pos is None: return
            grid_radius = 100

            for y in range(-grid_radius, grid_radius+1, int(self.grid_size)):
                for x in range(-grid_radius, grid_radius+1, int(self.grid_size)):
                    distance = Vec2(x,y).magnitude() / grid_radius
                    if distance > 1: continue
                    pos_x = x + self.mouse_pos.x - self.mouse_pos.x % self.grid_size
                    pos_y = y + self.mouse_pos.y - self.mouse_pos.y % self.grid_size
                    distance = min(max(0,Vec2(pos_x, pos_y).distance_to(self.mouse_pos) / grid_radius),1)
                    color = constants.Colors.grid.lerp(constants.Colors.background, distance)
                    gfxdraw.pixel(self.surface, int(pos_x), int(pos_y), color)

        def debug_txt(self:Playground):
            amt_txt = constants.Fonts.medium.render(f'{len(self.balls)} : amt balls',True,constants.Colors.text)
            pos = self.surface.width - amt_txt.width, 0
            self.surface.blit(amt_txt,pos)

        functions = [
            ('trajectory', draw_traj),
            ('center', draw_center),
            ('velocity',draw_vel),
        ]

    def __init__(self, window:pygame.Surface):
        pygame.font.init()
        self.window = window
        self.surface = window.copy()
        self.domain = window.get_rect()
        self.amt_balls = 3
        self.dt = 1
        self.grid_size = 20
        self.trail_size = 300
        self.playing = False
        self.pressed_alt = False
        self.mouse_pos = None
        self.draw_map = {n: [f, False] for n,f in self.draw_infos.functions}
        self.balls: list[ui_elements.Ball] = [ui_elements.Ball() for _ in range(self.amt_balls)]
        self.buttons = [ui_elements.Button((5, 5 + y*30), name) for y, name in enumerate(self.draw_map)]
        self.sliders = [
            ui_elements.Slider((5, self.surface.height-35, 100, 30), 0.005, 1, 'dt'),
            ui_elements.Slider((5, self.surface.height-70, 100, 30), 10, 1000, 'len')
        ]
        self.draw()

    def draw(self):
        if self.playing:
            self.update()

        self.surface.fill('grey15')

        if any((b.pressed_ctrl for b in self.balls)):
            self.draw_infos.draw_grid(self)

        for ball in self.balls:
            self.surface.blit(ball.surface, ball.pos-Vec2(ball.radius))

        for button in self.buttons:
            func, active = self.draw_map[button.text]

            if active:
                func(self)
                button.color = constants.Colors.active
            else:
                button.color = constants.Colors.inactive
            
            button.draw()
            self.surface.blit(button.surface, button.pos)

        for slider in self.sliders:
            slider.draw()
            self.surface.blit(slider.surface, slider.rect.topleft)

        self.draw_infos.debug_txt(self)

        self.window.blit(self.surface, (0,0))

    def handle_event(self, event:pygame.Event):
        calls = []

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                self.playing = not self.playing

            elif event.key == K_LALT:
                self.pressed_alt = True
        
        elif event.type == KEYUP:
            if event.key == K_LALT:
                self.pressed_alt = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 2:
                if self.balls:
                    for idx, ball in enumerate(self.balls):
                        if ball.pos.distance_to(event.pos) < ball.radius:
                            del self.balls[idx]
                            break
                    else:
                        self.balls.append(ui_elements.Ball(position=event.pos))
                else:
                    self.balls.append(ui_elements.Ball(position=event.pos))

        elif event.type == MOUSEWHEEL:
            if self.pressed_alt:
                self.grid_size *= 2**event.y

        elif event.type == VIDEORESIZE:
            self.domain = pygame.Rect((0,0),event.size)
            self.surface = pygame.Surface(self.domain.size)

            for idx, slider in enumerate(self.sliders):
                slider.rect = pygame.Rect((5, self.surface.height-35*(idx+1), 100, 30))

            for ball in self.balls:
                ball.pos.x = ball.pos.x % self.surface.width
                ball.pos.y = ball.pos.y % self.surface.height

            self.draw()

        elif event.type == MOUSEMOTION:
            self.mouse_pos = Vec2(event.pos)

        for ball in self.balls:
            if ball.handle_event(event, self.grid_size):
                self.draw()
        
        for button in self.buttons:
            if button.handle_event(event):
                self.draw_map[button.text][1] = not self.draw_map[button.text][1]
                self.draw()

        if self.sliders[0].handle_event(event):
            self.dt = self.sliders[0].val
            self.draw()
        
        if self.sliders[1].handle_event(event):
            self.trail_size = int(self.sliders[1].val)

    def update(self):
        for b1, b2 in combinations(self.balls, 2):
            b1.collide(b2)
            b1.force(b2)
            b2.force(b1)

        for ball in self.balls:
            ball.update(self.dt)
            ball.pos.x = ball.pos.x % self.surface.width
            ball.pos.y = ball.pos.y % self.surface.height

    def trajectories(self, steps:int) -> list[list[tuple[Vec2, float]]]:
        balls = [ball.copy() for ball in self.balls]
        lines:list[list[Vec2]] = [[b.pos.copy()] for b in balls]

        for _ in range(steps):
            for b1, b2 in combinations(balls, 2):
                b1.collide(b2)
                b1.force(b2)
                b2.force(b1)

            for idx, ball in enumerate(balls):
                ball.update(self.dt)
                if self.domain:
                    ball.pos.x = (ball.pos.x - self.domain.left) % self.domain.width + self.domain.left
                    ball.pos.y = (ball.pos.y - self.domain.top) % self.domain.height + self.domain.top

                lines[idx].append(ball.pos.copy())

        all_segments:list[list[Vec2]] = []

        for line in lines:
            idx = 0
            while idx < len(line)-1:
                if line[idx].distance_to(line[idx+1]) < 100:
                    break    
                idx += 1

            segments = [[(line[idx],0)]]  
            for idx, pos in enumerate(line[1:]):
                distance = pos.distance_to(segments[-1][-1][0])
                if 2 < distance < 100:
                    segments[-1].append((pos, idx/steps))
                elif distance > 100:
                    if len(segments[-1]) > 1:
                        segments.append([(pos,idx/steps)])
            segments[-1].append((pos,1))
            all_segments.extend(segments)

        return all_segments

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