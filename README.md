# Simple Sudoku

A sudoku app built with Python and pygame. Includes 50 pre-determined configurations to choose from.

## Instructions

### Using the Sudoku App

Either clone this repository onto your local machine with

```bash
git clone https://github.com/lexaprobe/sudoku.git
```

**OR** navigate to the main page of this repository, click the green Code button, and select "Download ZIP".

Then, in the project's root directory:

- Create a virtual environment and activate it

  ```bash
  python3.13 -m venv .venv
  source .venv/bin/activate
  ```

- Ensure pip is updated and install the sudoku package in editable mode

  ```bash
  pip install --upgrade pip
  pip install -e .
  ```

- Run the app with

  ```bash
  python -m sudoku <seed>
  ```

The seed argument determines which sudoku configuration will be used. Seeds can be a number from 1 through 50 *or* easy/medium/hard to play the corresponding daily NYT sudoku.

### How to Play

Click on a square to highlight it.

Once highlighted, a number can be entered using the keyboard.

To add a candidate to a square, hold SHIFT to enter candidate mode.

Candidates can then be added and removed using the keyboard.

To remove a number from a square, press DELETE.

Pause the game by pressing ESCAPE.
