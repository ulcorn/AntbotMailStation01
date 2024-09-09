import pygame
import logging
import time
import re  # Модуль для регулярных выражений

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

        self.board = Board("csv_files/colors.csv", "csv_files/targets.csv")
        self.players = [
            Player(color=color, num_robots=self.config.robots_per_player, idx=idx)
            for color, idx in [('blue', 1), ('red', 2), ('green', 3), ('orange', 4)][:self.config.get_num_players()]
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
        def is_valid_command(command):
            gamer_command = r"^GAMER \d+$"  # Команда GAMER X
            put_bot_command = r"^PUT BOT [a-g][1-8]$"  # Команда PUT BOT c3 (буквы от a до g и цифры от 1 до 8)
            move_command = r"^MOVE ([a-g][1-8]-)+[a-g][1-8]$"  # Команда MOVE c3-c2 или MOVE e4-f4-f3-f2
            end_command = r"^END$"  # Команда END

            if re.match(gamer_command, command):
                return True
            elif re.match(put_bot_command, command):
                return True
            elif re.match(move_command, command):
                return True
            elif re.match(end_command, command):
                return True
            else:
                return False

        cnt = 0

        self.running = True

        logging.info("run_game_mode_2 started")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    logging.info("Game terminated by user.")
                    break

            # Открываем файл и считываем все строки
            with open("commands.txt", "r") as file:
                commands = file.readlines()

                for command in commands[cnt:]:
                    command = command.strip()
                    if is_valid_command(command):
                        self.execute_command(command)
                        cnt += 1
                    else:
                        if command != '':
                            logging.warning(f"Invalid command: {command}")  # Логируем невалидные команды

            time.sleep(1)

        pygame.quit()

    def load_commands(self, filepath):
        with open(filepath, 'r') as file:
            commands = file.readlines()
        return commands

    def execute_command(self, command):
        parts = command.strip().split()
        if not parts:
            return

        if self.placing_phase and not (parts[0] == "PUT" and parts[1] == "BOT") and parts[0] != "GAMER":
            self.placing_phase = False
            logging.info(f"Placing phase ended.")
            self.simulator.update_package_visibility(self.placing_phase)

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
