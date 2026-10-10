from enum import Enum

import pygame

from .board import Sudoku
from .util import get_time

KEY_VALUES = {
    pygame.K_1: "1",
    pygame.K_2: "2",
    pygame.K_3: "3",
    pygame.K_4: "4",
    pygame.K_5: "5",
    pygame.K_6: "6",
    pygame.K_7: "7",
    pygame.K_8: "8",
    pygame.K_9: "9",
    pygame.K_BACKSPACE: "0",
}


class Event(Enum):
    NONE = 0
    PAUSE = 1
    RESET = 2
    SAVE = 3
    LOAD = 4
    HINT = 5
    QUIT = 6
    MOUSEDOWN = 7
    KEYDOWN = 8
    RESUME = 9
    DELETE = 10


class AppState:
    _mouse_pos: tuple[int, int] | None
    _last_key: int

    def __init__(self):
        pygame.init()
        self._mouse_pos = (0, 0)
        self._last_key = -1

    def update(self) -> Event:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return Event.QUIT
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._mouse_pos = pygame.mouse.get_pos()
                return Event.MOUSEDOWN
            elif e.type == pygame.KEYDOWN:
                self._last_key = e.key
                return Event.KEYDOWN
        return Event.NONE

    def mouse_pos(self) -> tuple[int, int] | None:
        """Returns the coordinates of the last mouse click"""
        return self._mouse_pos

    def get_key(self) -> str | None:
        try:
            return KEY_VALUES[self._last_key]
        except KeyError:
            return None

    def shift_pressed(self) -> int:
        return pygame.key.get_mods() & pygame.KMOD_SHIFT

    def quit(self):
        pygame.quit()


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
        """Loads a puzzle state from a given json object"""
        # TODO
        print("Loading...")

    def freeze(self) -> dict:
        """Saves the current puzzle state as a json object"""
        # TODO
        print("Saving...")
        return {}
