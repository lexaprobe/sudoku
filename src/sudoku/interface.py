from enum import Enum

import pygame


class ButtonTag(Enum):
    PAUSE = "Pause"
    RESET = "Reset"


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

    def set_image(self, image: pygame.Surface):
        rect = self.image.get_rect()
        self.image = pygame.transform.smoothscale(image, (rect.w, rect.h))

    def is_pressed(self) -> bool:
        action = False
        if (
            pygame.mouse.get_pressed()[0] == 1
            and self.image.get_rect().collidepoint(pygame.mouse.get_pos())
            and self.pressed == False
        ):
            self.pressed = True
            action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.pressed = False

        return action

    def pos(self) -> tuple[float, float]:
        rect = self.image.get_rect()
        return (rect.x, rect.y)

    def tag_pos(self) -> tuple[float, float]:
        rect = self.image.get_rect()
        return (rect.x + rect.w / 2, rect.h + rect.h / 3)

    def scale(self, factor: float):
        r = self.image.get_rect()
        self.image = pygame.transform.smoothscale(
            self.image, (r.w * factor, r.h * factor)
        )
