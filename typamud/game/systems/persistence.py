from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from typamud.game.entities.player import Player
from typamud.game.entities.stats import Stats
from typamud.game.world.loader import World


class Persistence:
    REQUIRED_COLUMNS = {
        "name",
        "room_id",
        "rent_room_id",
        "race_name",
        "class_name",
        "gold",
        "bank_gold",
        "rubies",
        "skill_levels_json",
        "level",
        "experience",
        "strength",
        "agility",
        "vitality",
        "max_hp",
        "hp",
        "max_mana",
        "mana",
        "max_move",
        "move",
        "inventory_json",
        "equipment_json",
    }

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'players'"
            ).fetchone()
            if existing:
                columns = {row[1] for row in connection.execute("PRAGMA table_info(players)").fetchall()}
                if not self.REQUIRED_COLUMNS.issubset(columns):
                    connection.execute("DROP TABLE players")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    name TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    rent_room_id TEXT NOT NULL,
                    race_name TEXT NOT NULL,
                    class_name TEXT NOT NULL,
                    gold INTEGER NOT NULL,
                    bank_gold INTEGER NOT NULL,
                    rubies INTEGER NOT NULL,
                    skill_levels_json TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    experience INTEGER NOT NULL,
                    strength INTEGER NOT NULL,
                    agility INTEGER NOT NULL,
                    vitality INTEGER NOT NULL,
                    max_hp INTEGER NOT NULL,
                    hp INTEGER NOT NULL,
                    max_mana INTEGER NOT NULL,
                    mana INTEGER NOT NULL,
                    max_move INTEGER NOT NULL,
                    move INTEGER NOT NULL,
                    inventory_json TEXT NOT NULL,
                    equipment_json TEXT NOT NULL
                )
                """
            )

    def load_player(self, name: str, world: World) -> Player | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT name, room_id, rent_room_id, race_name, class_name, gold, bank_gold, rubies, skill_levels_json,
                       level, experience, strength, agility, vitality,
                       max_hp, hp, max_mana, mana, max_move, move, inventory_json, equipment_json
                FROM players WHERE name = ?
                """,
                (name,),
            ).fetchone()
        if not row:
            return None
        (
            _,
            room_id,
            rent_room_id,
            race_name,
            class_name,
            gold,
            bank_gold,
            rubies,
            skill_levels_json,
            level,
            experience,
            strength,
            agility,
            vitality,
            max_hp,
            hp,
            max_mana,
            mana,
            max_move,
            move,
            inventory_json,
            equipment_json,
        ) = row
        player = Player(
            name=name,
            race_name=race_name,
            class_name=class_name,
            gold=gold,
            bank_gold=bank_gold,
            rubies=rubies,
            skill_levels=json.loads(skill_levels_json),
            stats=Stats(
                level=level,
                experience=experience,
                strength=strength,
                agility=agility,
                vitality=vitality,
                max_hp=max_hp,
                hp=hp,
                max_mana=max_mana,
                mana=mana,
                max_move=max_move,
                move=move,
            ),
        )
        player.saved_room_id = room_id
        player.rent_room_id = rent_room_id
        for item_id in json.loads(inventory_json):
            player.inventory.append(world.create_item(item_id))
        for slot, item_id in json.loads(equipment_json).items():
            player.equipment[slot] = world.create_item(item_id)
        return player

    def save_player(self, player: Player) -> None:
        room_id = player.room.id if player.room else getattr(player, "saved_room_id", "square")
        inventory_json = json.dumps([item.id for item in player.inventory], ensure_ascii=False)
        equipment_json = json.dumps({slot: item.id for slot, item in player.equipment.items()}, ensure_ascii=False)
        skill_levels_json = json.dumps(player.skill_levels, ensure_ascii=False)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO players (
                    name, room_id, rent_room_id, race_name, class_name, gold, bank_gold, rubies, skill_levels_json,
                    level, experience, strength, agility, vitality,
                    max_hp, hp, max_mana, mana, max_move, move, inventory_json, equipment_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    room_id = excluded.room_id,
                    rent_room_id = excluded.rent_room_id,
                    race_name = excluded.race_name,
                    class_name = excluded.class_name,
                    gold = excluded.gold,
                    bank_gold = excluded.bank_gold,
                    rubies = excluded.rubies,
                    skill_levels_json = excluded.skill_levels_json,
                    level = excluded.level,
                    experience = excluded.experience,
                    strength = excluded.strength,
                    agility = excluded.agility,
                    vitality = excluded.vitality,
                    max_hp = excluded.max_hp,
                    hp = excluded.hp,
                    max_mana = excluded.max_mana,
                    mana = excluded.mana,
                    max_move = excluded.max_move,
                    move = excluded.move,
                    inventory_json = excluded.inventory_json,
                    equipment_json = excluded.equipment_json
                """,
                (
                    player.name,
                    room_id,
                    player.rent_room_id,
                    player.race_name,
                    player.class_name,
                    player.gold,
                    player.bank_gold,
                    player.rubies,
                    skill_levels_json,
                    player.stats.level,
                    player.stats.experience,
                    player.stats.strength,
                    player.stats.agility,
                    player.stats.vitality,
                    player.stats.max_hp,
                    player.stats.hp,
                    player.stats.max_mana,
                    player.stats.mana,
                    player.stats.max_move,
                    player.stats.move,
                    inventory_json,
                    equipment_json,
                ),
            )
