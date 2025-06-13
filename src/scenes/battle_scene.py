import pygame
from models.player_action import PlayerAction

class BattleScene:
    def __init__(self, screen, battle_manager):
        self.screen = screen
        self.battle_manager = battle_manager
        self.selected_action = None
        self.font = pygame.font.SysFont("arial", 20)
        self.ui_state = "main_menu"
    
    def handle_input(self, event):
        fight_button_rect = pygame.Rect(50, 400, 100, 40)

        if self.ui_state == "main_menu":
            pygame.draw.rect(self.screen, (200, 200, 200), fight_button_rect)
            self.draw_text("Fight", 65, 410)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
        
        if fight_button_rect.collidepoint(pos):
            self.ui_state = "move_select"
        elif self.ui_state == "move_select":
            for i, rect in enumerate(self.move_buttons):
                if rect.collidepoint(pos):
                    move = self.battle_manager.player.active_pokemon().moves[i]
                    self.selected_action = PlayerAction(type="move", move=move)

    def update(self):
        if self.selected_action:
            ai_pokemon = self.battle_manager.opponent.active_pokemon()
            ai_move = ai_pokemon.moves[0]
            opponent_action = PlayerAction(type="move", move=ai_move)

            self.battle_manager.take_turn(self.selected_action, opponent_action)

            self.selected_action = None
            self.ui_state = "main_menu"

    def draw(self):
        player_pokemon = self.battle_manager.player.active_pokemon()
        opponent_pokemon = self.battle_manager.opponent.active_pokemon()

        self.draw_pokemon(player_pokemon.name, 100, 150)
        self.draw_pokemon(opponent_pokemon.name, 500, 50)

        self.draw_hp_bar(player_pokemon.battle_stats.current_hp, player_pokemon.stats["hp"], 100, 250)
        self.draw_hp_bar(opponent_pokemon.battle_stats.current_hp, opponent_pokemon.stats["hp"], 500, 150)


    def draw_pokemon(self, name, x, y):
        pygame.draw.rect(self.screen, (180, 180, 255), pygame.Rect(x, y , 100, 100))
        self.draw_text(name, x+10, y+40)
    
    def draw_hp_bar(self, current_hp, max_hp, x, y, width=100, height=10):
        ratio = current_hp / max_hp
        pygame.draw.rect(self.screen, (255, 0, 0), (x, y, width, height))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y, width * ratio, height))

    def draw_text(self, text, x, y):
        text_surface = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(text_surface, (x, y))