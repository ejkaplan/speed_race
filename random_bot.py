import random
from game_world.racetrack import RaceTrack


Point = tuple[int, int]


def random_move(loc: Point, vel: Point, track: RaceTrack) -> Point:
    return (random.randint(-1, 1), random.randint(-1, 1))
