from __future__ import annotations

import contextlib
from dataclasses import dataclass, field

from typamud.game.commands.base import CommandRegistry
from typamud.game.commands.character import equipment, help_text, inventory, look, rest, score, stand, who
from typamud.game.commands.combat import abilities, flee, kill, use_ability
from typamud.game.commands.movement import move
from typamud.game.commands.social import say
from typamud.game.data.catalog import ABILITY_BY_ID, CLASS_BY_INDEX, CLASS_BY_NAME, RACE_BY_INDEX, class_abilities, render_class_menu, render_race_menu
from typamud.game.entities.player import Player
from typamud.game.systems.messaging import render_room


@dataclass(slots=True)
class GameSession:
    server: "GameServer"
    reader: any
    writer: any
    world: any
    persistence: any
    player: Player | None = None
    commands: CommandRegistry = field(init=False)

    def __post_init__(self) -> None:
        self.commands = CommandRegistry()
        self._register_commands()

    def _register_commands(self) -> None:
        self.commands.register("помощь", "help")(help_text)
        self.commands.register("осмотреться", "look", "l")(look)
        self.commands.register("счет", "score", "sc")(score)
        self.commands.register("кто", "who")(who)
        self.commands.register("отдых", "rest")(rest)
        self.commands.register("встать", "stand")(stand)
        self.commands.register("инвентарь", "inventory", "i")(inventory)
        self.commands.register("экипировка", "equipment", "eq")(equipment)
        self.commands.register("сказать", "say", "'")(say)
        self.commands.register("взять", "get", "take")(self.get_item)
        self.commands.register("бросить", "drop")(self.drop_item)
        self.commands.register("надеть", "wear", "wield")(self.wear_item)
        self.commands.register("снять", "remove")(self.remove_item)
        self.commands.register("магазин", "shop")(self.list_shop)
        self.commands.register("купить", "buy")(self.buy_item)
        self.commands.register("продать", "sell")(self.sell_item)
        self.commands.register("учитель", "trainer")(self.show_trainer)
        self.commands.register("учить", "learn")(self.learn_skill)
        self.commands.register("баланс", "bankbalance")(self.bank_balance)
        self.commands.register("вклад", "deposit")(self.deposit_gold)
        self.commands.register("снятьденьги", "withdrawgold")(self.withdraw_gold)
        self.commands.register("снятькомнату", "rent", "arend")(self.rent_room)
        self.commands.register("расы", "races")(self.show_races)
        self.commands.register("классы", "classes")(self.show_classes)
        self.commands.register("умения", "skills", "abilities")(abilities)
        self.commands.register("bash")(lambda s, a: use_ability(s, a, "bash"))
        self.commands.register("rage")(lambda s, a: use_ability(s, a, "rage"))
        self.commands.register("fortify")(lambda s, a: use_ability(s, a, "fortify"))
        self.commands.register("smite")(lambda s, a: use_ability(s, a, "smite"))
        self.commands.register("heal")(lambda s, a: use_ability(s, a, "heal"))
        self.commands.register("holywrath")(lambda s, a: use_ability(s, a, "holy_wrath"))
        self.commands.register("sacredshield")(lambda s, a: use_ability(s, a, "sacred_shield"))
        self.commands.register("darkbolt")(lambda s, a: use_ability(s, a, "dark_bolt"))
        self.commands.register("souldrain")(lambda s, a: use_ability(s, a, "soul_drain"))
        self.commands.register("deathpact")(lambda s, a: use_ability(s, a, "death_pact"))
        self.commands.register("blindness")(lambda s, a: use_ability(s, a, "blindness"))
        self.commands.register("curse")(lambda s, a: use_ability(s, a, "curse"))
        self.commands.register("exorcism")(lambda s, a: use_ability(s, a, "exorcism"))
        self.commands.register("zealpurge")(lambda s, a: use_ability(s, a, "zeal_purge"))
        self.commands.register("fireburst")(lambda s, a: use_ability(s, a, "fire_burst"))
        self.commands.register("fireball")(lambda s, a: use_ability(s, a, "fireball"))
        self.commands.register("flamestorm")(lambda s, a: use_ability(s, a, "flame_storm"))
        self.commands.register("greaterheal")(lambda s, a: use_ability(s, a, "greater_heal"))
        self.commands.register("salvation")(lambda s, a: use_ability(s, a, "salvation"))
        self.commands.register("iceshard")(lambda s, a: use_ability(s, a, "ice_shard"))
        self.commands.register("icestrike")(lambda s, a: use_ability(s, a, "ice_strike"))
        self.commands.register("tidalwave")(lambda s, a: use_ability(s, a, "tidal_wave"))
        self.commands.register("tsunami")(lambda s, a: use_ability(s, a, "tsunami"))
        self.commands.register("stonefist")(lambda s, a: use_ability(s, a, "stone_fist"))
        self.commands.register("stoneskin")(lambda s, a: use_ability(s, a, "stone_skin"))
        self.commands.register("earthshatter")(lambda s, a: use_ability(s, a, "earth_shatter"))
        self.commands.register("mountainguard")(lambda s, a: use_ability(s, a, "mountain_guard"))
        self.commands.register("airburst")(lambda s, a: use_ability(s, a, "air_burst"))
        self.commands.register("lightning")(lambda s, a: use_ability(s, a, "lightning"))
        self.commands.register("thunderstorm")(lambda s, a: use_ability(s, a, "thunderstorm"))
        self.commands.register("restoreenergy")(lambda s, a: use_ability(s, a, "restore_energy"))
        self.commands.register("spiritlink")(lambda s, a: use_ability(s, a, "spirit_link"))
        self.commands.register("stormtotem")(lambda s, a: use_ability(s, a, "storm_totem"))
        self.commands.register("shadowflame")(lambda s, a: use_ability(s, a, "shadow_flame"))
        self.commands.register("abyssbolt")(lambda s, a: use_ability(s, a, "abyss_bolt"))
        self.commands.register("backstab")(lambda s, a: use_ability(s, a, "backstab"))
        self.commands.register("trip")(lambda s, a: use_ability(s, a, "trip"))
        self.commands.register("bless")(lambda s, a: use_ability(s, a, "bless"))
        for ability_id in class_abilities("шаман"):
            alias = ABILITY_BY_ID[ability_id].name
            self.commands.register(alias)(lambda s, a, ability_id=ability_id: use_ability(s, a, ability_id))
        self.commands.register("убить", "kill", "k")(kill)
        self.commands.register("сбежать", "flee")(flee)
        self.commands.register("север", "north", "n")(lambda s, a: move(s, a, "north"))
        self.commands.register("юг", "south", "s")(lambda s, a: move(s, a, "south"))
        self.commands.register("восток", "east", "e")(lambda s, a: move(s, a, "east"))
        self.commands.register("запад", "west", "w")(lambda s, a: move(s, a, "west"))
        self.commands.register("вверх", "up", "u")(lambda s, a: move(s, a, "up"))
        self.commands.register("вниз", "down", "d")(lambda s, a: move(s, a, "down"))

    async def write(self, message: str) -> None:
        self.writer.write(message.replace("\n", "\r\n").encode("utf-8") + b"\r\n")
        await self.writer.drain()

    async def prompt(self) -> None:
        if self.player and self.player.prompt_enabled:
            self.writer.write(
                f"<{self.player.stats.hp}hp {self.player.stats.mana}mn {self.player.stats.move}mv золото:{self.player.gold} банк:{self.player.bank_gold} руб:{self.player.rubies}> ".encode("utf-8")
            )
            await self.writer.drain()

    async def flush_channel(self) -> None:
        if not self.player:
            return
        while self.player.channel_messages:
            await self.write(self.player.channel_messages.pop(0))

    async def read_line(self) -> str:
        raw = await self.reader.readline()
        return raw.decode("utf-8", errors="ignore").strip()

    async def choose_race(self) -> tuple[str, object]:
        await self.write(render_race_menu())
        while True:
            await self.write("Введите номер расы:")
            selection = await self.read_line()
            if selection.isdigit() and int(selection) in RACE_BY_INDEX:
                race = RACE_BY_INDEX[int(selection)]
                return race.name, race
            await self.write("Неверный выбор. Попробуйте снова.")

    async def choose_class(self) -> tuple[str, object]:
        await self.write(render_class_menu())
        while True:
            await self.write("Введите номер класса:")
            selection = await self.read_line()
            if selection.isdigit() and int(selection) in CLASS_BY_INDEX:
                class_template = CLASS_BY_INDEX[int(selection)]
                return class_template.name, class_template
            await self.write("Неверный выбор. Попробуйте снова.")

    def apply_template(self, player: Player, template: object) -> None:
        player.stats.strength += template.strength
        player.stats.agility += template.agility
        player.stats.vitality += template.vitality
        player.stats.max_hp += template.hp
        player.stats.max_mana += template.mana
        player.stats.max_move += template.move
        player.stats.hp = player.stats.max_hp
        player.stats.mana = player.stats.max_mana
        player.stats.move = player.stats.max_move

    def initialize_skill_levels(self, player: Player) -> None:
        class_template = CLASS_BY_NAME[player.class_name]
        player.skill_levels = {
            ability_id: max(10, min(100, ABILITY_BY_ID[ability_id].base_percent + player.stats.level * 2))
            for ability_id in class_template.abilities
            if ABILITY_BY_ID[ability_id].required_level <= 1
        }

    async def login(self) -> None:
        await self.write(self.server.settings.motd)
        name = await self.read_line() or "Безымянный"
        player = self.persistence.load_player(name, self.world)
        if player is None:
            player = Player(name=name)
            race_name, race_template = await self.choose_race()
            class_name, class_template = await self.choose_class()
            player.race_name = race_name
            player.class_name = class_name
            self.apply_template(player, race_template)
            self.apply_template(player, class_template)
            self.initialize_skill_levels(player)
            player.gold = 120
            player.rubies = 3
            room = self.world.get_room(self.world.start_room_id)
            player.saved_room_id = room.id
            player.rent_room_id = self.world.recall_room_id
            player.inventory.append(self.world.create_item("training_sword"))
            player.inventory.append(self.world.create_item("quilt_armor"))
        else:
            room = self.world.get_room(getattr(player, "saved_room_id", self.world.start_room_id))
        room.add_character(player)
        self.player = player
        self.persistence.save_player(player)
        await self.write(f"Привет, {player.name}! Раса: {player.race_name}, класс: {player.class_name}.")
        await self.write(render_room(player))

    def get_item(self, session: "GameSession", args: list[str]) -> str:
        if not args or self.player is None or self.player.room is None:
            return "Взять что?"
        item = self.player.room.find_item(" ".join(args))
        if item is None:
            return "Здесь этого нет."
        self.player.room.items.remove(item)
        self.player.add_item(item)
        self.persistence.save_player(self.player)
        return f"Вы берете: {item.name}."

    def drop_item(self, session: "GameSession", args: list[str]) -> str:
        if not args or self.player is None or self.player.room is None:
            return "Бросить что?"
        item = self.player.find_inventory_item(" ".join(args))
        if item is None:
            return "У вас этого нет."
        self.player.remove_item(item)
        self.player.room.items.append(item)
        self.persistence.save_player(self.player)
        return f"Вы бросаете: {item.name}."

    def wear_item(self, session: "GameSession", args: list[str]) -> str:
        if not args or self.player is None:
            return "Надеть что?"
        item = self.player.find_inventory_item(" ".join(args))
        if item is None:
            return "У вас этого нет."
        if item.slot is None:
            return "Этот предмет нельзя надеть."
        previous = self.player.wear(item)
        if previous is not None:
            self.player.inventory.append(previous)
            replaced = f" Снимаете {previous.name}."
        else:
            replaced = ""
        self.persistence.save_player(self.player)
        return f"Вы экипируете {item.name}.{replaced}"

    def remove_item(self, session: "GameSession", args: list[str]) -> str:
        if self.player is None:
            return "Снимать нечего."
        if not args:
            return "Снять что?"
        needle = " ".join(args).lower()
        slot = None
        for current_slot, item in self.player.equipment.items():
            if needle in item.name.lower() or needle == current_slot:
                slot = current_slot
                break
        if slot is None:
            return "На вас этого нет."
        item = self.player.remove_equipment(slot)
        self.persistence.save_player(self.player)
        return f"Вы снимаете {item.name}."

    def current_service(self, service_name: str) -> str | None:
        if self.player is None or self.player.room is None:
            return None
        return self.player.room.services.get(service_name)

    def show_trainer(self, session: "GameSession", args: list[str]) -> str:
        trainer_class = self.current_service("trainer")
        if trainer_class is None or self.player is None:
            return "Здесь нет мастера гильдии."
        if trainer_class != self.player.class_name:
            return f"Мастер этой гильдии обучает только классу {trainer_class}."
        class_template = CLASS_BY_NAME[self.player.class_name]
        lines = [f"Мастер гильдии {self.player.class_name} предлагает обучение:"]
        for ability_id in class_template.abilities:
            ability = ABILITY_BY_ID[ability_id]
            known = self.player.skill_levels.get(ability_id)
            status = f"изучено {known}%" if known is not None else "не изучено"
            extra = " + книга" if ability.book_required else ""
            lines.append(
                f"- {ability.name}: круг {ability.circle}, ур. {ability.required_level}, "
                f"цена {ability.trainer_cost} золота{extra}, {status}"
            )
        return "\n".join(lines)

    def learn_skill(self, session: "GameSession", args: list[str]) -> str:
        if not args or self.player is None:
            return "Учить что?"
        trainer_class = self.current_service("trainer")
        if trainer_class is None:
            return "Здесь нет мастера гильдии."
        if trainer_class != self.player.class_name:
            return f"Этот мастер обучает только классу {trainer_class}."
        needle = " ".join(args).lower()
        class_template = CLASS_BY_NAME[self.player.class_name]
        ability = next((ABILITY_BY_ID[ability_id] for ability_id in class_template.abilities if needle == ABILITY_BY_ID[ability_id].name.lower()), None)
        if ability is None:
            return "Мастер не знает такого приема."
        if ability.id in self.player.skill_levels:
            return "Вы уже изучили этот навык."
        if self.player.stats.level < ability.required_level:
            return f"Для этого навыка нужен {ability.required_level} уровень."
        book_item = None
        if ability.book_required:
            book_item = next((item for item in self.player.inventory if item.teaches_skill == ability.id), None)
            if book_item is None:
                return "Для этого умения нужна учебная книга."
        if self.player.gold < ability.trainer_cost:
            return "У вас не хватает золота на обучение."
        self.player.gold -= ability.trainer_cost
        if book_item is not None:
            self.player.remove_item(book_item)
        self.player.skill_levels[ability.id] = ability.base_percent
        self.persistence.save_player(self.player)
        return f"Мастер обучает вас умению {ability.name}. Теперь у вас {ability.base_percent}% владения."

    def list_shop(self, session: "GameSession", args: list[str]) -> str:
        shop_id = self.current_service("shop")
        if shop_id is None:
            return "Здесь нет магазина."
        items = self.world.shop_items(shop_id)
        if not items:
            return "Лавка сегодня почти пуста."
        lines = ["В продаже:"]
        for item in items:
            currency = "руб." if shop_id == "ruby_shop" else "зол."
            price = max(1, item.value * (2 if shop_id == "ruby_shop" else 1))
            lines.append(f"- {item.name}: {price} {currency}")
        return "\n".join(lines)

    def buy_item(self, session: "GameSession", args: list[str]) -> str:
        if not args or self.player is None:
            return "Купить что?"
        shop_id = self.current_service("shop")
        if shop_id is None:
            return "Здесь нет магазина."
        for item in self.world.shop_items(shop_id):
            if item.matches(" ".join(args)):
                price = max(1, item.value * (2 if shop_id == "ruby_shop" else 1))
                if shop_id == "ruby_shop":
                    if self.player.rubies < price:
                        return "Недостаточно рубинов."
                    self.player.rubies -= price
                else:
                    if self.player.gold < price:
                        return "Недостаточно золота."
                    self.player.gold -= price
                self.player.inventory.append(item)
                self.persistence.save_player(self.player)
                return f"Вы покупаете {item.name}."
        return "Такого товара здесь нет."

    def sell_item(self, session: "GameSession", args: list[str]) -> str:
        if not args or self.player is None:
            return "Продать что?"
        shop_id = self.current_service("shop")
        if shop_id is None:
            return "Здесь нет магазина."
        if shop_id == "ruby_shop":
            return "Этот торговец не занимается обычной скупкой."
        item = self.player.find_inventory_item(" ".join(args))
        if item is None:
            return "У вас этого нет."
        self.player.remove_item(item)
        self.player.gold += max(1, item.value // 2)
        self.persistence.save_player(self.player)
        return f"Вы продаете {item.name}."

    def bank_balance(self, session: "GameSession", args: list[str]) -> str:
        if self.current_service("bank") is None or self.player is None:
            return "Здесь нет банка."
        return f"Наличные: {self.player.gold}. На счету: {self.player.bank_gold}."

    def deposit_gold(self, session: "GameSession", args: list[str]) -> str:
        if self.current_service("bank") is None or self.player is None:
            return "Здесь нет банка."
        if not args or not args[0].isdigit():
            return "Формат: вклад <сумма>"
        amount = int(args[0])
        if amount <= 0 or amount > self.player.gold:
            return "Недостаточно наличного золота."
        self.player.gold -= amount
        self.player.bank_gold += amount
        self.persistence.save_player(self.player)
        return f"Вы кладете в банк {amount} золота."

    def withdraw_gold(self, session: "GameSession", args: list[str]) -> str:
        if self.current_service("bank") is None or self.player is None:
            return "Здесь нет банка."
        if not args or not args[0].isdigit():
            return "Формат: снятьденьги <сумма>"
        amount = int(args[0])
        if amount <= 0 or amount > self.player.bank_gold:
            return "На счету недостаточно золота."
        self.player.bank_gold -= amount
        self.player.gold += amount
        self.persistence.save_player(self.player)
        return f"Вы снимаете со счета {amount} золота."

    def rent_room(self, session: "GameSession", args: list[str]) -> str:
        if self.current_service("inn") is None or self.player is None or self.player.room is None:
            return "Здесь нет гостиницы."
        price = 15
        if self.player.gold < price:
            return "У вас не хватает золота на комнату."
        self.player.gold -= price
        self.player.rent_room_id = self.player.room.id
        self.player.saved_room_id = self.player.room.id
        self.player.resting = True
        self.player.stats.hp = self.player.stats.max_hp
        self.player.stats.mana = self.player.stats.max_mana
        self.player.stats.move = self.player.stats.max_move
        self.persistence.save_player(self.player)
        return "Вы снимаете комнату в гостинице и полностью восстанавливаете силы."

    def show_races(self, session: "GameSession", args: list[str]) -> str:
        return render_race_menu()

    def show_classes(self, session: "GameSession", args: list[str]) -> str:
        return render_class_menu()

    async def run(self) -> None:
        await self.login()
        while not self.reader.at_eof():
            await self.flush_channel()
            await self.prompt()
            raw = await self.reader.readline()
            if not raw:
                break
            line = raw.decode("utf-8", errors="ignore").strip()
            if not line:
                continue
            if line.lower() in {"выход", "quit", "exit"}:
                await self.write("До встречи в typamud.")
                break
            if line.startswith("'"):
                command = "'"
                args = [line[1:].strip()] if line[1:].strip() else []
            else:
                command, *args = line.split()
            handler = self.commands.get(command.lower())
            response = handler(self, args) if handler else "Неизвестная команда. Введите: помощь"
            await self.write(response)
        await self.close()

    async def close(self) -> None:
        if self.player:
            self.player.resting = False
            if self.player.room is not None:
                self.player.saved_room_id = self.player.room.id
                self.player.room.remove_character(self.player)
            self.persistence.save_player(self.player)
        self.writer.close()
        with contextlib.suppress(Exception):
            await self.writer.wait_closed()
