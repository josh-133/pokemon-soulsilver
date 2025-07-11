import pygame
from models.pokemon import load_sprite

class PokemonSelectScene:
    def __init__(self, screen, pokemon_data, on_select_callback):
        self.screen = screen
        self.pokemon_data = pokemon_data[:493]
        self.on_select_callback = on_select_callback
        self.font = pygame.font.SysFont("arial", 16)
        self.buttons = []

        self.generate_buttons()


    def generate_buttons(self):
        columns = 6
        spacing_x = 130
        spacing_y = 130
        start_x = 40
        start_y = 40

        for idx, pokemon in enumerate(self.pokemon_data[:60]):
            col = idx % columns
            row = idx // columns

            x = start_x + col * spacing_x
            y = start_y + row * spacing_y

            rect = pygame.Rect(x, y, 100, 100)
            sprite = None

            if "sprites" in pokemon and "front_default" in pokemon["sprites"]:
                sprite_url = pokemon["sprites"]["front_default"]
                sprite = load_sprite(sprite_url)

            self.buttons.append((rect, pokemon, sprite))


    def draw(self):
        self.screen.fill((255, 255, 255))
        for rect, pokemon, sprite in self.buttons:
            pygame.draw.rect(self.screen, (200, 200, 200), rect)

            if sprite:
                sprite_rect = sprite.get_rect(center=(rect.centerx, rect.y + 40))
                self.screen.blit(sprite, sprite_rect) 

            name_surface = self.font.render(pokemon["name"].capitalize(), True, (0, 0, 0))
            name_rect = name_surface.get_rect(center=(rect.centerx, rect.y + 80))
            self.screen.blit(name_surface, name_rect)   

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            for rect, pokemon, _ in self.buttons:
                if rect.collidepoint(pos):
                    self.on_select_callback(pokemon)
                    return

    def update(self):
        pass