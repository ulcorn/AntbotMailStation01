from game.Robot import Robot


class Player:
    def __init__(self, color, num_robots, idx):
        self.color = color
        self.idx = idx
        self.num_robots = num_robots
        self.robots = []
        self.score = 0

    def place_robot(self, pos, board, robot_index):
        if not board.isOccupied(pos[0], pos[1]) and board[pos[0]][pos[1]].color == 'w':
            board.UpdatePosition(None, pos)
            robot = Robot(self.color, pos, robot_index + 1, self)
            self.robots.append(robot)
            return True
        return False

    def move_robot(self, robot_index, direction, board):
        if 0 <= robot_index < len(self.robots):
            return self.robots[robot_index].move(direction, board)
        return False

    def draw_robots(self, screen):
        for robot in self.robots:
            robot.RobotAnimator(screen)

    def all_robots_placed(self):
        return len(self.robots) == self.num_robots

    def increase_score(self, points):
        self.score += points
