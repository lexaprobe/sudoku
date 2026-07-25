import sys

import pygame

from sudoku import Cell, Sudoku

GREY = pygame.Color(223, 223, 223)
YELLOW = pygame.Color(249, 219, 74)
BLUE = pygame.Color(195, 225, 255)
RED = pygame.Color(236, 90, 92)
WHITE = pygame.Color(255, 255, 255)
BLACK = pygame.Color(0, 0, 0)

FONT_XS: pygame.font.Font | None = None
FONT_S: pygame.font.Font | None = None
FONT_M: pygame.font.Font | None = None
FONT_L: pygame.font.Font | None = None

GRID_WIDTH = 900
GRID_HEIGHT = 900
GRID_OFFSET = 81


def get_seed(seed: int) -> str:
    with open("grid_seeds.txt") as f:
        grid_seeds = f.read().split("\n\n")
        try:
            seed = int(seed)
            if seed < 0 or seed > 49:
                raise TypeError
        except TypeError:
            seed = 0
        return grid_seeds[seed].replace("\n", "")


def main():
    global FONT_XS, FONT_S, FONT_M, FONT_L
    if len(sys.argv) < 2:
        seed_number = 0
    else:
        seed_number = int(sys.argv[1])
    seed = get_seed(seed_number)

    sudoku = Sudoku()
    sudoku.set_grid(seed)

    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()
    FONT_XS = pygame.font.SysFont("Arial", 20)
    FONT_S = pygame.font.SysFont("Arial", 35)
    FONT_M = pygame.font.SysFont("Arial", 50)
    FONT_L = pygame.font.SysFont("Arial", 70)
    window = pygame.display.set_mode((GRID_WIDTH, GRID_HEIGHT + GRID_OFFSET))
    grid = pygame.surface.Surface((GRID_WIDTH, GRID_HEIGHT))
    header = pygame.surface.Surface((GRID_WIDTH, GRID_OFFSET))
    pygame.display.set_caption("Sudoku")

    candidate_mode = False
    coords = None
    frames = 0
    solved = False
    solve_time = (0, 0, 0)

    while True:
        cell = sudoku.current_cell()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coords = pygame.mouse.get_pos()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    candidate_mode = not candidate_mode
                if cell is None or cell.is_fixed():
                    continue
                digit = get_number(event.key)
                if digit is None or solved:
                    continue
                if not candidate_mode:
                    cell.insert_digit(digit)
                else:
                    if digit == "0":
                        cell.clear_candidates_corner()
                    else:
                        cell.insert_candidate_corner(digit)
        sudoku.set_current_cell(get_cell(coords))
        if not solved:
            solved = sudoku.is_solved()
            if solved:
                solve_time = get_time(frames, 60)

        window.blit(draw_grid(grid, sudoku), (0, GRID_OFFSET))
        time = solve_time if solved else get_time(frames, 60)
        window.blit(draw_header(header, time, solved), (0, 0))
        pygame.display.flip()

        clock.tick(60)
        frames += 1


def get_cell(coords: tuple | None) -> int | None:
    if coords is None or coords[1] <= GRID_OFFSET:
        return None
    cell_index = 0
    for y in range(GRID_OFFSET, 900 + GRID_OFFSET, 100):
        for x in range(0, 900, 100):
            x_diff = coords[0] - x
            y_diff = coords[1] - y
            if x_diff <= 100 and y_diff <= 100:
                return cell_index
            cell_index += 1
    return None


def get_time(frames: int, fps: int) -> tuple[int, int, int]:
    seconds = int(frames / fps)
    minutes = int((seconds - seconds % 60) / 60)
    hours = int((minutes - minutes % 60) / 60)
    return (seconds % 60, minutes % 60, hours % 24)


def draw_header(
    surface: pygame.Surface,
    time: tuple[int, int, int],
    solved: bool,
) -> pygame.Surface:
    surface.fill(GREY)
    if FONT_M is None or FONT_S is None or FONT_XS is None:
        return surface
    clock = f"{str(time[1]).rjust(2, "0")}:{str(time[0]).rjust(2, "0")}"
    if time[2] != 0:
        clock = f"{time[2]}:" + clock
    if not solved:
        display = FONT_M.render(clock, 1, BLACK)
        surface.blit(display, display.get_rect(center=surface.get_rect().center))
    else:
        display_1 = FONT_S.render("Congratulations!", 1, BLACK)
        rect_1 = pygame.Rect(0, 0, GRID_WIDTH, 2 * GRID_OFFSET / 3)
        surface.blit(display_1, display_1.get_rect(center=rect_1.center))
        display_2 = FONT_XS.render("Sudoku solved in " + clock, 1, BLACK)
        rect_2 = pygame.Rect(0, (2 * GRID_OFFSET / 3) - 5, GRID_WIDTH, GRID_OFFSET / 3)
        surface.blit(display_2, display_2.get_rect(center=rect_2.center))
    return surface


def draw_grid(
    surface: pygame.Surface,
    sudoku: Sudoku,
) -> pygame.Surface:
    surface.fill(WHITE)

    cell_number = 0
    current_cell = sudoku.current_cell()
    for y in range(0, 900, 100):
        for x in range(0, 900, 100):
            cell = sudoku.get_grid()[cell_number]

            # colour cell
            cell_colour = get_cell_colour(cell, current_cell)
            cell_rect = pygame.draw.rect(
                surface,
                cell_colour,
                pygame.Rect(x, y, 100, 100),
            )

            # draw cell digit(s)
            if FONT_XS is None or FONT_L is None:
                cell_number += 1
                continue
            if cell.digit() != "0":
                digit_colour = get_digit_colour(cell, sudoku)
                cell_display = FONT_L.render(cell.digit(), 1, digit_colour)
                surface.blit(
                    cell_display, cell_display.get_rect(center=cell_rect.center)
                )
            else:
                buffer_x = 0
                buffer_y = 0
                count = 0
                for p in range(1, 10):
                    if str(p) in cell.candidates_corner():
                        surface.blit(
                            FONT_XS.render(str(p), 1, BLACK),
                            (x + 30 - 17 + buffer_x, y + 10 - 1 + buffer_y),
                        )
                    buffer_x += 30
                    count += 1
                    if count % 3 == 0:
                        buffer_x = 0
                        buffer_y += 30
            cell_number += 1

    # 3x3 boxes
    pygame.draw.line(surface, BLACK, (300, 0), (300, 900), 4)
    pygame.draw.line(surface, BLACK, (600, 0), (600, 900), 4)
    pygame.draw.line(surface, BLACK, (0, 0), (900, 0), 4)
    pygame.draw.line(surface, BLACK, (0, 300), (900, 300), 4)
    pygame.draw.line(surface, BLACK, (0, 600), (900, 600), 4)

    # soft verticals
    for x in range(0, 900, 100):
        pygame.draw.line(surface, BLACK, (x, 0), (x, 900))
    # soft horizontals
    for y in range(0, 900, 100):
        pygame.draw.line(surface, BLACK, (0, y), (900, y))

    return surface


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


def get_digit_colour(cell: Cell, sudoku: Sudoku) -> pygame.Color:
    digit_colour = BLACK
    for i in cell.sightline():
        c = sudoku.get_cell(i)
        if c != None and c.digit() == cell.digit():
            digit_colour = RED
            break
    return digit_colour


def get_number(key):
    if key == pygame.K_1:
        return "1"
    elif key == pygame.K_2:
        return "2"
    elif key == pygame.K_3:
        return "3"
    elif key == pygame.K_4:
        return "4"
    elif key == pygame.K_5:
        return "5"
    elif key == pygame.K_6:
        return "6"
    elif key == pygame.K_7:
        return "7"
    elif key == pygame.K_8:
        return "8"
    elif key == pygame.K_9:
        return "9"
    elif key == pygame.K_BACKSPACE:
        return "0"
    else:
        return None


if __name__ == "__main__":
    main()
