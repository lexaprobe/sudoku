import sys

import pygame

from sudoku import Sudoku


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
    if len(sys.argv) < 2:
        seed_number = 0
    else:
        seed_number = int(sys.argv[1])
    seed = get_seed(seed_number)

    sudoku = Sudoku()
    sudoku.set_grid(seed)

    pygame.init()
    pygame.font.init()
    font_a = pygame.font.SysFont("Arial", 70)
    font_b = pygame.font.SysFont("Arial", 20)
    window = pygame.display.set_mode((900, 900))
    pygame.display.set_caption("Sudoku")

    candidate_mode = False
    coords = None

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
                if digit is None:
                    continue
                if not candidate_mode:
                    cell.insert_digit(digit)
                else:
                    if digit == "0":
                        cell.clear_candidates_corner()
                    else:
                        cell.insert_candidate_corner(digit)

        sudoku.set_current_cell(get_cell(coords))
        draw_grid(window, sudoku, font_a, font_b)
        pygame.display.update()


def get_cell(coords: tuple | None) -> int | None:
    if coords is None:
        return None
    cell_index = 0
    for y in range(0, 900, 100):
        for x in range(0, 900, 100):
            x_diff = coords[0] - x
            y_diff = coords[1] - y
            if x_diff <= 100 and y_diff <= 100:
                return cell_index
            cell_index += 1
    return None


def draw_grid(
    window: pygame.Surface,
    sudoku: Sudoku,
    font_a: pygame.font.Font,
    font_b: pygame.font.Font,
):
    window.fill(pygame.Color("WHITE"))

    # light grey - 223, 223, 223
    # yellow - 249, 219, 74
    # blue - 177, 215, 251
    # light blue - 223, 238, 253

    # cell tints and digits
    cell_number = 0
    for y in range(0, 900, 100):
        for x in range(0, 900, 100):
            cell = sudoku.get_grid()[cell_number]
            if cell.is_fixed():
                pygame.draw.rect(
                    window, pygame.Color(223, 223, 223), pygame.Rect(x, y, 100, 100)
                )
            if sudoku.is_current_cell(cell):
                pygame.draw.rect(
                    window, pygame.Color(177, 215, 251), pygame.Rect(x, y, 100, 100)
                )
            if cell.digit() != "0":
                window.blit(
                    font_a.render(cell.digit(), 1, cell.digit_colour()),
                    (x + 30, y + 10),
                )
            else:
                buffer_x = 0
                buffer_y = 0
                count = 0
                for p in range(1, 10):
                    if str(p) in cell.candidates_corner():
                        window.blit(
                            font_b.render(str(p), 1, cell.digit_colour()),
                            (x + 30 - 17 + buffer_x, y + 10 - 1 + buffer_y),
                        )
                    buffer_x += 30
                    count += 1
                    if count % 3 == 0:
                        buffer_x = 0
                        buffer_y += 30
            cell_number += 1

    # 3x3 boxes
    pygame.draw.line(window, pygame.Color("BLACK"), (300, 0), (300, 900), 4)
    pygame.draw.line(window, pygame.Color("BLACK"), (600, 0), (600, 900), 4)
    pygame.draw.line(window, pygame.Color("BLACK"), (0, 300), (900, 300), 4)
    pygame.draw.line(window, pygame.Color("BLACK"), (0, 600), (900, 600), 4)

    # soft verticals
    for x in range(0, 900, 100):
        pygame.draw.line(window, pygame.Color("BLACK"), (x, 0), (x, 900))
    # soft horizontals
    for y in range(0, 900, 100):
        pygame.draw.line(window, pygame.Color("BLACK"), (0, y), (900, y))


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
