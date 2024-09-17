import logging
import random
import time  # импортируем модуль time для добавления задержки
from collections import deque


def allocate_packages(robots, packages):
    """Распознание посылок"""
    assignments = {}
    remaining_packages = packages[:]

    for robot in robots:
        closest_package = None
        closest_distance = float('inf')

        for package in remaining_packages:
            distance = abs(robot.pos[0] - package.pos[0]) + abs(robot.pos[1] - package.pos[1])
            if distance < closest_distance:
                closest_distance = distance
                closest_package = package

        if closest_package:
            assignments[robot] = closest_package
            remaining_packages.remove(closest_package)

    return assignments


class AutoPlay:
    def __init__(self, player, board):
        self.player = player
        self.board = board
        self.active = True

    def find_white_cells(self):
        return self.board.get_cells_by_color('w')

    def get_random_white_cell_position(self):
        white_cells = self.find_white_cells()
        if white_cells:
            cell = random.choice(white_cells)
            return cell.x, cell.y
        return None

    # def find_most_expensive_package(self):
    #     max_value = 0
    #     target_package = None
    #     target_pos = None
    #     for row in self.board.cells:
    #         for cell in row:
    #             if cell.package and not cell.package.picked_up:
    #                 if cell.package.number > max_value:
    #                     max_value = cell.package.number
    #                     target_package = cell.package
    #                     x, y = cell.package.pos
    #                     target_pos = (x, y + 1)  # Позиция зелёной клетки над посылкой
    #
    #     return target_package, target_pos

    def find_target_cell(self, package):
        for row in self.board.cells:
            for cell in row:
                if cell.target == package.number:
                    return cell

    def is_valid_move(self, robot, new_pos):
        x, y = new_pos
        if 0 <= x < self.board.size and 0 <= y < self.board.size:
            target_cell = self.board.cells[y][x]
            if self.board.is_occupied(x, y):
                logging.debug(f"Cell at {new_pos} is occupied by another robot.")
                return False
            if target_cell.target:
                if robot.package and target_cell.target == robot.package.number:
                    logging.debug(f"Cell at {new_pos} is robot's own target cell.")
                    pass
                else:
                    logging.debug(f"Cell at {new_pos} is a target cell for another package. Move not allowed.")
                    return False
            if target_cell.color in ('w', 'a', 'g', 'y'):
                logging.debug(f"Cell at {new_pos} is valid for movement.")
                return True
            else:
                logging.debug(f"Cell at {new_pos} has invalid color '{target_cell.color}'.")
                return False
        logging.debug(f"Cell at {new_pos} is out of bounds.")
        return False

    def move_robot_towards(self, robot, target_pos):
        path = self.find_path(robot, target_pos)
        if path:
            direction, new_pos = path[0]
            if robot.move(direction, self.board):
                target_cell = self.board.cells[new_pos[1]][new_pos[0]]
                if target_cell.target and robot.package and target_cell.target == robot.package.number:
                    robot.drop_package(target_cell)
                    logging.info(f"Robot {robot.index} delivered package at {new_pos}. Movement ends.")
                    return None

                if not robot.has_package:
                    if target_cell.color == 'a':
                        below_cell = self.board[new_pos[1] + 1][new_pos[0]]
                        if below_cell.color == 'r' and below_cell.package and not below_cell.package.picked_up:
                            robot.pick_package(below_cell.package, self.board)
                            logging.info(f"Robot {robot.index} picked up package from {below_cell.pos}")

                return new_pos

        logging.warning(f"No path found for robot at {robot.pos} to target {target_pos}")
        return None

    def play(self):
        move_limit = self.player.move_limit_per_turn
        num_robots = len(self.player.robots)
        base_moves_per_robot = move_limit // num_robots
        extra_moves = move_limit % num_robots

        available_moves = False

        robots = self.player.robots
        for i, robot in enumerate(robots):
            robot_move_limit = base_moves_per_robot + (extra_moves if i == 0 else 0)
            remaining_moves = robot_move_limit

            while remaining_moves > 0:
                if robot.has_package:
                    target_cell = self.find_target_cell(robot.package)
                    if target_cell:
                        new_pos = self.move_robot_towards(robot, (target_cell.x, target_cell.y))
                        if new_pos is None:
                            logging.info(f"Robot {robot.index} delivered the package and is removed from the turn.")
                            robot.has_package = False
                            break
                        remaining_moves -= 1
                        available_moves = True
                    else:
                        logging.error(f"No target cell found for package {robot.package.number}")
                        break
                else:
                    packages = [cell.package for row in self.board.cells for cell in row if
                                cell.package and not cell.package.picked_up]
                    if not packages:
                        logging.info(f"No packages available for robot {robot.index}.")
                        break

                    closest_package = min(packages, key=lambda pkg: abs(robot.pos[0] - pkg.pos[0]) + abs(
                        robot.pos[1] - pkg.pos[1]))
                    target_pos = (closest_package.pos[0], closest_package.pos[1] - 1)
                    new_pos = self.move_robot_towards(robot, target_pos)

                    if new_pos:
                        remaining_moves -= 1
                        available_moves = True
                    else:
                        logging.warning(f"Robot {robot.index} could not move towards package at {target_pos}")
                        break

            if remaining_moves == 0:
                logging.info(f"Robot {robot.index} used all its moves for this turn.")

        if not available_moves:
            logging.info("No available moves, skipping turn.")

        return available_moves

    def find_path(self, robot, target_pos):
        queue = deque()
        visited = set()
        parent = {}

        start_pos = robot.pos
        queue.append(start_pos)
        visited.add(start_pos)
        logging.debug(f"Starting BFS from {start_pos} to {target_pos}")

        while queue:
            current_pos = queue.popleft()
            logging.debug(f"Visiting {current_pos}")

            if current_pos == target_pos:
                path = []
                while current_pos != start_pos:
                    prev_pos, direction = parent[current_pos]
                    path.append((direction, current_pos))
                    current_pos = prev_pos
                path.reverse()
                logging.debug(f"Path found: {path}")
                return path
            else:
                directions = [
                    ("up", (current_pos[0], current_pos[1] - 1)),
                    ("down", (current_pos[0], current_pos[1] + 1)),
                    ("left", (current_pos[0] - 1, current_pos[1])),
                    ("right", (current_pos[0] + 1, current_pos[1]))
                ]
                for direction, new_pos in directions:
                    if (0 <= new_pos[0] < self.board.size and
                            0 <= new_pos[1] < self.board.size and
                            new_pos not in visited):
                        if self.is_valid_move(robot, new_pos):
                            visited.add(new_pos)
                            parent[new_pos] = (current_pos, direction)
                            queue.append(new_pos)
                        else:
                            logging.debug(f"Move to {new_pos} is invalid.")
                    else:
                        logging.debug(f"Position {new_pos} is out of bounds or already visited.")
        logging.warning(f"No path found from {start_pos} to {target_pos}")
        return None
