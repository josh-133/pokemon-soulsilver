class PlayerAction:
    def __init__(self, type: str, move=None, switch_to=None, item=None):
        self.type = type
        self.move = move
        self.switch_to = switch_to
        self.item = item
        