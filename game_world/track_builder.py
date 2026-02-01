import select
import sys
from turtle import color

import pygame
import pygame.locals

from racetrack import RaceTrack, blank_track


class Button:

    def __init__(
        self, x: float, y: float, width: float, height: float, surface: pygame.Surface
    ) -> None:
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.surface = pygame.transform.scale(surface, (width, height))

    def point_inside(self, x: float, y: float) -> bool:
        return self.x < x < self.x + self.width and self.y < y < self.y + self.height

    def blit(self, surface: pygame.Surface, selected: bool) -> None:
        surface.blit(self.surface, (self.x, self.y))
        if selected:
            pygame.draw.rect(
                surface,
                "#000000",
                (self.x - 10, self.y - 10, self.width + 20, self.height + 20),
                5,
            )


def make_solid_colored_button(
    x: float, y: float, width: float, height: float, color: pygame.Color
) -> Button:
    surface = pygame.Surface((width, height))
    surface.fill(color)
    return Button(x, y, width, height, surface)


def main():
    fps = 60
    fps_clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((800, 600))

    track = blank_track((50, 50), (600, 600), 7)
    color_buttons = {
        i: make_solid_colored_button(620, 20 + 50 * (i + 1), 30, 30, color)
        for i, color in track.color_scheme.items()
    }
    circle = pygame.Surface((30, 30))
    pygame.draw.circle(circle, "#a4a4a4", (15, 15), 10)
    star_img = pygame.image.load("star.png")
    star_img = pygame.transform.scale(star_img, (25, 25))

    type_buttons = {
        "wall": make_solid_colored_button(700, 20, 30, 30, pygame.Color("#ffffff")),
        "button": Button(700, 70, 30, 30, circle),
        "target": Button(700, 120, 30, 30, star_img),
    }
    selected_color = -1
    selected_kind = "wall"
    pressed = False

    cursor_size = 1

    while True:
        screen.fill("#A6A6A6")
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.locals.MOUSEBUTTONDOWN:
                pressed = True
                for i, button in color_buttons.items():
                    if button.point_inside(mx, my):
                        selected_color = i
                for kind, button in type_buttons.items():
                    if button.point_inside(mx, my):
                        selected_kind = kind
            if event.type == pygame.locals.MOUSEBUTTONUP:
                pressed = False
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.K_UP:
                    cursor_size += 1
                elif event.key == pygame.K_DOWN:
                    cursor_size = max(1, cursor_size - 1)

        click_track(
            track,
            selected_color,
            selected_kind,
            pressed,
            mx,
            my,
            cursor_size,
        )

        screen.blit(track.surface, (0, 0))
        for i, button in color_buttons.items():
            button.blit(screen, i == selected_color)
        for kind, button in type_buttons.items():
            button.blit(screen, kind == selected_kind)

        pygame.display.flip()
        fps_clock.tick(fps)


def click_track(
    track: RaceTrack,
    selected_color: int,
    selected_kind: str,
    pressed: bool,
    mx: int,
    my: int,
    cursor_size: int,
):
    if not pressed or not track.surface.get_rect().collidepoint(mx, my):
        return
    row, col = track.get_grid_coord(mx, my)
    for r in range(row - cursor_size + 1, row + cursor_size):
        for c in range(col - cursor_size + 1, col + cursor_size):
            if r not in range(track.shape[0]) or c not in range(track.shape[1]):
                continue
            match selected_kind:
                case "wall":
                    if selected_color == 0:
                        track.walls[r, c] = 0
                    else:
                        track.walls[r, c] = 1
                    track.targets[r, c] = 0
                    track.colors[r, c] = selected_color
                case "button":
                    if selected_color == 0:
                        track.buttons[r, c] = 0
                    else:
                        track.buttons[r, c] = 1
                    track.walls[r, c] = 0
                    track.targets[r, c] = 0
                    track.colors[r, c] = selected_color
                case "target":
                    track.targets[r, c] = 1 - track.targets[r, c]
                    track.walls[r, c] = 0
                    track.buttons[r, c] = 0
                    track.colors[r, c] = 0
    track.surface = track.render(track.surface.get_width(), track.surface.get_height())


if __name__ == "__main__":
    main()
