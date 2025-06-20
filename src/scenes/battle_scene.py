import pygame
from models.player_action import PlayerAction
from models.type_colouring import TYPE_COLORS

class BattleScene:
    def __init__(self, screen, battle_manager):
        self.screen = screen
        self.battle_manager = battle_manager
        self.selected_action = None
        self.font = pygame.font.SysFont("arial", 20)
        self.ui_state = "main_menu"
        self.fight_button_rect = None
        self.move_buttons = []
    
    def handle_input(self, event):
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
                        self.selected_action = PlayerAction(type="move", move=move)

    def update(self):
        if self.selected_action:
            ai_pokemon = self.battle_manager.opponent.active_pokemon()
            ai_move = ai_pokemon.moves[0]
            opponent_action = PlayerAction(type="move", move=ai_move)

            self.battle_manager.take_turn(self.selected_action, opponent_action)

            self.selected_action = None
            self.ui_state = "main_menu"
        if self.battle_manager.battle_over:
            return

    def draw(self):
        self.screen.fill((255, 255, 255))

        player_pokemon = self.battle_manager.player.active_pokemon()
        opponent_pokemon = self.battle_manager.opponent.active_pokemon()

        self.draw_pokemon(player_pokemon, 100, 150, is_player=True)
        self.draw_pokemon(opponent_pokemon, 500, 50, is_player=False)

        self.draw_hp_bar(player_pokemon.battle_stats.current_hp, player_pokemon.stats["hp"], 100, 250)
        self.draw_hp_bar(opponent_pokemon.battle_stats.current_hp, opponent_pokemon.stats["hp"], 500, 150)
        self.fight_button_rect = pygame.Rect(200, 400, 350, 150)

        if self.ui_state == "main_menu":
            pygame.draw.rect(self.screen, (200, 200, 200), self.fight_button_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), self.fight_button_rect, 2)
            self.draw_text("Fight", 355, 460)

        if self.ui_state == "move_select":
            self.move_buttons = []
            moves = self.battle_manager.player.active_pokemon().moves

            start_x = 150  # left edge
            start_y = 400  # top edge
            button_width = 240
            button_height = 50
            padding = 20

            for i, move in enumerate(moves):
                row = i // 2
                col = i % 2
                x = start_x + col * (button_width + padding)
                y = start_y + row * (button_height + padding)

                move_type = move.move_type.lower()
                colour = TYPE_COLORS.get(move_type, (180, 180, 180))

                rect = pygame.Rect(x, y, button_width, button_height)
                pygame.draw.rect(self.screen, colour, rect)
                pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

                move_text = f"{move.name} (PP: {self.battle_manager.player.active_pokemon().battle_stats.pp[move.name]})"
                self.draw_text(move_text, x + 10, y + 10)
                self.move_buttons.append(rect)

        if self.battle_manager.battle_over:
            self.draw_text("Battle Over!", 320, 200)


    def draw_pokemon(self, pokemon, x, y, is_player):
        sprite = pokemon.back_sprite if is_player else pokemon.front_sprite
        
        if sprite:
            self.screen.blit(sprite, (x, y))
        else:
            print("RIP NO SPRITE")
        self.draw_text(pokemon.name, x+10, y+40)
    
    def draw_hp_bar(self, current_hp, max_hp, x, y, width=100, height=10):
        ratio = current_hp / max_hp
        pygame.draw.rect(self.screen, (255, 0, 0), (x, y, width, height))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y, width * ratio, height))

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (x, y))