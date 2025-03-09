from ui_elements import Ball
from util import Vec2
from random import randint

ARRANGEMENTS: list[list[Ball]] = [
    # [
    #     Ball(1, (258.5,400), (0,-1.5)),
    #     Ball(5, (270,400), (0,-2.9)),
    #     Ball(20, (350,400), (0,2)),
    #     Ball(20, (400,400), (0,-2)),
    #     Ball(5, (480,400), (0,2.9)),
    #     Ball(1, (491.5,400), (0,1.5)),
    # ],
    # [
    #     Ball(20, (300,300), Vec2(2**0.5,0).rotate(-60)),
    #     Ball(20, (500,300), Vec2(2**0.5,0).rotate(60)),
    #     Ball(20, (400,300+100*3**0.5), Vec2(2**0.5,0).rotate(180))
    # ],
    [
        Ball(20, (400,300), Vec2(2,0)),
        Ball(20, (500,400), Vec2(0,2)),
        Ball(20, (400,500), Vec2(-2,0)),
        Ball(20, (300,400), Vec2(0,-2)),
    ]
]

def gyat(idx:int = None):
    if idx is None:
        idx = randint(0,len(ARRANGEMENTS)-1)
    return [ball.copy() for ball in ARRANGEMENTS[idx]], idx