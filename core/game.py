from world.player import Player

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.player = Player(x=100, y=100)
    
    def handle_event(self, event):
        self.player.handle_event(event)

    def update(self, dt):
        self.player.update(dt)

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.player.draw(self.screen)