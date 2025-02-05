from itertools import combinations
from pygame import Vector2 as Vec2
from pygame import Rect
from ui_elements import Ball

def trajectories(balls:list[Ball], dt:int, steps:int, min_size:float, max_size:float, domain:Rect = None):
    balls = [ball.copy() for ball in balls]
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

    for line in lines:
        idx = 0
        while idx < len(line)-1:
            if line[idx].distance_to(line[idx+1]) < 100:
                break    
            idx += 1
        
        segment = ([line[idx]], [0]) # tuple of 2 lists, one for x,y pos and one for distance for lerp
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

def points_on_grid(grid:float, radius:float, pos:Vec2):
    near = lambda x : x - x % grid + grid
    left = near(pos.x - radius)
    right = near(pos.x + radius)
    while left < right:
        dx = abs(left - pos.x)
        height = (radius**2 - dx**2) ** 0.5
        bottom = near(pos.y - height)
        top = near(pos.y + height)
        while bottom < top:
            yield Vec2(left,bottom)
            bottom += grid
        left += grid
