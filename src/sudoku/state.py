from enum import Enum

from .board import Sudoku
from .util import get_time


class Action(Enum):
    PAUSE = 1
    RESET = 2
    QUIT = 3
    SAVE = 4
    LOAD = 5
    HINT = 6


class PuzzleState:
    sudoku: Sudoku
    candidate_mode: bool
    paused: bool
    solved: bool
    time: tuple[int, int, int]
    solve_time: tuple[int, int, int]

    def __init__(self, sudoku: Sudoku):
        self.sudoku = sudoku
        self.candidate_mode = False
        self.paused = False
        self.solved = False
        self.time = (0, 0, 0)
        self.solve_time = self.time

    def update(self, frames: int, fps: int):
        if not self.solved:
            self.solved = self.sudoku.is_solved()
            if self.solved:
                self.solve_time = get_time(frames, fps)
        if not self.paused:
            self.time = self.solve_time if self.solved else get_time(frames, fps)

    def reset(self):
        self.sudoku.reset()
        self.solved = False
        self.time = (0, 0, 0)
        self.solve_time = self.time

    def load(self, state: dict):
        """Loads a state from a given json object"""
        # TODO
        pass

    def freeze(self) -> dict:
        """Saves the current state as a json object"""
        # TODO
        return {}
