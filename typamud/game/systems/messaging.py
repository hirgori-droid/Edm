from __future__ import annotations

from typing import Iterable

from typamud.game.entities.character import Character

DIRECTION_LABELS = {
    "north": "север",
    "south": "юг",
    "east": "восток",
    "west": "запад",
    "up": "вверх",
    "down": "вниз",
}

SERVICE_LABELS = {
    "shop": "магазин",
    "bank": "банк",
    "inn": "гостиница",
    "trainer": "мастер гильдии",
}


def render_room(viewer: Character) -> str:
    room = viewer.room
    if room is None:
        return "Вы потерялись в пустоте."
    exits = ", ".join(DIRECTION_LABELS.get(direction, direction) for direction in sorted(room.exits.keys())) if room.exits else "нет"
    others = [char.name for char in room.other_characters(viewer) if char.alive]
    others_text = "Никого." if not others else "Здесь: " + ", ".join(others)
    items_text = "Ничего ценного не видно."
    if room.items:
        items_text = "На земле лежит: " + ", ".join(item.name for item in room.items)
    services_text = ""
    if room.services:
        services_text = "Услуги: " + ", ".join(SERVICE_LABELS.get(kind, kind) for kind in sorted(room.services)) + "\n"
    return f"\n[{room.area}] {room.title}\n{room.description}\n{services_text}Выходы: {exits}\n{items_text}\n{others_text}\n"


def broadcast(room_characters: Iterable[Character], message: str, exclude: Character | None = None) -> list[Character]:
    recipients = []
    for character in room_characters:
        if character is exclude or not character.is_player:
            continue
        recipients.append(character)
        character.channel_messages.append(message)
    return recipients
