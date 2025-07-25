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
                for i,rect in enumerate(self.move_buttons):
                    if rect.collidepoint(pos):
                        move = moves[i]
                        self.selected_action = PlayerAction(type="move", move_name=move.name)

    def update(self):
        if self.selected_action:
            opponent_action = self.battle_manager.make_ai_action(self.battle_manager.opponent, self.battle_manager.player)


            self.log_message(f"{self.battle_manager.player.active_pokemon().name} used {self.selected_action.move_name}!")
            self.draw()
            pygame.display.flip()
            time.sleep(1)

            self.log_message(f"{self.battle_manager.opponent.active_pokemon().name} used {opponent_action.move_name}")
            self.draw()
            pygame.display.flip()
            time.sleep(1)

            self.battle_manager.take_turn(self.selected_action, opponent_action)

            self.selected_action = None
            self.ui_state = "main_menu"
        if self.battle_manager.battle_over:
            return

    def draw(self):
        self.screen.fill((255, 255, 255))

        player_pokemon = self.battle_manager.player.active_pokemon()
        opponent_pokemon = self.battle_manager.opponent.active_pokemon()

        self.draw_pokemon(player_pokemon, 200, 250, is_player=True)
        self.draw_pokemon(opponent_pokemon, 1000, 150, is_player=False)

        self.draw_hp_bar(player_pokemon.battle_stats.current_hp, player_pokemon.stats["hp"], 200, 350)
        self.draw_hp_bar(opponent_pokemon.battle_stats.current_hp, opponent_pokemon.stats["hp"], 1000, 250)
        self.fight_button_rect = pygame.Rect(300, 440, 600, 250)

        # Line to separate menu from pokemon battling
        pygame.draw.line(self.screen, (0, 0, 0), (0, 400), (1200, 400), 2)

        if self.ui_state == "main_menu":
            pygame.draw.rect(self.screen, (200, 200, 200), self.fight_button_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), self.fight_button_rect, 2)
            self.draw_text("Fight", 570, 575)

        if self.ui_state == "move_select":
            self.move_buttons = []
            moves = self.battle_manager.player.active_pokemon().moves

            start_x = 350  # left edge
            start_y = 500  # top edge
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