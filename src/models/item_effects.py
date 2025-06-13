ITEM_EFFECTS = {
    "Potion": lambda user, target: target.heal(20),
    "Super Potion": lambda user, target: target.heal(50),
    "Moomoo Milk": lambda user, target: target.heal(100),
    "Hyper Potion": lambda user, target: target.heal(200),    
}