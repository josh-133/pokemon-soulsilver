from pokemon import Pokemon

class BattleStats:
    def __init__(self, actual_stats: Pokemon.stats):
        self.max_hp = actual_stats.hp
        self.current_hp = self.max_hp
        self.battle_stats = {
            "attack": actual_stats.attack,
            "defense": actual_stats.defense,
            "sp_attack": actual_stats.sp_attack,
            "sp_defense": actual_stats.sp_defense,
            "speed": actual_stats.speed,
        }
        self.stat_modifiers = {stat: 0 for stat in self.battle_stats}

    def modify_stat(self, stat_name: str, stat_change: int, ):
        if stat_name not in self.stat_modifiers:
            return
        
        current_stage = self.stat_modifiers[stat_name]
        new_stage = max(-6, min(6, current_stage + stat_change))
        self.stat_modifiers[stat_name] = new_stage

    def get_effective_stat(self, stat_name: str):
        base = self.battle_stats[stat_name]
        stage = self.stat_modifiers[stat_name]
        multiplier = self.get_stage_multiplier(stage)
        return int(base * multiplier)

    def get_stage_multiplier(self, stage: int) -> float:
        if stage >= 0:
            return (2 + stage) / 2
        else:
            return 2 / (2 - stage)
        
    def get_acc_eva_multiplier(self, stage) -> float:
        if stage >= 0:
            return (3 + stage) / 3
        else:
            return 3 / (3 - stage)