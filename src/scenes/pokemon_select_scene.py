import pygame
from models.pokemon import load_sprite

class PokemonSelectScene:
    def __init__(self, screen, pokemon_data, on_select_callback):
        self.screen = screen
        self.pokemon_data = pokemon_data[:493]
        self.on_select_callback = on_select_callback
        self.font = pygame.font.SysFont("arial", 16)
        self.page = 0
        self.page_size = 24
        self.buttons = []

        self.prev_button = pygame.Rect(100, 540, 100, 40)
        self.next_button = pygame.Rect(600, 540, 100, 40)

        self.generate_buttons()


    def generate_buttons(self):
        self.buttons = []

        columns = 6
        spacing_x = 130
        spacing_y = 130
        start_x = 40
        start_y = 40

        start_index = self.page * self.page_size
        end_index = start_index + self.page_size
        current_pokemon = self.pokemon_data[start_index:end_index]

        for idx, pokemon in enumerate(current_pokemon):
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

         # Draw navigation buttons
        pygame.draw.rect(self.screen, (100, 100, 255), self.prev_button)
        prev_text = self.font.render("Previous", True, (255, 255, 255))
        self.screen.blit(prev_text, self.prev_button.move(10, 5))

        pygame.draw.rect(self.screen, (100, 100, 255), self.next_button)
        next_text = self.font.render("Next", True, (255, 255, 255))
        self.screen.blit(next_text, self.next_button.move(25, 5))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.prev_button.collidepoint(pos) and self.page > 0:
                self.page -= 1
                self.generate_buttons()

            elif self.next_button.collidepoint(pos):
                if (self.page + 1) * self.page_size < len(self.pokemon_data):
                    self.page += 1
                    self.generate_buttons()

            else:
                for rect, pokemon, _ in self.buttons:
                    if rect.collidepoint(pos):
                        self.on_select_callback(pokemon)

            for rect, pokemon, _ in self.buttons:
                if rect.collidepoint(pos):
                    self.on_select_callback(pokemon)
                    return

    def update(self):
        pass