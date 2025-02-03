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
            # self.touching = True
            # if (distance_squared - combined_radius ** 2) ** 0.5 > 1:
                # self.touching = False

        # if not self.touching:
        #     self.touching = True  
        #     return

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
        # self.pos.x = self.pos.x % self.domain.width
        # self.pos.y = self.pos.y % self.domain.height

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
                if self.pressed_ctrl:
                    print(self.radius)
                    grid_size = 20
                    x,y = self.pos - event.pos + Vec2(grid_size/2)
                    x = x - x % grid_size
                    y = y - y % grid_size
                    self.radius = Vec2(x,y).magnitude()
                    # self.radius = self.radius - self.radius & grid_size
                    print(self.radius)
                else:
                    self.radius += sum(Vec2(event.rel))
                self.radius = min(max(1,self.radius),10000)

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
        surface = pygame.Surface(Vec2(self.radius*2), SRCALPHA)
        pygame.draw.aacircle(surface, self.color, (self.radius, self.radius), self.radius, 2)
        return surface

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
    def __init__(self, window:pygame.Surface):
        pygame.font.init()
        self.window = window
        self.surface = window.copy()
        self.domain = window.get_rect()
        self.amt_balls = 3
        self.playing = False
        self.dt = 1
        self.mouse_pos = None
        self.grid_size = 20

        self.color_active = pygame.Color('#47914f')
        self.color_inactive = pygame.Color('#994946')

        self.draw_map = {
            'trajectory' : [self.draw_traj, False],
            'center' : [self.draw_center, False],
            'velocity' : [self.draw_vel, False],
        }

        self.balls: list[Ball] = [Ball() for _ in range(self.amt_balls)]
        self.buttons = [Button((5, 5 + y*30), name) for y, name in enumerate(self.draw_map)]
        self.slider = Slider((0,self.surface.height-20,100,20),0.01, 1)

        self.draw()

    def draw_traj(self):
        for line in self.trajectories(300, self.dt, self.surface.get_rect()):
            pygame.draw.aalines(self.surface, 'orange', False, line)

    def draw_center(self):
        mass = [b.radius**2 for b in self.balls]
        pos = [b.pos.copy() for b in self.balls]
        r = reduce(lambda x,y : x+y, (m*p for m,p in zip(mass,pos)))
        d = reduce(lambda x,y : x+y, mass)
        pygame.draw.circle(self.surface, 'red', r/d,3)

    def draw_vel(self):
        for ball in self.balls:
            pygame.draw.line(self.surface, '#4e9c60', ball.pos, ball.pos + ball.vel*30)

    def draw_grid(self):
        if self.mouse_pos is None: return
        grid_radius = 100

        for y in range(-grid_radius, grid_radius+1, self.grid_size):
            for x in range(-grid_radius, grid_radius+1, self.grid_size):
                distance = Vec2(x,y).magnitude() / grid_radius
                if distance > 1: continue
                color = pygame.Color('orange').lerp('grey15',distance)
                pos_x = x + self.mouse_pos.x - self.mouse_pos.x % self.grid_size + self.grid_size/2
                pos_y = y + self.mouse_pos.y - self.mouse_pos.y % self.grid_size + self.grid_size/2
                pygame.draw.aacircle(self.surface, color, (pos_x,pos_y), 1)

    def draw(self):
        if self.playing:
            self.update()

        self.surface.fill('grey15')

        if any((b.pressed_ctrl for b in self.balls)):
            self.draw_grid()

        for ball in self.balls:
            ball.pos.x = ball.pos.x % self.surface.width
            ball.pos.y = ball.pos.y % self.surface.height
            self.surface.blit(ball.draw(), ball.pos-Vec2(ball.radius))

        for button in self.buttons:
            func, active = self.draw_map[button.text]

            if active:
                func()
                button.color = self.color_active
            else:
                button.color = self.color_inactive
            
            button.draw()
            self.surface.blit(button.surface, button.pos)

        self.slider.draw()
        self.surface.blit(self.slider.surface, self.slider.rect.topleft)

        self.window.blit(self.surface, (0,0))

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
                    self.balls.append(Ball(position=event.pos))

        elif event.type == VIDEORESIZE:
            self.domain = pygame.Rect((0,0),event.size)
            self.surface = pygame.Surface(self.domain.size)
            self.slider.rect = pygame.Rect(0,self.surface.height-20,100,20)
            for ball in self.balls:
                ball.pos.x = ball.pos.x % self.surface.width
                ball.pos.y = ball.pos.y % self.surface.height
            self.draw()

        elif event.type == MOUSEMOTION:
            self.mouse_pos = Vec2(event.pos)

        for ball in self.balls:
            if ball.handle_event(event):
                self.draw()
        
        for button in self.buttons:
            if button.handle_event(event):
                self.draw_map[button.text][1] = not self.draw_map[button.text][1]
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

    def trajectories(self, steps:int, dt:float, domain:pygame.Rect=None) -> list[list[Vec2]]:
        balls:list[Ball] = []
        for ball in self.balls:
            balls.append(
                Ball(
                    position=ball.pos,
                    velocity=ball.vel,
                    radius=ball.radius
                ))
            
        lines:list[list[Vec2]] = [[b.pos.copy()] for b in balls]

        for _ in range(steps):
            for b1, b2 in combinations(balls, 2):
                b1.collide(b2)
                b1.force(b2)
                b2.force(b1)

            for idx, ball in enumerate(balls):
                ball.update(dt)
                if domain:
                    ball.pos.x = (ball.pos.x - domain.left) % domain.width + domain.left
                    ball.pos.y = (ball.pos.y - domain.top) % domain.height + domain.top

                lines[idx].append(ball.pos.copy())

        all_segments:list[list[Vec2]] = []

        for line in lines:
            idx = 0
            while idx < len(line)-1:
                if line[idx].distance_to(line[idx+1]) < 100:
                    break    
                idx += 1

            segments = [[line[idx]]]  
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
    # random.seed(0)
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