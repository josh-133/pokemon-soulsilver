import pygame
import threading
import time
from models.pokemon import load_sprite

class PokemonSelectScene:
    def __init__(self, screen, pokemon_data, on_select_callback):
        self.screen = screen
        self.pokemon_data = pokemon_data[:493]
        self.on_select_callback = on_select_callback
        self.font = pygame.font.SysFont("arial", 16)
        self.page = 0
        self.page_size = 45
        self.buttons = []
        self.sprite_cache = {}
        self.start_background_sprite_loader()

        self.selected_team = []
        self.start_button = pygame.Rect(500, 720, 160, 40)

        self.prev_button = pygame.Rect(300, 720, 100, 40)
        self.next_button = pygame.Rect(800, 720, 100, 40)

        self.generate_buttons()

    def preload_sprites(self):
        for pokemon in self.pokemon_data:
            if "sprites" in pokemon and "front_default" in pokemon["sprites"]:
                sprite_url = pokemon["sprites"]["front_default"]

                if sprite_url not in self.sprite_cache:
                    sprite = load_sprite(sprite_url)
                    self.sprite_cache[sprite_url] = sprite
                    time.sleep(0.01)
    
    def start_background_sprite_loader(self):
        threading.Thread(target=self.preload_sprites, daemon=True).start()

    def generate_buttons(self):
        self.buttons = []

        columns = 9
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

             # Load sprite from cache or download if needed
            if "sprites" in pokemon and "front_default" in pokemon["sprites"]:
                url = pokemon["sprites"]["front_default"]
                if url in self.sprite_cache:
                    sprite = self.sprite_cache[url]
                else:
                    sprite = load_sprite(url)
                    self.sprite_cache[url] = sprite  # Save for reuse

            self.buttons.append((rect, pokemon, sprite))

    def draw(self):
        # Clear screen
        self.screen.fill((255, 255, 255))

        # Draw pokemon grid
        for rect, pokemon, sprite in self.buttons:
            pygame.draw.rect(self.screen, (200, 200, 200), rect)

            if sprite:
                sprite_rect = sprite.get_rect(center=(rect.centerx, rect.y + 40))
                self.screen.blit(sprite, sprite_rect) 

            name_surface = self.font.render(pokemon["name"].capitalize(), True, (0, 0, 0))
            name_rect = name_surface.get_rect(center=(rect.centerx, rect.y + 80))
            self.screen.blit(name_surface, name_rect)   

            # Highlight selected
            if pokemon in self.selected_team:
                pygame.draw.rect(self.screen, (0, 255, 0), rect, 3)

        # Draw team bar
        pygame.draw.rect(self.screen, (230, 230, 250), (0, 700, 1200, 100))
        for i, pokemon in enumerate(self.selected_team):
            name_surface = self.font.render(pokemon["name"].capitalize(), True, (0, 0, 0))
            self.screen.blit(name_surface, (20 + i * 120, 470))

        # Draw start button
        pygame.draw.rect(self.screen, (100, 200, 100), self.start_button)
        button_text = self.font.render("Start battle", True, (255, 255, 255))
        text_rect = button_text.get_rect(center=self.start_button.center)
        self.screen.blit(button_text, text_rect)

        # Draw navigation buttons
        pygame.draw.rect(self.screen, (100, 100, 255), self.prev_button)
        prev_text = self.font.render("Previous", True, (255, 255, 255))
        self.screen.blit(prev_text, self.prev_button.move(10, 5))

        pygame.draw.rect(self.screen, (100, 100, 255), self.next_button)
        next_text = self.font.render("Next", True, (255, 255, 255))
        self.screen.blit(next_text, self.next_button.move(25, 5))

        # Page indicator text
        total_pages = (len(self.pokemon_data) + self.page_size - 1) // self.page_size
        page_label = self.font.render(f"Page {self.page + 1} / {total_pages}", True, (0, 0, 0))
        self.screen.blit(page_label, (540, 780))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.prev_button.collidepoint(pos) and self.page > 0:
                self.page -= 1
                self.generate_buttons()

            if self.next_button.collidepoint(pos):
                if (self.page + 1) * self.page_size < len(self.pokemon_data):
                    self.page += 1
                    self.generate_buttons()

            # Start battle button
            if self.start_button.collidepoint(pos) and 1 <= len(self.selected_team) <= 6:
                self.on_select_callback(self.selected_team)
                return
        
            for rect, pokemon, _ in self.buttons:
                if rect.collidepoint(pos):
                    if pokemon not in self.selected_team and len(self.selected_team) < 6:
                        self.selected_team.append(pokemon)
                    elif pokemon in self.selected_team:
                        self.selected_team.remove(pokemon)
                    return

            for rect, pokemon, _ in self.buttons:
                if rect.collidepoint(pos):
                    self.on_select_callback(pokemon)
                    return

    def update(self):
        pass