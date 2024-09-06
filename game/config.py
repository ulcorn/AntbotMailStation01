class GameConfig:
    def __init__(self, config_path):
        self.config_path = config_path
        self.game_mode = None
        self.version = None
        self.run_count = None
        self.players_info = []
        self.win_packages_count = None
        self.robots_per_player = None
        self.charging_accounting = None
        self._parse_config()

    def _parse_config(self):
        with open(self.config_path, 'r') as file:
            lines = file.readlines()
            self.game_mode = int(lines[0].strip())
            self.version = float(lines[1].strip())
            self.run_count = int(lines[2].strip())
            self.players_info = list(map(int, lines[3].strip().split()))
            self.win_packages_count = int(lines[4].strip())
            self.robots_per_player = int(lines[5].strip())
            self.charging_accounting = int(lines[6].strip())

    def get_num_players(self):
        return self.players_info[0]

    def get_player_types(self):
        return self.players_info[1:]