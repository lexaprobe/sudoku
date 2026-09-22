import json

import requests
from bs4 import BeautifulSoup

URL = "https://www.nytimes.com/puzzles/sudoku/hard"


def fetch_puzzle_data():
    r = requests.get(URL)
    if not r.ok:
        return None

    for script in BeautifulSoup(r.text, "html.parser").find_all("script"):
        if "window.gameData" in script.text:
            puzzle_data = json.loads(script.text.lstrip("window.gameData = "))
            break

    return puzzle_data


def daily_puzzle(mode: str) -> str:
    puzzle_data = fetch_puzzle_data()
    if puzzle_data is None or mode.lower() not in ["easy", "medium", "hard"]:
        return ""
    return "".join(str(x) for x in puzzle_data[mode]["puzzle_data"]["puzzle"])
