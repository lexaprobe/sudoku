class PuzzleState:
    candidate_mode: bool
    paused: bool
    solved: bool
    time: tuple[int, int, int]
    solve_time: tuple[int, int, int]

    def __init__(self):
        self.candidate_mode = False
        self.paused = False
        self.solved = False
        self.time = (0, 0, 0)
        self.solve_time = self.time
