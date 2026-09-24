#  0  1  2 |  3  4  5 |  6  7  8
#  9 10 11 | 12 13 14 | 15 16 17
# 18 19 20 | 21 22 23 | 24 25 26
# ——————————————————————————————
# 27 28 29 | 30 31 32 | 33 34 35
# 36 37 38 | 39 40 41 | 42 43 44
# 45 46 47 | 48 49 50 | 51 52 53
# ——————————————————————————————
# 54 55 56 | 57 58 59 | 60 61 62
# 63 64 65 | 66 67 68 | 69 70 71
# 72 73 74 | 75 76 77 | 78 79 80

BOX_1 = [0, 1, 2, 9, 10, 11, 18, 19, 20]
BOX_2 = [3, 4, 5, 12, 13, 14, 21, 22, 23]
BOX_3 = [6, 7, 8, 15, 16, 17, 24, 25, 26]
BOX_4 = [27, 28, 29, 36, 37, 38, 45, 46, 47]
BOX_5 = [30, 31, 32, 39, 40, 41, 48, 49, 50]
BOX_6 = [33, 34, 35, 42, 43, 44, 51, 52, 53]
BOX_7 = [54, 55, 56, 63, 64, 65, 72, 73, 74]
BOX_8 = [57, 58, 59, 66, 67, 68, 75, 76, 77]
BOX_9 = [60, 61, 62, 69, 70, 71, 78, 79, 80]
BOXES = [BOX_1, BOX_2, BOX_3, BOX_4, BOX_5, BOX_6, BOX_7, BOX_8, BOX_9]


class Cell:
    _digit: str
    _index: int | None
    _candidates: list[str]
    _fixed: bool = False

    def __init__(self, index: int):
        self._digit = "0"
        self._index = index
        self._candidates = []

    def digit(self) -> str:
        return self._digit

    def index(self) -> int | None:
        return self._index

    def candidates(self) -> list[str]:
        return self._candidates

    def is_fixed(self) -> bool:
        return self._fixed

    def is_valid_digit(self, digit: str) -> bool:
        return digit in [str(d) for d in range(10)]

    def sightline(self) -> list[int]:
        if self._index is None:
            return []

        col_number = self._index % 9
        row_number = int((self._index - col_number) / 9)
        row_sightline = [i for i in range(9 * row_number, 9 * (row_number + 1))]
        col_sightline = [j for j in range(col_number, 81 + col_number, 9)]
        sightline = list(set(row_sightline) | set(col_sightline))

        for box in BOXES:
            if self._index in box:
                sightline = list(set(sightline) | set(box))
                break

        return list(set(sightline) - set([self._index]))

    def fix_digit(self):
        self._fixed = True

    def insert_digit(self, digit: str):
        if not self.is_valid_digit(digit) or self._fixed:
            return
        self._digit = "0" if digit == self._digit else digit

    def insert_candidate(self, digit: str):
        if not self.is_valid_digit(digit) or self._fixed:
            return
        if digit in self._candidates:
            self._candidates.remove(digit)
        else:
            self._candidates.append(digit)

    def clear_candidates(self):
        self._candidates.clear()


class Sudoku:
    title: str = "Sudoku"
    _puzzle: str
    _cells: list[Cell]
    _current_cell: Cell | None = None

    def __init__(self):
        self.cells = [Cell(i) for i in range(81)]

    def set_puzzle(self, puzzle: str) -> bool:
        if len(puzzle) != 81:
            return False
        self._puzzle = puzzle
        for i in range(81):
            cell = self.cells[i]
            cell.insert_digit(puzzle[i])
            if puzzle[i] != "0":
                cell.fix_digit()
        return True

    def set_current_cell(self, index: int | None):
        if index is None or not index in range(81):
            self._current_cell = None
            return
        cell = self.cells[index]
        if cell != None:
            self._current_cell = cell
        return True

    def get_cells(self) -> list[Cell]:
        return self._cells

    def get_cell(self, index: int) -> Cell | None:
        if not index in range(81):
            return None
        return self.cells[index]

    def insert_digit(self, digit: str, cell: Cell | None):
        if cell is None:
            return
        cell.insert_digit(digit)

    def insert_candidate(self, digit: str, cell: Cell | None):
        if cell is None:
            return
        cell.insert_candidate(digit)

    def current_cell(self) -> Cell | None:
        return self._current_cell

    def is_current_cell(self, cell: Cell) -> bool:
        return self._current_cell == cell

    def is_solved(self) -> bool:
        for cell in self.cells:
            if cell.digit() == "0":
                return False
            for i in cell.sightline():
                if self.cells[i].digit() == cell.digit():
                    return False
        return True

    def string(self) -> str:
        return self._puzzle

    def pstring(self) -> str:
        pstr = ""
        hline = f"{"":—>25}\n"
        vline = "|"
        for i in range(81):
            cell = self.get_cell(i)
            if cell is None:
                # something has gone very wrong here
                raise IndexError
            if i % 27 == 0:
                pstr += hline
            if i % 9 == 0:
                pstr += vline
            digit = cell.digit() if cell.digit() != "0" else ""
            pstr += f"{digit:>2}"
            if (i + 1) % 3 == 0:
                pstr += f" {vline}"
            if (i + 1) % 9 == 0:
                pstr += "\n"
            if (i + 1) == 81:
                pstr += hline.rstrip("\n")
        return pstr
