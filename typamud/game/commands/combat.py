from __future__ import annotations

import random

from typamud.game.data.catalog import render_abilities_for_class


def _find_target(session: "GameSession", args: list[str]):
    player = session.player
    room = player.room
    if room is None:
        return None
    if args:
        needle = " ".join(args).lower()
        for character in room.characters:
            if character is player or not character.alive:
                continue
            if needle in character.name.lower():
                return character
        return None
    return player.target


def kill(session: "GameSession", args: list[str]) -> str:
    if not args:
        return "Убить кого?"
    target = _find_target(session, args)
    if target is None:
        return "Такой цели здесь нет."
    if target.is_player:
        return "PvP отключен: атаковать других игроков нельзя."
    player = session.player
    player.engage(target)
    if not target.fighting:
        target.engage(player)
    return f"Вы вступаете в бой с {target.name}!"


def flee(session: "GameSession", args: list[str]) -> str:
    player = session.player
    if not player.fighting or player.room is None:
        return "Вы и так не в бою."
    exits = list(player.room.exits.items())
    if not exits:
        return "Некуда бежать!"
    flee_chance = 45 + player.total_agility
    if random.randint(1, 100) > flee_chance:
        return "Вы заметались, но противник не дает вырваться из боя."
    direction, room_id = random.choice(exits)
    if player.target is not None:
        player.target.disengage()
    player.disengage()
    player.room.remove_character(player)
    session.world.get_room(room_id).add_character(player)
    player.saved_room_id = room_id
    session.persistence.save_player(player)
    return f"Вы в панике сбегаете на {direction}."


def abilities(session: "GameSession", args: list[str]) -> str:
    return render_abilities_for_class(session.player.class_name, session.player.skill_levels)


def use_ability(session: "GameSession", args: list[str], ability_id: str) -> str:
    player = session.player
    target = _find_target(session, args)
    if target is not None and target.is_player and target is not player:
        return "PvP отключен: умения по другим игрокам недоступны."
    messages, _ = session.server.combat.perform_ability(player, target, ability_id)
    if player.room is not None:
        for message in messages[1:]:
            for character in player.room.characters:
                if character.is_player and character is not player:
                    character.channel_messages.append(message)
    session.persistence.save_player(player)
    return "\n".join(messages)
