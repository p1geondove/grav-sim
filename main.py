import pygame
import sys
from playground import Playground
from startpos import ARRANGEMENTS
from const import steps_per_update

def main():
    # random.seed(0)
    pygame.font.init()
    window = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
    playground = Playground(window)
    playground.balls = ARRANGEMENTS[0]
    clock = pygame.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            playground.handle_event(event)
        
        # print('\n'+'\n'.join([str(ball) for ball in playground.balls]))
        playground.update()
        playground.draw()
        pygame.display.flip()
        clock.tick(60)
        print(f'fps: {clock.get_fps():.0f}', end=f'{" "*10}\r')

if __name__ == '__main__':
    main()