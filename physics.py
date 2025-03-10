from __future__ import annotations
import numpy as np
from const import Var
from ui_elements import Ball

import ntimer

class PhysicsEngine:
    def __init__(self, balls:list[Ball] | PhysicsEngine = None):
        if isinstance(balls, list):
            if isinstance(balls[0], Ball):
                self.from_balls(balls)

        elif isinstance(balls, PhysicsEngine):
            self.positions:np.ndarray = balls.positions.copy()
            self.velocities:np.ndarray = balls.velocities.copy()
            self.masses:np.ndarray = balls.masses.copy()
            self.radii:np.ndarray = balls.radii.copy()

        else:
            self.positions:np.ndarray = np.zeros((1,2),dtype=Var.dtype)
            self.velocities:np.ndarray = np.zeros((1,2),dtype=Var.dtype)
            self.masses:np.ndarray = np.zeros((1,),dtype=Var.dtype)
            self.radii:np.ndarray = np.zeros((1,),dtype=Var.dtype)
        
        self.collision_enabled = False
        self.history = [self.positions.copy()]
        self.trajectory = []

    def add_ball(self, ball:Ball):
        """Add ball to engine"""
        self.positions = np.vstack((self.positions, ball.pos))
        self.velocities = np.vstack((self.velocities, ball.vel))
        self.masses = np.append(self.masses, ball.mass)
        self.radii = np.append(self.radii, ball.radius)
    
    def remove_ball(self, index):
        """Remove ball from engine"""
        delete = lambda args : np.reshape(np.delete(args[0],(args[1]*2,args[1]*2+1)),(len(args[0])-1,2))
        self.positions = delete((self.positions, index))
        self.velocities = delete((self.velocities, index))
        self.masses = np.delete(self.masses, index)
        self.radii = np.delete(self.radii, index)

    def compute_accelerations(self):
        """Calculates accelerations used for Runge-Kutta"""
        diff = self.positions[:, np.newaxis, :] - self.positions[np.newaxis, :, :]
        distances_sq = np.sum(diff**2, axis=2)
        np.fill_diagonal(distances_sq, 1.0)
        inv_distances_cubed = (1/np.sqrt(distances_sq))**3
        np.fill_diagonal(inv_distances_cubed, 0.0)
        masses_matrix = self.masses[:, np.newaxis] * self.masses[np.newaxis, :]
        forces = -Var.G * masses_matrix[..., np.newaxis] * diff * inv_distances_cubed[..., np.newaxis]
        accelerations = np.sum(forces, axis=1) / self.masses[:, np.newaxis]
        return accelerations

    def euler_step(self, dt):
        """Euler step with collision check"""
        accelerations = self.compute_accelerations()
        self.velocities += accelerations * dt
        self.positions += self.velocities * dt
        if self.collision_enabled:
            self.handle_collisions()
    
    def runge_kutta_step(self, dt):
        """Runge-Kutta step with collisions check"""
        orig_pos = self.positions.copy()
        orig_vel = self.velocities.copy()
        
        k1_acc = self.compute_accelerations()
        k1_vel = self.velocities.copy()
        
        self.positions = orig_pos + k1_vel * (dt * 0.5)
        self.velocities = orig_vel + k1_acc * (dt * 0.5)
        k2_acc = self.compute_accelerations()
        k2_vel = self.velocities.copy()
        
        self.positions = orig_pos + k2_vel * (dt * 0.5)
        self.velocities = orig_vel + k2_acc * (dt * 0.5)
        k3_acc = self.compute_accelerations()
        k3_vel = self.velocities.copy()
        
        self.positions = orig_pos + k3_vel * dt
        self.velocities = orig_vel + k3_acc * dt
        k4_acc = self.compute_accelerations()
        k4_vel = self.velocities.copy()
        
        self.positions = orig_pos + (dt/6.0) * (k1_vel + 2*k2_vel + 2*k3_vel + k4_vel)
        self.velocities = orig_vel + (dt/6.0) * (k1_acc + 2*k2_acc + 2*k3_acc + k4_acc)
        
        if self.collision_enabled:
            self.handle_collisions()

    def handle_collisions(self):
        """Handles collisions between balls as perfect elastic collision"""
        diff = self.positions[:, np.newaxis, :] - self.positions[np.newaxis, :, :]
        distances:np.ndarray = np.linalg.norm(diff, axis=-1)
        combined_radii = self.radii[:, np.newaxis] + self.radii[np.newaxis, :]
        
        for i, j in np.argwhere(np.triu(distances < combined_radii,1)):
            direction = diff[i, j] / distances[i, j]
            overlap = combined_radii[i, j] - distances[i, j]
            ratio_i = self.masses[j] / (self.masses[i] + self.masses[j])
            ratio_j = self.masses[i] / (self.masses[i] + self.masses[j])
            self.positions[i] += (direction * overlap * ratio_i)
            self.positions[j] -= (direction * overlap * ratio_j)
            rel_vel = self.velocities[j] - self.velocities[i]
            v_proj = np.dot(rel_vel, direction)
            
            if 0 < v_proj:
                impulse = 2 * v_proj / (self.masses[i] + self.masses[j])
                self.velocities[i] += direction * (impulse * self.masses[j]) * Var.dampening
                self.velocities[j] += -direction * (impulse * self.masses[i]) * Var.dampening
   
    def update_physics(self, dt, method='runge_kutta', collision=False, steps=1):
        """Update physics"""
        if self.positions.shape == 0: return
        self.collision_enabled = collision
        if method == 'runge_kutta':
            for _ in range(steps):
                self.runge_kutta_step(dt)
        else:
            for _ in range(steps):
                self.euler_step(dt)

    def update_balls(self, balls:list[Ball]):
        """Update existing balls position and velicoty"""
        for i, ball in enumerate(balls):
            ball.pos = self.positions[i]
            ball.vel = self.velocities[i]
    
    def to_balls(self) -> list[Ball]:
        """Convert Physics-Engine to list of Balls"""
        balls = []
        for index in range(len(self.masses) ):
            balls.append(Ball(
                self.radii[index],
                self.positions[index],
                self.velocities[index],
            ))
        return balls

    def from_balls(self, balls:list[Ball]):
        """Apply position/velocity/etc from list of balls"""
        n = len(balls)
        self.positions = np.zeros((n, 2), dtype=np.float64)
        self.velocities = np.zeros((n, 2), dtype=np.float64)
        self.masses = np.zeros(n, dtype=np.float64)
        self.radii = np.zeros(n, dtype=np.float64)

        for i, ball in enumerate(balls):
            self.positions[i] = ball.pos
            self.velocities[i] = ball.vel
            self.masses[i] = ball.mass
            self.radii[i] = ball.radius

    def kinetic(self):
        vel = np.sum(self.velocities**2, axis=1)
        kin = 0.5 * self.masses * vel
        return np.sum(kin)
    
    def potential(self):
        masses_matrix = self.masses[:, np.newaxis] * self.masses[np.newaxis, :]
        diff = self.positions[:, np.newaxis, :] - self.positions[np.newaxis, :, :]
        distances_sq = np.sum(diff**2, axis=2)
        np.fill_diagonal(distances_sq, np.inf)
        inv_distances = 1.0 / np.sqrt(distances_sq)
        # print(distances_sq)
        pair_energies = -Var.G * masses_matrix * inv_distances
        return np.sum(pair_energies) / 2.0
    