import sys
from time import monotonic
from typing import Callable

import pygame
import pygame.locals

from game_world.racetrack import RaceTrack, bresenham


Point = tuple[int, int]
Player = Callable[
    [Point, Point, RaceTrack], Point
]  # (location, velocity, track) -> change_in_velocity


def grid_dist(a: Point, b: Point) -> int:
    return len(list(bresenham(*a, *b)))


def play_game(
    player: Player,
    track: RaceTrack,
    time: float = 10,
    delay_time: float = 5,
    max_turns_without_progress: int = 100,
) -> tuple[list[Point], bool, str]:
    pos = track.spawn
    vel = (0, 0)
    min_distance_to_target = grid_dist(pos, track.target)
    turns_without_progress = 0
    path = [pos]
    while pos != track.target:
        start_time = monotonic()
        action = player(pos, vel, track)
        time_taken = monotonic() - start_time
        time -= time_taken
        if time < 0:
            return path, False, "Racer ran out of time!"
        time += min(time_taken, delay_time)
        if not (-1 <= action[0] <= 1 and -1 <= action[1] <= 1):
            return path, False, f"Racer made illegal move {action}!"
        vel = (vel[0] + action[0], vel[1] + action[1])
        next_pos = (pos[0] + vel[0], pos[1] + vel[1])
        if not track.line_traversable(pos, next_pos):
            path.append(next_pos)
            return path, False, f"Racer crashed into a wall!"
        new_dist = grid_dist(pos, next_pos)
        if new_dist < min_distance_to_target:
            min_distance_to_target = new_dist
            turns_without_progress = 0
        else:
            turns_without_progress += 1
            if turns_without_progress >= max_turns_without_progress:
                return path, False, "Racer spent too many ticks dawdling!"
    return path, True, f"Racer finished the race in {len(path)} ticks!"



def main():
    print(list(bresenham(*(0, 0), *(5, 19))))


if __name__ == "__main__":
    main()
