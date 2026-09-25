from abc import ABC, abstractmethod

import pygame

from .board import Cell, Sudoku
from .state import PuzzleState

GREY = pygame.Color(223, 223, 223)
YELLOW = pygame.Color(249, 219, 74)
BLUE = pygame.Color(195, 225, 255)
DARK_BLUE = pygame.Color(55, 95, 209)
RED = pygame.Color(236, 90, 92)
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)

FONT_XS = 20
FONT_S = 35
FONT_M = 50
FONT_L = 70


class FontManager:
    _fonts: dict = {}

    def __init__(self):
        pygame.font.init()

    def load_font(self, size: int):
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont("Arial", size)
        return self._fonts[size]


class Button:
    rect: pygame.Rect
    pressed: bool = False

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = pygame.Rect(x, y, w, h)

    def is_pressed(self) -> bool:
        action = False
        if (
            pygame.mouse.get_pressed()[0] == 1
            and self.rect.collidepoint(pygame.mouse.get_pos())
            and self.pressed == False
        ):
            self.pressed = True
            action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.pressed = False

        return action


class ViewPane(ABC):
    surface: pygame.Surface
    x: int
    y: int
    buttons: list[Button]

    def __init__(
        self, surface: pygame.Surface, x: int, y: int, buttons: list[Button] = []
    ):
        self.surface = surface
        self.x = x
        self.y = y
        self.buttons = buttons

    @abstractmethod
    def draw(
        self, state: PuzzleState, sudoku: Sudoku, fm: FontManager
    ) -> pygame.Surface:
        return self.surface


class Grid(ViewPane):
    def draw(
        self, state: PuzzleState, sudoku: Sudoku, fm: FontManager
    ) -> pygame.Surface:
        self.surface.fill(WHITE)
        font_l = fm.load_font(FONT_L)
        font_xs = fm.load_font(FONT_XS)

        if state.paused:
            display = font_l.render("PAUSED", 1, BLACK)
            self.surface.blit(
                display, display.get_rect(center=self.surface.get_rect().center)
            )
            pygame.draw.line(self.surface, BLACK, (0, 0), (900, 0), 4)
            return self.surface

        cell_number = 0
        current_cell = sudoku.current_cell()
        for y in range(0, 900, 100):
            for x in range(0, 900, 100):
                cell = sudoku.get_cell(cell_number)
                if cell is None:
                    continue
                # colour cell
                cell_colour = Renderer.get_cell_colour(cell, current_cell)
                cell_rect = pygame.draw.rect(
                    self.surface,
                    cell_colour,
                    pygame.Rect(x, y, 100, 100),
                )

                # draw cell digit(s)
                if FONT_XS is None or FONT_L is None:
                    cell_number += 1
                    continue
                if cell.digit() != "0":
                    digit_colour = Renderer.get_digit_colour(cell, sudoku)
                    cell_display = font_l.render(cell.digit(), 1, digit_colour)
                    self.surface.blit(
                        cell_display, cell_display.get_rect(center=cell_rect.center)
                    )
                else:
                    buffer_x = 0
                    buffer_y = 0
                    count = 0
                    for p in range(1, 10):
                        if str(p) in cell.candidates():
                            self.surface.blit(
                                font_xs.render(str(p), 1, BLACK),
                                (x + 30 - 17 + buffer_x, y + 10 - 1 + buffer_y),
                            )
                        buffer_x += 30
                        count += 1
                        if count % 3 == 0:
                            buffer_x = 0
                            buffer_y += 30
                cell_number += 1

        # 3x3 boxes
        pygame.draw.line(self.surface, BLACK, (300, 0), (300, 900), 4)
        pygame.draw.line(self.surface, BLACK, (600, 0), (600, 900), 4)
        pygame.draw.line(self.surface, BLACK, (0, 0), (900, 0), 4)
        pygame.draw.line(self.surface, BLACK, (0, 300), (900, 300), 4)
        pygame.draw.line(self.surface, BLACK, (0, 600), (900, 600), 4)

        # soft verticals
        for x in range(0, 900, 100):
            pygame.draw.line(self.surface, BLACK, (x, 0), (x, 900))
        # soft horizontals
        for y in range(0, 900, 100):
            pygame.draw.line(self.surface, BLACK, (0, y), (900, y))

        return self.surface


class Header(ViewPane):
    def draw(
        self, state: PuzzleState, sudoku: Sudoku, fm: FontManager
    ) -> pygame.Surface:
        self.surface.fill(GREY)

        font_s = fm.load_font(FONT_S)
        font_xs = fm.load_font(FONT_XS)
        if font_s is None or font_xs is None:
            return self.surface

        time = state.time
        clock = f"{str(time[1]).rjust(2, "0")}:{str(time[0]).rjust(2, "0")}"
        if time[2] != 0:
            clock = f"{time[2]}:" + clock
        if not state.solved:
            msg_1 = clock
            msg_2 = sudoku.title
        else:
            msg_1 = "Congratulations!"
            msg_2 = "Sudoku solved in " + clock

        rect = self.surface.get_rect()
        display_1 = font_s.render(msg_1, 1, BLACK)
        rect_1 = pygame.Rect(0, 0, rect.w, 2 * rect.h / 3)
        self.surface.blit(display_1, display_1.get_rect(center=rect_1.center))
        display_2 = font_xs.render(msg_2, 1, BLACK)
        rect_2 = pygame.Rect(0, (2 * rect.h / 3) - 5, rect.w, rect.h / 3)
        self.surface.blit(display_2, display_2.get_rect(center=rect_2.center))

        for b in self.buttons:
            pygame.draw.rect(self.surface, WHITE, b.rect)

        return self.surface


class Renderer:
    _window: pygame.Surface
    _font_manager: FontManager
    _panes: list[ViewPane] = []

    def __init__(self, width: int, height: int):
        pygame.init()
        self._window = pygame.display.set_mode((width, height))
        self._font_manager = FontManager()

    def update(self, state: PuzzleState, sudoku: Sudoku):
        for p in self._panes:
            if p is None:
                continue
            self._window.blit(p.draw(state, sudoku, self._font_manager), (p.x, p.y))
        pygame.display.flip()

    def add_pane(self, p: ViewPane):
        if p is not None:
            self._panes.append(p)

    def clear_panes(self):
        self._panes.clear()

    def set_caption(self, caption: str):
        pygame.display.set_caption(caption)

    @staticmethod
    def get_cell_colour(cell: Cell | None, current_cell: Cell | None) -> pygame.Color:
        if cell is None:
            return WHITE
        colour = WHITE
        if cell.is_fixed():
            colour = GREY
        if current_cell != None:
            if cell == current_cell or (
                cell.digit() == current_cell.digit() and cell.digit() != "0"
            ):
                colour = YELLOW
            if cell.index() in current_cell.sightline():
                colour = BLUE
        return colour

    @staticmethod
    def get_digit_colour(cell: Cell, sudoku: Sudoku) -> pygame.Color:
        digit_colour = DARK_BLUE if not cell.is_fixed() else BLACK
        for i in cell.sightline():
            c = sudoku.get_cell(i)
            if c != None and c.digit() == cell.digit():
                digit_colour = RED
                break
        return digit_colour
