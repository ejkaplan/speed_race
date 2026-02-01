import colorsys
from itertools import product
import sys
import pygame
import pygame.locals
import numpy as np


def make_color_scheme(n: int) -> dict[int, pygame.Color]:
    colors = [colorsys.hsv_to_rgb(h, 1, 1) for h in np.linspace(0, 1, n, False)]
    colors = [(int(255 * c[0]), int(255 * c[1]), int(255 * c[2])) for c in colors]
    return {i + 1: pygame.Color(color) for i, color in enumerate(colors)}


class RaceTrack:

    def __init__(
        self,
        walls: np.ndarray,
        active: np.ndarray,
        buttons: np.ndarray,
        colors: np.ndarray,
        targets: np.ndarray,
        screen_size: tuple[int, int],
        color_scheme: dict[int, pygame.Color],
    ) -> None:
        if not (walls.shape == active.shape == buttons.shape):
            raise ValueError("All map layers must be same shape.")
        self.walls = walls
        self.active = active
        self.buttons = buttons
        self.colors = colors
        self.shape = walls.shape
        self.color_scheme = {i: pygame.Color(c) for i, c in color_scheme.items()} | {
            -1: pygame.Color(0, 0, 0),
            0: pygame.Color(255, 255, 255),
        }
        self.targets = targets
        self.surface = self.render(*screen_size)

    def render(self, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill("#ffffff")
        rows, cols = self.shape
        w, h = width / cols, height / rows
        star_img = pygame.image.load("star.png")
        star_img = pygame.transform.scale(star_img, (0.8 * w, 0.8 * h))
        for row, col in product(range(rows), range(cols)):
            x, y = col * w, row * h
            active = self.active[row, col]
            wall = self.walls[row, col]
            color_type = self.colors[row, col]
            button = self.buttons[row, col]
            color = self.color_scheme[color_type]
            if wall:
                pygame.draw.rect(surface, color, (x, y, w, h), 0 if active else 5)
            elif button:
                pygame.draw.circle(
                    surface, color, (x + w / 2, y + h / 2), 0.4 * min(w, h)
                )
            elif self.targets[row, col]:
                surface.blit(star_img, (x + 0.1 * w, y + 0.1 * h))
        return surface

    def find_wall_locations(
        self, color: int | None = None, active: bool | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        output = np.where(
            self.walls
            & (color is None or self.colors == color)
            & (active is None or self.active)
        )
        assert len(output) == 2
        return output

    def find_traversable_cells(self) -> tuple[np.ndarray, np.ndarray]:
        output = np.where(self.walls == 0 | 1 - self.active)
        assert len(output) == 2
        return output

    def toggle(self, color: int) -> None:
        self.active[self.find_wall_locations(color)] = (
            1 - self.active[self.find_wall_locations(color)]
        )
        self.surface = self.render(self.surface.get_width(), self.surface.get_height())

    def get_grid_coord(self, x: float, y: float) -> tuple[int, int]:
        screen_width, screen_height = (
            self.surface.get_width(),
            self.surface.get_height(),
        )
        rows, cols = self.shape
        w, h = screen_width / cols, screen_height / rows
        return int(y / h), int(x / w)


def blank_track(
    grid_size: tuple[int, int], screen_size: tuple[int, int], n_colors: int
) -> RaceTrack:
    walls = np.zeros(grid_size)
    buttons = np.zeros(grid_size)
    active = np.ones(grid_size)
    colors = np.zeros(grid_size)
    targets = np.zeros(grid_size)
    theme = make_color_scheme(n_colors)
    return RaceTrack(walls, active, buttons, colors, targets, screen_size, theme)
