import csv
from game.Cell import Cell
from game.Package import Package
from game.consts import DEFAULT_IMAGE_SIZE


class Board:
    def __init__(self, colors, targets) -> None:
        self.cells: list[list[Cell]] = None
        self.load_from_file(colors, targets)
        self.size = len(self.cells[0])
        self.current_player_index = 0

        self.yellow_cells = self.get_cells_by_color('y')
        self.red_cells = self.get_cells_by_color('r')
        self.green_cells = self.get_cells_by_color('a')
        self.blue_cells = self.get_cells_by_color('b')
        self.white_cells = self.get_cells_by_color('w')
        self.occupied_cells = {}

    def get_cells_by_color(self, color):
        return [cell for row_cell in self.cells for cell in row_cell if cell.color == color]

    def load_from_file(self, colors_map, targets_map):
        self.cells: list[list[Cell]] = []

        with (open(colors_map, mode='r') as colors_map_file,
              open(targets_map, mode='r') as targets_map_file):
            color_matrix = csv.reader(colors_map_file)
            target_matrix = csv.reader(targets_map_file)

            for i, (color_row, target_row) in enumerate(zip(color_matrix, target_matrix)):
                row = list()
                for j, (color, target) in enumerate(zip(color_row, target_row)):
                    row.append(Cell(i, j, color=color, target=int(target)))
                self.cells.append(row)

    def __getitem__(self, index):
        return self.cells[index]

    def is_occupied(self, x, y):
        return (x, y) in self.occupied_cells

    def update_position(self, old_pos, new_pos):
        if old_pos in self.occupied_cells:
            del self.occupied_cells[old_pos]
        self.occupied_cells[new_pos] = True

    def place_package(self, pos):
        package = Package(pos)
        self.cells[pos[1]][pos[0]].package = package
        return package

    def display_cells(self, screen):
        for i in range(self.size):
            for j in range(self.size):
                self.cells[i][j].draw(screen)
