import pygame

class Player:
    def __init__(self, x, y):
        self.image = pygame.Surface((32, 32)) # Temporary red square
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x,y))
        self.speed = 200 # pixels per second

    def handle_event(self, event):
        pass

    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed * dt
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed * dt
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed * dt

    def draw(self, surface):
        surface.blit(self.image, self.rect)