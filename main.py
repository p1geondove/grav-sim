if __name__ == '__main__':
    import pygame # >:)
    from scripts import *

    playground = Playground()
    clock = pygame.time.Clock()

    while True:  
        for event in pygame.event.get():
            playground.handle_event(event)

        playground.update()
        pygame.display.flip()
        clock.tick(Var.framerate_limit)
        pygame.display.set_caption(f'FPS: {clock.get_fps():.0f}')
