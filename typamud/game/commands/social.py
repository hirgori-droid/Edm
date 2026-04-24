from __future__ import annotations

from typamud.game.systems.messaging import broadcast


def say(session: "GameSession", args: list[str]) -> str:
    if not args:
        return "Сказать что?"
    phrase = " ".join(args)
    player = session.player
    room = player.room
    if room is None:
        return "Вас никто не слышит."
    broadcast(room.characters, f"{player.name} говорит: {phrase}", exclude=player)
    return f"Вы говорите: {phrase}"
