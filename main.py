import pygame
from playground import Playground

def main():
    pygame.font.init()
    window = pygame.display.set_mode((800, 800), pygame.SRCALPHA or pygame.RESIZABLE)
    playground = Playground(window)
    clock = pygame.Clock()

    while True:
        for event in pygame.event.get():
            playground.handle_event(event)
        
        playground.update(100)
        playground.draw()
        pygame.display.flip()
        clock.tick(150)
        # print(f'fps: {clock.get_fps():.0f}', end=f'{" "*10}\r')

if __name__ == '__main__':
    main()