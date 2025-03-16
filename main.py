import pygame
from scripts import *

def main():
    pygame.font.init()
    get_monitor()
    window = pygame.display.set_mode(Var.window_size, pygame.SRCALPHA | pygame.RESIZABLE)
    playground = Playground(window)
    clock = pygame.time.Clock()
    set_icon()

    while True:  
        for event in pygame.event.get():
            playground.handle_event(event)

        playground.update()
        playground.draw()
        pygame.display.flip()
        clock.tick(Var.framerate_limit)
        pygame.display.set_caption(f'FPS: {clock.get_fps():.0f}')

if __name__ == '__main__':
    main() 