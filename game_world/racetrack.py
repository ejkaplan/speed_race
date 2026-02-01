import colorsys
from itertools import product
import pickle
from typing import Iterable
import pygame
import numpy as np

Point = tuple[int, int]


def make_color_scheme(n: int) -> dict[int, pygame.Color]:
    colors = [colorsys.hsv_to_rgb(h, 1, 1) for h in np.linspace(0, 1, n, False)]
    colors = [(int(255 * c[0]), int(255 * c[1]), int(255 * c[2])) for c in colors]
    return {i + 1: pygame.Color(color) for i, color in enumerate(colors)}


def bresenham(x0: int, y0: int, x1: int, y1: int) -> Iterable[Point]:
    # Taken from https://github.com/encukou/bresenham/tree/master
    dx = x1 - x0
    dy = y1 - y0

    x_sign = 1 if dx > 0 else -1
    y_sign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = x_sign, 0, 0, y_sign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, y_sign, x_sign, 0

    D = 2 * dy - dx
    y = 0

    for x in range(dx + 1):
        yield x0 + x * xx + y * yx, y0 + x * xy + y * yy
        if D >= 0:
            y += 1
            D -= 2 * dx
        D += 2 * dy


class RaceTrack:

    def __init__(
        self,
        walls: np.ndarray,
        active: np.ndarray,
        buttons: np.ndarray,
        colors: np.ndarray,
        target: Point,
        spawn: Point,
        screen_size: Point,
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
        self.spawn = spawn
        self.target = target
        self.surface = self.render(*screen_size)
        self.screen_size = screen_size

    def render(self, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill("#ffffff")
        rows, cols = self.shape
        w, h = width / cols, height / rows
        star_img = pygame.image.load("star.png")
        star_img = pygame.transform.scale(star_img, (0.8 * w, 0.8 * h))
        triangle = pygame.Surface((0.8 * w, 0.8 * w))
        triangle.fill("#ffffff")
        pygame.draw.polygon(
            triangle, "#278B00", [(0.4 * w, 0), (0.8 * w, 0.8 * h), (0, 0.8 * h)]
        )
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
            elif (row, col) == self.target:
                surface.blit(star_img, (x + 0.1 * w, y + 0.1 * h))
            if (row, col) == self.spawn:
                surface.blit(triangle, (x + 0.1 * w, y + 0.1 * h))
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

    def find_traversable_cells(self) -> set[Point]:
        output = np.where((self.walls == 0).astype(int) | (1 - self.active).astype(int))
        return set(zip(output[0].astype(int), output[1].astype(int)))

    def line_traversable(self, start: Point, end: Point) -> bool:
        safe_cells = self.find_traversable_cells()
        line = set(bresenham(*start, *end))
        return safe_cells >= line

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

    def save(self, filename: str) -> None:
        save_data = (
            self.walls,
            self.active,
            self.buttons,
            self.colors,
            self.target,
            self.spawn,
            self.screen_size,
            self.color_scheme,
        )
        with open(filename, "wb") as f:
            pickle.dump(save_data, f)


def load_track(filename: str) -> RaceTrack:
    with open(filename, "rb") as f:
        data = pickle.load(f)
    track = RaceTrack(*data)
    track.surface = track.render(*track.screen_size)
    return track


def blank_track(
    grid_size: tuple[int, int], screen_size: tuple[int, int], n_colors: int
) -> RaceTrack:
    walls = np.zeros(grid_size)
    buttons = np.zeros(grid_size)
    active = np.ones(grid_size)
    colors = np.zeros(grid_size)
    theme = make_color_scheme(n_colors)
    return RaceTrack(
        walls,
        active,
        buttons,
        colors,
        (grid_size[0] - 1, grid_size[1] - 1),
        (0, 0),
        screen_size,
        theme,
    )


def main():
    track = load_track("track.pkl")
    print(track.line_traversable((0, 0), (0, 9)))


if __name__ == "__main__":
    main()
