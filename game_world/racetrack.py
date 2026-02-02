from copy import deepcopy
from itertools import product
import pickle
import pygame
import numpy as np

Point = tuple[int, int]


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
    ) -> None:
        if not (walls.shape == active.shape == buttons.shape):
            raise ValueError("All map layers must be same shape.")
        self.walls = walls
        self.active = active
        self.buttons = buttons
        self.colors = colors
        self.shape = walls.shape
        colors_basic = {
            0: "#ffffff",
            1: "#000000",
            2: "#d20000",
            3: "#de9f00",
            4: "#00AE00",
            5: "#0000cd",
            6: "#8b008b",
            7: "#739F9F",
        }
        self.color_scheme = {i: pygame.Color(c) for i, c in colors_basic.items()}
        self.spawn = spawn
        self.target = target
        self.surface = self.render(*screen_size)
        self.screen_size = screen_size

    def __deepcopy__(self, memo) -> "RaceTrack":
        return RaceTrack(
            deepcopy(self.walls, memo),
            deepcopy(self.active, memo),
            deepcopy(self.buttons, memo),
            deepcopy(self.colors, memo),
            deepcopy(self.target, memo),
            deepcopy(self.spawn, memo),
            deepcopy(self.screen_size, memo),
        )

    def render(self, width: int, height: int) -> pygame.Surface:
        """Draw out the track in its current state"""
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
            if wall != 0:
                pygame.draw.rect(
                    surface, color, (x, y, w + 1, h + 1), 0 if active else int(0.2 * w)
                )
            elif button:
                pygame.draw.circle(
                    surface, color, (x + w / 2, y + h / 2), 0.4 * min(w, h)
                )
            elif (row, col) == self.target:
                surface.blit(star_img, (x + 0.1 * w, y + 0.1 * h))
            if (row, col) == self.spawn:
                surface.blit(triangle, (x + 0.1 * w, y + 0.1 * h))
            pygame.draw.rect(surface, "#000000", (x, y, w + 1, h + 1), 2)
        return surface

    def find_wall_locations_np(
        self, color: int | None = None, active: bool | None = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Return the locations of all the walls.

        Args:
            color (int | None, optional): The color of wall you want to find. Defaults to None - if none returns all walls.
            active (bool | None, optional): Do you want only active walls, or inactive. Defaults to None - if none, returns all walls

        Returns:
            tuple[np.ndarray, np.ndarray]: A tuple containing an array of all the row numbers and an array of all the column numbers
        """
        color_mask = (
            (self.colors == color) if color is not None else np.ones(self.shape)
        ).astype(int)
        active_mask = (
            (self.active == active) if active is not None else np.ones(self.shape)
        ).astype(int)
        output = np.where(self.walls.astype(int) & color_mask & active_mask)
        assert len(output) == 2
        return output

    def find_wall_locations(
        self, color: int | None = None, active: bool | None = None
    ) -> set[Point]:
        """
        Return the locations of all the walls.

        Args:
            color (int | None, optional): The color of wall you want to find. Defaults to None - if none returns all walls.
            active (bool | None, optional): Do you want only active walls, or inactive. Defaults to None - if none, returns all walls

        Returns:
            set[Point]: A set containing the coordinates (row, col) of walls with the criteria given.
        """
        rows, cols = self.find_wall_locations_np(color, active)
        return set(zip(rows.astype(int), cols.astype(int)))

    def find_buttons(self, color: int | None = None) -> set[Point]:
        """
        Find the locations of the buttons

        Args:
            color (int | None, optional): The color of button you want to find. Defaults to None.
                Returns all buttons of any color if None

        Returns:
            set[Point]: A set containing the coordinates (row, col) of the buttons.
        """
        color_mask = (
            (self.colors == color) if color is not None else np.ones(self.shape)
        ).astype(int)
        rows, cols = np.where(self.buttons.astype(int) & color_mask)
        return set(zip(rows.astype(int), cols.astype(int)))

    def find_traversable_cells(self) -> set[Point]:
        """
        Return a set of all the coordinates (row, col) where your bot can currently exist.
        Buttons and deactivated walls are included in this set.

        Returns:
            set[Point]: The locations where you can currently walk.
        """
        output = np.where((self.walls == 0).astype(int) | (1 - self.active).astype(int))
        return set(zip(output[0].astype(int), output[1].astype(int)))

    def toggle(self, color: int) -> None:
        self.active[self.find_wall_locations_np(color)] = (
            1 - self.active[self.find_wall_locations_np(color)]
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
    return RaceTrack(
        walls,
        active,
        buttons,
        colors,
        (grid_size[0] - 1, grid_size[1] - 1),
        (0, 0),
        screen_size,
    )
