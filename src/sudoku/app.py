import sys

import pygame

from . import util
from .board import Cell, Sudoku
from .display import Button, Grid, Header, Sidebar, WindowManager
from .state import PuzzleState

FPS = 60

GRID_SIZE = 750
BOX_SIZE = GRID_SIZE / 9
HEAD_BUFFER = BOX_SIZE
SIDE_BUFFER = 4 * BOX_SIZE
WINDOW_WIDTH = GRID_SIZE + SIDE_BUFFER
WINDOW_HEIGHT = GRID_SIZE + HEAD_BUFFER


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

    buttons = []
    buffer = 0.2 * BOX_SIZE
    size = BOX_SIZE - 2 * buffer

    pause = Button(buffer, buffer - 10, size, size, tag="Pause")
    pause.add_image(util.load_image(pause.tag))
    buttons.append(pause)

    reset = Button(buffer + 12 * BOX_SIZE, buffer - 10, size, size, tag="Reset")
    reset.add_image(util.load_image(reset.tag))
    buttons.append(reset)

    wm = WindowManager(WINDOW_WIDTH, WINDOW_HEIGHT)
    wm.add_viewpane(Grid(0, HEAD_BUFFER, GRID_SIZE, GRID_SIZE))
    wm.add_viewpane(Sidebar(GRID_SIZE, HEAD_BUFFER, SIDE_BUFFER, GRID_SIZE))
    wm.add_viewpane(Header(0, 0, WINDOW_WIDTH, HEAD_BUFFER, buttons))
    wm.set_caption("Sudoku")

    run(sudoku, wm)


def run(sudoku: Sudoku, wm: WindowManager):
    state = PuzzleState()
    frames = 0
    coords = None
    clock = pygame.time.Clock()
    b_pause = wm.get_button("Pause")
    b_reset = wm.get_button("Reset")

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
                elif not state.paused and not state.solved:
                    handle_input(
                        state, util.get_digit(event.key), sudoku.current_cell()
                    )

        if b_pause.is_pressed():
            state.paused = not state.paused
            if state.paused:
                b_pause.tag = "Play"
            else:
                b_pause.tag = "Pause"

        if b_reset.is_pressed():
            sudoku.reset()
            state.reset()
            frames = 0

        if not state.solved:
            state.solved = sudoku.is_solved()
            if state.solved:
                state.solve_time = util.get_time(frames, FPS)

        if not state.paused:
            sudoku.set_current_cell(find_cell(coords))
            state.time = (
                state.solve_time if state.solved else util.get_time(frames, FPS)
            )
            clock.tick(FPS)
            frames += 1

        wm.update(state, sudoku)


def handle_input(state: PuzzleState, digit: str | None, cell: Cell | None):
    if digit is None or cell is None or cell.is_fixed():
        return
    if digit == "0" and (state.candidate_mode or cell.digit() == "0"):
        cell.clear_candidates()
    elif state.candidate_mode:
        cell.insert_candidate(digit)
    else:
        cell.insert_digit(digit)


def find_cell(coords: tuple[int, int] | None) -> int:
    if coords is None or coords[1] <= HEAD_BUFFER:
        return -1
    cell_index = 0
    for y in util.fstep(HEAD_BUFFER, BOX_SIZE, 9):
        for x in util.fstep(0, BOX_SIZE, 9):
            x_diff = coords[0] - x
            y_diff = coords[1] - y
            if x_diff <= BOX_SIZE and y_diff <= BOX_SIZE:
                return cell_index
            cell_index += 1
    return -1
