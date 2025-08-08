from .player import Player
from .player_action import PlayerAction
from .type_chart import get_type_multiplier
from .item_effects import ITEM_EFFECTS
from .move import Move
import random
import logging

class BattleManager:
    def __init__(self, player: Player, opponent: Player, ui_logger=None):
        self.player = player
        self.opponent = opponent
        self.battle_log = []
        self.battle_over = False
        self.ui_logger = ui_logger

    def log(self, message: str):
        self.battle_log.append(message)
        logging.info(message)
        if hasattr(self, "ui_logger") and self.ui_logger:
            self.ui_logger(message)
    
    def make_ai_action(self, player, opponent):
        best_move = None
        best_score = float('-inf')
        attacker = player.active_pokemon()
        defender = opponent.active_pokemon()

        for move in attacker.moves:
            if not attacker.battle_stats.has_pp(move.name):
                continue

            score = 0
            for defender_type in defender.types:
                multiplier = get_type_multiplier(move.move_type, defender_type)
                score += multiplier

            if move.move_type in attacker.types:
                score *= 1.5

            if hasattr(move, "power") and move.power:
                score *= move.power

            print(f"Evaluating move: {move.name}, score: {score}")

            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None:
            best_move = attacker.moves[0]

        print(f"AI selected move: {best_move.name}")
        return PlayerAction(type="move", move=best_move)

    def take_turn(self, player_action: PlayerAction, opponent_action: PlayerAction):
        if self.battle_over:
            return
        # Determine turn order
        first, second = self.determine_turn_order(player_action, opponent_action)

        first_action = player_action if first == self.player else opponent_action
        second_action = opponent_action if first == self.player else player_action

        move = first.active_pokemon().get_move_by_name(first_action.move_name)
        self.execute_move(first, second, move)

        if self.ui_logger:
            self.ui_logger(f"{first.active_pokemon().name} used {first_action.move_name}")
        
        if second.active_pokemon().is_fainted():
            self.handle_faint(second)
            if self.check_battle_end():
                return
            
        move = second.active_pokemon().get_move_by_name(second_action.move_name)
        self.execute_move(second, first, move)
            
        if self.ui_logger:
            self.ui_logger(f"{second.active_pokemon().name} used {second_action.move_name}")

        if (first.active_pokemon().is_fainted()):
            self.handle_faint(first)

        # check if battle is over
        if self.check_battle_end():
            return
        
        self.apply_end_of_turn_status_effects([
            self.player.active_pokemon(),
            self.opponent.active_pokemon()
        ])

    def choose_best_counter(self, current_opponent_pokemon, player_active_pokemon):
        best_index = None
        best_score = float('-inf')

        for i, poke in enumerate(current_opponent_pokemon.team):
            if poke != current_opponent_pokemon.active_pokemon() and poke.battle_stats.current_hp > 0:
                # Basic Heuristic: count the number of type advantages
                score = 0
                for move in poke.moves:
                    for player_type in player_active_pokemon.types:
                        multiplier = get_type_multiplier(move.move_type, player_type)
                        score += multiplier
                if score > best_score:
                    best_score = score
                    best_index = i
        return best_index
    
    def determine_turn_order(self, player_action=None, opponent_action=None):
        player_priority = 0
        opponent_priority = 0
        
        if player_action and player_action.move and hasattr(player_action.move, 'priority'):
            player_priority = player_action.move.priority or 0
        if opponent_action and opponent_action.move and hasattr(opponent_action.move, 'priority'):
            opponent_priority = opponent_action.move.priority or 0
        
        if player_priority > opponent_priority:
            return (self.player, self.opponent)
        elif opponent_priority > player_priority:
            return (self.opponent, self.player)
        else:
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
            return []
        pokemon = pokemon_list[0]
        status = pokemon.battle_stats.status
        status_effects = []
        
        print(f"Checking end-of-turn effects for {pokemon.name}, status: {status}")
        
        if status == "poison":
            if pokemon.battle_stats.badly_poisoned:
                pokemon.battle_stats.toxic_turns += 1
                turns = pokemon.battle_stats.toxic_turns
                damage = max(1, (pokemon.battle_stats.max_hp * turns) // 16)
                message = f"{pokemon.name} is badly poisoned!"
            else:
                damage = max(1, pokemon.battle_stats.max_hp // 8)
                message = f"{pokemon.name} was hurt by poison!"
            
            new_hp = max(0, pokemon.battle_stats.current_hp - damage)
            status_effects.append((self.get_pokemon_owner(pokemon), new_hp, message))
            status_effects.append((self.get_pokemon_owner(pokemon), new_hp, f"It took {damage} damage."))
            
        elif status == "burn":
            damage = max(1, pokemon.battle_stats.max_hp // 16)
            message = f"{pokemon.name} was hurt by burn!"
            new_hp = max(0, pokemon.battle_stats.current_hp - damage)
            status_effects.append((self.get_pokemon_owner(pokemon), new_hp, message))
            status_effects.append((self.get_pokemon_owner(pokemon), new_hp, f"It took {damage} damage."))

        status_effects.extend(self.apply_end_of_turn_status_effects(pokemon_list[1:]))
        return status_effects
    
    def get_pokemon_owner(self, pokemon):
        """Helper method to find which player owns a pokemon"""
        if self.player.active_pokemon() == pokemon:
            return self.player
        elif self.opponent.active_pokemon() == pokemon:
            return self.opponent
        return None       

    def check_status_prevents_move(self, attacker):
        """Check if status effects prevent the pokemon from using a move, return (can_move, status_message)"""
        attacker_status = attacker.active_pokemon().battle_stats.status
        
        # Sleep check
        if attacker_status == "sleep":
            # Decrement sleep turns
            attacker.active_pokemon().battle_stats.sleep_turns -= 1
            if attacker.active_pokemon().battle_stats.sleep_turns <= 0:
                attacker.active_pokemon().battle_stats.status = None
                attacker.active_pokemon().battle_stats.sleep_turns = 0
                return True, f"{attacker.active_pokemon().name} woke up!"
            else:
                return False, f"{attacker.active_pokemon().name} is fast asleep!"
        
        # Paralysis check (25% chance to be fully paralyzed and unable to move)
        if attacker_status == "paralysis":
            if random.randint(1, 4) == 1:  # 25% chance
                return False, f"{attacker.active_pokemon().name} is paralyzed! It can't move!"
        
        return True, None

    def execute_move_calculate_only(self, attacker, defender, move: Move):
        """Execute move calculations without applying damage immediately"""
        if not attacker.active_pokemon().battle_stats.has_pp(move.name):
            self.log(f"{attacker.active_pokemon().name} has no PP left for {move.name}")
            return None, False, False
        
        print(f"Executing move: {move.name}")

        if move.accuracy is not None:
            attacker_accuracy_stage = attacker.active_pokemon().battle_stats.stat_modifiers.get("accuracy", 0)
            defender_evasion_stage = defender.active_pokemon().battle_stats.stat_modifiers.get("evasion", 0)

            acc_mod = attacker.active_pokemon().battle_stats.get_acc_eva_multiplier(attacker_accuracy_stage)
            eva_mod = defender.active_pokemon().battle_stats.get_acc_eva_multiplier(defender_evasion_stage)

            final_accuracy = move.accuracy * acc_mod / eva_mod
            if random.random() * 100 > final_accuracy:
                self.log(f"{attacker.active_pokemon().name}'s {move.name} missed!")
                return None, False, True
        
        print("PP map before:", attacker.active_pokemon().battle_stats.pp)
        print("Move used:", move.name)
        print("Is move in PP map?", move.name in attacker.active_pokemon().battle_stats.pp)
        # Use PP but don't apply damage yet
        attacker.active_pokemon().battle_stats.use_pp(move.name)
        damage, is_critical = self.calculate_damage(attacker, defender, move)

        return damage, is_critical, False

    def apply_move_effects(self, attacker, defender, move: Move):
        """Apply non-damage effects of a move (status effects, stat changes)"""
        effects = move.effects_info
        print(f"Checking move effects for {move.name}: {effects}")
        if effects:
            # Ailment (e.g., poison, burn)
            if effects.ailment and effects.ailment != "none":
                ailment_chance = effects.ailment_chance or 100
                roll = random.randint(1, 100)
                print(f"Status effect check: {move.name} has {effects.ailment} with {ailment_chance}% chance, rolled {roll}")
                # Temporarily increase chance to 100% for testing
                if roll <= 100:  # Was: ailment_chance
                    target = defender.active_pokemon().battle_stats
                    print(f"Applying status {effects.ailment} to {defender.active_pokemon().name}")
                    if effects.is_badly_poisoning:
                        target.status = "poison"
                        target.badly_poisoned = True
                        target.toxic_turns = 0
                        self.log(f"{defender.active_pokemon().name} was badly poisoned!")
                    else:
                        if target.status is None:
                            target.apply_status(effects.ailment)
                            # Set sleep turns for sleep status
                            if effects.ailment == "sleep":
                                target.sleep_turns = random.randint(1, 3)  # Sleep for 1-3 turns in Gen IV
                            self.log(f"{defender.active_pokemon().name} was {effects.ailment}ed!")
                            print(f"Status applied: {target.status}")
                        else:
                            print(f"Status not applied - {defender.active_pokemon().name} already has status: {target.status}")

            # Stat changes (e.g., Swords Dance)
            if effects.stat_changes:
                target = defender if move.target == "opponent" else attacker
                target_stats = target.active_pokemon().battle_stats

                if effects.stat_chance is None or random.randint(1, 100) <= effects.stat_chance:
                    for stat, change in effects.stat_changes.items():
                        target_stats.apply_stat_change(stat, change)
                        stage = "sharply " if abs(change) == 2 else ""
                        direction = "rose" if change > 0 else "fell"
                        self.log(f"{target.active_pokemon().name}'s {stat.capitalize()} {stage}{direction}!")

    def execute_move(self, attacker, defender, move: Move):
        damage, is_critical, missed = self.execute_move_calculate_only(attacker, defender, move)
        
        if missed or damage is None:
            return
            
        # Apply damage and effects immediately (original behavior)
        ability = defender.active_pokemon().ability
        if hasattr(ability, "on_damage_taken"):
            ability.on_damage_taken(attacker.active_pokemon(), defender.active_pokemon(), move, damage)

        self.apply_calculated_damage(attacker, defender, move, damage, is_critical)
        self.apply_move_effects(attacker, defender, move)

    def prompt_action_input(self, prompt_text, valid_options):
        choice = input(prompt_text)
        if choice not in valid_options:
            logging.info("Invalid choice.")
            return self.prompt_action_input(prompt_text, valid_options)
        return choice

    def calculate_damage(self, attacker, defender, move):
        """Calculate damage without applying it or logging messages"""
        damage, is_critical = move.apply_damage(attacker.active_pokemon(), defender.active_pokemon())

        ability = defender.active_pokemon().ability
        if hasattr(ability, "modify_damage"):
            damage = ability.modify_damage(attacker.active_pokemon(), defender.active_pokemon(), move, damage)

        if (
            move.damage_class == "Physical"
            and attacker.active_pokemon().battle_stats.status == "burn"
        ):
            # Check if Pokemon has Guts ability (which prevents burn attack reduction)
            has_guts = hasattr(attacker.active_pokemon().ability, 'name') and attacker.active_pokemon().ability.name == "Guts"
            if not has_guts:
                damage = damage // 2

        return damage, is_critical

    def apply_calculated_damage(self, attacker, defender, move, damage, is_critical, skip_damage_application=False, skip_crit_message=False):
        """Apply pre-calculated damage and log appropriate messages"""
        if (
            move.damage_class == "Physical"
            and attacker.active_pokemon().battle_stats.status == "burn"
        ):
            # Check if Pokemon has Guts ability (which prevents burn attack reduction)
            has_guts = hasattr(attacker.active_pokemon().ability, 'name') and attacker.active_pokemon().ability.name == "Guts"
            if not has_guts:
                self.log(f"{attacker.active_pokemon().name}'s attack was halved due to burn!")

        if is_critical and not skip_crit_message:
            self.log("A critical hit!")
        
        if not skip_damage_application:
            defender.active_pokemon().take_damage(damage)
        self.log(f"It dealt {damage} damage to {defender.active_pokemon().name}.")

    def apply_damage(self, attacker, defender, move):
        damage, is_critical = self.calculate_damage(attacker, defender, move)
        
        ability = defender.active_pokemon().ability
        if hasattr(ability, "on_damage_taken"):
            ability.on_damage_taken(attacker.active_pokemon(), defender.active_pokemon(), move, damage)

        self.apply_calculated_damage(attacker, defender, move, damage, is_critical)

    def handle_faint(self, player):
        if player.active_pokemon().is_fainted():
            self.log(f"{player.active_pokemon().name} has fainted!")

            if player.has_available_pokemon():
                if player.is_ai:
                    # 🧠 Smart AI switch using type effectiveness
                    opponent = self.player if player == self.opponent else self.opponent
                    replacement = self.choose_best_counter(player, opponent.active_pokemon())
                    if replacement:
                        player.switch_to(replacement)
                        self.log(f"{player.name} sent out {player.team[replacement].name}!")
                else:
                    # Player manual switch
                    valid_choices = [(i, p) for i, p in enumerate(player.team) if not p.is_fainted()]
                    while True:
                        print("\nYour Pokemon:")
                        for i, p in valid_choices:
                            print(f"{i + 1}. {p.name} (HP: {p.current_hp}/{p.stats['hp']})")

                        try:
                            choice = int(input("Switch to: ")) - 1
                            if any(i == choice for i, _ in valid_choices):
                                player.switch_to(choice)
                                break
                            else:
                                self.log("Invalid choice. Try again.")
                        except ValueError:
                            self.log("Please enter a number.")

    def check_battle_end(self):
        if not self.player.has_available_pokemon() or not self.opponent.has_available_pokemon():
            self.battle_over = True
            self.log(f"Battle over: {self.battle_over}")
