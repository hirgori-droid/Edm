from __future__ import annotations

import random
from dataclasses import dataclass, field

from typamud.game.entities.character import Character
from typamud.game.entities.stats import Stats
from typamud.game.world.item import Item


@dataclass(slots=True)
class NPC(Character):
    respawn_room_id: str = ""
    experience_reward: int = 25
    gold_reward: int = 0
    aggressive: bool = False
    attacks_per_round: int = 1
    prototype: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict, item_factory: callable | None = None) -> "NPC":
        stats = Stats(
            level=payload.get("level", 1),
            strength=payload.get("strength", 10),
            agility=payload.get("agility", 10),
            vitality=payload.get("vitality", 10),
            max_hp=payload.get("max_hp", 20),
            hp=payload.get("max_hp", 20),
            max_mana=payload.get("max_mana", 0),
            mana=payload.get("max_mana", 0),
            max_move=payload.get("max_move", 100),
            move=payload.get("max_move", 100),
        )
        inventory: list[Item] = []
        if item_factory is not None:
            inventory = [item_factory(item_id) for item_id in payload.get("inventory", [])]
            for loot_entry in payload.get("loot_table", []):
                if random.randint(1, 100) <= loot_entry.get("chance", 100):
                    inventory.append(item_factory(loot_entry["item"]))
        npc = cls(
            name=payload["name"],
            stats=stats,
            inventory=inventory,
            gold=payload.get("gold", 0),
            respawn_room_id=payload["room"],
            experience_reward=payload.get("experience_reward", 25),
            gold_reward=payload.get("gold_reward", payload.get("gold", 0)),
            aggressive=payload.get("aggressive", False),
            attacks_per_round=max(1, payload.get("attacks_per_round", 1)),
            prototype=dict(payload),
        )
        for item_id in payload.get("equipment", []):
            if item_factory is None:
                continue
            item = item_factory(item_id)
            if item.slot:
                npc.equipment[item.slot] = item
        return npc
