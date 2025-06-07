from .player import Player

class BattleManager:
    def __init__(self, player: Player, opponent: Player):
        self.player = player
        self.opponent = opponent
        self.battle_over = False

    def take_turn(self, player_move, opponent_move):
        # Determine turn order
        first, second = self.determine_turn_order()

        # execute moves and handle faints if necessary
        self.execute_move(first, second, player_move if first == self.player else opponent_move)
        if (second.active_pokemon().is_fainted()):
            self.handle_faint(second)

        self.execute_move(second, first, opponent_move if first == self.opponent else player_move)
        if (first.active_pokemon().is_fainted()):
            self.handle_faint(first)

        # check if battle is over
        self.check_battle_end()

    def determine_turn_order(self):
        player_speed = self.player.active_pokemon().battle_stats.get_effective_stat("speed")
        opponent_speed = self.opponent.active_pokemon().battle_stats.get_effective_stat("speed")

        return (self.player, self.opponent) if player_speed >= opponent_speed else (self.opponent, self.player)

    def execute_move(self, attacker, defender, move):
        pass

    def apply_damage(self, attacker, defender, move):
        pass

    def handle_faint(self, player):
        pass

    def check_battle_end(self):
        if not self.player.has_available_pokemon() or not self.opponent.has_available_pokemon():
            self.battle_over = True
