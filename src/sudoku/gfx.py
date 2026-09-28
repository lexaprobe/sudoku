from abc import ABC, abstractmethod

import pygame

from .board import Cell, Sudoku
from .state import PuzzleState
from .util import fstep

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
    image: pygame.Surface | None = None
    pressed: bool = False
    tag: str

    def __init__(self, x: float, y: float, w: float, h: float, tag: str = "button"):
        self.rect = pygame.Rect(x, y, w, h)
        self.tag = tag

    def add_image(self, image: pygame.Surface):
        if image is None:
            return
        self.image = pygame.transform.smoothscale(image, (self.rect.w, self.rect.h))
        x, y = self.rect.x, self.rect.y
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

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

    def scale(self, factor: float):
        r = self.rect
        self.rect = pygame.Rect(r.x, r.y, r.w * factor, r.h * factor)


class ViewPane(ABC):
    surface: pygame.Surface
    x: float
    y: float
    buttons: list[Button]
    tag: str

    def __init__(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        buttons: list[Button] = [],
        tag: str = "pane",
    ):
        self.x = x
        self.y = y
        self.surface = pygame.Surface((w, h))
        self.buttons = buttons
        self.tag = tag

    @abstractmethod
    def draw(
        self, state: PuzzleState, sudoku: Sudoku, fm: FontManager
    ) -> pygame.Surface:
        return self.surface

    def get_button(self, button_tag: str) -> Button | None:
        for b in self.buttons:
            if b.tag == button_tag:
                return b
        return None

    def scale(self, value: float) -> int:
        """Scales a value with this ViewPane's dimensions"""
        return max((int)(value * self.surface.get_rect().w / 900), 1)


class Grid(ViewPane):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        rect = self.surface.get_rect()
        if rect.w != rect.h:
            # grid rendering logic relies on width and height being the same
            raise ValueError
        if self.tag == "pane":
            self.tag = "grid"

    def draw(
        self, state: PuzzleState, sudoku: Sudoku, fm: FontManager
    ) -> pygame.Surface:
        grid = self.surface.get_rect()
        font_l = fm.load_font(self.scale(FONT_L))
        font_xs = fm.load_font(self.scale(FONT_XS))
        line = self.scale(4)

        self.surface.fill(WHITE)

        if state.paused:
            display = font_l.render("PAUSED", 1, BLACK)
            self.surface.blit(display, display.get_rect(center=grid.center))
            pygame.draw.line(self.surface, BLACK, (0, 0), (grid.w, 0), line)
            return self.surface

        cell_w = grid.w / 9
        cell_h = grid.h / 9
        index = 0
        current_cell = sudoku.current_cell()
        for y in fstep(0, cell_h, 9):
            for x in fstep(0, cell_w, 9):
                cell = sudoku.get_cell(index)
                if cell is None:
                    continue
                # colour cell
                cell_colour = Renderer.get_cell_colour(cell, current_cell)
                cell_rect = pygame.draw.rect(
                    self.surface,
                    cell_colour,
                    pygame.Rect(x, y, cell_w, cell_h),
                )
                # draw cell digit(s)
                if cell.digit() != "0":
                    digit_colour = Renderer.get_digit_colour(cell, sudoku)
                    cell_display = font_l.render(cell.digit(), 1, digit_colour)
                    self.surface.blit(
                        cell_display, cell_display.get_rect(center=cell_rect.center)
                    )
                else:
                    for c in cell.candidates():
                        i = int(c) - 1
                        xb = (i % 3) * (grid.w / 30) + (cell_w / 7)
                        yb = (int)(i / 3) * (grid.h / 30) + (cell_h / 11)
                        self.surface.blit(
                            font_xs.render(c, 1, BLACK),
                            (x + xb, y + yb),
                        )
                index += 1

        # split grid into 9 equal-sized boxes
        h1 = grid.w / 3
        v1 = grid.h / 3
        h2 = 2 * grid.w / 3
        v2 = 2 * grid.h / 3
        pygame.draw.line(self.surface, BLACK, (h1, 0), (h1, grid.h), line)
        pygame.draw.line(self.surface, BLACK, (h2, 0), (h2, grid.h), line)
        pygame.draw.line(self.surface, BLACK, (0, 0), (grid.w, 0), line)
        pygame.draw.line(self.surface, BLACK, (0, v1), (grid.w, v1), line)
        pygame.draw.line(self.surface, BLACK, (0, v2), (grid.w, v2), line)

        # split each box into 9 equal-sized cells
        for x in fstep(0, cell_w, 9):
            pygame.draw.line(self.surface, BLACK, (x, 0), (x, grid.h))
        for y in fstep(0, cell_h, 9):
            pygame.draw.line(self.surface, BLACK, (0, y), (grid.w, y))

        return self.surface


class Header(ViewPane):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.tag == "pane":
            self.tag = "header"

    def draw(
        self, state: PuzzleState, sudoku: Sudoku, fm: FontManager
    ) -> pygame.Surface:
        font_s = fm.load_font(self.scale(FONT_S))
        font_xs = fm.load_font(self.scale(FONT_XS))

        self.surface.fill(GREY)

        time = state.time
        clock = f"{str(time[1]).rjust(2, "0")}:{str(time[0]).rjust(2, "0")}"
        if time[2] != 0:
            clock = f"{time[2]}:" + clock
        if not state.solved:
            msg_1 = clock
            msg_2 = sudoku.title
        else:
            msg_1 = "Congratulations!"
            msg_2 = f"Puzzle solved in {clock}"

        head = self.surface.get_rect()
        display_1 = font_s.render(msg_1, 1, BLACK)
        rect_1 = pygame.Rect(0, head.h * 0.1, head.w, head.h * 0.5)
        self.surface.blit(display_1, display_1.get_rect(center=rect_1.center))
        display_2 = font_xs.render(msg_2, 1, BLACK)
        rect_2 = pygame.Rect(0, head.h * 0.5, head.w, head.h * 0.5)
        self.surface.blit(display_2, display_2.get_rect(center=rect_2.center))

        for b in self.buttons:
            if b.image is not None:
                self.surface.blit(b.image, (b.rect.x, b.rect.y))
            else:
                pygame.draw.rect(self.surface, WHITE, b.rect, border_radius=15)
            text = font_xs.render(b.tag, 1, BLACK)
            self.surface.blit(
                text,
                text.get_rect(
                    center=(b.rect.x + b.rect.w / 2, b.rect.h + b.rect.h / 3)
                ),
            )

        return self.surface


class Renderer:
    _window: pygame.Surface
    _font_manager: FontManager
    panes: list[ViewPane] = []

    def __init__(self, width: float, height: float):
        pygame.init()
        self._window = pygame.display.set_mode((width, height))
        self._font_manager = FontManager()

    def update(self, state: PuzzleState, sudoku: Sudoku):
        for p in self.panes:
            if p is None:
                continue
            self._window.blit(p.draw(state, sudoku, self._font_manager), (p.x, p.y))
        pygame.display.flip()

    def add_viewpane(self, p: ViewPane):
        if p is not None:
            self.panes.append(p)

    def viewpanes(self) -> dict[str, ViewPane]:
        viewpanes = {}
        for p in self.panes:
            viewpanes[p.tag] = p
        return viewpanes

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
