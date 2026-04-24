from __future__ import annotations

from dataclasses import dataclass, field

from typamud.game.entities.character import Character


@dataclass(slots=True)
class Player(Character):
    is_player: bool = True
    prompt_enabled: bool = True
    channel_messages: list[str] = field(default_factory=list)
    saved_room_id: str = "square"
    rent_room_id: str = "square"
    race_name: str = "человек"
    class_name: str = "воин"
    bank_gold: int = 0
    rubies: int = 0
    skill_levels: dict[str, int] = field(default_factory=dict)
