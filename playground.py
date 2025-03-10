from __future__ import annotations
import pygame
from pygame.locals import *
import sys
import numpy as np

from physics import PhysicsEngine
from const import Fonts, Colors, Var
from ui_elements import Ball, Button, Slider, EnergyGraph
from startpos import get_random

class Playground:
    class Camera:
        def __init__(self, playground:Playground):
            self.window:pygame.Surface = playground.window
            self.surface:pygame.Surface = playground.window.copy()
            self.pos:np.ndarray = np.zeros(2, dtype=Var.dtype)
            self.zoom_val:float = 1.0
            self.playground:Playground = playground

        def move(self, pixel_pos):
            pixel_pos = np.array(pixel_pos, dtype=Var.dtype)
            self.pos += pixel_pos * self.zoom_val

        def zoom(self, zoom_amt):
            if not 2**-10 < self.zoom_val/2**zoom_amt < 2**5: 
                return
            
            mouse_pos = np.array(self.playground.mouse_pos, dtype=Var.dtype)

            if zoom_amt > 0:
                self.zoom_val /= 2**zoom_amt
                self.pos -= mouse_pos * self.zoom_val
            else:
                self.pos += mouse_pos * self.zoom_val
                self.zoom_val /= 2**zoom_amt

        def get_rect(self):
            window_size = np.array(self.window.get_size(), dtype=Var.dtype)
            size = window_size / self.zoom_val
            return Rect(self.pos[0], self.pos[1], size[0], size[1])

        def center(self):
            if not len(self.playground.balls): 
                return
                
            masses = np.array([b.radius**2 for b in self.playground.balls])
            positions = np.array([b.pos for b in self.playground.balls])
            
            center_pos = np.sum(positions * masses[:, np.newaxis], axis=0) / np.sum(masses)
            center_screen = self.to_screen_pos(center_pos)
            
            pygame.draw.aacircle(self.surface, Colors.center2, 
                                (int(center_screen[0]), int(center_screen[1])), 9, 0, True, False, True, False)
            pygame.draw.aacircle(self.surface, Colors.center, 
                                (int(center_screen[0]), int(center_screen[1])), 10, 1)

        def vel(self):
            for ball in self.playground.balls:
                start = self.to_screen_pos(ball.pos)
                end = self.to_screen_pos(ball.pos + ball.vel * 30)
                pygame.draw.aaline(self.surface, Colors.vel_vector, 
                                (int(start[0]), int(start[1])), 
                                (int(end[0]), int(end[1])))

        def grid(self):
            grid_radius = self.zoom_val * min(self.window.get_size()) * 0.3
            mouse_pos = self.to_world_pos(np.array(self.playground.mouse_pos))
            grid_size = self.playground.grid_size
            left = int((mouse_pos[0] - grid_radius) // grid_size) * grid_size
            right = int((mouse_pos[0] + grid_radius) // grid_size + 1) * grid_size
            bottom = int((mouse_pos[1] - grid_radius) // grid_size) * grid_size
            top = int((mouse_pos[1] + grid_radius) // grid_size + 1) * grid_size
            x_coords = np.arange(left, right, grid_size)
            y_coords = np.arange(bottom, top, grid_size)
            xx, yy = np.meshgrid(x_coords, y_coords)
            grid_points = np.column_stack((xx.flatten(), yy.flatten()))
            distances = np.linalg.norm(grid_points - mouse_pos, axis=1)
            valid_points = grid_points[distances <= grid_radius]
            valid_distances = distances[distances <= grid_radius]
            lerp_vals = np.minimum(np.maximum(0, valid_distances / grid_radius), 1)
            screen_points = np.array([self.to_screen_pos(point) for point in valid_points])
            
            for i, point in enumerate(screen_points):
                lerp_val = lerp_vals[i]
                color_mid = Colors.grid.lerp(Colors.background, lerp_val)
                color_around = color_mid.lerp(Colors.background, 0.6)
                px, py = int(point[0]), int(point[1])
                self.surface.set_at((px, py), color_mid)
                self.surface.set_at((px-1, py), color_around)
                self.surface.set_at((px, py-1), color_around)
                self.surface.set_at((px+1, py), color_around)
                self.surface.set_at((px, py+1), color_around)

        def balls(self):
            for ball in self.playground.balls:
                screen_pos = self.to_screen_pos(ball.pos)
                radius = ball.radius / self.zoom_val
                pygame.draw.aacircle(self.surface, ball.color, 
                                (int(screen_pos[0]), int(screen_pos[1])), 
                                radius, 2)

        def to_world_pos(self, screen_pos):
            """Convert screen coordinates to world coordinates"""
            screen_pos = np.array(screen_pos, dtype=Var.dtype)
            return screen_pos * self.zoom_val - self.pos

        def to_screen_pos(self, world_pos):
            """Convert world coordinates to screen coordinates"""
            world_pos = np.array(world_pos, dtype=Var.dtype)
            return (world_pos + self.pos) / self.zoom_val

        def draw(self):
            self.surface.fill('grey15')

            if self.playground.dragging or self.playground.pressed_ctrl:
                self.grid()

            try:
                self.balls()
                for name, actve in self.playground.infos_states.items():
                    if actve: self.functions[name](self)
            except OverflowError:
                self.playground.reset()

            self.ui()

            return self.surface

        def ui(self):
            for button in self.playground.buttons_debug:
                self.surface.blit(button.surface, button.pos)

            for button in self.playground.buttons_solver:
                self.surface.blit(button.surface, button.pos)

            for slider in self.playground.sliders:
                self.surface.blit(slider.surface, slider.rect.topleft)
            
            self.surface.blit(self.playground.energy_graph.draw(), self.playground.energy_graph.position)

            self.debug_txt()

        def debug_txt(self):
            amt_txt = Fonts.medium.render(str(len(self.playground.balls)), True, Colors.text)
            size = np.array(self.surface.get_size(), dtype=Var.dtype)
            text_size = np.array(amt_txt.get_size(), dtype=Var.dtype)
            pos = size - text_size - Var.pad
            self.surface.blit(amt_txt, (int(pos[0]), int(pos[1])))

        functions = {
            'center':center,
            'velocity':vel,
        }
    
    def __init__(self, window:pygame.Surface):
        self.window = window
        self.domain = window.get_rect()

        self.dt = 0.03
        self.grid_size = 20
        self.trail_size = 300

        self.playing = False
        self.pressed_alt = False
        self.pressed_ctrl = False
        self.pressed_left = False
        self.pressed_right = False
        self.dragging = False
        self.show_grid = False
        self.collisions = False
        
        self.mouse_pos = np.array((0,0),dtype=Var.dtype)
        self.infos_states = {n:False for n in self.Camera.functions}
        self.solver_method = 'euler'

        self.balls, self.start_balls = get_random()
        self.physics = PhysicsEngine(self.balls)
        self.energy_graph = EnergyGraph((Var.window_size-Var.energy_graph_size, Var.energy_graph_size))

        fontheight = Fonts.large.get_height() + Var.pad
        
        self.buttons_debug:list[Button] = []
        for y, (name, state) in enumerate(self.infos_states.items()):
            color = Colors.active if state else Colors.inactive
            self.buttons_debug.append(Button((Var.pad, Var.pad + y*fontheight), name, color))
        self.buttons_debug.append(Button((Var.pad,Var.pad+(y+1)*fontheight), 'collision', Colors.inactive))

        self.buttons_solver:list[Button] = []
        for idx, name in enumerate(['euler','runge_kutta']):
            button = Button((self.window.width - Fonts.large.size(name)[0] - Var.pad, Var.pad + fontheight * idx), name, Colors.inactive)
            self.buttons_solver.append(button)
        self.buttons_solver[0].color = Colors.active
        self.buttons_solver[0].draw()

        self.sliders = [
            Slider('dt', 0, self.dt, (Var.pad, int(self.window.height-Var.slider_size[1]-Var.pad), int(Var.slider_size[0]), int(Var.slider_size[1]))),
            Slider('fps', 0, 300, (Var.pad, int(self.window.height-Var.slider_size[1]*2-Var.pad*2), int(Var.slider_size[0]), int(Var.slider_size[1]))),
        ]

        self.camera = self.Camera(self)
        self.draw()

    def draw(self):
        self.window.blit(self.camera.draw(), (0,0))

    def handle_event(self, event:pygame.Event):
        calls = []

        for idx, ball in enumerate(self.balls):
            if any(s.hover for s in self.sliders): break
            if calls_ball := ball.handle_event(event, self.grid_size, self.camera):
                if 'dragged_ball' in calls_ball:
                    self.physics.from_balls(self.balls)
                    self.dragging = False
                calls.extend(calls_ball)
        
        for button in self.buttons_debug:
            if button.handle_event(event):
                if button.text in self.infos_states:
                    self.infos_states[button.text] = not self.infos_states[button.text]
                    button.color = Colors.active if self.infos_states[button.text] else Colors.inactive
                elif button.text == 'collision':
                    self.collisions = not self.collisions
                    button.color = Colors.active if self.collisions else Colors.inactive
                button.draw()
        
        for button in self.buttons_solver:
            if button.handle_event(event):
                self.solver_method = button.text
                for b in self.buttons_solver:
                    b.color = Colors.active if b is button else Colors.inactive
                    b.draw()

        if self.sliders[0].handle_event(event):
            self.dt = self.sliders[0].val
            self.dragging = False
        
        if self.sliders[1].handle_event(event):
            Var.framerate_limit = int(self.sliders[1].val)
            self.dragging = False

        if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                self.playing = not self.playing

            elif event.key == K_LCTRL:
                self.pressed_ctrl = True

            elif event.key == K_LALT:
                self.pressed_alt = True

            elif event.key == K_r:
                if any(b.hover for b in self.balls): # reset velocity from hovered ball
                    index = [b.hover for b in self.balls].index(True)
                    self.physics.velocities[index][0] = 0
                    self.physics.velocities[index][1] = 0
                    
                elif self.balls: # if no hovered ball, reset simulation
                    self.reset()
                 
        elif event.type == KEYUP:
            if event.key == K_LCTRL:
                self.pressed_ctrl = False

            elif event.key == K_LALT:
                self.pressed_alt = False

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                hover = any((
                    any(b.hover for b in self.balls),
                    any(b.hover for b in self.buttons_debug),
                    any(b.hover for b in self.buttons_solver),
                    any(s.hover for s in self.sliders)
                ))
                if not hover: # careful with empty balls list
                    self.dragging = True
                

            elif event.button == 2:
                for idx, ball in enumerate(self.balls):
                    if ball.hover:
                        del self.balls[idx]
                        self.physics.remove_ball(idx)
                        break
                else:
                    ball = Ball(position=self.camera.to_world_pos(event.pos))
                    self.balls.append(ball)
                    self.physics.add_ball(ball)
            
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
            
            self.grid_size = min(max(2**-5, self.grid_size), 2**10)
            self.grid_size = min(max(self.camera.zoom_val * 8, self.grid_size), self.camera.zoom_val * 64)
                
        elif event.type == MOUSEMOTION:
            self.mouse_pos = np.array(event.pos,dtype=Var.dtype)
            if self.dragging:
                self.show_grid = True
                self.camera.move(event.rel)

        elif event.type == VIDEORESIZE:
            self.camera.surface = pygame.Surface(event.size)

            for idx, slider in enumerate(self.sliders):
                slider.rect = pygame.Rect((Var.pad, self.window.height-35*(idx+1), 100, 30))
    
            for button in self.buttons_solver:
                button.pos[0] = self.window.width - Fonts.large.size(button.text)[0] - Var.pad

            self.energy_graph.resize((
                self.window.size - Var.energy_graph_size,
                Var.energy_graph_size
            ))

        self.show_grid = self.show_grid or self.pressed_ctrl

    def update(self, steps=1):
        if not self.playing: 
            return
            
        steps = int(max(1, steps))
        self.physics.update_physics(self.dt, self.solver_method, self.collisions, steps)
        self.physics.update_balls(self.balls)

        self.energy_graph.update(
            self.physics.potential(),
            self.physics.kinetic()
        )

    def reset(self):
        self.balls = get_random(self.start_balls)[0]
        self.physics = PhysicsEngine(self.balls)
        self.camera.pos = np.array((0,0),Var.dtype)
        self.camera.zoom_val = 1
