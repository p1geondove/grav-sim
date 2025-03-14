from __future__ import annotations
import numpy as np
from const import Var
from ui_elements import Ball

class PhysicsEngine:
    def __init__(self, dt:float, method=None, collisions:bool=False, buffer:int=100, balls:list[Ball] | PhysicsEngine = None):
        self.buffer = buffer # size of buffer. half the buffer is for trajectory, the other for actual history. the "current" state is in the middle
        self.dt = dt
        self.collision_enabled = collisions
        self.counter = 0

        if method is None:
            self.method = self.euler_step

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
            self.masses:np.ndarray = np.ones((1,),dtype=Var.dtype)
            self.radii:np.ndarray = np.ones((1,),dtype=Var.dtype)
        
        self.history_pos = self.positions[np.newaxis, :] # list of oldest to newest set of positions [t-3, t-2, t-1, t]
        self.history_vel = self.velocities[np.newaxis, :]
        self.update_physics()

    def __repr__(self):
        return f'<Phys amt:{len(self.positions)} buf:{len(self.history_pos)}>'
    
    def add_ball(self, ball: Ball):
        """Add ball to engine"""
        index = max(0, len(self.history_pos) - self.buffer // 2)
        history_slice = slice(index, None)
        self.positions = np.vstack((self.positions, ball.pos))
        self.velocities = np.vstack((self.velocities, ball.vel))
        self.masses = np.append(self.masses, ball.mass)
        self.radii = np.append(self.radii, ball.radius)
        time_steps = len(self.history_pos[history_slice])
        old_ball_count = self.history_pos.shape[1]
        new_ball_history = np.tile(ball.pos, (time_steps, 1))
        new_ball_vel_history = np.tile(ball.vel, (time_steps, 1))
        new_history_pos = np.zeros((time_steps, old_ball_count + 1, 2), dtype=self.history_pos.dtype)
        new_history_vel = np.zeros((time_steps, old_ball_count + 1, 2), dtype=self.history_vel.dtype)
        new_history_pos[:, :-1, :] = self.history_pos[history_slice]
        new_history_vel[:, :-1, :] = self.history_vel[history_slice]
        new_history_pos[:, -1, :] = new_ball_history
        new_history_vel[:, -1, :] = new_ball_vel_history
        self.history_pos = new_history_pos
        self.history_vel = new_history_vel
        self.update_physics()

    def remove_ball(self, index):
        """Remove ball from engine"""
        self.positions = np.delete(self.positions, index, axis=0)
        self.velocities = np.delete(self.velocities, index, axis=0)
        self.masses = np.delete(self.masses, index)
        self.radii = np.delete(self.radii, index)
        self.history_pos = np.delete(self.history_pos, index, axis=1)
        self.history_vel = np.delete(self.history_vel, index, axis=1)
        self.update_physics()

    def compute_accelerations(self):
        """Calculates accelerations"""
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
   
    def update_physics(self, steps=Var.steps_per_draw, dt:float=None, method:function=None, collision:bool=None):
        """Update physics"""
        if dt:
            self.dt = float(dt)
        if method:
            self.method = method
        if collision:
            self.collision_enabled = bool(collision)
        
        for _ in range(steps):
            self.method(self.dt)
        
        self.history_pos = np.concatenate((self.history_pos, [self.positions]))
        self.history_vel = np.concatenate((self.history_vel, [self.velocities]))
        
        while len(self.history_pos) < self.buffer//2:
            self.counter += 1
            for _ in range(steps):
                self.method(self.dt)
            self.history_pos = np.concatenate((self.history_pos, [self.positions]))
            self.history_vel = np.concatenate((self.history_vel, [self.velocities]))
        
        self.history_pos = self.history_pos[-self.buffer:]
        self.history_vel = self.history_vel[-self.buffer:]
        self.counter = 0

    def update_balls(self, balls:list[Ball]):
        """Update existing balls position and velicoty"""
        index = max(0, len(self.history_pos) - self.buffer//2)
        for i, ball in enumerate(balls):
            ball.pos = self.history_pos[index][i]
            ball.vel = self.history_vel[index][i]
    
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

        self.history_pos = self.positions[np.newaxis,:]
        self.history_vel = self.velocities[np.newaxis,:]
        self.update_physics()

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
        pair_energies = -Var.G * masses_matrix * inv_distances
        return np.sum(pair_energies) / 2.0
    