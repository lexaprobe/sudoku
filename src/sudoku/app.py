import sys

import pygame

from . import util
from .board import Cell, Sudoku
from .gfx import Button, Grid, Header, Renderer
from .state import PuzzleState

FPS = 60

GRID_SIZE = 750
BOX_SIZE = GRID_SIZE / 9
HEAD_OFFSET = BOX_SIZE


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

    reset = Button(buffer + 8 * BOX_SIZE, buffer - 10, size, size, tag="Reset")
    reset.add_image(util.load_image(reset.tag))
    buttons.append(reset)

    renderer = Renderer(GRID_SIZE, GRID_SIZE + HEAD_OFFSET)
    renderer.add_viewpane(Grid(0, HEAD_OFFSET, GRID_SIZE, GRID_SIZE, tag="grid"))
    renderer.add_viewpane(Header(0, 0, GRID_SIZE, HEAD_OFFSET, buttons, tag="header"))
    renderer.set_caption("Sudoku")

    run(sudoku, renderer)


def run(sudoku: Sudoku, renderer: Renderer):
    state = PuzzleState()
    frames = 0
    coords = None
    clock = pygame.time.Clock()
    viewpanes = renderer.viewpanes()
    button_pause = viewpanes["header"].get_button("Pause")
    button_reset = viewpanes["header"].get_button("Reset")
    if button_pause is None or button_reset is None:
        return

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
                if event.key == pygame.K_ESCAPE:
                    state.paused = not state.paused
                elif not state.paused and not state.solved:
                    handle_input(state, util.get_digit(event.key), cell)

        if button_pause.is_pressed():
            state.paused = not state.paused
            if state.paused:
                button_pause.tag = "Play"
            else:
                button_pause.tag = "Pause"

        if button_reset.is_pressed():
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


def find_cell(coords: tuple[int, int] | None) -> int | None:
    if coords is None or coords[1] <= HEAD_OFFSET:
        return None
    cell_index = 0
    for y in util.fstep(HEAD_OFFSET, BOX_SIZE, 9):
        for x in util.fstep(0, BOX_SIZE, 9):
            x_diff = coords[0] - x
            y_diff = coords[1] - y
            if x_diff <= BOX_SIZE and y_diff <= BOX_SIZE:
                return cell_index
            cell_index += 1
    return None
