class PlayerAction:
    def __init__(self, type: str, move_name=None, switch_to=None, item=None):
        self.type = type
        self.move_name = move_name
        self.switch_to = switch_to
        self.item = item
        