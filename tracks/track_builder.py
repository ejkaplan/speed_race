import sys

import pygame
import pygame.locals


def main():
    fps = 60
    fps_clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((600, 600))

    while True:
        screen.fill("#000000")

        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        fps_clock.tick(fps)


if __name__ == "__main__":
    main()
