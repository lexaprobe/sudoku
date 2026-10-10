from enum import Enum

import pygame


class ButtonTag(Enum):
    PAUSE = "Pause"
    RESUME = "Resume"
    RESET = "Reset"
    SAVE = "Save"
    LOAD = "Load"
    HINT = "Hint"
    SWITCH = "Switch Mode"
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

    def set_image(self, image_path: str):
        try:
            image = pygame.image.load(image_path)
            w, h = self.image.get_size()
            self.image = pygame.transform.smoothscale(image, (w, h))
        except FileNotFoundError:
            print(f"Failed to load image: {image_path}")

    def is_pressed(self, mouse_pos: tuple[int, int]) -> bool:
        return pygame.Rect((self.x, self.y), self.image.get_size()).collidepoint(
            mouse_pos
        )

    def pos(self) -> tuple[float, float]:
        return (self.x, self.y)

    def tag_pos(self) -> tuple[float, float]:
        w, h = self.image.get_size()
        return (self.x + w / 2, self.y + 4 * h / 3)

    def scale(self, factor: float):
        w, h = self.image.get_size()
        self.image = pygame.transform.smoothscale(self.image, (w * factor, h * factor))
