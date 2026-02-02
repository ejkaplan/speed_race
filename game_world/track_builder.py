import sys

import pygame
import pygame.locals

from racetrack import RaceTrack, blank_track, load_track

WIDTH = 600
GRID_SIZE = (15, 10)
SAVE_FILE_NAME = "tracks/your_map.pkl"  # Where do you want to save this track? (Press 'enter' to save)
STARTING_TRACK_NAME = None  # None if you want to start blank.
# Hold A to paint in deactivated walls
# press up and down on arrow keys to increase brush size


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


def click_track(
    track: RaceTrack,
    selected_color: int,
    selected_kind: str,
    pressed: bool,
    mx: int,
    my: int,
    cursor_size: int,
    handled_points: set[tuple[int, int]],
    shift_held: bool,
):
    if not pressed or not track.surface.get_rect().collidepoint(mx, my):
        return
    row, col = track.get_grid_coord(mx, my)
    for r in range(row - cursor_size + 1, row + cursor_size):
        for c in range(col - cursor_size + 1, col + cursor_size):
            if (
                r not in range(track.shape[0])
                or c not in range(track.shape[1])
                or (r, c) in handled_points
            ):
                continue
            handled_points.add((r, c))
            match selected_kind:
                case "wall":
                    if selected_color == 0:
                        track.walls[r, c] = 0
                    else:
                        track.walls[r, c] = 1
                        track.active[r, c] = 1 - int(shift_held)
                    track.colors[r, c] = selected_color
                    track.buttons[r, c] = 0
                case "button":
                    if selected_color == 0:
                        track.buttons[r, c] = 0
                    else:
                        track.buttons[r, c] = 1
                    track.walls[r, c] = 0
                    track.colors[r, c] = selected_color
                    track.active[r, c] = 1
                case "target":
                    track.target = (r, c)
                    track.walls[r, c] = 0
                    track.buttons[r, c] = 0
                    track.colors[r, c] = 0
                    track.active[r, c] = 1
                case "spawn":
                    track.spawn = (r, c)
                    track.walls[r, c] = 0
                    track.buttons[r, c] = 0
                    track.colors[r, c] = 0
                    track.active[r, c] = 1
    track.surface = track.render(track.surface.get_width(), track.surface.get_height())


def main():
    fps = 60
    fps_clock = pygame.time.Clock()
    pygame.init()
    screen_size = (WIDTH, round(WIDTH * GRID_SIZE[0] / GRID_SIZE[1]))
    screen = pygame.display.set_mode((screen_size[0] + 170, screen_size[1]))

    track = (
        load_track(STARTING_TRACK_NAME)
        if STARTING_TRACK_NAME
        else blank_track(GRID_SIZE, screen_size, 7)
    )
    color_buttons = {
        i: make_solid_colored_button(screen_size[0] + 30, 20 + 50 * i, 30, 30, color)
        for i, color in track.color_scheme.items()
    }
    circle = pygame.Surface((30, 30))
    pygame.draw.circle(circle, "#a4a4a4", (15, 15), 10)
    star_img = pygame.image.load("star.png")
    star_img = pygame.transform.scale(star_img, (25, 25))
    triangle = pygame.Surface((30, 30))
    triangle.fill("#ffffff")
    pygame.draw.polygon(triangle, "#278B00", [(15, 5), (25, 25), (5, 25)])

    type_buttons = {
        "wall": make_solid_colored_button(
            screen_size[0] + 100, 20, 30, 30, pygame.Color("#ffffff")
        ),
        "button": Button(screen_size[0] + 100, 70, 30, 30, circle),
        "target": Button(screen_size[0] + 100, 120, 30, 30, star_img),
        "spawn": Button(screen_size[0] + 100, 170, 30, 30, triangle),
    }

    selected_color = 1
    selected_kind = "wall"
    pressed = False
    shift_held = False

    cursor_size = 1
    handled_points = set()

    while True:
        screen.fill("#A6A6A6")
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.locals.MOUSEBUTTONDOWN:
                pressed = True
                for i, button in color_buttons.items():
                    if button.point_inside(mx, my):
                        selected_color = i
                for kind, button in type_buttons.items():
                    if button.point_inside(mx, my):
                        selected_kind = kind
            elif event.type == pygame.locals.MOUSEBUTTONUP:
                pressed = False
                handled_points.clear()
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.K_UP:
                    cursor_size += 1
                elif event.key == pygame.K_DOWN:
                    cursor_size = max(1, cursor_size - 1)
                elif event.key == pygame.K_RETURN:
                    track.save(SAVE_FILE_NAME)
                    print(f"Saved track to {SAVE_FILE_NAME}")
                elif event.key == pygame.K_a:
                    shift_held = True
            elif event.type == pygame.locals.KEYUP:
                if event.key == pygame.K_a:
                    shift_held = False

        click_track(
            track,
            selected_color,
            selected_kind,
            pressed,
            mx,
            my,
            cursor_size,
            handled_points,
            shift_held,
        )

        screen.blit(track.surface, (0, 0))
        for i, button in color_buttons.items():
            button.blit(screen, i == selected_color)
        for kind, button in type_buttons.items():
            button.blit(screen, kind == selected_kind)

        pygame.display.flip()
        fps_clock.tick(fps)


if __name__ == "__main__":
    main()
