# Pokemon SoulSilver - Class Diagram

```mermaid
classDiagram
    %% Core Battle System
    class BattleManager {
        -Player player
        -Player opponent
        -List~String~ battle_log
        -boolean battle_over
        +__init__(player, opponent)
        +take_turn(player_action, opponent_action)
        +execute_move(attacker, defender, move)
        +apply_damage(attacker, defender, move)
        +handle_faint(player)
        +check_battle_end()
        +make_ai_action(player, opponent)
    }

    class Player {
        -String name
        -boolean is_ai
        -List~Pokemon~ team
        -int active_index
        +__init__(name, is_ai, team)
        +active_pokemon() Pokemon
        +has_available_pokemon() boolean
        +switch_to(index)
    }

    class Pokemon {
        -String name
        -Ability ability
        -BaseStats base_stats
        -List~Type~ types
        -List~Move~ moves
        -int level
        -Dict iv
        -Dict ev
        -Dict stats
        -BattleStats battle_stats
        +__init__(name, ability, base_stats, types, moves, level, iv, ev, front_sprite, back_sprite)
        +calculate_stats() Dict
        +get_move_by_name(move_name) Move
        +is_fainted() boolean
        +take_damage(amount)
        +heal(amount)
        +generate_random_iv()$ Dict
        +generate_default_ev()$ Dict
    }

    class BattleStats {
        -int max_hp
        -int current_hp
        -Dict battle_stats
        -String status
        -boolean badly_poisoned
        -int toxic_turns
        -Dict pp
        -Dict stat_modifiers
        +__init__(pokemon)
        +is_fainted() boolean
        +apply_status(condition)
        +use_pp(move_name)
        +has_pp(move_name) boolean
        +apply_stat_change(stat_name, amount)
        +get_effective_stat(stat_name) int
        +take_damage(amount)
        +heal(amount)
    }

    %% Move System
    class Move {
        -String name
        -int accuracy
        -int pp
        -int priority
        -int power
        -String damage_class
        -float crit_rate
        -String category
        -Type move_type
        -HitInfo hit_info
        -MoveEffects effects_info
        +__init__(name, accuracy, pp, priority, power, damage_class, crit_rate, category, move_type, hit_info, effects_info)
        +apply_damage(attacker, defender) int
    }

    class HitInfo {
        -int min_hits
        -int max_hits
        -int min_turns
        -int max_turns
        +__init__(min_hits, max_hits, min_turns, max_turns)
    }

    class MoveEffects {
        -int effect_chance
        -String ailment
        -int drain
        -int healing
        -int ailment_chance
        -int flinch_chance
        -int stat_chance
        -boolean is_badly_poisoning
        +__init__(effect_chance, ailment, drain, healing, ailment_chance, flinch_chance, stat_chance, is_badly_poisoning)
    }

    %% Ability System
    class Ability {
        <<abstract>>
        -String name
        -String description
        +__init__(name, description)
        +on_switch_in(pokemon, battle_manager)
        +on_damage_take(attacker, defender, move, damage)
        +modify_damage(attacker, defender, move, damage) int
    }

    class Static {
        +__init__()
        +on_damage_take(attacker, defender, move, damage)
    }

    class PoisonPoint {
        +__init__()
        +on_damage_take(attacker, defender, move, damage)
    }

    class Levitate {
        +__init__()
        +modify_damage(attacker, defender, move, damage) int
    }

    %% Data Classes
    class BaseStats {
        -int hp
        -int attack
        -int defense
        -int sp_attack
        -int sp_defense
        -int speed
        +__init__(hp, attack, defense, sp_attack, sp_defense, speed)
    }

    class Type {
        <<enumeration>>
        NORMAL
        GRASS
        FIRE
        WATER
        ELECTRIC
        POISON
        FLYING
        FIGHTING
        BUG
        PSYCHIC
        DARK
        GHOST
        GROUND
        ROCK
        STEEL
        ICE
        DRAGON
        FAIRY
    }

    class PlayerAction {
        -String type
        -String move_name
        -int switch_to
        -String item
        +__init__(type, move_name, switch_to, item)
    }

    %% UI Classes
    class BattleScene {
        -Screen screen
        -BattleManager battle_manager
        -String ui_state
        -Font font
        -List~String~ battle_log
        +__init__(screen, battle_manager)
        +handle_input(event)
        +update()
        +draw()
        +draw_pokemon(pokemon, x, y, is_player)
    }

    class PokemonSelectScene {
        -Screen screen
        -Dict pokemon_data
        -List~Pokemon~ selected_team
        -Dict sprite_cache
        -int page
        +__init__(screen, pokemon_data, on_select_callback)
        +preload_sprites()
        +generate_buttons()
        +handle_input(event)
        +draw()
    }

    %% AI Environment
    class PokemonEnv {
        -ActionSpace action_space
        -ObservationSpace observation_space
        -Player player
        -Player opponent
        -BattleManager battle
        +__init__(opponent_model)
        +reset() observation
        +step(action) tuple
        +_get_obs(perspective) array
        +render()
    }

    %% Relationships
    BattleManager --> Player : manages
    BattleManager --> PlayerAction : processes
    BattleManager --> Move : executes
    Player --> Pokemon : has team of
    Pokemon --> Ability : has
    Pokemon --> BaseStats : has
    Pokemon --> BattleStats : has
    Pokemon --> Move : knows
    Pokemon --> Type : is of type
    Move --> HitInfo : has
    Move --> MoveEffects : has
    Move --> Type : is of type
    BattleStats --> Pokemon : belongs to
    Static --|> Ability : inherits
    PoisonPoint --|> Ability : inherits
    Levitate --|> Ability : inherits
    BattleScene --> BattleManager : displays
    PokemonSelectScene --> Pokemon : selects
    PokemonEnv --> Player : simulates
    PokemonEnv --> BattleManager : uses
```

## Class Overview

**18 Total Classes** organized into 6 main categories:

### Core Battle System (4 classes)
- `BattleManager` - Orchestrates battles and turn execution
- `Player` - Represents human/AI players with Pokemon teams  
- `Pokemon` - Individual Pokemon with stats, moves, and abilities
- `BattleStats` - Runtime battle statistics and status effects

### Move System (3 classes)
- `Move` - Pokemon moves with damage calculation
- `HitInfo` - Multi-hit move information
- `MoveEffects` - Status effects and secondary effects

### Ability System (4 classes)
- `Ability` - Abstract base class for Pokemon abilities
- `Static` - Paralyzes on physical contact
- `PoisonPoint` - Poisons on physical contact  
- `Levitate` - Immunity to Ground-type moves

### Data Models (3 classes)
- `BaseStats` - Pokemon base statistics
- `Type` - Enumeration of all 18 Pokemon types
- `PlayerAction` - Represents player choices (move/switch/item)

### UI Layer (2 classes)
- `BattleScene` - Main battle interface
- `PokemonSelectScene` - Pokemon team selection

### AI Integration (1 class)
- `PokemonEnv` - OpenAI Gym environment for reinforcement learning

## Key Relationships
- **Composition**: Pokemon contains BattleStats, BaseStats, Ability, and Moves
- **Inheritance**: Ability system uses polymorphism for different ability types
- **Dependency**: BattleManager orchestrates interactions between all core classes