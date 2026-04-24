from __future__ import annotations

import json
from pathlib import Path

from typamud.game.entities.npc import NPC
from typamud.game.world.item import Item
from typamud.game.world.room import Room


class World:
    def __init__(
        self,
        rooms: dict[str, Room],
        mobs: list[NPC],
        item_prototypes: dict[str, Item],
        shops: dict[str, list[str]],
        start_room_id: str,
        recall_room_id: str,
    ):
        self.rooms = rooms
        self.mobs = mobs
        self.item_prototypes = item_prototypes
        self.shops = shops
        self.start_room_id = start_room_id
        self.recall_room_id = recall_room_id

    def get_room(self, room_id: str) -> Room:
        return self.rooms[room_id]

    def create_item(self, item_id: str) -> Item:
        return self.item_prototypes[item_id].clone()

    def shop_items(self, shop_id: str) -> list[Item]:
        return [self.create_item(item_id) for item_id in self.shops.get(shop_id, [])]


class WorldLoader:
    VALID_DIRECTIONS = {"north", "south", "east", "west", "up", "down"}

    @classmethod
    def _validate_rooms(cls, rooms: dict[str, Room]) -> None:
        for room_id, room in rooms.items():
            for direction, target_room_id in room.exits.items():
                if direction not in cls.VALID_DIRECTIONS:
                    raise ValueError(f"Комната {room_id} использует неподдерживаемое направление: {direction}")
                if target_room_id not in rooms:
                    raise ValueError(f"Комната {room_id} ведет в неизвестную комнату: {target_room_id}")

    @staticmethod
    def load(path: Path) -> World:
        payload = json.loads(path.read_text(encoding="utf-8"))
        item_prototypes = {
            item_id: Item.from_dict(item_id, item_payload) for item_id, item_payload in payload.get("items", {}).items()
        }
        rooms = {
            room_id: Room(
                id=room_id,
                title=room_payload["title"],
                description=room_payload["description"],
                exits=room_payload.get("exits", {}),
                area=room_payload.get("area", "Безымянная область"),
                sector=room_payload.get("sector", "inside"),
                services=room_payload.get("services", {}),
                items=[item_prototypes[item_id].clone() for item_id in room_payload.get("items", [])],
            )
            for room_id, room_payload in payload["rooms"].items()
        }
        WorldLoader._validate_rooms(rooms)
        shops = payload.get("shops", {})
        mobs: list[NPC] = []
        for mob_payload in payload.get("mobs", []):
            npc = NPC.from_dict(mob_payload, lambda item_id: item_prototypes[item_id].clone())
            rooms[npc.respawn_room_id].add_character(npc)
            mobs.append(npc)
        return World(
            rooms=rooms,
            mobs=mobs,
            item_prototypes=item_prototypes,
            shops=shops,
            start_room_id=payload.get("start_room", "square"),
            recall_room_id=payload.get("recall_room", payload.get("start_room", "square")),
        )
