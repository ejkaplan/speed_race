from enum import Enum
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

class Status(Enum):
    ONGOING = 1
    FINISH = 2
    DNF = 3

def grid_dist(a: Point, b: Point) -> int:
    return len(list(bresenham(*a, *b)))


class Game:

    def __init__(self, player: Player, track: RaceTrack, time: float, delay: float, max_turns_without_progress: int = 100) -> None:
        self.player = player
        self.track = track
        self.time = time
        self.delay = delay
        self.turns_without_progress = 0
        self.max_turns_without_progress = max_turns_without_progress
        self.pos = track.spawn
        self.vel = (0, 0)
        self.min_dist = float('inf')
        self.path = [self.pos]

    def tick(self) -> tuple[Status, str]:
        start_time = monotonic()
        action = self.player(self.pos, self.vel, self.track)
        time_taken = monotonic() - start_time
        self.time -= time_taken
        if self.time < 0:
            return Status.DNF, "Timed Out"
        self.time += min(time_taken, self.delay)
        if not (-1 <= action[0] <= 1 and -1 <= action[1] <= 1):
            return Status.DNF, f"Racer made illegal move {action}!"
        vel = (self.vel[0] + action[0], self.vel[1] + action[1])
        next_pos = (self.pos[0] + vel[0], self.pos[1] + vel[1])
        if not self.track.line_traversable(self.pos, next_pos):
            self.path.append(next_pos)
            return Status.DNF, f"Racer crashed into a wall!"
        new_dist = grid_dist(self.pos, self.track.target)
        if new_dist < self.min_dist:
            self.min_dist = new_dist
            self.turns_without_progress = 0
        else:
            self.turns_without_progress += 1
            if self.turns_without_progress >= self.max_turns_without_progress:
                return Status.DNF, "Racer spent too many ticks dawdling!"
        self.pos = next_pos
        self.path.append(self.pos)
        if self.pos == self.track.target:
            return Status.FINISH, "Racer made it to the finish line!"
        return Status.ONGOING, "Still racing."
        

def play_game(self) -> tuple[Status, str]:
    status, msg = Status.ONGOING, "Just Started."
    while status == Status.ONGOING:
        status, msg = self.tick()
    return status, msg



def main():
    print(list(bresenham(*(0, 0), *(5, 19))))


if __name__ == "__main__":
    main()
