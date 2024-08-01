import random
from game.Robot import Robot

class Player:
    def __init__(self, color, num_robots, white_cells):
        self.color = color
        self.robots = []
        for i in range(num_robots):
            pos = random.choice(white_cells)
            white_cells.remove(pos)
            robot = Robot(color, pos=pos, index=i + 1)
            self.robots.append(robot)

    def move_robot(self, robot_index, direction, board):

        if 0 <= robot_index < len(self.robots):
            return self.robots[robot_index].move(direction, board)
        return False

    def draw_robots(self, screen):
        for robot in self.robots:
            robot.draw(screen)