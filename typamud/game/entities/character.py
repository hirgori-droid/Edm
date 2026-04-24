from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from typamud.game.entities.stats import Stats

if TYPE_CHECKING:
    from typamud.game.world.room import Room
    from typamud.game.world.item import Item


@dataclass(slots=True)
class Character:
    name: str
    room: Room | None = None
    stats: Stats = field(default_factory=Stats)
    inventory: list[Item] = field(default_factory=list)
    equipment: dict[str, Item] = field(default_factory=dict)
    target: Character | None = None
    fighting: bool = False
    is_player: bool = False
    alive: bool = True
    resting: bool = False
    gold: int = 0
    effects: dict[str, dict[str, int]] = field(default_factory=dict)
    cooldowns: dict[str, int] = field(default_factory=dict)

    def equipment_bonus(self, attribute: str) -> int:
        return sum(getattr(item, attribute) for item in self.equipment.values())

    def effect_modifier(self, attribute: str) -> int:
        return sum(payload.get(attribute, 0) for payload in self.effects.values())

    @property
    def total_strength(self) -> int:
        return self.stats.strength + self.equipment_bonus("strength") + self.effect_modifier("strength")

    @property
    def total_agility(self) -> int:
        return self.stats.agility + self.equipment_bonus("agility") + self.effect_modifier("agility")

    @property
    def total_vitality(self) -> int:
        return self.stats.vitality + self.equipment_bonus("vitality") + self.effect_modifier("vitality")

    @property
    def armor_rating(self) -> int:
        return self.total_vitality // 3 + sum(item.armor for item in self.equipment.values()) + self.effect_modifier("armor")

    @property
    def wielded_weapon(self) -> Item | None:
        return self.equipment.get("weapon")

    def short_status(self) -> str:
        return (
            f"{self.name}: HP {self.stats.hp}/{self.stats.max_hp}, "
            f"MN {self.stats.mana}/{self.stats.max_mana}, MV {self.stats.move}/{self.stats.max_move}, "
            f"ур. {self.stats.level}, золото {self.gold}"
        )

    def engage(self, target: Character) -> None:
        self.target = target
        self.fighting = True
        self.resting = False

    def disengage(self) -> None:
        self.target = None
        self.fighting = False

    def receive_damage(self, amount: int) -> bool:
        self.resting = False
        self.stats.hp = max(0, self.stats.hp - amount)
        if self.stats.hp == 0:
            self.alive = False
            self.disengage()
            return True
        return False

    def add_item(self, item: Item) -> None:
        self.inventory.append(item)

    def remove_item(self, item: Item) -> None:
        if item in self.inventory:
            self.inventory.remove(item)

    def find_inventory_item(self, needle: str) -> Item | None:
        for item in self.inventory:
            if item.matches(needle):
                return item
        return None

    def equipped_in_slot(self, slot: str) -> Item | None:
        return self.equipment.get(slot)

    def wear(self, item: Item) -> Item | None:
        if item.slot is None:
            raise ValueError("Этот предмет нельзя экипировать.")
        previous = self.equipment.get(item.slot)
        self.equipment[item.slot] = item
        if item in self.inventory:
            self.inventory.remove(item)
        return previous

    def remove_equipment(self, slot: str) -> Item | None:
        item = self.equipment.pop(slot, None)
        if item is not None:
            self.inventory.append(item)
        return item

    def set_cooldown(self, ability_name: str, ticks: int) -> None:
        self.cooldowns[ability_name] = ticks

    def has_cooldown(self, ability_name: str) -> bool:
        return self.cooldowns.get(ability_name, 0) > 0

    def add_effect(self, effect_name: str, duration: int, **modifiers: int) -> None:
        self.effects[effect_name] = {"duration": duration, **modifiers}

    def has_effect(self, effect_name: str) -> bool:
        return effect_name in self.effects

    def tick_temporary_states(self) -> list[str]:
        expired: list[str] = []
        for ability_name in list(self.cooldowns):
            self.cooldowns[ability_name] -= 1
            if self.cooldowns[ability_name] <= 0:
                del self.cooldowns[ability_name]
        for effect_name in list(self.effects):
            self.effects[effect_name]["duration"] -= 1
            if self.effects[effect_name]["duration"] <= 0:
                del self.effects[effect_name]
                expired.append(effect_name)
        return expired
