from itertools import combinations
from util import Vec2
from ui_elements import Ball
from const import G

def trajectories(balls:list[Ball], dt:int, steps:int, solver:str, min_size:float, max_size:float):
    """
    ## Generate points of future trajectory

    It simulates the balls for n steps and returns the positions.
    Its optimized for drawing, so it takes in min_size and max_size wich sets the size of whats a viable line
    It returns a bunch lists wich can be used in `pygame.draw.lines`
    But be careful it actually returns 2 lists: `list[Vec2]` and `list[float]`
    The second one being a float from 0 to 1 used for lerping/fading the colors

    Args:
        balls (list[Ball]): list of Ball objects
        dt (int): uses constant dt
        steps (int): amount of steps into the future
        min_size (float): smallest line distance
        max_size (float): maximum line distance
        domain (Rect, optional): Optional domain of type Rect. Defaults to None.

    Yields:
        tuple[ list[Vec2], list[float] ]: list of x,y points and list of float from 0-1
    """
    balls = [ball.copy() for ball in balls]
    lines:list[list[Vec2]] = [[b.pos.copy()] for b in balls]

    # get all the positions
    for _ in range(steps):
        update_physics(balls, dt, solver)
        for idx, ball in enumerate(balls):
            lines[idx].append(ball.pos.copy())

    # remove unessecary points
    for line in lines:
        idx = 0
        while idx < len(line)-1:
            if line[idx].distance_to(line[idx+1]) < 100:
                break    
            idx += 1
        
        segment = ([line[idx]], [0])
        pos = None
        for idx, pos in enumerate(line[idx+1:]):
            distance = pos.distance_to(segment[0][-1])
            if min_size < distance < max_size:
                segment[0].append(pos)
                segment[1].append(idx/steps)
            elif distance > 100:
                if len(segment[0]) > 1:
                    yield segment
                    segment = ([line[idx]], [0])
        if pos:
            segment[0].append(pos)
            segment[1].append(idx/steps)
            yield segment

def runge_kutta_step(ball1:Ball, ball2:Ball, dt:float):
    """Fourth-order Runge-Kutta integration for gravitational interaction between two bodies"""
    # Save original values
    orig_pos1 = ball1.pos.copy()
    orig_vel1 = ball1.vel.copy()
    orig_pos2 = ball2.pos.copy()
    orig_vel2 = ball2.vel.copy()
    
    # Function to calculate acceleration based on positions
    def calculate_acceleration(pos1:Vec2, pos2:Vec2, mass1:float, mass2:float):
        # Vector FROM pos1 TO pos2
        r_vec = pos2 - pos1
        distance_squared = r_vec.magnitude_squared()
        
        # Minimum distance to avoid numerical instability
        min_distance_squared = 1.0
        if distance_squared < min_distance_squared:
            distance_squared = min_distance_squared
        
        distance = distance_squared**0.5
        # Normalize direction vector
        force_dir = r_vec / distance if distance > 0 else Vec2(1, 0)
        
        # Force magnitude follows Newton's law of gravitation
        force_magnitude = G * (mass1 * mass2) / distance_squared
        
        # Acceleration vectors point toward each other
        acc1 = force_dir * (force_magnitude / mass1)
        acc2 = -force_dir * (force_magnitude / mass2)
        
        return acc1, acc2
    
    # k1 calculation
    k1_acc1, k1_acc2 = calculate_acceleration(orig_pos1, orig_pos2, ball1.mass, ball2.mass)
    k1_vel1 = orig_vel1.copy()
    k1_vel2 = orig_vel2.copy()
    
    # k2 calculation
    temp_pos1 = orig_pos1 + k1_vel1 * (dt * 0.5)
    temp_pos2 = orig_pos2 + k1_vel2 * (dt * 0.5)
    temp_vel1 = orig_vel1 + k1_acc1 * (dt * 0.5)
    temp_vel2 = orig_vel2 + k1_acc2 * (dt * 0.5)
    
    k2_acc1, k2_acc2 = calculate_acceleration(temp_pos1, temp_pos2, ball1.mass, ball2.mass)
    k2_vel1 = temp_vel1.copy()
    k2_vel2 = temp_vel2.copy()
    
    # k3 calculation
    temp_pos1 = orig_pos1 + k2_vel1 * (dt * 0.5)
    temp_pos2 = orig_pos2 + k2_vel2 * (dt * 0.5)
    temp_vel1 = orig_vel1 + k2_acc1 * (dt * 0.5)
    temp_vel2 = orig_vel2 + k2_acc2 * (dt * 0.5)
    
    k3_acc1, k3_acc2 = calculate_acceleration(temp_pos1, temp_pos2, ball1.mass, ball2.mass)
    k3_vel1 = temp_vel1.copy()
    k3_vel2 = temp_vel2.copy()
    
    # k4 calculation
    temp_pos1 = orig_pos1 + k3_vel1 * dt
    temp_pos2 = orig_pos2 + k3_vel2 * dt
    temp_vel1 = orig_vel1 + k3_acc1 * dt
    temp_vel2 = orig_vel2 + k3_acc2 * dt
    
    k4_acc1, k4_acc2 = calculate_acceleration(temp_pos1, temp_pos2, ball1.mass, ball2.mass)
    k4_vel1 = temp_vel1.copy()
    k4_vel2 = temp_vel2.copy()
    
    # Final position and velocity calculation
    ball1.pos = orig_pos1 + dt/6.0 * (k1_vel1 + 2*k2_vel1 + 2*k3_vel1 + k4_vel1)
    ball1.vel = orig_vel1 + dt/6.0 * (k1_acc1 + 2*k2_acc1 + 2*k3_acc1 + k4_acc1)
    
    ball2.pos = orig_pos2 + dt/6.0 * (k1_vel2 + 2*k2_vel2 + 2*k3_vel2 + k4_vel2)
    ball2.vel = orig_vel2 + dt/6.0 * (k1_acc2 + 2*k2_acc2 + 2*k3_acc2 + k4_acc2)

def euler_step(ball1:Ball, ball2:Ball, dt:float):
    # print('euler')
    """Einfacher Euler-Schritt für Vergleichszwecke"""
    # Vektor zwischen den Körpern
    r_vec = ball2.pos - ball1.pos
    distance_squared = r_vec.magnitude_squared()
    
    # Minimale Entfernung, um Division durch Null zu vermeiden
    min_distance_squared = 1.0
    if distance_squared < min_distance_squared:
        distance_squared = min_distance_squared
    
    # Kraftberechnung
    distance = distance_squared**0.5
    if distance > 0:
        force_dir = r_vec / distance
    else:
        force_dir = Vec2(1, 0)
    
    force_magnitude = G * (ball1.mass * ball2.mass) / distance_squared
    
    # Beschleunigungen berechnen
    acc1 = force_dir * force_magnitude / ball1.mass
    acc2 = -force_dir * force_magnitude / ball2.mass
    
    # Positionen und Geschwindigkeiten aktualisieren
    ball1.vel += acc1 * dt
    ball2.vel += acc2 * dt
    ball1.pos += ball1.vel * dt
    ball2.pos += ball2.vel * dt

def update_physics(balls:list[Ball], dt:float, method='euler', collision=False):
    """Aktualisiert alle Bälle mit der gewählten Integrationsmethode"""
    for ball in balls:
        ball.prev_pos = ball.pos.copy()

    for ball1, ball2 in combinations(balls, 2):
        if method == 'runge_kutta':
            runge_kutta_step(ball1, ball2, dt)
        elif method == 'euler':
            euler_step(ball1, ball2, dt)
    
    if collision:
        for ball1, ball2 in combinations(balls, 2):
            ball1.collide(ball2) # to be continued
