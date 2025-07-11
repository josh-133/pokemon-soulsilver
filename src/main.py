import pygame
from scenes.battle_scene import BattleScene
from scenes.pokemon_select_scene import PokemonSelectScene
from models.battle_manager import BattleManager
from models.player import Player
from data.loaders import load_pokemon, get_move_lookup, POKEMON_DATA
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,600))

move_lookup = get_move_lookup()

pokemon_data = POKEMON_DATA

def run_game_loop(scene):
    pygame.display.set_caption("Pokemon Battles!")
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            scene.handle_input(event)

        # Draw all elements
        # Update everything
        scene.update()
        scene.draw()
        pygame.display.flip()
        clock.tick(60)

def on_pokemon_selected(pokemon_data):
    player = Player("Ash", False, [load_pokemon(pokemon_data["name"], move_lookup)])
    opponent = Player("Red", True, [load_pokemon("charizard", move_lookup)])
    battle_manager = BattleManager(player, opponent)
    scene = BattleScene(screen, battle_manager)
    run_game_loop(scene)

select_scene = PokemonSelectScene(screen, pokemon_data, on_pokemon_selected)
run_game_loop(select_scene)