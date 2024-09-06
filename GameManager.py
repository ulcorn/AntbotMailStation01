import pygame
import logging
from game.Board import Board
from game.Player import Player
from game.config import GameConfig
from game.PlayerSimulator import PlayerSimulator
from game.consts import DEFAULT_IMAGE_SIZE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('game.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(asctime)s - %(message)s'))

logging.getLogger().addHandler(file_handler)

pygame.init()

class GameManager:
    def __init__(self):
        self.config = GameConfig("game.config")
        self.screen = pygame.display.set_mode((DEFAULT_IMAGE_SIZE[0] * 11, DEFAULT_IMAGE_SIZE[1] * 11))
        pygame.display.set_caption('Robotics Board Game')

        self.board = Board("csv_files/colors.csv", "csv_files/numbers.csv")
        self.players = [
            Player(color=color, num_robots=self.config.robots_per_player)
            for color in ['blue', 'red', 'green', 'orange'][:self.config.get_num_players()]
        ]

        self.simulator = PlayerSimulator(self.players, self.board, self.screen)
        self.running = False
        self.placing_phase = True

    def run_game_mode_1(self):
        self.running = True
        self.placing_phase = True
        logging.info("run_game_mode_1 started")
        self.simulator.update_package_visibility(self.placing_phase)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    logging.info("Game terminated by user.")
                elif event.type == pygame.MOUSEBUTTONDOWN and self.placing_phase:
                    self.placing_phase = not self.simulator.PlaceRobotSuccess(event.pos[0], event.pos[1])
                    self.simulator.update_package_visibility(self.placing_phase)
                elif event.type == pygame.KEYDOWN and not self.placing_phase:
                    self.simulator.PressedKey(event)
            self.simulator.ScreenAnimator()
        pygame.quit()

    def run_game_mode_2(self):
        executed_commands = set()  # To keep track of executed commands

        self.running = True
        logging.info("run_game_mode_2 started")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    logging.info("Game terminated by user.")

            # Reload commands on each iteration
            commands = self.load_commands("commands.txt")
            new_commands = [cmd for cmd in commands if cmd not in executed_commands]

            for command in new_commands:
                self.execute_command(command)
                executed_commands.add(command)

            pygame.time.delay(500)

        pygame.quit()

    def load_commands(self, filepath):
        with open(filepath, 'r') as file:
            commands = file.readlines()
        return commands

    def execute_command(self, command):
        parts = command.strip().split()
        if not parts:
            return

        if parts[0] == "GAMER":
            self.simulator.current_player_index = int(parts[1]) - 1
            logging.info(f"Switched to Player {self.simulator.current_player_index + 1}.")
        elif parts[0] == "PUT" and parts[1] == "BOT":
            self.simulator.execute_put_bot(self.simulator.current_player_index, parts[2])
        elif parts[0] == "MOVE":
            self.simulator.StartTurn(self.simulator.current_player_index, parts[1])
        elif parts[0] == "END":
            self.simulator.ENDGAME()
            self.running = False

    def run(self):
        if self.config.game_mode == 1:
            self.run_game_mode_1()
        elif self.config.game_mode == 2:
            self.run_game_mode_2()


if __name__ == "__main__":
    game_manager = GameManager()
    game_manager.run()