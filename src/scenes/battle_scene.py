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

    def log_message(self, text):
        self.battle_log.append(text)
        if len(self.battle_log) > 4:
            self.battle_log.pop(0)

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

    def update(self):

        current_time = time.time()

        if self.battle_manager.battle_over:
            return

        if self.turn_state == "start" and self.selected_action:
            # self.log_message(f"What will {self.battle_manager.player.active_pokemon().name} do?")
            self.opponent_action = self.battle_manager.make_ai_action(
                self.battle_manager.opponent, self.battle_manager.player
            )
            self.first, self.second = self.battle_manager.determine_turn_order()
            self.first_action = self.selected_action if self.first == self.battle_manager.player else self.opponent_action
            self.second_action = self.opponent_action if self.first == self.battle_manager.player else self.selected_action

            self.turn_state = "first_move"
            self.action_timer = current_time + 1
            return

        elif self.turn_state == "first_move" and current_time >= self.action_timer:
            self.battle_manager.execute_move(self.first, self.second, self.first_action.move)
            self.log_message(f"{self.first.active_pokemon().name} used {self.first_action.move.name}!")
            self.draw(); pygame.display.flip()
            self.action_timer = current_time + 1
            self.turn_state = "check_faint1"
            return

        elif self.turn_state == "check_faint1" and current_time >= self.action_timer:
            if self.second.active_pokemon().is_fainted():
                self.battle_manager.handle_faint(self.second)
                if self.battle_manager.check_battle_end():
                    self.turn_state = "end"
                    return
            self.turn_state = "second_move"
            self.action_timer = current_time + 1
            return

        elif self.turn_state == "second_move" and current_time >= self.action_timer:
            self.battle_manager.execute_move(self.second, self.first, self.second_action.move)
            self.log_message(f"{self.second.active_pokemon().name} used {self.second_action.move.name}!")
            self.draw(); pygame.display.flip()
            self.action_timer = current_time + 1
            self.turn_state = "check_faint2"
            return

        elif self.turn_state == "check_faint2" and current_time >= self.action_timer:
            if self.first.active_pokemon().is_fainted():
                self.battle_manager.handle_faint(self.first)
                if self.battle_manager.check_battle_end():
                    self.turn_state = "end"
                    return
            self.turn_state = "status"
            self.action_timer = current_time + 1
            return

        elif self.turn_state == "status" and current_time >= self.action_timer:
            self.battle_manager.apply_end_of_turn_status_effects([
                self.battle_manager.player.active_pokemon(),
                self.battle_manager.opponent.active_pokemon()
            ])
            self.draw(); pygame.display.flip()
            self.action_timer = current_time + 1
            self.turn_state = "end"
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
        self.draw_text(pokemon.name, x + 10, y + 75)

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