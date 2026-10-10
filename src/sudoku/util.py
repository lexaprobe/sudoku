import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

IMAGES = "src/sudoku/resources/images"
PUZZLES = "src/sudoku/resources/puzzles.txt"

NYT_SUDOKU_URL = "https://www.nytimes.com/puzzles/sudoku/hard"


def image_path(tag: str) -> str:
    return str(Path(f"{IMAGES}/{tag}.png").resolve())


def fetch_puzzle_data():
    r = requests.get(NYT_SUDOKU_URL)
    if not r.ok:
        return None

    for script in BeautifulSoup(r.text, "html.parser").find_all("script"):
        if "window.gameData" in script.text:
            puzzle_data = json.loads(script.text.lstrip("window.gameData = "))
            break

    return puzzle_data


def fetch_daily_puzzle(mode: str) -> str:
    puzzle_data = fetch_puzzle_data()
    if puzzle_data is None or mode.lower() not in ["easy", "medium", "hard"]:
        return ""
    return "".join(str(x) for x in puzzle_data[mode]["puzzle_data"]["puzzle"])


def get_puzzle(args: list[str]) -> tuple[str, str]:
    puzzle = ""
    msg = ""
    if len(args) < 2:
        msg = f"\nError: No parameters given\nExpected:\n\tmain.py <seed>\nOR\n\tmain.py <mode>"
        return (puzzle, msg)

    p = args[1]
    if p.isdigit():
        with open(Path(PUZZLES).resolve()) as f:
            puzzles = f.read().split("\n\n")
            seed = int(p) - 1
            if seed < 0 or seed > 49:
                msg = (
                    f"\nError: Invalid seed: '{p}'\nExpected a number between 1 and 50"
                )
            else:
                puzzle = puzzles[seed].replace("\n", "")
                msg = f"Puzzle {p}"
    elif p.isalpha():
        mode = p.lower()
        data = fetch_puzzle_data()
        puzzle = fetch_daily_puzzle(mode)
        if data is not None:
            msg = f"NYT {mode.capitalize()} Puzzle — {data["displayDate"]}"
        if puzzle == "":
            msg = f"\nError: Invalid mode: '{p}'\nExpected one of: 'easy', 'medium', or 'hard'"
    else:
        msg = f"\nError: Invalid parameter: '{p}'\nExpected:\n\tmain.py <seed>\nOR\n\tmain.py <mode>"
    return (puzzle, msg)


def get_time(frames: int, fps: int) -> tuple[int, int, int]:
    seconds = int(frames / fps)
    minutes = int((seconds - seconds % 60) / 60)
    hours = int((minutes - minutes % 60) / 60)
    return (seconds % 60, minutes % 60, hours % 24)


def fstep(start: float, step: float, num_steps: int) -> list[float]:
    return [start + (x * step) for x in range(0, num_steps)]
