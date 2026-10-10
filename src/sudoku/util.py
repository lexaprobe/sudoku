import json
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup

IMAGES = "src/sudoku/resources/images"
PUZZLES = "src/sudoku/resources/puzzles.txt"

NYT_SUDOKU_URL = "https://www.nytimes.com/puzzles/sudoku/hard"


def image_path(tag: str) -> str:
    return str(Path(f"{IMAGES}/{tag}.png").resolve())


def fetch_daily_puzzle(mode: str) -> dict[str, Any] | None:
    if mode.lower() not in ["easy", "medium", "hard"]:
        return None

    r = requests.get(NYT_SUDOKU_URL)
    if not r.ok:
        return None
    for script in BeautifulSoup(r.text, "html.parser").find_all("script"):
        if "window.gameData" in script.text:
            puzzle_data = json.loads(script.text.lstrip("window.gameData = "))
            break

    if puzzle_data is None:
        return None
    puzzle = "".join(str(x) for x in puzzle_data[mode.lower()]["puzzle_data"]["puzzle"])
    hints = puzzle_data[mode.lower()]["puzzle_data"]["hints"]
    title = f"NYT {mode.capitalize()} Puzzle — {puzzle_data["displayDate"]}"
    return {"puzzle": puzzle, "hints": hints, "title": title}


def get_puzzle(args: list[str]) -> dict[str, Any]:
    ret = {"puzzle": "", "title": "", "hints": [], "err": ""}
    if len(args) < 2:
        ret["err"] = (
            f"\nError: No parameters given\nExpected:\n\tmain.py <seed>\nOR\n\tmain.py <mode>"
        )
        return ret
    p = args[1]
    if p.isdigit():
        with open(Path(PUZZLES).resolve()) as f:
            puzzles = f.read().split("\n\n")
            seed = int(p) - 1
            if seed < 0 or seed > 49:
                ret["err"] = (
                    f"\nError: Invalid seed: '{p}'\nExpected a number between 1 and 50"
                )
            else:
                ret["puzzle"] = puzzles[seed].replace("\n", "")
                ret["title"] = f"Puzzle {p}"
    elif p.isalpha():
        mode = p.lower()
        puzzle_data = fetch_daily_puzzle(mode)
        if puzzle_data is None:
            ret["err"] = f"\nError: Unable to retrieve puzzle data for mode '{mode}'"
            return ret
        ret["puzzle"] = puzzle_data["puzzle"]
        ret["title"] = puzzle_data["title"]
        ret["hints"] = puzzle_data["hints"]
    else:
        ret["err"] = (
            f"\nError: Invalid parameter: '{p}'\nExpected:\n\tmain.py <seed>\nOR\n\tmain.py <mode>"
        )
    return ret


def get_time(frames: int, fps: int) -> tuple[int, int, int]:
    seconds = int(frames / fps)
    minutes = int((seconds - seconds % 60) / 60)
    hours = int((minutes - minutes % 60) / 60)
    return (seconds % 60, minutes % 60, hours % 24)


def fstep(start: float, step: float, num_steps: int) -> list[float]:
    return [start + (x * step) for x in range(0, num_steps)]
