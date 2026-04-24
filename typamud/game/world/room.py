from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typamud.game.entities.character import Character
    from typamud.game.world.item import Item


@dataclass(slots=True)
class Room:
    id: str
    title: str
    description: str
    exits: dict[str, str] = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    area: str = "Безымянная область"
    sector: str = "inside"
    services: dict[str, str] = field(default_factory=dict)

    def add_character(self, character: Character) -> None:
        if character not in self.characters:
            self.characters.append(character)
            character.room = self

    def remove_character(self, character: Character) -> None:
        if character in self.characters:
            self.characters.remove(character)
            character.room = None

    def other_characters(self, current: Character) -> list[Character]:
        return [character for character in self.characters if character is not current]

    def find_item(self, needle: str) -> Item | None:
        for item in self.items:
            if item.matches(needle):
                return item
        return None
