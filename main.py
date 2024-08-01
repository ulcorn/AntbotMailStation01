import pygame
from game.Board import Board
from game.consts import DEFAULT_IMAGE_SIZE
from game.Player import Player

pygame.init()

def display_board(board, screen):
    for i in range(board.size):
        for j in range(board.size):
            board[i][j].display_cell(screen)

def main():
    screen = pygame.display.set_mode((DEFAULT_IMAGE_SIZE[0] * 11, DEFAULT_IMAGE_SIZE[1] * 11))
    pygame.display.set_caption('Robotics Board Game')

    board = Board("csv_files/colors.csv", "csv_files/numbers.csv")

    white_cells = [(i, j) for i in range(board.size) for j in range(board.size) if board[i][j].color == 'w']
    num_players = 2
    num_robots_per_player = 3

    players = [
        Player(color='blue', num_robots=num_robots_per_player, white_cells=white_cells),
        Player(color='red', num_robots=num_robots_per_player, white_cells=white_cells),
    ]

    current_player_index = 0
    current_robot_index = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_TAB:
                    current_player_index = (current_player_index + 1) % num_players
                    current_robot_index = 0

                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]:
                    current_robot_index = event.key - pygame.K_1

                elif event.key == pygame.K_UP:
                    players[current_player_index].move_robot(current_robot_index, 'up', board)
                elif event.key == pygame.K_DOWN:
                    players[current_player_index].move_robot(current_robot_index, 'down', board)
                elif event.key == pygame.K_LEFT:
                    players[current_player_index].move_robot(current_robot_index, 'left', board)
                elif event.key == pygame.K_RIGHT:
                    players[current_player_index].move_robot(current_robot_index, 'right', board)

        screen.fill((255, 255, 255))
        display_board(board, screen)
        for player in players:
            player.draw_robots(screen)

        pygame.display.update()

if __name__ == "__main__":
    main()