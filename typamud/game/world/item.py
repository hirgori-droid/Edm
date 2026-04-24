from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Item:
    id: str
    name: str
    description: str
    keywords: list[str] = field(default_factory=list)
    slot: str | None = None
    weapon_type: str | None = None
    damage_min: int = 0
    damage_max: int = 0
    armor: int = 0
    strength: int = 0
    agility: int = 0
    vitality: int = 0
    value: int = 0
    teaches_skill: str | None = None

    @classmethod
    def from_dict(cls, item_id: str, payload: dict) -> "Item":
        return cls(
            id=item_id,
            name=payload["name"],
            description=payload["description"],
            keywords=payload.get("keywords", []),
            slot=payload.get("slot"),
            weapon_type=payload.get("weapon_type"),
            damage_min=payload.get("damage_min", 0),
            damage_max=payload.get("damage_max", 0),
            armor=payload.get("armor", 0),
            strength=payload.get("strength", 0),
            agility=payload.get("agility", 0),
            vitality=payload.get("vitality", 0),
            value=payload.get("value", 0),
            teaches_skill=payload.get("teaches_skill"),
        )

    def clone(self) -> "Item":
        return Item(
            id=self.id,
            name=self.name,
            description=self.description,
            keywords=list(self.keywords),
            slot=self.slot,
            weapon_type=self.weapon_type,
            damage_min=self.damage_min,
            damage_max=self.damage_max,
            armor=self.armor,
            strength=self.strength,
            agility=self.agility,
            vitality=self.vitality,
            value=self.value,
            teaches_skill=self.teaches_skill,
        )

    def matches(self, needle: str) -> bool:
        lowered = needle.lower()
        return lowered == self.id.lower() or lowered in self.name.lower() or lowered in [keyword.lower() for keyword in self.keywords]
