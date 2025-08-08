import pygame
import time
import logging
from models.player_action import PlayerAction
from models.type_colouring import TYPE_COLORS

class BattleScene:
    def __init__(self, screen, battle_manager):
        self.screen = screen
        self.battle_manager = battle_manager
        self.selected_action = None
        self.font = pygame.font.SysFont("arial", 20)
        self.ui_state = "main_menu"
        self.fight_button_rect = pygame.Rect(200, 400, 650, 150)
        self.move_buttons = []
        self.battle_log = []

        self.turn_state = "start"
        self.action_timer = 0
        self.first = None
        self.second = None
        self.first_action = None
        self.second_action = None
        self.status_queue = []
        self.previous_player_pokemon = None
        self.previous_opponent_pokemon = None

    def log_message(self, text):
        self.battle_log.append(text)
        if len(self.battle_log) > 4:
            self.battle_log.pop(0)
    
    def check_pokemon_switches(self):
        current_player_pokemon = self.battle_manager.player.active_pokemon()
        current_opponent_pokemon = self.battle_manager.opponent.active_pokemon()
        
        if (self.previous_player_pokemon != current_player_pokemon or 
            self.previous_opponent_pokemon != current_opponent_pokemon):
            self.selected_action = None
            self.ui_state = "main_menu"
            
        self.previous_player_pokemon = current_player_pokemon
        self.previous_opponent_pokemon = current_opponent_pokemon

    def handle_input(self, event):
        if self.battle_manager.battle_over:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.ui_state == "main_menu":
                if self.fight_button_rect.collidepoint(pos):
                    self.ui_state = "move_select"

            elif self.ui_state == "move_select":
                moves = self.battle_manager.player.active_pokemon().moves
                for i, rect in enumerate(self.move_buttons):
                    if rect.collidepoint(pos):
                        move = moves[i]
                        self.selected_action = PlayerAction(type="move", move=move)

    def animate_hp_change(self, pokemon_owner, new_hp):
        current_hp = pokemon_owner.active_pokemon().battle_stats.current_hp
        hp_diff = new_hp - current_hp
        steps = max(abs(hp_diff), 1)
        step_fraction = hp_diff / steps
        for i in range(steps):
            current_hp += step_fraction
            pokemon_owner.active_pokemon().battle_stats.current_hp = int(round(current_hp))
            self.draw()
            pygame.display.flip()
            pygame.time.delay(35)
        pokemon_owner.active_pokemon().battle_stats.current_hp = new_hp
        self.draw()
        pygame.display.flip()

    def update(self):
        self.check_pokemon_switches()
        
        current_time = time.time()

        if self.battle_manager.battle_over:
            return

        if self.turn_state == "start" and self.selected_action:
            # self.log_message(f"What will {self.battle_manager.player.active_pokemon().name} do?")
            self.opponent_action = self.battle_manager.make_ai_action(
                self.battle_manager.opponent, self.battle_manager.player
            )
            self.first, self.second = self.battle_manager.determine_turn_order(self.selected_action, self.opponent_action)
            self.first_action = self.selected_action if self.first == self.battle_manager.player else self.opponent_action
            self.second_action = self.opponent_action if self.first == self.battle_manager.player else self.selected_action

            self.turn_state = "first_move"
            self.action_timer = current_time + 1
            return

        elif self.turn_state == "first_move" and current_time >= self.action_timer:
            if self.first_action and self.first_action.move:
                self.log_message(f"{self.first.active_pokemon().name} used {self.first_action.move.name}!")
                self.draw(); pygame.display.flip()
                self.action_timer = current_time + 1
                self.turn_state = "first_damage_anim"
            else:
                self.turn_state = "start"
            return

        elif self.turn_state == "first_damage_anim" and current_time >= self.action_timer:
            if self.first_action and self.first_action.move:
                previous_status = self.second.active_pokemon().battle_stats.status
                
                # Calculate move damage without applying it
                damage, is_critical, missed = self.battle_manager.execute_move_calculate_only(
                    self.first, self.second, self.first_action.move)
                
                if missed or damage is None:
                    self.turn_state = "second_move"
                    self.action_timer = current_time + 1
                    return
                
                # Calculate new HP for animation
                original_hp = self.second.active_pokemon().battle_stats.current_hp
                new_hp = max(0, original_hp - damage)
                
                # Animate HP change
                self.animate_hp_change(self.second, new_hp)
                
                # Show critical hit message after HP animation if applicable
                if is_critical:
                    self.log_message("A critical hit!")
                    self.draw()
                    pygame.display.flip()
                    pygame.time.delay(800)
                
                # Apply effects and show damage message (damage already applied by animation)
                ability = self.second.active_pokemon().ability
                if hasattr(ability, "on_damage_taken"):
                    ability.on_damage_taken(self.first.active_pokemon(), self.second.active_pokemon(), self.first_action.move, damage)
                
                # Skip damage application since animate_hp_change already applied it, and skip crit message since we showed it above
                self.battle_manager.apply_calculated_damage(self.first, self.second, self.first_action.move, damage, is_critical, skip_damage_application=True, skip_crit_message=True)
                
                # Apply move effects (status effects, stat changes)
                self.battle_manager.apply_move_effects(self.first, self.second, self.first_action.move)
                
                new_status = self.second.active_pokemon().battle_stats.status
                if previous_status is None and new_status is not None:
                    status_name = new_status.name if hasattr(new_status, 'name') else str(new_status)
                    self.log_message(f"{self.second.active_pokemon().name} is now {status_name}!")
                    self.draw()
                    pygame.display.flip()
                    pygame.time.delay(1000)
                
                self.action_timer = current_time + 1
                self.turn_state = "check_faint1"
            else:
                self.turn_state = "start"
            return

        elif self.turn_state == "check_faint1" and current_time >= self.action_timer:
            if self.second.active_pokemon().is_fainted():
                self.battle_manager.handle_faint(self.second)
                self.selected_action = None
                self.first_action = None
                self.second_action = None
                self.ui_state = "main_menu"
                if self.battle_manager.check_battle_end():
                    self.turn_state = "end"
                    return
            self.turn_state = "second_move"
            self.action_timer = current_time + 1
            return

        elif self.turn_state == "second_move" and current_time >= self.action_timer:
            if self.second_action and self.second_action.move:
                self.log_message(f"{self.second.active_pokemon().name} used {self.second_action.move.name}!")
                self.draw(); pygame.display.flip()
                self.action_timer = current_time + 1
                self.turn_state = "second_damage_anim"
            else:
                self.turn_state = "start"
            return

        elif self.turn_state == "second_damage_anim" and current_time >= self.action_timer:
            if self.second_action and self.second_action.move:
                previous_status = self.first.active_pokemon().battle_stats.status
                
                # Calculate move damage without applying it
                damage, is_critical, missed = self.battle_manager.execute_move_calculate_only(
                    self.second, self.first, self.second_action.move)
                
                if missed or damage is None:
                    self.turn_state = "status"
                    self.action_timer = current_time + 1
                    return
                
                # Calculate new HP for animation
                original_hp = self.first.active_pokemon().battle_stats.current_hp
                new_hp = max(0, original_hp - damage)
                
                # Animate HP change
                self.animate_hp_change(self.first, new_hp)
                
                # Show critical hit message after HP animation if applicable
                if is_critical:
                    self.log_message("A critical hit!")
                    self.draw()
                    pygame.display.flip()
                    pygame.time.delay(800)
                
                # Apply effects and show damage message (damage already applied by animation)
                ability = self.first.active_pokemon().ability
                if hasattr(ability, "on_damage_taken"):
                    ability.on_damage_taken(self.second.active_pokemon(), self.first.active_pokemon(), self.second_action.move, damage)
                
                # Skip damage application since animate_hp_change already applied it, and skip crit message since we showed it above
                self.battle_manager.apply_calculated_damage(self.second, self.first, self.second_action.move, damage, is_critical, skip_damage_application=True, skip_crit_message=True)
                
                # Apply move effects (status effects, stat changes)
                self.battle_manager.apply_move_effects(self.second, self.first, self.second_action.move)
                
                new_status = self.first.active_pokemon().battle_stats.status
                if previous_status is None and new_status is not None:
                    status_name = new_status.name if hasattr(new_status, 'name') else str(new_status)
                    self.log_message(f"{self.first.active_pokemon().name} is now {status_name}!")
                    self.draw()
                    pygame.display.flip()
                    pygame.time.delay(1000)
                
                self.action_timer = current_time + 1
                self.turn_state = "check_faint2"
            else:
                self.turn_state = "start"
            return

        elif self.turn_state == "check_faint2" and current_time >= self.action_timer:
            if self.first.active_pokemon().is_fainted():
                self.battle_manager.handle_faint(self.first)
                self.selected_action = None
                self.first_action = None
                self.second_action = None
                self.ui_state = "main_menu"
                if self.battle_manager.check_battle_end():
                    self.turn_state = "end"
                    return
            self.turn_state = "status"
            self.action_timer = current_time + 1
            return

        elif self.turn_state == "status" and current_time >= self.action_timer:
            # Apply status effects and get list of (owner, new_hp, message)
            self.status_queue = self.battle_manager.apply_end_of_turn_status_effects([
                self.battle_manager.player.active_pokemon(),
                self.battle_manager.opponent.active_pokemon()
            ])
            if self.status_queue:
                owner, new_hp, message = self.status_queue.pop(0)
                self.log_message(message)
                self.draw()
                pygame.display.flip()
                self.action_timer = current_time + 1
                self.current_status_owner = owner
                self.current_status_new_hp = new_hp
                self.turn_state = "status_damage_anim"
            else:
                self.turn_state = "end"
                self.action_timer = current_time + 1
            return

        elif self.turn_state == "status_damage_anim" and current_time >= self.action_timer:
            self.animate_hp_change(self.current_status_owner, self.current_status_new_hp)
            if self.status_queue:
                owner, new_hp, message = self.status_queue.pop(0)
                self.log_message(message)
                self.draw()
                pygame.display.flip()
                self.action_timer = current_time + 1
                self.current_status_owner = owner
                self.current_status_new_hp = new_hp
                self.turn_state = "status_damage_anim"
            else:
                self.turn_state = "end"
                self.action_timer = current_time + 1
            return

        elif self.turn_state == "end" and current_time >= self.action_timer:
            self.selected_action = None
            self.turn_state = "start"
            self.ui_state = "main_menu"

    def draw(self):
        self.screen.fill((255, 255, 255))

        player_pokemon = self.battle_manager.player.active_pokemon()
        opponent_pokemon = self.battle_manager.opponent.active_pokemon()

        self.draw_pokemon(player_pokemon, 200, 250, is_player=True)
        self.draw_pokemon(opponent_pokemon, 1000, 150, is_player=False)

        self.draw_hp_bar(player_pokemon.battle_stats.current_hp, player_pokemon.stats["hp"], 200, 350)
        self.draw_hp_bar(opponent_pokemon.battle_stats.current_hp, opponent_pokemon.stats["hp"], 1000, 250)
        self.fight_button_rect = pygame.Rect(300, 440, 600, 250)

        pygame.draw.line(self.screen, (0, 0, 0), (0, 400), (1200, 400), 2)

        if self.ui_state == "main_menu":
            pygame.draw.rect(self.screen, (200, 200, 200), self.fight_button_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), self.fight_button_rect, 2)
            self.draw_text("Fight", 570, 575)

        if self.ui_state == "move_select":
            self.move_buttons = []
            moves = self.battle_manager.player.active_pokemon().moves

            start_x = 350
            start_y = 500
            button_width = 250
            button_height = 50
            padding = 20

            for i, move in enumerate(moves):
                row = i // 2
                col = i % 2
                x = start_x + col * (button_width + padding)
                y = start_y + row * (button_height + padding)

                move_type = move.move_type.value.lower()
                colour = TYPE_COLORS.get(move_type, (180, 180, 180))

                rect = pygame.Rect(x, y, button_width, button_height)
                pygame.draw.rect(self.screen, colour, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

                move_text = f"{move.name} (PP: {self.battle_manager.player.active_pokemon().battle_stats.pp[move.name]})"
                self.draw_text(move_text, x + 10, y + 10)
                self.move_buttons.append(rect)

        if self.battle_manager.battle_over:
            self.draw_text("Battle Over!", 560, 300)

        self.draw_dialogue_box()

    def draw_pokemon(self, pokemon, x, y, is_player):
        sprite = pokemon.back_sprite if is_player else pokemon.front_sprite

        if sprite:
            self.screen.blit(sprite, (x, y))
        else:
            logging.info("RIP NO SPRITE")
        name_x = x + 10
        name_y = y + 75
        self.draw_text(pokemon.name, name_x, name_y)
        # Draw status label if there is a status
        status = pokemon.battle_stats.status
        if status is not None:
            # status may be an Enum, str, or object with .name
            if hasattr(status, "name"):
                status_text = status.name
            else:
                status_text = str(status)
            self.draw_status_label(status_text, name_x + self.font.size(pokemon.name)[0] + 10, name_y)

    def draw_hp_bar(self, current_hp, max_hp, x, y, width=100, height=10):
        ratio = current_hp / max_hp
        pygame.draw.rect(self.screen, (255, 0, 0), (x, y, width, height))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y, width * ratio, height))

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (x, y))

    def draw_dialogue_box(self):
        box_rect = pygame.Rect(100, 700, 1000, 40)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), box_rect, 2)

        if self.battle_log:
            self.draw_text(self.battle_log[-1], box_rect.x + 10, box_rect.y + 10)
    def draw_status_label(self, status, x, y):
        # Map status names to colors
        STATUS_COLORS = {
            "burn": (220, 50, 50),        # red
            "poison": (130, 0, 180),      # purple
            "sleep": (50, 90, 200),       # blue
            "paralysis": (240, 220, 60),  # yellow
            "freeze": (100, 200, 255),    # light blue
            "confusion": (200, 120, 200), # pinkish
        }
        # Normalize status string (lowercase)
        status_key = status.lower()
        color = STATUS_COLORS.get(status_key, (90, 90, 90))
        label_font = pygame.font.SysFont("arial", 16, bold=True)
        text_surf = label_font.render(status.capitalize(), True, (255, 255, 255))
        padding_x = 8
        padding_y = 2
        rect_width = text_surf.get_width() + 2 * padding_x
        rect_height = text_surf.get_height() + 2 * padding_y
        rect = pygame.Rect(x, y, rect_width, rect_height)
        pygame.draw.rect(self.screen, color, rect, border_radius=5)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1, border_radius=5)
        self.screen.blit(text_surf, (x + padding_x, y + padding_y))