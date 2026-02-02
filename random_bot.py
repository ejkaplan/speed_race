import random
from game_world.racetrack import RaceTrack


Point = tuple[int, int]


def random_move(loc: Point, track: RaceTrack) -> Point:
    safe = track.find_traversable_cells()
    options = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = {opt: (loc[0] + opt[0], loc[1] + opt[1]) for opt in options}
    safe_options = [opt for opt in neighbors if neighbors[opt] in safe]
    return random.choice(safe_options)
