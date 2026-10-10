from abc import ABC, abstractmethod
from enum import Enum

import pygame

from .board import Cell, Sudoku
from .interface import Button, ButtonTag
from .state import AppState, Event, PuzzleState
from .util import fstep, image_path

GREY = pygame.Color(223, 223, 223)
YELLOW = pygame.Color(249, 219, 74)
BLUE = pygame.Color(195, 225, 255)
DARK_BLUE = pygame.Color(55, 95, 209)
RED = pygame.Color(236, 90, 92)
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)

FONT_XS = 17
FONT_S = 20
FONT_M = 35
FONT_L = 55


class FontManager:
    _fonts: dict = {}

    def __init__(self):
        pygame.font.init()

    def load_font(self, size: int):
        if size not in self._fonts:
            self._fonts[size] = pygame.font.SysFont("Arial", size)
        return self._fonts[size]


class Pane:
    surface: pygame.Surface
    x: int
    y: int

    def __init__(self, x: int, y: int, w: int, h: int):
        self.surface = pygame.Surface((w, h), pygame.SRCALPHA)
        self.x = x
        self.y = y

    @classmethod
    def from_rect(cls, rect: pygame.Rect):
        x, y = rect.topleft
        return cls(x, y, rect.w, rect.h)

    def pos(self) -> tuple[int, int]:
        return (self.x, self.y)

    def size(self) -> tuple[int, int]:
        return self.surface.get_size()

    def center(self) -> tuple[int, int]:
        return self.surface.get_rect().center

    def rect(self) -> pygame.Rect:
        return self.surface.get_rect()

    def outline(self, color: pygame.Color = BLACK, width: int = 4):
        """Draws an outline around this pane"""
        rect = self.rect()
        # top outline
        pygame.draw.line(self.surface, color, (0, 0), (rect.w, 0), width)
        # bottom outline
        pygame.draw.line(self.surface, color, (0, rect.h), (rect.w, rect.h), width)
        # left outline
        pygame.draw.line(self.surface, color, (0, 0), (0, rect.h), width)
        # right outline
        pygame.draw.line(self.surface, color, (rect.w, 0), (rect.w, rect.h), width)


class ScreenTag(Enum):
    MENU = 1
    PUZZLE = 2


class Screen(ABC):
    screen: pygame.Surface
    tag: ScreenTag
    buttons: dict[ButtonTag, Button] = {}

    def __init__(self, size: tuple[int, int], tag: ScreenTag):
        self.screen = pygame.Surface(size)
        self.tag = tag

    @abstractmethod
    def load_buttons(self, size: int):
        pass

    @abstractmethod
    def draw(self, *args, **kwargs) -> pygame.Surface:
        return self.screen

    @abstractmethod
    def query(self, mouse_click: tuple[int, int]) -> Event:
        return Event.NONE

    @abstractmethod
    def get_button_event(self, b: Button) -> Event:
        return Event.NONE

    def scale(self, value: float, side: str = "w") -> int:
        """Scales a value with one of this screen's dimensions"""
        if side not in ["w", "h"]:
            raise ValueError
        if side == "w":
            factor = self.screen.get_rect().w
        elif side == "h":
            factor = self.screen.get_rect().h
        return max(round(value * factor / 1000), 1)


# TODO
class MenuScreen(Screen):
    def __init__(self, size: tuple[int, int]):
        super().__init__(size, ScreenTag.MENU)

    def load_buttons(self, size: int):
        pass

    def draw(self, state: AppState) -> pygame.Surface:
        return self.screen

    def query(self, mouse_pos: tuple[int, int]) -> Event:
        return Event.NONE

    def get_button_event(self, b: Button) -> Event:
        return Event.NONE


class PuzzleScreen(Screen):
    overlay: Pane
    header: Pane
    grid: Pane
    sidebar: Pane
    popup: Pane

    def __init__(self, size: tuple[int, int]):
        super().__init__(size, ScreenTag.PUZZLE)
        # screen should be 13 blocks wide and 10 blocks high
        w = size[0]
        bw = round(w / 13)
        gw = 9 * bw  # grid width
        sw = 4 * bw  # sidebar width
        self.overlay = Pane(0, bw, w, gw)
        self.header = Pane(0, 0, w, bw)
        self.grid = Pane(0, bw, gw, gw)
        self.sidebar = Pane(gw, bw, sw, gw)
        backer = pygame.Rect((0, 0), (6 * bw, 4 * bw))
        backer.center = (round(w / 2), round(bw + (bw * 9 / 2)))
        self.popup = Pane.from_rect(backer)
        self.load_buttons(round(bw / 2))

    def load_buttons(self, size: int):
        buttons = []
        buttons.append(Button(20, 10, size, size, ButtonTag.PAUSE))
        buttons.append(Button(20 + 2 * size, 10, size, size, ButtonTag.DELETE))
        buttons.append(Button(20 + 4 * size, 10, size, size, ButtonTag.HINT))
        buttons.append(Button(20 + 20 * size, 10, size, size, ButtonTag.SAVE))
        buttons.append(Button(20 + 22 * size, 10, size, size, ButtonTag.LOAD))
        buttons.append(Button(20 + 24 * size, 10, size, size, ButtonTag.RESET))

        for b in buttons:
            b.set_image(image_path(b.tag.value))
            self.buttons[b.tag] = b

    def query(self, mouse_pos: tuple[int, int]) -> Event:
        for _, b in self.buttons.items():
            if b.is_pressed(mouse_pos):
                return self.get_button_event(b)
        # TODO: check if keypad on sidebar is pressed here
        return Event.NONE

    def get_button_event(self, b: Button) -> Event:
        if b is None:
            return Event.NONE
        match b.tag:
            case ButtonTag.PAUSE:
                self.buttons.pop(b.tag)
                b.tag = ButtonTag.RESUME
                b.set_image(image_path(b.tag.value))
                self.buttons[b.tag] = b
                return Event.PAUSE
            case ButtonTag.RESUME:
                self.buttons.pop(b.tag)
                b.tag = ButtonTag.PAUSE
                b.set_image(image_path(b.tag.value))
                self.buttons[b.tag] = b
                return Event.RESUME
            case ButtonTag.RESET:
                return Event.RESET
            case ButtonTag.SAVE:
                return Event.SAVE
            case ButtonTag.LOAD:
                return Event.LOAD
            case ButtonTag.DELETE:
                return Event.DELETE
            case ButtonTag.HINT:
                return Event.HINT
            case _:
                return Event.NONE

    def draw(self, puzzle: PuzzleState, fm: FontManager) -> pygame.Surface:
        # if puzzle has hints, add hint button here
        self.screen.fill(WHITE)

        self.screen.blit(self.draw_grid(puzzle, fm), self.grid.pos())
        self.screen.blit(self.draw_header(puzzle, fm), self.header.pos())
        self.screen.blit(self.draw_sidebar(puzzle, fm), self.sidebar.pos())

        font_xs = fm.load_font(self.scale(FONT_XS))
        for _, b in self.buttons.items():
            self.screen.blit(b.image.convert_alpha(), b.pos())
            text = font_xs.render(b.tag.value, 1, BLACK)
            self.screen.blit(
                text,
                text.get_rect(center=b.tag_pos()),
            )

        if puzzle.paused:
            self.overlay.surface.fill((255, 255, 255, 128))
            self.screen.blit(self.overlay.surface, self.overlay.pos())
            self.screen.blit(self.draw_popup(fm), self.popup.pos())

        return self.screen

    def draw_grid(self, puzzle: PuzzleState, fm: FontManager) -> pygame.Surface:
        font_l = fm.load_font(self.scale(FONT_L))
        font_xs = fm.load_font(self.scale(FONT_XS))

        self.grid.surface.fill(WHITE)
        rect = self.grid.rect()

        cell_w = round(rect.w / 9)
        cell_h = round(rect.h / 9)
        index = 0
        for y in fstep(0, cell_h, 9):
            for x in fstep(0, cell_w, 9):
                cell = puzzle.sudoku.get_cell(index)
                # colour cell
                cell_colour = get_cell_colour(cell, puzzle.sudoku)
                cell_rect = pygame.draw.rect(
                    self.grid.surface,
                    cell_colour,
                    pygame.Rect(x, y, cell_w, cell_h),
                )
                # draw cell digit(s)
                if cell.digit() != "0":
                    digit_colour = get_digit_colour(cell, puzzle.sudoku)
                    cell_display = font_l.render(cell.digit(), 1, digit_colour)
                    self.grid.surface.blit(
                        cell_display, cell_display.get_rect(center=cell_rect.center)
                    )
                else:
                    for c in cell.candidates():
                        i = int(c) - 1
                        xb = (i % 3) * (rect.w / 30) + (cell_w / 7)
                        yb = (int)(i / 3) * (rect.h / 30) + (cell_h / 11)
                        self.grid.surface.blit(
                            font_xs.render(c, 1, BLACK),
                            (x + xb, y + yb),
                        )
                index += 1

        # split grid into 9 equal-sized boxes
        line = self.scale(4)
        d1 = round(rect.w / 3)
        d2 = round(2 * rect.w / 3)
        pygame.draw.line(self.grid.surface, BLACK, (d1, 0), (d1, rect.h), line)
        pygame.draw.line(self.grid.surface, BLACK, (d2, 0), (d2, rect.h), line)
        pygame.draw.line(self.grid.surface, BLACK, (0, d1), (rect.w, d1), line)
        pygame.draw.line(self.grid.surface, BLACK, (0, d2), (rect.w, d2), line)

        # split each box into 9 equal-sized cells
        for x in fstep(0, cell_w, 9):
            pygame.draw.line(self.grid.surface, BLACK, (x, 0), (x, rect.h))
        for y in fstep(0, cell_h, 9):
            pygame.draw.line(self.grid.surface, BLACK, (0, y), (rect.w, y))

        self.grid.outline(width=line)
        return self.grid.surface

    def draw_header(self, puzzle: PuzzleState, fm: FontManager) -> pygame.Surface:
        font_m = fm.load_font(self.scale(FONT_M))
        font_s = fm.load_font(self.scale(FONT_S))

        time = puzzle.time
        clock = f"{str(time[1]).rjust(2, "0")}:{str(time[0]).rjust(2, "0")}"
        if time[2] != 0:
            clock = f"{time[2]}:" + clock
        if not puzzle.solved:
            msg_1 = clock
            msg_2 = puzzle.sudoku.title
        else:
            msg_1 = "Congratulations!"
            msg_2 = f"Puzzle solved in {clock}"

        self.header.surface.fill(GREY)
        head = self.header.rect()
        display_1 = font_m.render(msg_1, 1, BLACK)
        rect_1 = pygame.Rect(0, head.h * 0.1, head.w, head.h * 0.5)
        self.header.surface.blit(display_1, display_1.get_rect(center=rect_1.center))
        display_2 = font_s.render(msg_2, 1, BLACK)
        rect_2 = pygame.Rect(0, head.h * 0.5, head.w, head.h * 0.5)
        self.header.surface.blit(display_2, display_2.get_rect(center=rect_2.center))

        self.header.outline(width=self.scale(4))
        return self.header.surface

    def draw_sidebar(self, puzzle: PuzzleState, fm: FontManager) -> pygame.Surface:
        self.sidebar.surface.fill(GREY)

        rect = self.sidebar.rect()
        size = round(3 * rect.w / 4)
        xo = round(rect.w / 8)
        yo = round(rect.h / 3)
        xe = xo + size
        ye = yo + size
        pygame.draw.line(self.sidebar.surface, BLACK, (xo, yo), (xe, yo))  # top
        pygame.draw.line(self.sidebar.surface, BLACK, (xo, ye), (xe, ye))  # bottom
        pygame.draw.line(self.sidebar.surface, BLACK, (xe, yo), (xe, ye))  # right
        pygame.draw.line(self.sidebar.surface, BLACK, (xo, yo), (xo, ye))  # left

        font_size = FONT_XS if puzzle.candidate_mode else FONT_M
        font = fm.load_font(self.scale(font_size))
        div = round(rect.w / 4)
        i = 1
        for y in fstep(yo, div, 3):
            for x in fstep(xo, div, 3):
                r = pygame.draw.rect(
                    self.sidebar.surface, WHITE, pygame.Rect((x, y), (div, div))
                )
                text = font.render(str(i), 1, BLACK)
                self.sidebar.surface.blit(text, text.get_rect(center=r.center))
                i += 1

        for x in fstep(xo, div, 3):
            pygame.draw.line(self.sidebar.surface, BLACK, (x, yo), (x, ye))
        for y in fstep(yo, div, 3):
            pygame.draw.line(self.sidebar.surface, BLACK, (xo, y), (xe, y))

        self.sidebar.outline(width=self.scale(4))
        return self.sidebar.surface

    def draw_popup(self, fm: FontManager) -> pygame.Surface:
        font_l = fm.load_font(self.scale(FONT_L))
        rect = self.popup.surface.get_rect()
        pygame.draw.rect(self.popup.surface, WHITE, rect, border_radius=20)
        display = font_l.render("Game Paused", 1, BLACK)
        self.popup.surface.blit(display, display.get_rect(center=rect.center))
        return self.popup.surface


class ScreenManager:
    """Manages the main pygame window as well as all app screens."""

    _window: pygame.Surface
    _font_manager: FontManager
    _screens: dict[ScreenTag, Screen] = {}
    _current: Screen | None = None
    _clock: pygame.time.Clock
    fps: int

    def __init__(self, window_width: int, fps: int):
        # maintain 13:10 screen size
        height = round(10 * window_width / 13)
        self._window = pygame.display.set_mode((window_width, height))
        self._font_manager = FontManager()
        self._clock = pygame.time.Clock()
        self.fps = fps

    def width(self) -> int:
        return self._window.get_rect().w

    def height(self) -> int:
        return self._window.get_rect().h

    def size(self) -> tuple[int, int]:
        return self._window.get_size()

    def update(self, puzzle: PuzzleState):
        s = self._current
        if s != None:
            screen = s.draw(puzzle, self._font_manager)
            scaled = pygame.transform.scale(screen, self.size())
            self._window.blit(scaled, (0, 0))
        pygame.display.flip()
        self._clock.tick(self.fps)

    def add_screen(self, tag: ScreenTag):
        match tag:
            case ScreenTag.MENU:
                self._screens[tag] = MenuScreen(self.size())
            case ScreenTag.PUZZLE:
                self._screens[tag] = PuzzleScreen(self.size())
            case _:
                raise KeyError

    def get_screen(self, tag: ScreenTag) -> Screen:
        return self._screens[tag]

    def get_screens(self) -> dict[ScreenTag, Screen]:
        return self._screens

    def swap_screen(self, tag: ScreenTag):
        if tag not in list(self._screens):
            self.add_screen(tag)
        self._current = self.get_screen(tag)

    def set_caption(self, caption: str):
        pygame.display.set_caption(caption)

    def query(self, mouse_pos: tuple[int, int] | None) -> Event:
        if self._current is not None and mouse_pos is not None:
            return self._current.query(mouse_pos)
        else:
            return Event.NONE


def get_cell_colour(cell: Cell, sudoku: Sudoku) -> pygame.Color:
    current_cell = sudoku.current_cell()
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


def get_digit_colour(cell: Cell, sudoku: Sudoku) -> pygame.Color:
    digit_colour = DARK_BLUE if not cell.is_fixed() else BLACK
    for i in cell.sightline():
        c = sudoku.get_cell(i)
        if c.digit() == cell.digit():
            digit_colour = RED
            break
    return digit_colour
