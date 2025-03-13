import pygame
from playground import Playground
from const import Var
from util import resource_path

def main(): 
    pygame.font.init()
    window = pygame.display.set_mode(Var.window_size, pygame.SRCALPHA | pygame.RESIZABLE)
    pygame.display.set_icon(pygame.image.load(resource_path('./assets/logo.ico')))
    playground = Playground(window)
    clock = pygame.time.Clock()

    while True:  
        for event in pygame.event.get():
            playground.handle_event(event)

        playground.update(Var.steps_per_draw)
        playground.draw()
        pygame.display.flip()
        clock.tick(Var.framerate_limit)
        pygame.display.set_caption(f'FPS: {clock.get_fps():.0f}')

if __name__ == '__main__':
    main() 