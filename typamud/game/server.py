from __future__ import annotations

import asyncio
import contextlib

from typamud.config import settings
from typamud.game.entities.npc import NPC
from typamud.game.session import GameSession
from typamud.game.systems.combat import CombatEngine
from typamud.game.world.loader import WorldLoader


class GameServer:
    def __init__(self) -> None:
        self.settings = settings
        self.world = WorldLoader.load(self.settings.world_path)
        from typamud.game.systems.persistence import Persistence

        self.persistence = Persistence(self.settings.db_path)
        self.sessions: list[GameSession] = []
        self.combat = CombatEngine()
        self.server: asyncio.AbstractServer | None = None
        self.tick_task: asyncio.Task | None = None

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        session = GameSession(self, reader, writer, self.world, self.persistence)
        self.sessions.append(session)
        try:
            await session.run()
        finally:
            if session in self.sessions:
                self.sessions.remove(session)

    async def run_tick_loop(self) -> None:
        while True:
            await asyncio.sleep(self.settings.tick_interval)
            await self.process_world_tick()

    async def process_world_tick(self) -> None:
        self.process_regeneration_tick()
        self.process_aggression_tick()
        await self.process_combat_tick()

    def process_regeneration_tick(self) -> None:
        for room in self.world.rooms.values():
            for character in room.characters:
                expired = character.tick_temporary_states()
                if character.is_player:
                    for effect_name in expired:
                        character.channel_messages.append(f"Эффект {effect_name} спадает.")
                if character.alive and not character.fighting:
                    character.stats.tick_regeneration(resting=character.resting)

    def process_aggression_tick(self) -> None:
        for room in self.world.rooms.values():
            players = [character for character in room.characters if character.is_player and character.alive]
            if not players:
                continue
            for npc in [character for character in room.characters if isinstance(character, NPC)]:
                if not npc.alive or npc.fighting or not npc.aggressive:
                    continue
                target = next((player for player in players if not player.fighting), players[0])
                npc.engage(target)
                if not target.fighting:
                    target.engage(npc)
                target.channel_messages.append(f"{npc.name} бросается на вас без предупреждения!")

    async def process_combat_tick(self) -> None:
        participants = [
            character
            for room in self.world.rooms.values()
            for character in room.characters
            if character.fighting and character.target is not None and character.alive
        ]
        for attacker in participants:
            rounds = attacker.attacks_per_round if isinstance(attacker, NPC) else 1
            for _ in range(rounds):
                defender = attacker.target
                if defender is None or not defender.alive or attacker.room is None or defender.room is None or attacker.room != defender.room:
                    attacker.disengage()
                    break
                messages, died = self.combat.resolve_attack(attacker, defender)
                await self._dispatch_combat_messages(attacker, messages)
                if died:
                    await self._handle_death(attacker, defender)
                    break

    async def _dispatch_combat_messages(self, attacker, messages: list[str]) -> None:
        if attacker.room is None:
            return
        recipients = [character for character in attacker.room.characters if character.is_player]
        for message in messages:
            for player in recipients:
                player.channel_messages.append(message)

    async def _handle_death(self, attacker, defender) -> None:
        if defender.room is None:
            return
        room = defender.room
        room.remove_character(defender)
        if defender.is_player:
            recall_room = self.world.get_room(self.world.recall_room_id)
            defender.alive = True
            defender.stats.hp = max(1, defender.stats.max_hp // 2)
            defender.stats.mana = max(1, defender.stats.max_mana // 2)
            defender.resting = False
            defender.disengage()
            recall_room.add_character(defender)
            defender.saved_room_id = recall_room.id
            defender.channel_messages.append("Вы пали в бою и приходите в себя в безопасном месте.")
            self.persistence.save_player(defender)
            if attacker.alive:
                attacker.disengage()
            return
        if isinstance(defender, NPC):
            for item in defender.inventory:
                room.items.append(item)
            for item in defender.equipment.values():
                room.items.append(item)
            replacement = NPC.from_dict(defender.prototype, self.world.create_item)
            self.world.get_room(defender.respawn_room_id).add_character(replacement)
        attacker.disengage()

    async def start(self) -> None:
        self.server = await asyncio.start_server(self.handle_client, self.settings.host, self.settings.port)
        self.tick_task = asyncio.create_task(self.run_tick_loop())
        async with self.server:
            await self.server.serve_forever()

    async def stop(self) -> None:
        if self.tick_task:
            self.tick_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.tick_task
        if self.server:
            self.server.close()
            await self.server.wait_closed()
