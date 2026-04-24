from __future__ import annotations

from typamud.game.systems.messaging import render_room


def move(session: "GameSession", args: list[str], direction: str) -> str:
    player = session.player
    room = player.room
    if room is None:
        return "Некуда идти."
    if player.fighting:
        return "Вы заняты боем и не можете уйти просто так. Попробуйте: сбежать"
    destination_id = room.exits.get(direction)
    if not destination_id:
        return "Туда нет выхода."
    if player.stats.move < 3:
        return "Вы слишком устали для перехода. Попробуйте отдохнуть."
    player.stats.move = max(0, player.stats.move - 3)
    player.resting = False
    room.remove_character(player)
    session.world.get_room(destination_id).add_character(player)
    player.saved_room_id = destination_id
    session.persistence.save_player(player)
    return render_room(player)
