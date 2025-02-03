from __future__ import annotations
import sys
import os
import pygame
from pygame.locals import *
from pygame import Vector2 as Vec2
import random
from itertools import combinations
from functools import reduce

class Ball:
    def __init__(self, surface: pygame.Surface, radius:float = None, position:Vec2 = None, velocity:Vec2 = None):
        self.surface = surface

        if radius is None:
            self.radius = random.uniform(5,50)
        else: self.radius = radius

        if position is None:
            self.pos = Vec2(
                random.uniform(self.radius, surface.width-self.radius),
                random.uniform(self.radius, surface.height-self.radius))
        else: self.pos = Vec2(position)

        if velocity is None:
            self.vel = Vec2(random.uniform(-5, 5), random.uniform(-5, 5)) * 0.01
        else: self.vel = Vec2(velocity)

        self.color = pygame.Color([int(random.uniform(0, 255)) for _ in range(3)])
        self.acc = Vec2(0)
        self.pressed_left = False
        self.pressed_right = False
        self.pressed_ctrl = False
        self.touching = False

    def collide(self, other: Ball):
        impact_vector = other.pos - self.pos
        distance_squared = impact_vector.magnitude_squared()
        combined_radius = self.radius + other.radius

        # self.touching = True
        if distance_squared > combined_radius ** 2:
            self.touching = True
            if (distance_squared - combined_radius ** 2) ** 0.5 > 1:
                self.touching = False

        if not self.touching:
            self.touching = True  
            return

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
        force = (self.radius**2 * other.radius**2) / self.pos.distance_to(other.pos)**2
        self.acc += impact_vector.normalize() * force / self.radius**2

    def update(self, dt=1):
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        self.acc = Vec2(0)
        self.pos.x = self.pos.x % self.surface.get_width()
        self.pos.y = self.pos.y % self.surface.get_height()

    def handle_event(self, event):
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
                self.radius += sum(Vec2(event.rel))

            elif self.pressed_left:
                if self.pressed_ctrl:
                    grid_size = 20
                    x = event.pos[0] + grid_size/2 - event.pos[0] % grid_size
                    y = event.pos[1] + grid_size/2 - event.pos[1] % grid_size
                    self.pos = Vec2(x,y)
                else:
                    self.pos += Vec2(event.rel)

            elif self.pressed_right:
                if self.pressed_ctrl:
                    grid_size = 20
                    x,y = self.pos - event.pos
                    x = x-x%10
                    y = y-y%10
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
        pygame.draw.aacircle(self.surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius, 2)

class Button:
    def __init__(self, pos:pygame.Rect, text:str = 'button'):
        self.pos = Vec2(pos)
        self.text = text
        self.color = 'white'

        try:
            path = resource_path('AgaveNerdFontMono-Regular.ttf')
            font = pygame.Font(path,30)
        except:
            font = pygame.Font(None,30)
        finally:
            self.font = font
            
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
        # print(self.rect)
        self.start = start
        self.end = end
        self.pos = (end - start) / 2
        self.pressed = False

    def draw(self):
        self.surface = pygame.Surface(self.rect.size, SRCALPHA)
        pos_x = (self.end - self.pos) / (self.end - self.start) * self.rect.width
        rect_hori = pygame.Rect(0,self.rect.height/2-2,self.rect.width,4)
        rect_vert = pygame.Rect(pos_x-5, 0, 10, self.rect.height)
        pygame.draw.rect(self.surface, 'grey50', rect_hori, 0, 2)
        pygame.draw.rect(self.surface, 'grey70', rect_vert, 0, 4)
    
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

class PlayGround:
    def __init__(self, surface:pygame.Surface):
        pygame.font.init()
        self.surface = surface
        self.amt_balls = 3
        self.balls: list[Ball] = [Ball(surface) for _ in range(self.amt_balls)]
        self.buttons: list[Button] = [
            Button((5,5),'trajectory'),
            Button((5,30),'center'),
            Button((5,55),'velocity')
        ]
        self.slider = Slider((0,surface.height-20,100,20),0.01, 1)
        self.playing = False
        self.mode_active = [False]*len(self.buttons)
        self.dt = 1
        self.draw_map = []
        self.color_active = pygame.Color('#47914f')
        self.color_inactive = pygame.Color('#994946')
        self.draw()

    def draw(self):
        def draw_traj():
            for line in self.trajectories(300, self.dt):
                pygame.draw.aalines(self.surface, 'orange', False, line)

        def draw_center():
            mass = [b.radius**2 for b in self.balls]
            pos = [b.pos.copy() for b in self.balls]
            r = reduce(lambda x,y : x+y, (m*p for m,p in zip(mass,pos)))
            d = reduce(lambda x,y : x+y, mass)
            pygame.draw.circle(self.surface, 'red', r/d,3)

        def draw_vel():
            for ball in self.balls:
                pygame.draw.line(self.surface, '#4e9c60', ball.pos, ball.pos + ball.vel*30)

        if self.playing:
            self.update()

        self.draw_map = [
            draw_traj,
            draw_center,
            draw_vel,
        ]

        self.surface.fill('grey15')

        for draw, active in zip(self.draw_map, self.mode_active):
            if active: draw()

        for ball in self.balls:
            ball.draw()
        
        for idx, button in enumerate(self.buttons):
            button.color = self.color_active if self.mode_active[idx] else self.color_inactive
            button.draw()
            self.surface.blit(button.surface, button.pos)

        self.slider.draw()
        self.surface.blit(self.slider.surface, self.slider.rect.topleft)
        # print(self.slider.rect.topleft)

    def handle_event(self, event:pygame.Event):
        calls = []

        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                self.playing = not self.playing

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 2:
                for idx, ball in enumerate(self.balls):
                    if ball.pos.distance_to(event.pos) < ball.radius:
                        del self.balls[idx]
                        break
                else:
                    self.balls.append(Ball(self.surface, position=event.pos))

        for ball in self.balls:
            if ball.handle_event(event):
                self.draw()

        for idx, button in enumerate(self.buttons):
            if button.handle_event(event):
                self.mode_active[idx] = not self.mode_active[idx]
                button.color = self.color_active if self.mode_active[idx] else self.color_inactive
                self.draw()
    
        if self.slider.handle_event(event):
            self.dt = self.slider.pos
            self.draw()

    def update(self):
        for b1, b2 in combinations(self.balls, 2):
            b1.collide(b2)
            b1.force(b2)
            b2.force(b1)

        for ball in self.balls:
            ball.update(self.dt)

    def trajectories(self, steps:int, dt:float) -> list[list[Vec2]]:
        new_balls:list[Ball] = []

        for ball in self.balls:
            new_balls.append(
                Ball(
                    surface=ball.surface,
                    position=ball.pos,
                    velocity=ball.vel,
                    radius=ball.radius
                ))
        balls = new_balls
            
        lines:list[list[Vec2]] = [[] for _ in balls]
        segments = [[b.pos.copy()] for b in balls]

        for _ in range(steps):
            for b1, b2 in combinations(balls, 2):
                b1.collide(b2)
                b1.force(b2)
                b2.force(b1)

            for idx, ball in enumerate(balls):
                ball.update(dt)
                lines[idx].append(ball.pos.copy())

        all_segments:list[list[Vec2]] = []

        for line in lines:
            segments = [[line[0]]]  
            for pos in line[1:]:
                distance = pos.distance_to(segments[-1][-1])
                if 2 < distance < 100:
                    segments[-1].append(pos)
                elif distance > 100:
                    if len(segments[-1]) > 1:
                        segments.append([pos])
            segments[-1].append(pos)
            all_segments.extend(segments)

        return all_segments

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    random.seed(0)
    winsize = pygame.Vector2(800, 800)
    window = pygame.display.set_mode(winsize, RESIZABLE)
    playground = PlayGround(window)
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