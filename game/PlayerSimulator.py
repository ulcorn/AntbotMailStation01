import pygame
import logging
from game.Board import Board
from game.consts import DEFAULT_IMAGE_SIZE


class PlayerSimulator:
    def __init__(self, players, board, screen):
        self.players = players
        self.board = board
        self.screen = screen
        self.current_player_index = 0
        self.current_robot_index = 0
        self.current_robot_counts = [0] * len(players)
        self.total_robots_to_place = len(players) * players[0].num_robots
        self.robots_placed = 0
        self.placing_phase = True
        self.place_initial_packages()

    def place_initial_packages(self):
        red_cells = self.board.get_cells_by_color('r')
        for i, cell in enumerate(red_cells):
            package = self.board.place_package((cell.x, cell.y))
            package.visible = False  # Initially hide the packages

    def update_package_visibility(self, placing_phase):
        self.placing_phase = placing_phase
        for row in self.board.cells:
            for cell in row:
                if cell.package:
                    cell.package.visible = not placing_phase

    def PlaceRobotSuccess(self, mouse_x, mouse_y):
        cell_x = (mouse_x // DEFAULT_IMAGE_SIZE[0]) - 1
        cell_y = (mouse_y // DEFAULT_IMAGE_SIZE[1]) - 1
        if 0 <= cell_x < self.board.size and 0 <= cell_y < self.board.size:
            if self.players[self.current_player_index].place_robot((cell_x, cell_y), self.board,
                                                                   self.current_robot_counts[
                                                                       self.current_player_index]):
                logging.info(
                    f"Player {self.current_player_index + 1} placed robot at ({self.index_to_letter(cell_x)}, {cell_y + 1}).")
                self.current_robot_counts[self.current_player_index] += 1
                self.robots_placed += 1
                if self.robots_placed >= self.total_robots_to_place:
                    logging.info("Placing phase ended. All players have placed their robots.")
                    self.current_player_index = 0
                    self.current_robot_index = 0
                    self.update_package_visibility(False)
                    return True
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                self.current_robot_index = 0
        return False

    def execute_put_bot(self, player_index, pos):
        row = int(pos[1]) - 1
        col = ord(pos[0].lower()) - ord('a')
        if self.players[player_index].place_robot((col, row), self.board, len(self.players[player_index].robots)):
            logging.info(f"Player {player_index + 1} placed robot at ({pos}).")
            self.ScreenAnimator()
            pygame.time.delay(50)

    def StartTurn(self, player_index, move_steps):
        move_steps = move_steps.split('-')
        start_pos = self.parse_position(move_steps[0])
        end_pos = self.parse_position(move_steps[-1])

        robot = None
        for r in self.players[player_index].robots:
            if r.pos == start_pos:
                robot = r
                break

        if not robot:
            logging.warning(f"No robot found at start position: {start_pos}")
            return

        for step in range(1, len(move_steps)):
            step_pos = self.parse_position(move_steps[step])
            direction = None
            if robot.pos[0] < step_pos[0]:
                direction = "right"
            elif robot.pos[0] > step_pos[0]:
                direction = "left"
            elif robot.pos[1] < step_pos[1]:
                direction = "down"
            elif robot.pos[1] > step_pos[1]:
                direction = "up"

            if direction and robot.move(direction, self.board):
                pos = robot.pos
                logging.info(
                    f"Player {player_index + 1} moved robot {robot.index} {direction} to ({self.index_to_letter(pos[0])}, {pos[1] + 1}).")
                self.ScreenAnimator()
                pygame.time.delay(50)

    def PressedKey(self, event):
        if event.key == pygame.K_TAB:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.current_robot_index = 0
            logging.info(f"Switched to player {self.current_player_index + 1}.")
        elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
            robot_num = event.key - pygame.K_1
            if robot_num < len(self.players[self.current_player_index].robots):
                self.current_robot_index = robot_num
                logging.info(f"Player {self.current_player_index + 1} switched to robot {robot_num + 1}.")
        elif event.key == pygame.K_UP:
            if self.players[self.current_player_index].move_robot(self.current_robot_index, 'up', self.board):
                pos = self.players[self.current_player_index].robots[self.current_robot_index].pos
                logging.info(
                    f"Player {self.current_player_index + 1} moved robot {self.current_robot_index + 1} up to ({self.index_to_letter(pos[0])}, {pos[1] + 1}).")
        elif event.key == pygame.K_DOWN:
            if self.players[self.current_player_index].move_robot(self.current_robot_index, 'down', self.board):
                pos = self.players[self.current_player_index].robots[self.current_robot_index].pos
                logging.info(
                    f"Player {self.current_player_index + 1} moved robot {self.current_robot_index + 1} down to ({self.index_to_letter(pos[0])}, {pos[1] + 1}).")
        elif event.key == pygame.K_LEFT:
            if self.players[self.current_player_index].move_robot(self.current_robot_index, 'left', self.board):
                pos = self.players[self.current_player_index].robots[self.current_robot_index].pos
                logging.info(
                    f"Player {self.current_player_index + 1} moved robot {self.current_robot_index + 1} left to ({self.index_to_letter(pos[0])}, {pos[1] + 1}).")
        elif event.key == pygame.K_RIGHT:
            if self.players[self.current_player_index].move_robot(self.current_robot_index, 'right', self.board):
                pos = self.players[self.current_player_index].robots[self.current_robot_index].pos
                logging.info(
                    f"Player {self.current_player_index + 1} moved robot {self.current_robot_index + 1} right to ({self.index_to_letter(pos[0])}, {pos[1] + 1}).")

    def ScreenAnimator(self):
        self.screen.fill((255, 255, 255))
        for i in range(self.board.size):
            for j in range(self.board.size):
                self.board[i][j].display_cell(self.screen)
        for player in self.players:
            player.draw_robots(self.screen)
        pygame.display.update()

    def parse_position(self, pos_str):
        column = ord(pos_str[0].lower()) - ord('a')
        row = int(pos_str[1]) - 1
        return column, row

    def index_to_letter(self, index):
        return chr(ord('A') + index)

    def ENDGAME(self):
        logging.info("Player has ended the game")
