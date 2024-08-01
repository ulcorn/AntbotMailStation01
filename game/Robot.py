import pygame

class Robot:

    image_paths = {
        'blue': 'images/blue_robot.png',
        'red': 'images/red_robot.png',
        'green': 'images/green_robot.png',
        'orange': 'images/orange_robot.png'
    }

    def __init__(self, color, pos, index, width=48, height=48):
        self.number_img = None
        self.color = color
        self.pos = pos
        self.has_package = False
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
            self.pos = (new_x, new_y)
            self.rect.topleft = ((new_x + 1) * 48, (new_y + 1) * 48)
            return True
        return False

    def draw(self, screen):

        screen.blit(self.image, self.rect)

        if self.number_img:

            number_pos = (
                self.rect.x + self.rect.width // 2 - self.number_img.get_width() // 2,
                self.rect.y + self.rect.height // 2 - self.number_img.get_height() // 2
            )
            screen.blit(self.number_img, number_pos)

    def set_number_image(self):
        robot_number_font = pygame.font.SysFont(None, 32)
        self.number_img = robot_number_font.render(str(self.index), True, (0, 0, 0))