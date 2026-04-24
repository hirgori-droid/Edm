from __future__ import annotations

from typamud.game.systems.combat import CombatEngine
from typamud.game.systems.messaging import render_room


SLOT_LABELS = {
    "weapon": "оружие",
    "body": "тело",
    "head": "голова",
}


def score(session: "GameSession", args: list[str]) -> str:
    player = session.player
    return (
        f"{player.short_status()}\n"
        f"Раса: {player.race_name}, класс: {player.class_name}\n"
        f"Сила {player.total_strength}, Ловкость {player.total_agility}, Телосложение {player.total_vitality}, Броня {player.armor_rating}\n"
        f"Банк: {player.bank_gold}, рубины: {player.rubies}\n"
        f"До следующего уровня: {CombatEngine.experience_to_next_level(player.stats.level) - player.stats.experience} опыта"
    )


def who(session: "GameSession", args: list[str]) -> str:
    names = sorted(active.player.name for active in session.server.sessions if active.player is not None)
    return "Сейчас в игре: " + ", ".join(names)


def look(session: "GameSession", args: list[str]) -> str:
    if not args:
        return render_room(session.player)
    needle = " ".join(args)
    room = session.player.room
    if room is None:
        return "Вы ничего не видите."
    for character in room.characters:
        if character is session.player:
            continue
        if needle.lower() in character.name.lower():
            return f"{character.name}: HP {character.stats.hp}/{character.stats.max_hp}, выглядит {'опасно' if character.fighting else 'спокойно'}."
    item = room.find_item(needle) or session.player.find_inventory_item(needle)
    if item:
        return item.description
    return "Ничего подходящего не найдено."


def rest(session: "GameSession", args: list[str]) -> str:
    if session.player.fighting:
        return "Не до отдыха — идет бой!"
    session.player.resting = True
    session.player.stats.restore_after_rest()
    session.persistence.save_player(session.player)
    return "Вы садитесь перевести дух и чувствуете, как силы понемногу возвращаются."


def stand(session: "GameSession", args: list[str]) -> str:
    if not session.player.resting:
        return "Вы и так стоите на ногах."
    session.player.resting = False
    return "Вы встаете и снова готовы к дороге."


def inventory(session: "GameSession", args: list[str]) -> str:
    player = session.player
    if not player.inventory:
        return f"Инвентарь пуст. Золото: {player.gold}, рубины: {player.rubies}."
    return "У вас при себе:\n" + "\n".join(f"- {item.name}" for item in player.inventory) + f"\nЗолото: {player.gold}, рубины: {player.rubies}"


def equipment(session: "GameSession", args: list[str]) -> str:
    player = session.player
    if not player.equipment:
        return "На вас ничего не надето."
    return "Экипировка:\n" + "\n".join(
        f"- {SLOT_LABELS.get(slot, slot)}: {item.name}" for slot, item in sorted(player.equipment.items())
    )


def help_text(session: "GameSession", args: list[str]) -> str:
    return (
        "Команды: помощь, осмотреться/look, счет, кто, отдых, встать, инвентарь, экипировка, "
        "взять, бросить, надеть, снять, магазин, купить, продать, учитель, учить, баланс, вклад, снятьденьги, снятькомнату, "
        "умения, bash, rage, fortify, smite, heal, holywrath, sacredshield, darkbolt, souldrain, deathpact, "
        "blindness, curse, exorcism, zealpurge, fireburst, fireball, flamestorm, greaterheal, salvation, iceshard, "
        "icestrike, tidalwave, tsunami, stonefist, stoneskin, earthshatter, mountainguard, airburst, lightning, "
        "thunderstorm, restoreenergy, spiritlink, stormtotem, shadowflame, abyssbolt, backstab, trip, bless, "
        "север/n, юг/s, восток/e, запад/w, вверх/u, вниз/d, сказать, убить, сбежать, выход"
    )
