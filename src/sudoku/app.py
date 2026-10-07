import sys

import pygame

from . import util
from .board import Cell, Sudoku
from .display import ScreenManager, ScreenTag
from .state import PuzzleState


def init(window_width: int = 1040, fps: int = 60):
    sudoku = Sudoku()
    puzzle, msg = util.get_puzzle(sys.argv)
    if puzzle == "":
        print(msg, file=sys.stderr)
        exit(1)
    if not sudoku.set_puzzle(puzzle):
        print("\nError: Invalid grid format", file=sys.stderr)
        exit(2)
    sudoku.title = msg

    sm = ScreenManager(window_width)
    sm.add_screen(ScreenTag.PUZZLE)
    sm.swap_screen(ScreenTag.PUZZLE)
    sm.set_caption("Sudoku")

    run(sm, PuzzleState(sudoku), fps)


def run(sm: ScreenManager, state: PuzzleState, fps: int):
    frames = 0
    coords = None
    clock = pygame.time.Clock()

    while True:
        state.candidate_mode = (
            True if pygame.key.get_mods() & pygame.KMOD_SHIFT else False
        )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coords = pygame.mouse.get_pos()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state.paused = not state.paused
                if not state.paused and not state.solved:
                    handle_input(
                        state, util.get_digit(event.key), state.sudoku.current_cell()
                    )

        state.update(frames, fps)
        if not state.paused:
            cell = find_cell(round(sm.width() / 13), coords)
            state.sudoku.set_current_cell(cell)
            clock.tick(fps)
            frames += 1
        sm.update(state)


def handle_input(state: PuzzleState, digit: str | None, cell: Cell | None):
    if digit is None or cell is None or cell.is_fixed():
        return
    if digit == "0" and (state.candidate_mode or cell.digit() == "0"):
        cell.clear_candidates()
    elif state.candidate_mode:
        cell.insert_candidate(digit)
    else:
        cell.insert_digit(digit)


def find_cell(block_size: int, coords: tuple[int, int] | None) -> int:
    if coords is None or coords[1] <= block_size:
        return -1
    cell_index = 0
    for y in util.fstep(block_size, block_size, 9):
        for x in util.fstep(0, block_size, 9):
            x_diff = coords[0] - x
            y_diff = coords[1] - y
            if x_diff <= block_size and y_diff <= block_size:
                return cell_index
            cell_index += 1
    return -1
