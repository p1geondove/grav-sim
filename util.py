from itertools import combinations
from pygame import Vector2 as Vec2
from pygame import Rect
from ui_elements import Ball

def trajectories(balls:list[Ball], dt:int, steps:int, domain:Rect = None) -> list[list[tuple[Vec2, float]]]:
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

def points_on_grid(grid:int, radius:float, pos:Vec2):
    grid = int(grid)
    near = lambda x: int(x - x % grid + grid)
    left = near(pos.x - radius)
    right = near(pos.x + radius)
    for x in range(left, right, grid):
        dx = abs(x-pos.x)
        height = (radius**2 - dx**2) ** 0.5
        bottom = near(pos.y - height)
        top = near(pos.y + height)
        for y in range(bottom, top, grid):
            yield Vec2(x,y)