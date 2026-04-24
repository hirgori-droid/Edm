from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Stats:
    level: int = 1
    experience: int = 0
    strength: int = 12
    agility: int = 12
    vitality: int = 12
    max_hp: int = 30
    hp: int = 30
    max_mana: int = 20
    mana: int = 20
    max_move: int = 100
    move: int = 100

    def restore_after_rest(self) -> None:
        self.hp = min(self.max_hp, self.hp + 8)
        self.mana = min(self.max_mana, self.mana + 8)
        self.move = min(self.max_move, self.move + 12)

    def tick_regeneration(self, resting: bool = False) -> None:
        hp_gain = 3 if resting else 1
        mana_gain = 3 if resting else 1
        move_gain = 5 if resting else 2
        self.hp = min(self.max_hp, self.hp + hp_gain)
        self.mana = min(self.max_mana, self.mana + mana_gain)
        self.move = min(self.max_move, self.move + move_gain)
