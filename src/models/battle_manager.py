from .player import Player
from .move import apply_damage
import random

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
        if not attacker.active_pokemon().battle_stats.has_pp(move.name):
            print("f{attacker.active_pokemon().name} has no PP left for {move.name}")
            return

        if move.accuracy is not None:
            attacker_accuracy_stage = attacker.active_pokemon().battle_stats.stat_modifiers.get("accuracy", 0)
            defender_evasion_stage = defender.active_pokemon().battle_stats.stat_modifiers.get("evasion", 0)

            acc_mod = attacker.active_pokemon().battle_stats.get_acc_eva_multiplier(attacker_accuracy_stage)
            eva_mod = defender.active_pokemon().battle_stats.get_acc_eva_multiplier(defender_evasion_stage)

            final_accuracy = move.accuracy * acc_mod / eva_mod
            if random.random() * 100 > final_accuracy:
                print(f"{attacker.active_pokemon().name}'s {move.name} missed!")
        
        # Use PP and apply damage
        attacker.active_pokemon().battle_stats.use_pp(move.name)
        self.apply_damage(attacker, defender, move)

        if hasattr(move, "ailment") and hasattr(move, "ailment_chance"):
            if random.randint(1, 100) <= move.status_chance:
                defender.active_pokemon().battle_stats.apply_status(move.status_effect)

        if hasattr(move, "stat_changes") and hasattr(move, "stat_chance"):
            if random.randint(1, 100) <= move.stat_chance:
                for stat, change in move.stat_changes.items():
                    defender.active_pokemon().battle_stats.apply_stat_change(stat, change);

    def apply_damage(self, attacker, defender, move):
        damage = apply_damage(move, attacker.active_pokemon(), defender.active_pokemon())
        defender.active_pokemon().take_damage()
        print(f"{attacker.active_pokemon().name} used {move.name}!")
        print(f"It dealt {damage} damage to {defender.active_pokemon().name}.")

    def handle_faint(self, player):
        if player.active_pokemon().is_fainted():
            if player.has_available_pokemon():
                if player.is_ai:
                    for i, p in enumerate(player.team):
                        if not p.is_fainted():
                            player.switch_to(i)
                            break
                        else:
                            valid_choices = [
                                (i,p) for i, p in enumerate(player.team)
                                if not p.is_fainted()
                            ]

                            while True:
                                choice = int(input("Switch to: ")) - 1
                                if any(i == choice for i,_ in valid_choices):
                                    player.switch_to(choice)
                                    break
                                else:
                                    print("Invalid choice. Try again.")

    def check_battle_end(self):
        if not self.player.has_available_pokemon() or not self.opponent.has_available_pokemon():
            self.battle_over = True
