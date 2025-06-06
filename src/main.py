import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Pokemon Battles!")
clock = pygame.time.Clock()

test_surface = pygame.Surface((10,10))
test_surface.fill('Blue')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(test_surface,(200,100))

    # Draw all elements
    # Update everything
    pygame.display.update()
    clock.tick(60)