from __future__ import annotations

import json
import tempfile
import asyncio
from pathlib import Path
from types import SimpleNamespace

from typamud.game.data.catalog import ABILITY_BY_ID, CLASS_BY_INDEX, CLASS_BY_NAME, DRUID_ALL_SPELL_IDS, DRUID_SPELL_CIRCLE_SIZES, DRUID_SPELL_CIRCLES, RACE_BY_INDEX, class_abilities
from typamud.game.commands.combat import kill, use_ability
from typamud.game.entities.player import Player
from typamud.game.server import GameServer
from typamud.game.session import GameSession
from typamud.game.systems.combat import CombatEngine
from typamud.game.systems.persistence import Persistence
from typamud.game.world.loader import WorldLoader


def test_world_loads_default_data() -> None:
    world = WorldLoader.load(Path("data/world.json"))
    payload = json.loads(Path("data/world.json").read_text(encoding="utf-8"))

    assert world.start_room_id == "square"
    assert world.recall_room_id == "temple"
    assert set(world.rooms) == set(payload["rooms"])
    assert any("крыса" in mob.name for mob in world.mobs)
    assert "training_sword" in world.item_prototypes
    assert world.item_prototypes["book_fireball"].teaches_skill == "fireball"
    assert world.get_room("sewer_tunnel").items[0].name == "крысиный клык"
    assert world.get_room("weapon_shop_room").services["shop"] == "weapon_shop"
    assert len(world.shop_items("ruby_shop")) == 1
    assert world.get_room("guild_fire_mage").services["trainer"] == "маг огня"


def test_longred_layout_uses_explicit_room_connections() -> None:
    world = WorldLoader.load(Path("data/world.json"))

    assert world.get_room("square").exits == {
        "north": "guild_square",
        "east": "market_lane",
        "south": "temple_courtyard",
        "west": "west_lane",
    }
    assert world.get_room("market_lane").exits["north"] == "library_entry"
    assert world.get_room("west_lane").exits["west"] == "park_gate"
    assert world.get_room("temple_courtyard").exits["down"] == "sewer_entry"
    assert world.get_room("tavern_entry").exits["up"] == "tavern_room"
    assert world.get_room("guild_shield_warrior").exits == {"west": "hall_martial"}
    assert world.get_room("guild_black_knight").exits == {"west": "hall_shadow"}


def test_park_zone_contains_progression_mobs_and_boss_loot() -> None:
    world = WorldLoader.load(Path("data/world.json"))

    park_mobs = [mob for mob in world.mobs if mob.room and mob.room.area == "Парк Лонгреда"]
    boss = next(mob for mob in park_mobs if mob.name == "бешеный пес")

    assert {mob.stats.level for mob in park_mobs} == {1, 2, 3, 4, 5, 7}
    assert boss.aggressive is True
    assert boss.room.id == "dog_pit"
    assert {entry["item"] for entry in boss.prototype["loot_table"]} == {
        "book_blindness",
        "book_fire_burst",
        "book_ice_strike",
        "book_stone_fist",
        "book_air_burst",
        "book_restore_energy",
    }


def test_sewer_zone_contains_requested_mobs_boss_loot_and_weapon_types() -> None:
    world = WorldLoader.load(Path("data/world.json"))

    sewer_mobs = [mob for mob in world.mobs if mob.room and mob.room.area == "Канализация Лонгреда"]
    rat_king = next(mob for mob in sewer_mobs if mob.name == "крысиный король")

    assert {mob.stats.level for mob in sewer_mobs} == {5, 6, 8, 10}
    assert sum(1 for mob in sewer_mobs if mob.name == "бешенная крыса" and mob.aggressive) == 2
    assert rat_king.attacks_per_round == 4
    assert {entry["item"] for entry in rat_king.prototype["loot_table"]} >= {
        "book_holy_wrath",
        "book_soul_drain",
        "book_exorcism",
        "book_greater_heal",
        "book_spirit_link",
        "book_shadow_flame",
        "book_fireball",
        "book_tidal_wave",
        "book_earth_shatter",
        "book_lightning",
        "rat_king_blade",
        "rat_king_axe",
        "rat_king_mace",
        "rat_king_shiv",
        "rat_king_polearm",
    }
    assert {
        world.item_prototypes["rat_king_blade"].weapon_type,
        world.item_prototypes["rat_king_axe"].weapon_type,
        world.item_prototypes["rat_king_mace"].weapon_type,
        world.item_prototypes["rat_king_shiv"].weapon_type,
        world.item_prototypes["rat_king_polearm"].weapon_type,
    } == {"клинки", "топоры", "булавы и молоты", "короткие клинки", "копья и шесты"}


def test_library_zone_contains_requested_mobs_and_boss_circle_four_books() -> None:
    world = WorldLoader.load(Path("data/world.json"))

    library_mobs = [mob for mob in world.mobs if mob.room and mob.room.area == "Библиотека Лонгреда"]
    boss = next(mob for mob in library_mobs if mob.name == "главный библиотекарь")

    assert len(library_mobs) == 10
    assert sum(1 for mob in library_mobs if mob.name == "задумчивый читатель" and mob.stats.level == 10) == 3
    assert sum(1 for mob in library_mobs if mob.name == "любопытная читательница" and mob.stats.level == 12) == 3
    assert sum(1 for mob in library_mobs if mob.name == "серьезный читатель" and mob.stats.level == 13) == 3
    assert boss.stats.level == 15
    assert {entry["item"] for entry in boss.prototype["loot_table"]} == {
        "book_sacred_shield",
        "book_death_pact",
        "book_zeal_purge",
        "book_salvation",
        "book_storm_totem",
        "book_abyss_bolt",
        "book_flame_storm",
        "book_tsunami",
        "book_mountain_guard",
        "book_thunderstorm",
    }


def test_rat_king_hits_four_times_per_world_tick() -> None:
    server = GameServer()
    boss = next(mob for mob in server.world.mobs if mob.name == "крысиный король")
    room = server.world.get_room("sewer_boss")
    player = Player(name="Танк")
    room.add_character(player)
    boss.engage(player)
    player.engage(boss)
    server.combat.hit_roll = lambda attacker, defender: True
    server.combat.damage_roll = lambda attacker, defender: 1

    asyncio.run(server.process_combat_tick())

    hit_messages = [message for message in player.channel_messages if "крысиный король бьет" in message]
    assert len(hit_messages) == 4


def test_pvp_is_disabled_for_attack_and_abilities() -> None:
    world = WorldLoader.load(Path("data/world.json"))
    with tempfile.TemporaryDirectory() as temp_dir:
        persistence = Persistence(Path(temp_dir) / "players.db")
        session = GameSession(SimpleNamespace(combat=CombatEngine(), server=None), None, None, world, persistence)
        attacker = Player(name="Игрок1")
        attacker.class_name = "шаман"
        attacker.skill_levels = {"heal": 100}
        defender = Player(name="Игрок2")
        room = world.get_room("square")
        room.add_character(attacker)
        room.add_character(defender)
        session.player = attacker
        session.server = SimpleNamespace(combat=CombatEngine())

        assert kill(session, ["Игрок2"]) == "PvP отключен: атаковать других игроков нельзя."
        assert use_ability(session, ["Игрок2"], "heal") == "PvP отключен: умения по другим игрокам недоступны."


def test_persistence_roundtrip_with_inventory_equipment_and_economy() -> None:
    world = WorldLoader.load(Path("data/world.json"))
    with tempfile.TemporaryDirectory() as temp_dir:
        db_path = Path(temp_dir) / "players.db"
        persistence = Persistence(db_path)
        player = Player(name="Тестер", gold=42, bank_gold=90, rubies=5)
        player.saved_room_id = "temple"
        player.rent_room_id = "inn_room"
        player.race_name = "человек"
        player.class_name = "берсерк"
        player.skill_levels = {"bash": 67, "rage": 51}
        player.stats.hp = 17
        player.inventory.append(world.create_item("rat_fang"))
        sword = world.create_item("training_sword")
        player.equipment["weapon"] = sword
        persistence.save_player(player)

        loaded = persistence.load_player("Тестер", world)
        assert loaded is not None
        assert loaded.name == "Тестер"
        assert loaded.saved_room_id == "temple"
        assert loaded.rent_room_id == "inn_room"
        assert loaded.stats.hp == 17
        assert loaded.gold == 42
        assert loaded.bank_gold == 90
        assert loaded.rubies == 5
        assert loaded.skill_levels["bash"] == 67
        assert loaded.inventory[0].id == "rat_fang"
        assert loaded.equipment["weapon"].id == "training_sword"


def test_combat_engine_levels_up_character() -> None:
    player = Player(name="Герой")
    player.class_name = "берсерк"
    player.stats.experience = CombatEngine.experience_to_next_level(1)
    messages = CombatEngine().maybe_level_up(player)
    assert any("новый уровень" in message for message in messages)
    assert player.stats.level == 2
    assert player.stats.hp == player.stats.max_hp


def test_race_class_and_ability_catalogs_contain_requested_options() -> None:
    race_names = {template.name for template in RACE_BY_INDEX.values()}
    class_names = {template.name for template in CLASS_BY_INDEX.values()}
    ability_names = set(ABILITY_BY_ID)
    assert race_names == {"лесные эльфы", "высшие эльфы", "полуэльфы", "горные дварфы", "глубинные дварфы", "человек", "орк", "гоблин", "великан", "полуорк"}
    assert class_names == {"берсерк", "воин щита", "авангард", "защитник", "паладин", "черный рыцарь", "инквизитор", "лекарь", "шаман", "варлок", "маг огня", "маг воды", "маг земли", "маг воздуха", "разбойник", "ассасин"}
    assert {template.name for template in CLASS_BY_INDEX.values() if template.group == "воины без магии"} == {"берсерк", "воин щита", "авангард", "защитник"}
    assert {template.name for template in CLASS_BY_INDEX.values() if template.group == "воины с магией"} == {"паладин", "черный рыцарь"}
    assert {template.name for template in CLASS_BY_INDEX.values() if template.group == "священники"} == {"инквизитор", "лекарь", "шаман"}
    assert {template.name for template in CLASS_BY_INDEX.values() if template.group == "маги"} == {"варлок", "маг огня", "маг воды", "маг земли", "маг воздуха"}
    assert {template.name for template in CLASS_BY_INDEX.values() if template.group == "разведчики"} == {"разбойник", "ассасин"}
    assert "Башер" in CLASS_BY_NAME["воин щита"].description
    assert "Атакующий воин" in CLASS_BY_NAME["авангард"].description
    assert "Танк" in CLASS_BY_NAME["защитник"].description
    assert {"bash", "rage", "fortify", "smite", "heal", "holy_wrath", "sacred_shield", "dark_bolt", "soul_drain", "death_pact", "blindness", "curse", "exorcism", "zeal_purge", "fire_burst", "fireball", "flame_storm", "greater_heal", "salvation", "ice_shard", "ice_strike", "tidal_wave", "tsunami", "stone_fist", "stone_skin", "earth_shatter", "mountain_guard", "air_burst", "lightning", "thunderstorm", "restore_energy", "spirit_link", "storm_totem", "shadow_flame", "abyss_bolt", "backstab", "trip", "bless"}.issubset(ability_names)


def test_druid_spell_proposal_has_nine_circles_and_requested_sizes() -> None:
    assert set(DRUID_SPELL_CIRCLES) == {1, 2, 3, 4, 5, 6, 7, 8, 9}
    assert DRUID_SPELL_CIRCLE_SIZES[1] == 6
    assert DRUID_SPELL_CIRCLE_SIZES[2] == 6
    assert DRUID_SPELL_CIRCLE_SIZES[3] == 6
    assert DRUID_SPELL_CIRCLE_SIZES[4] == 6
    assert DRUID_SPELL_CIRCLE_SIZES[5] == 5
    assert DRUID_SPELL_CIRCLE_SIZES[6] == 5
    assert DRUID_SPELL_CIRCLE_SIZES[7] == 4
    assert DRUID_SPELL_CIRCLE_SIZES[8] == 3
    assert DRUID_SPELL_CIRCLE_SIZES[9] == 2
    existing_ids = {spell_id for circle_spells in DRUID_SPELL_CIRCLES.values() for spell_id, _, is_existing in circle_spells if is_existing}
    assert {"heal", "curse", "ice_shard", "restore_energy", "spirit_link", "storm_totem"}.issubset(existing_ids)
    assert set(DRUID_ALL_SPELL_IDS).issubset(ABILITY_BY_ID)
    assert class_abilities("шаман") == DRUID_ALL_SPELL_IDS


def test_combat_ability_applies_damage_and_cooldown() -> None:
    engine = CombatEngine()
    attacker = Player(name="Воин")
    attacker.class_name = "берсерк"
    attacker.skill_levels = {"bash": 100}
    defender = Player(name="Цель")
    messages, died = engine.perform_ability(attacker, defender, "bash")
    assert not died
    assert any("bash" in message for message in messages)
    assert defender.stats.hp < defender.stats.max_hp
    assert attacker.has_cooldown("bash")


def test_support_ability_heals_player() -> None:
    engine = CombatEngine()
    player = Player(name="Лекарь")
    player.class_name = "лекарь"
    player.skill_levels = {"heal": 100}
    player.stats.hp = 10
    messages, died = engine.perform_ability(player, None, "heal")
    assert not died
    assert any("восстанавливает" in message for message in messages)
    assert player.stats.hp > 10


def test_restore_energy_recovers_mana_and_move() -> None:
    engine = CombatEngine()
    player = Player(name="Шаман")
    player.class_name = "шаман"
    player.skill_levels = {"restore_energy": 100}
    player.stats.mana = 10
    player.stats.move = 20
    messages, died = engine.perform_ability(player, None, "restore_energy")
    assert not died
    assert any("восстанавливает" in message for message in messages)
    assert player.stats.mana > 10 - ABILITY_BY_ID["restore_energy"].mana_cost
    assert player.stats.move > 20


def test_skill_percent_is_clamped_between_ten_and_hundred() -> None:
    engine = CombatEngine()
    player = Player(name="Маг")
    player.class_name = "маг огня"
    player.skill_levels = {"fireball": 999, "curse": 1}
    assert engine.skill_percent(player, "fireball") == 100
    assert engine.skill_percent(player, "curse") == 10


def test_guild_master_can_teach_book_based_skill() -> None:
    world = WorldLoader.load(Path("data/world.json"))
    with tempfile.TemporaryDirectory() as temp_dir:
        persistence = Persistence(Path(temp_dir) / "players.db")
        session = GameSession(SimpleNamespace(combat=CombatEngine()), None, None, world, persistence)
        player = Player(name="Магистр", gold=200)
        player.class_name = "маг огня"
        player.stats.level = 10
        player.skill_levels = {}
        player.inventory.append(world.create_item("book_fireball"))
        world.get_room("guild_fire_mage").add_character(player)
        session.player = player

        result = session.learn_skill(session, ["fireball"])
        assert "обучает вас умению fireball" in result
        assert player.skill_levels["fireball"] == ABILITY_BY_ID["fireball"].base_percent
