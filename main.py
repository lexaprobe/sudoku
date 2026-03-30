import sys

import pygame


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
        seed = 0
    else:
        seed = sys.argv[1]
    grid = get_seed(seed)
    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 70)
    font_b = pygame.font.SysFont("Arial", 20)
    window = pygame.display.set_mode((900, 900))
    pygame.display.set_caption("Sudoku")

    sudoku = []
    candidates = []
    for i in range(81):
        candidates.append([])
    set_indices = []
    for i in range(len(grid)):
        sudoku.append(grid[i])
        if grid[i] != "0":
            set_indices.append(i)

    coords = None
    current = None
    candidate_mode = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                coords = pygame.mouse.get_pos()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    candidate_mode = not candidate_mode
                if event.key == pygame.K_s:
                    save_state(sudoku, candidates)
                if current is None or current in set_indices:
                    continue
                number = get_number(event.key)
                if number is None:
                    continue
                if not candidate_mode:
                    sudoku[current] = number
                else:
                    if number == "0":
                        candidates[current] = []
                    elif number not in candidates[current]:
                        candidates[current].append(number)
                    else:
                        candidates[current].remove(number)

        window.fill(pygame.Color("WHITE"))
        current = highlight_square(coords, window, candidate_mode)

        # 3x3 grids
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

        box = 0
        for j in range(10, 910, 100):
            for i in range(30, 930, 100):
                if sudoku[box] != "0":
                    window.blit(
                        font.render(sudoku[box], 1, pygame.Color("BLACK")), (i, j)
                    )
                else:
                    buffer_x = 0
                    buffer_y = 0
                    count = 0
                    for p in range(1, 10):
                        if str(p) in candidates[box]:
                            window.blit(
                                font_b.render(str(p), 1, pygame.Color("BLACK")),
                                (i - 17 + buffer_x, j - 1 + buffer_y),
                            )
                        buffer_x += 30
                        count += 1
                        if count % 3 == 0:
                            buffer_x = 0
                            buffer_y += 30
                box += 1

        pygame.display.update()


def highlight_square(
    coords: tuple | None, window: pygame.Surface, candidate_mode: bool
):
    if coords is None:
        return None
    current = 0
    for y in range(0, 900, 100):
        for x in range(0, 900, 100):
            x_diff = coords[0] - x
            y_diff = coords[1] - y
            if x_diff <= 100 and y_diff <= 100:
                color = pygame.Color("GRAY")
                if candidate_mode:
                    color = pygame.Color("LIGHT BLUE")
                pygame.draw.rect(window, color, pygame.Rect(x, y, 100, 100))
                return current
            current += 1


def save_state(sudoku: list[str], candidates: list[str]):
    pass


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
