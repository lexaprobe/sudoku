from enum import Enum

from pygame import Color


class Cell:
    _digit: str
    _digit_colour: Color
    _candidates_corner: list[str]
    _candidates_centre: list[str]
    fixed: bool = False

    def __init__(self):
        self._digit = "0"
        self._digit_colour = Color("BLACK")
        self._candidates_corner = []
        self._candidates_centre = []

    def digit(self) -> str:
        return self._digit

    def digit_colour(self) -> Color:
        return self._digit_colour

    def candidates_corner(self) -> list[str]:
        return self._candidates_corner

    def is_fixed(self) -> bool:
        return self.fixed

    def is_valid_digit(self, digit: str) -> bool:
        return digit in [str(d) for d in range(10)]

    def fix_digit(self):
        self.fixed = True

    def insert_digit(self, digit: str):
        if not self.is_valid_digit(digit) or self.fixed:
            return
        self._digit = "0" if self._digit == digit else digit

    def insert_candidate_corner(self, digit: str):
        if not self.is_valid_digit(digit) or self.fixed:
            return
        if digit in self._candidates_corner:
            self._candidates_corner.remove(digit)
        else:
            self._candidates_corner.append(digit)

    def clear_candidates_corner(self):
        self._candidates_corner.clear()

    def paint_digit(self, colour: Color):
        if not self.fixed:
            self._digit_colour = colour


class Sudoku:
    cells: list[Cell]
    _current_cell: Cell | None = None

    def __init__(self):
        self.cells = [Cell() for _ in range(81)]

    def set_grid(self, seed: str) -> bool:
        if len(seed) != 81:
            return False
        for i in range(81):
            cell = self.cells[i]
            cell.insert_digit(seed[i])
            if seed[i] != "0":
                cell.fix_digit()
        return True

    def set_current_cell(self, index: int | None) -> bool:
        if index is None or not index in range(81):
            return False
        cell = self.cells[index]
        if cell is None or cell.is_fixed():
            return False
        self._current_cell = cell
        return True

    def get_grid(self) -> list[Cell]:
        return self.cells

    def current_cell(self) -> Cell | None:
        return self._current_cell

    def is_current_cell(self, cell: Cell) -> bool:
        return self._current_cell == cell
