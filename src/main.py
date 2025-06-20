import pygame
from scenes.battle_scene import BattleScene
from models.battle_manager import BattleManager
from models.player import Player
from data.loaders import load_pokemon, get_move_lookup
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,600))

move_lookup = get_move_lookup()
pikachu = load_pokemon("pikachu", move_lookup)
charmander = load_pokemon("charmander", move_lookup)

player = Player("Ash", False, [pikachu])
opponent = Player("Red", True, [charmander])

battle_manager = BattleManager(player, opponent)
scene = BattleScene(screen, battle_manager)

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