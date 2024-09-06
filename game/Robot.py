import random
import pygame
from game.Package import Package
from game.consts import DEFAULT_IMAGE_SIZE


class Robot:
    image_paths = {
        'blue': 'images/blue_robot.png',
        'red': 'images/red_robot.png',
        'green': 'images/green_robot.png',
        'orange': 'images/orange_robot.png'
    }

    def __init__(self, color, pos, index, width=DEFAULT_IMAGE_SIZE[0], height=DEFAULT_IMAGE_SIZE[1]):
        self.number_img = None
        self.color = color
        self.pos = pos
        self.has_package = False
        self.package = None
        self.index = index
        self.set_number_image()
        image = pygame.image.load(Robot.image_paths[color])
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect(topleft=((pos[0] + 1) * width, (pos[1] + 1) * height))

    def move(self, direction, board):
        x, y = self.pos
        if direction == "up" and y > 0:
            new_y = y - 1
            new_x = x
        elif direction == "down" and y < board.size - 1:
            new_y = y + 1
            new_x = x
        elif direction == "left" and x > 0:
            new_x = x - 1
            new_y = y
        elif direction == "right" and x < board.size - 1:
            new_x = x + 1
            new_y = y
        else:
            return False
        if 0 <= new_x < board.size and 0 <= new_y < board.size:
            if not board.isOccupied(new_x, new_y):
                board.UpdatePosition(self.pos, (new_x, new_y))
                if not self.has_package:
                    cell = board[new_y][new_x]
                    if cell.color == 'a':
                        below_cell = board[new_y + 1][new_x]
                        if below_cell.color == 'r' and below_cell.package and not below_cell.package.picked_up:
                            self.pick_package(below_cell.package, board)
                    elif cell.package and not cell.package.picked_up and cell.color != 'a':
                        self.pick_package(cell.package, board)
                self.pos = (new_x, new_y)
                self.rect.topleft = ((new_x + 1) * DEFAULT_IMAGE_SIZE[0], (new_y + 1) * DEFAULT_IMAGE_SIZE[1])
                if self.package:
                    self.package.set_position(self.pos)
                return True
        return False

    def pick_package(self, package, board):
        self.has_package = True
        self.package = package
        package.pick_up()

        # Generate a new package at the old position
        new_package = Package(package.pos)
        new_package.number = random.randint(1, 9)  # Assign a random number to the new package
        board[package.pos[1]][package.pos[0]].package = new_package

    def drop_package(self):
        if not self.has_package:
            return False

        self.package.drop_off()
        self.package = None
        self.has_package = False
        return True

    def RobotAnimator(self, screen):
        screen.blit(self.image, self.rect)
        if self.number_img:
            number_pos = (
                self.rect.x + self.rect.width // 2 - self.number_img.get_width() // 2,
                self.rect.y + self.rect.height // 2 - self.number_img.get_height() // 2
            )

            screen.blit(self.number_img, number_pos)

        if self.package:
            package_image = pygame.image.load('images/package.png')
            package_image = pygame.transform.scale(package_image,
                                                   (DEFAULT_IMAGE_SIZE[0] * 1.3, DEFAULT_IMAGE_SIZE[1] * 1.3))
            package_pos = (
                self.rect.x + self.rect.width // 2 - package_image.get_width() // 2,
                self.rect.y - self.rect.height // 2 + DEFAULT_IMAGE_SIZE[0] * 0.38
            )
            screen.blit(package_image, package_pos)

            package_number_font = pygame.font.SysFont(None, 48)  # Увеличиваем шрифт
            number_img = package_number_font.render(str(self.package.number), True, (0, 0, 0))
            number_pos = (
                package_pos[0] + package_image.get_width() // 2 - number_img.get_width() // 2,
                package_pos[1] + package_image.get_height() // 2 - number_img.get_height() * 1.4  # Смещение выше
            )
            screen.blit(number_img, number_pos)

    def set_number_image(self):
        robot_number_font = pygame.font.SysFont(None, 32)
        self.number_img = robot_number_font.render(str(self.index), True, (0, 0, 0))
