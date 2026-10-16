from enum import Enum

import pygame


class ButtonTag(Enum):
    PAUSE = "Pause"
    RESUME = "Resume"
    RESET = "Reset"
    SAVE = "Save"
    LOAD = "Load"
    HINT = "Hint"
    NORMAL = "Normal Mode"
    CANDIDATE = "Candidate Mode"
    DELETE = "Delete"


class Button:
    image: pygame.Surface
    x: int
    y: int
    tag: ButtonTag
    pressed: bool = False

    def __init__(self, x: int, y: int, w: int, h: int, tag: ButtonTag):
        self.x = x
        self.y = y
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.tag = tag

    def set_image(self, image: pygame.Surface | None):
        w, h = self.image.get_size()
        if image is None:
            image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image = pygame.transform.smoothscale(image, (w, h))

    def rect(self) -> pygame.Rect:
        return pygame.Rect((self.x, self.y), self.image.get_size())

    def is_pressed(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect().collidepoint(mouse_pos)

    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def scale(self, factor: float):
        w, h = self.image.get_size()
        self.image = pygame.transform.smoothscale(self.image, (w * factor, h * factor))
