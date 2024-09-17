import random

import pygame

from game.consts import DEFAULT_IMAGE_SIZE


class Package:
    def __init__(self, pos):
        self.pos = pos
        self.number = random.randint(1, 9)  # Generate a random number
        self.picked_up = False
        self.visible = True
        self.image = pygame.transform.scale(
            pygame.image.load('images/package.png'),
            (DEFAULT_IMAGE_SIZE[0] * 2,
             DEFAULT_IMAGE_SIZE[1] * 2
             )
        )

    def pick_up(self):
        self.picked_up = True

    def drop_off(self):
        self.picked_up = False
        self.number = None

    def set_position(self, pos):
        self.pos = pos

    def draw(self, screen, x: int, y: int):
        pos = (
            (x + 1) * DEFAULT_IMAGE_SIZE[0] + (DEFAULT_IMAGE_SIZE[0] - self.image.get_width()) / 2,
            (y + 2) * DEFAULT_IMAGE_SIZE[1] - self.image.get_height() / 2
        )
        screen.blit(self.image, pos)

        number_font = pygame.font.SysFont(None, 48)
        number_img = number_font.render(
            str(self.number),
            True,
            (0, 0, 0)
        )
        number_pos = (
            pos[0] + self.image.get_width() / 2 - number_img.get_width() / 2,
            pos[1] + self.image.get_height() / 2 - number_img.get_height() / 2 - 40
        )
        screen.blit(number_img, number_pos)
