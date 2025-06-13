from .player import Player
from .player_action import PlayerAction
from .item_effects import ITEM_EFFECTS
from .move import apply_damage
import random

class BattleManager:
    def __init__(self, player: Player, opponent: Player):
        self.player = player
        self.opponent = opponent
        self.battle_log = []
        self.battle_over = False

    def log(self, message: str):
        self.battle_log.append(message)
        print(message)

        with open("battle_log.txt", "w") as f:
            for line in self.battle_log:
                f.write(line + "\n")

    def take_turn(self, player_action: PlayerAction, opponent_action: PlayerAction):
        # Determine turn order
        first, second = self.determine_turn_order()

        # execute moves and handle faints if necessary
        self.execute_move(first, second, player_action if first == self.player else opponent_action)
        if (second.active_pokemon().is_fainted()):
            self.handle_faint(second)

        self.execute_move(second, first, opponent_action if first == self.opponent else player_action)
        if (first.active_pokemon().is_fainted()):
            self.handle_faint(first)

        # check if battle is over
        self.check_battle_end()

    def determine_turn_order(self):
        player_speed = self.player.active_pokemon().battle_stats.get_effective_stat("speed")
        opponent_speed = self.opponent.active_pokemon().battle_stats.get_effective_stat("speed")

        return (self.player, self.opponent) if player_speed >= opponent_speed else (self.opponent, self.player)

    def resolve_action(self, actor, opponent, action: PlayerAction):
        if action.type == "move":
            self.execute_move(actor, opponent, action.move)
        if action.type == "switch":
            actor.switch_to(action.switch_to)
        if action.type == "item":
            self.use_item(actor, action.item)

    def use_item(self, player, item_name):
        item_fn = ITEM_EFFECTS.get(item_name)
        if item_fn:
            item_fn(player, player.active_pokemon())
            self.log(f"{player.name} used {item_name}!")
        else:
            self.log(f"Item {item_name} does nothing")

    def apply_end_of_turn_status_effects(self, pokemon_list):
        if not pokemon_list:
            return
        pokemon = pokemon_list[0]
        status = pokemon.battle_stats.status
        if status == "poison":
            if pokemon.battle_stats.badly_poisoned:
                pokemon.battle_stats.toxic_turns += 1
                turns = pokemon.battle_stats.toxic_turns
                damage = max(1, (pokemon.battle_stats.max_hp * turns) // 16)
                self.log(f"{pokemon.name} is badly poisoned!")
            else:
                damage = max(1, pokemon.battle_stats.max_hp // 8)
                pokemon.take_damage(damage)
            self.log(f"{pokemon.name} was hurt by poison!")
        elif status == "burn":
            damage = max(1, pokemon.battle_stats.max_hp // 16)
            pokemon.take_damage(damage)
            self.log(f"{pokemon.name} was hurt by burn!")

        self.apply_end_of_turn_status_effects(pokemon_list[1:])       

    def execute_move(self, attacker, defender, move):
        if not attacker.active_pokemon().battle_stats.has_pp(move.name):
            self.log("f{attacker.active_pokemon().name} has no PP left for {move.name}")
            return

        if move.accuracy is not None:
            attacker_accuracy_stage = attacker.active_pokemon().battle_stats.stat_modifiers.get("accuracy", 0)
            defender_evasion_stage = defender.active_pokemon().battle_stats.stat_modifiers.get("evasion", 0)

            acc_mod = attacker.active_pokemon().battle_stats.get_acc_eva_multiplier(attacker_accuracy_stage)
            eva_mod = defender.active_pokemon().battle_stats.get_acc_eva_multiplier(defender_evasion_stage)

            final_accuracy = move.accuracy * acc_mod / eva_mod
            if random.random() * 100 > final_accuracy:
                self.log(f"{attacker.active_pokemon().name}'s {move.name} missed!")
        
        # Use PP and apply damage
        attacker.active_pokemon().battle_stats.use_pp(move.name)
        self.apply_damage(attacker, defender, move)

        effects = move.effects_info
        if effects and effects.ailment:     
            if random.randint(1, 100) <= effects.ailment_chance:
                target_stats = defender.active_pokemon().battle_stats
                if effects.is_badly_poisoning:
                    target_stats.status = "poison"
                    target_stats.badly_poisoned = True
                    target_stats.toxic_turns = 0
                else:
                    target_stats.apply_status(effects.ailment)
        if effects and effects.stat_chance:
            if hasattr(move, "stat_changes") and hasattr(move, "stat_chance"):
                if random.randint(1, 100) <= move.effects_info.stat_chance:
                    for stat, change in move.stat_changes.items():
                        defender.active_pokemon().battle_stats.apply_stat_change(stat, change)

    def prompt_action_input(self, prompt_text, valid_options):
        choice = input(prompt_text)
        if choice not in valid_options:
            print("Invalid choice.")
            return self.prompt_action_input(prompt_text, valid_options)

    def apply_damage(self, attacker, defender, move):
        damage = apply_damage(move, attacker.active_pokemon(), defender.active_pokemon())

        ability = defender.active_pokemon().ability
        if hasattr(ability, "modify_damage"):
            damage = ability.modify_damage(attacker.active_pokemon(), defender.active_pokemon(), move, damage)
        if hasattr(ability, "on_damage_taken"):
            ability.on_damage_taken(attacker.active_pokemon(), defender.active_pokemon(), move, damage)

        if (
            move.damage_class == "Physical"
            and attacker.active_pokemon().battle_stats.status == "burn"
            and attacker.active_pokemon().battle_stats.status != "Guts"
        ):
            damage = damage // 2
            self.log(f"{attacker.active_pokemon().name}'s attack was halved due to burn!")

        defender.active_pokemon().take_damage(damage)
        self.log(f"It dealt {damage} damage to {defender.active_pokemon().name}.")

    def handle_faint(self, player):
        if player.active_pokemon().is_fainted():
            self.log(f"{player.active_pokemon} has fainted!")

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
                                    self.log("Invalid choice. Try again.")

    def check_battle_end(self):
        if not self.player.has_available_pokemon() or not self.opponent.has_available_pokemon():
            self.battle_over = True
