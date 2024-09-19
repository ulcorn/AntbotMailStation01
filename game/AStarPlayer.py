import logging
import random
import time
import queue
from collections import deque
from game.AutoPlay import AutoPlay
from game.Robot import Robot

class AStarPlayer(AutoPlay):
    def __init__(self, player, board):
        super().__init__(player, board)
        
    @staticmethod
    def heuristic(a: tuple[int, int],
                  b: tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, robot: Robot, target_pos: tuple[int, int]):

        start = robot.pos
        open_set: queue.PriorityQueue = queue.PriorityQueue()
        open_set.put((0, start))

        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        i = 0
        while not open_set.empty():
            current = open_set.get()[1]

            if current == target_pos:
                path = []
                while current != start:
                    direction, previous = came_from[current]
                    path.append((direction, current))
                    current = previous
                path.reverse()
                return path

            directions = [
                    ("up", (current[0], current[1] - 1)),
                    ("down", (current[0], current[1] + 1)),
                    ("left", (current[0] - 1, current[1])),
                    ("right", (current[0] + 1, current[1]))
                ]
            #Reverse neighbors list if i is odd,
            #change order putting cell to queue
            #According to that, we don't get cell from queue over
            #one row or column and search over diagonal
            if i % 2 == 1:
                directions.reverse()
            for direction, new_pos in directions:
                new_cost = cost_so_far[current] + 1
                if (new_pos not in cost_so_far or new_cost < cost_so_far[new_pos]) and (
                    0 <= new_pos[0] < self.board.size) and (
                        0 <= new_pos[1] < self.board.size) and (self.is_valid_move(robot, new_pos) or new_pos == start or new_pos == target_pos):
                    cost_so_far[new_pos] = new_cost
                    priority = new_cost + self.heuristic(new_pos, target_pos)
                    open_set.put((priority, new_pos))
                    came_from[new_pos] = (direction, current)
            i += 1
        return None