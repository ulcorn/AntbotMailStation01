import sys
import pygame
import logging
import time
import re

from pygame import Surface

from game.Board import Board
from game.Player import Player
from game.config import GameConfig
from game.PlayerSimulator import PlayerSimulator
from game.consts import DEFAULT_IMAGE_SIZE
from game.AutoPlay import AutoPlay

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(asctime)s - %(message)s')

file_handler = logging.FileHandler('game.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(asctime)s - %(message)s'))

logging.getLogger().addHandler(file_handler)

pygame.init()


class GameManager:
    def __init__(self):
        self.config: GameConfig = GameConfig("game.config")
        self.screen: Surface = pygame.display.set_mode(
            (
                DEFAULT_IMAGE_SIZE[0] * 15,
                DEFAULT_IMAGE_SIZE[1] * 11
            )
        )
        pygame.display.set_caption('Robotics Board Game')
        self.board: Board = None
        self.players: list[Player] = None
        self.simulator: PlayerSimulator = None
        self.auto_play: list[AutoPlay] = None
        self.running: bool = False
        self.placing_phase: bool = None
        self.current_player: int = 0
        self.game_reset: bool = False
        self.played_games: int = 0
        self.init_game()

    def init_game(self):
        self.board = Board("csv_files/map.csv", "csv_files/targets.csv")
        self.players = [
            Player(color=color, num_robots=self.config.robots_per_player, idx=idx,
                   move_limit_per_turn=self.config.move_limit_per_turn, game_manager=self)
            for color, idx in [('blue', 0), ('red', 1), ('green', 2), ('orange', 3)][:self.config.get_num_players()]
        ]
        self.simulator = PlayerSimulator(self.players, self.board, self)
        self.auto_play = [AutoPlay(player, self.board) for player_type, player in
                          zip(self.config.players_info[1:], self.players) if player_type == 1]
        self.running = False
        self.placing_phase = self.simulator.placing_phase
        self.current_player = 0
        self.game_reset = False

    def reset_game(self):
        """Сброс: Перезапуск игры"""
        logging.info("Resetting the game.")
        self.played_games += 1
        if self.played_games >= self.config.run_count:
            logging.info("Game limit reached. Exiting.")
            sys.exit()
        self.init_game()
        time.sleep(5)
        logging.info("reset is done.")
        self.run()

    def handle_events(self):
        """Обработка ввода игрока"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                logging.info("Game terminated by user.")
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and self.placing_phase:
                cell_x = (event.pos[0] // DEFAULT_IMAGE_SIZE[0]) - 1
                cell_y = (event.pos[1] // DEFAULT_IMAGE_SIZE[1]) - 1
                success = self.simulator.place_robot_at_position(cell_x, cell_y)
                if success:
                    self.placing_phase = not success
                    self.simulator.update_package_visibility(self.placing_phase)
            elif event.type == pygame.KEYDOWN and not self.placing_phase:
                current_player = self.players[self.current_player]
                if current_player not in [auto_play.player for auto_play in self.auto_play]:
                    self.simulator.pressed_key(event)

    def run_game_mode_1(self):
        """Режим игры 1: Запуск первого режима игры, тут могут быть роботы-автоботы"""
        self.running = True
        self.placing_phase = True
        logging.info("run_game_mode_1 started")
        self.simulator.update_package_visibility(self.placing_phase)

        while self.running:
            if self.game_reset:
                break

            while self.placing_phase and self.running:
                if self.game_reset:
                    break

                self.screen.fill((255, 255, 255))
                current_player = self.players[self.current_player]

                if current_player in [auto_play.player for auto_play in self.auto_play]:
                    autoplay = next(auto_play for auto_play in self.auto_play if auto_play.player == current_player)
                    random_pos = autoplay.get_random_white_cell_position()
                    if random_pos:
                        time.sleep(0.08)
                        success = self.simulator.place_robot_at_position(random_pos[0], random_pos[1])
                        if success:
                            pass
                    else:
                        logging.error("No white cells available to place robot.")
                else:
                    self.handle_events()
                self.simulator.screen_animator()
                pygame.display.flip()

            # Основной игровой цикл
            while not self.placing_phase and self.running:
                if self.game_reset:
                    break

                current_player_idx = self.current_player
                current_player = self.players[current_player_idx]

                if current_player in [auto_play.player for auto_play in self.auto_play]:
                    autoplay = next(auto_play for auto_play in self.auto_play if auto_play.player == current_player)
                    autoplay.play()
                    self.simulator.switch_to_next_player()
                else:
                    self.handle_events()
                    self.simulator.screen_animator()
                    pygame.display.flip()
                    pygame.time.wait(100)

        pygame.quit()

    def run_game_mode_2(self):
        """Режим игры 2: ввод из commands txt, примеры комманд там же, здесь только ручной ввод"""

        def is_valid_command(command):
            gamer_command = r"^GAMER \d+$"
            put_bot_command = r"^PUT BOT [a-g][1-8]$"
            move_command = r"^MOVE ([a-g][1-8]-)+[a-g][1-8]$"
            end_command = r"^END$"

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
            if self.game_reset:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    logging.info("Game terminated by user.")
                    break

            with open("commands.txt", "r") as file:
                commands = file.readlines()

                for command in commands[cnt:]:
                    command = command.strip()
                    if is_valid_command(command):
                        self.execute_command(command)
                        cnt += 1
                    else:
                        if command != '':
                            logging.warning(f"Invalid command: {command}")

            time.sleep(1)

        pygame.quit()

    @staticmethod
    def load_commands(filepath):
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
            self.simulator.game_manager.current_player = int(parts[1]) - 1
            logging.info(f"Switched to Player {self.current_player + 1}.")
        elif parts[0] == "PUT" and parts[1] == "BOT":
            self.simulator.execute_put_bot(self.simulator.game_manager.current_player, parts[2])
        elif parts[0] == "MOVE":
            self.simulator.start_turn(self.simulator.game_manager.current_player, parts[1])
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