import sys

import pygame

from . import util
from .board import Cell, Sudoku
from .gfx import Grid, Header, Renderer
from .state import PuzzleState

FPS = 60

GRID_WIDTH = 900
GRID_HEIGHT = 900
GRID_OFFSET = 81


def init():
    sudoku = Sudoku()
    puzzle, msg = util.get_puzzle(sys.argv)
    if puzzle == "":
        print(msg, file=sys.stderr)
        exit(1)
    if not sudoku.set_puzzle(puzzle):
        print("\nError: Invalid grid format", file=sys.stderr)
        exit(2)
    sudoku.title = msg

    renderer = Renderer(GRID_WIDTH, GRID_HEIGHT + GRID_OFFSET)
    renderer.add_pane(
        Grid(pygame.surface.Surface((GRID_WIDTH, GRID_HEIGHT)), 0, GRID_OFFSET)
    )
    renderer.add_pane(Header(pygame.surface.Surface((GRID_WIDTH, GRID_OFFSET)), 0, 0))
    renderer.set_caption("Sudoku")

    run(sudoku, renderer)


def run(sudoku: Sudoku, renderer: Renderer):
    state = PuzzleState()
    frames = 0
    coords = None
    clock = pygame.time.Clock()

    while True:
        cell = sudoku.current_cell()
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
                if event.key in [pygame.K_ESCAPE, pygame.K_p]:
                    state.paused = not state.paused
                elif not state.paused:
                    handle_input(state, util.get_digit(event.key), cell)

        if not state.solved:
            state.solved = sudoku.is_solved()
            if state.solved:
                state.solve_time = util.get_time(frames, FPS)

        if not state.paused:
            sudoku.set_current_cell(get_cell(coords))
            state.time = (
                state.solve_time if state.solved else util.get_time(frames, FPS)
            )
            clock.tick(FPS)
            frames += 1

        renderer.update(state, sudoku)


def handle_input(state: PuzzleState, digit: str | None, cell: Cell | None):
    if digit is None or cell is None or cell.is_fixed():
        return
    if digit == "0" and (state.candidate_mode or cell.digit() == "0"):
        cell.clear_candidates()
    elif state.candidate_mode:
        cell.insert_candidate(digit)
    else:
        cell.insert_digit(digit)


def get_cell(coords: tuple | None) -> int | None:
    if coords is None or coords[1] <= 81:
        return None
    cell_index = 0
    for y in range(81, 900 + 81, 100):
        for x in range(0, 900, 100):
            x_diff = coords[0] - x
            y_diff = coords[1] - y
            if x_diff <= 100 and y_diff <= 100:
                return cell_index
            cell_index += 1
    return None
