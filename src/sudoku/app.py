import sys

from . import util
from .board import Sudoku
from .display import ScreenManager, ScreenTag
from .state import AppState, Event, PuzzleState


def init(window_width: int = 1040, fps: int = 60):
    app = AppState()

    screen = ScreenManager(window_width, fps)
    screen.swap_screen(ScreenTag.PUZZLE)
    screen.set_caption("Sudoku")

    sudoku = Sudoku()
    data = util.get_puzzle(sys.argv)
    if data["err"] != "":
        print(data["err"], file=sys.stderr)
        exit(1)
    if not sudoku.set_puzzle(data["puzzle"], hints=data["hints"], title=data["title"]):
        print("\nError: Invalid puzzle format", file=sys.stderr)
        exit(2)

    run_puzzle(app, PuzzleState(sudoku), screen)

    app.quit()


def run_puzzle(app: AppState, puzzle: PuzzleState, screen: ScreenManager):
    frames = 0
    while True:
        digit = None
        cc = None

        event = app.update()
        if event == Event.QUIT:
            return
        elif event == Event.MOUSEDOWN:
            action = screen.query(app.mouse_pos())
            if action in [Event.PAUSE, Event.RESUME]:
                puzzle.paused = not puzzle.paused
            elif action == Event.RESET:
                puzzle.reset()
                frames = 0
            elif action == Event.SAVE:
                puzzle.freeze()
            elif action == Event.LOAD:
                puzzle.load({})
            elif action == Event.DELETE:
                digit = "0"
            elif action == Event.HINT:
                cc = puzzle.sudoku.next_hint()
        elif event == Event.KEYDOWN:
            digit = app.get_key()

        puzzle.candidate_mode = True if app.shift_pressed() else False
        if not puzzle.paused:
            if cc is None:
                cc = find_cell(round(screen.width() / 13), app.mouse_pos())
            puzzle.sudoku.set_current_cell(cc)
            if not puzzle.solved:
                handle_input(puzzle, digit)
            frames += 1
        puzzle.update(frames, screen.fps)

        screen.update(puzzle)


def handle_input(puzzle: PuzzleState, digit: str | None):
    cell = puzzle.sudoku.current_cell()
    if digit is None or cell is None or cell.is_fixed():
        return
    if digit == "0" and (puzzle.candidate_mode or cell.digit() == "0"):
        cell.clear_candidates()
    elif puzzle.candidate_mode:
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
