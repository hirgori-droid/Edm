from __future__ import annotations

import random

from typamud.game.data.catalog import ABILITY_BY_ID, class_abilities
from typamud.game.entities.character import Character
from typamud.game.entities.npc import NPC


class CombatEngine:
    @staticmethod
    def hit_roll(attacker: Character, defender: Character) -> bool:
        attack = attacker.total_agility + attacker.stats.level * 2 + random.randint(1, 20)
        defense = defender.total_agility + defender.stats.level * 2 + 10
        return attack >= defense

    @staticmethod
    def damage_roll(attacker: Character, defender: Character) -> int:
        weapon = attacker.wielded_weapon
        weapon_min = weapon.damage_min if weapon else 1
        weapon_max = weapon.damage_max if weapon else 4
        base = random.randint(weapon_min, max(weapon_min, weapon_max)) + attacker.total_strength // 4
        mitigation = defender.armor_rating // 4
        return max(1, base - mitigation)

    @staticmethod
    def experience_to_next_level(level: int) -> int:
        return 100 + (level - 1) * 75

    def maybe_level_up(self, character: Character) -> list[str]:
        messages: list[str] = []
        while character.stats.experience >= self.experience_to_next_level(character.stats.level):
            character.stats.experience -= self.experience_to_next_level(character.stats.level)
            character.stats.level += 1
            character.stats.max_hp += 8
            character.stats.max_mana += 4
            character.stats.max_move += 6
            character.stats.strength += 1
            character.stats.agility += 1
            character.stats.vitality += 1
            character.stats.hp = character.stats.max_hp
            character.stats.mana = character.stats.max_mana
            character.stats.move = character.stats.max_move
            messages.append(f"{character.name} получает новый уровень! Теперь уровень {character.stats.level}.")
        return messages

    def resolve_attack(self, attacker: Character, defender: Character) -> tuple[list[str], bool]:
        messages: list[str] = []
        if not attacker.alive or not defender.alive:
            return messages, False
        if attacker.has_effect("stun"):
            messages.append(f"{attacker.name} оглушен и не может действовать.")
            return messages, False
        if attacker.stats.move > 0:
            attacker.stats.move = max(0, attacker.stats.move - 2)
        if not self.hit_roll(attacker, defender):
            messages.append(f"{attacker.name} промахивается по {defender.name}.")
            return messages, False
        damage = self.damage_roll(attacker, defender)
        died = defender.receive_damage(damage)
        messages.append(f"{attacker.name} бьет {defender.name} на {damage} урона.")
        if died:
            messages.extend(self._handle_kill_rewards(attacker, defender))
        return messages, died

    def _handle_kill_rewards(self, attacker: Character, defender: Character) -> list[str]:
        messages = [f"{defender.name} погибает."]
        if isinstance(defender, NPC) and attacker.is_player:
            attacker.stats.experience += defender.experience_reward
            attacker.gold += defender.gold_reward
            messages.append(f"{attacker.name} получает {defender.experience_reward} опыта и {defender.gold_reward} золота.")
            messages.extend(self.maybe_level_up(attacker))
        return messages

    def available_abilities(self, class_name: str) -> tuple[str, ...]:
        return class_abilities(class_name)

    @staticmethod
    def skill_percent(character: Character, ability_id: str) -> int:
        raw_value = getattr(character, "skill_levels", {}).get(ability_id, ABILITY_BY_ID[ability_id].base_percent)
        return max(10, min(100, raw_value))

    @staticmethod
    def maybe_improve_skill(character: Character, ability_id: str, success: bool) -> None:
        skill_levels = getattr(character, "skill_levels", None)
        if skill_levels is None:
            return
        current = max(10, min(100, skill_levels.get(ability_id, ABILITY_BY_ID[ability_id].base_percent)))
        if current >= 100:
            skill_levels[ability_id] = 100
            return
        improve_roll = random.randint(1, 100)
        threshold = 25 if success else 10
        if improve_roll <= threshold:
            skill_levels[ability_id] = min(100, current + 1)

    def perform_ability(self, attacker: Character, defender: Character | None, ability_id: str) -> tuple[list[str], bool]:
        ability = ABILITY_BY_ID[ability_id]
        messages: list[str] = []
        died = False
        if ability_id not in self.available_abilities(getattr(attacker, "class_name", "")):
            return ["Ваш класс не владеет этим умением."], False
        if ability_id not in getattr(attacker, "skill_levels", {}):
            return ["Вы еще не изучили это умение у мастера гильдии."], False
        if attacker.has_cooldown(ability_id):
            return [f"Умение {ability.name} еще не готово."], False
        if ability.mana_cost > attacker.stats.mana:
            return ["Недостаточно маны."], False
        if ability.move_cost > attacker.stats.move:
            return ["Недостаточно сил для приема."], False
        if ability.target_required and defender is None:
            return ["Для этого умения нужна цель."], False
        attacker.stats.mana -= ability.mana_cost
        attacker.stats.move -= ability.move_cost
        attacker.set_cooldown(ability_id, ability.cooldown)
        skill_percent = self.skill_percent(attacker, ability_id)
        if random.randint(1, 100) > skill_percent:
            self.maybe_improve_skill(attacker, ability_id, success=False)
            return [f"{attacker.name} пытается использовать {ability.name}, но прием срывается. ({skill_percent}%)"], False

        if ability_id == "rage":
            attacker.add_effect("rage", duration=4, strength=3)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} впадает в ярость.")
            return messages, False
        if ability_id == "fortify":
            attacker.add_effect("fortify", duration=4, armor=5)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} встает в укрепленную стойку.")
            return messages, False
        if ability_id == "heal":
            amount = 12 + attacker.stats.level * 2
            attacker.stats.hp = min(attacker.stats.max_hp, attacker.stats.hp + amount)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} восстанавливает {amount} здоровья.")
            return messages, False
        if ability_id == "greater_heal":
            amount = 22 + attacker.stats.level * 3
            attacker.stats.hp = min(attacker.stats.max_hp, attacker.stats.hp + amount)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} закрывает тяжелые раны и восстанавливает {amount} здоровья.")
            return messages, False
        if ability_id == "restore_energy":
            mana_amount = 8 + attacker.stats.level * 2
            move_amount = 10 + attacker.stats.level * 2
            attacker.stats.mana = min(attacker.stats.max_mana, attacker.stats.mana + mana_amount)
            attacker.stats.move = min(attacker.stats.max_move, attacker.stats.move + move_amount)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} восстанавливает {mana_amount} маны и {move_amount} единиц энергии.")
            return messages, False
        if ability_id == "spirit_link":
            hp_amount = 10 + attacker.stats.level * 2
            mana_amount = 10 + attacker.stats.level * 2
            attacker.stats.hp = min(attacker.stats.max_hp, attacker.stats.hp + hp_amount)
            attacker.stats.mana = min(attacker.stats.max_mana, attacker.stats.mana + mana_amount)
            attacker.add_effect("spirit_link", duration=4, vitality=2)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} связывается с духами и восстанавливает {hp_amount} здоровья и {mana_amount} маны.")
            return messages, False
        if ability_id == "sacred_shield":
            attacker.add_effect("sacred_shield", duration=5, armor=8, vitality=2)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} поднимает сияющий священный щит.")
            return messages, False
        if ability_id == "salvation":
            amount = 28 + attacker.stats.level * 3
            attacker.stats.hp = min(attacker.stats.max_hp, attacker.stats.hp + amount)
            attacker.add_effect("salvation", duration=3, armor=3)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} призывает спасение и исцеляет {amount} здоровья.")
            return messages, False
        if ability_id == "mountain_guard":
            attacker.add_effect("mountain_guard", duration=5, armor=10, vitality=3, agility=-1)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} покрывается печатью горной стражи.")
            return messages, False
        if ability_id == "storm_totem":
            attacker.add_effect("storm_totem", duration=5, agility=2, armor=3)
            attacker.stats.mana = min(attacker.stats.max_mana, attacker.stats.mana + 8 + attacker.stats.level)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} воздвигает тотем бури и наполняется силой духов.")
            return messages, False
        if not ability.target_required:
            circle = max(1, ability.circle)
            heal_amount = 6 + circle * 3 + attacker.stats.level
            attacker.stats.hp = min(attacker.stats.max_hp, attacker.stats.hp + heal_amount)
            attacker.add_effect(ability_id, duration=3 + min(3, circle // 2), armor=min(8, circle + 1), vitality=min(5, circle // 2 + 1))
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} использует {ability.name} и укрепляет связь с природой.")
            return messages, False
        if ability_id == "bless":
            attacker.add_effect("bless", duration=5, agility=2, armor=2)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"{attacker.name} получает благословение.")
            return messages, False
        if ability_id == "stone_skin":
            attacker.add_effect("stone_skin", duration=5, armor=7)
            self.maybe_improve_skill(attacker, ability_id, success=True)
            messages.append(f"Кожа {attacker.name} покрывается каменной броней.")
            return messages, False

        if defender is None:
            return ["Для этого умения нужна цель."], False

        if ability_id == "bash":
            damage = self.damage_roll(attacker, defender) + 4
            defender.add_effect("stun", duration=1)
            messages.append(f"{attacker.name} проводит мощный bash по {defender.name}.")
        elif ability_id == "smite":
            damage = self.damage_roll(attacker, defender) + 6 + attacker.stats.level
            messages.append(f"{attacker.name} поражает {defender.name} светом.")
        elif ability_id == "holy_wrath":
            damage = 12 + attacker.stats.level + random.randint(2, 8)
            defender.add_effect("holy_wrath", duration=3, armor=-2)
            messages.append(f"{attacker.name} низводит на {defender.name} священный гнев.")
        elif ability_id == "zeal_purge":
            damage = 14 + attacker.stats.level + random.randint(3, 9)
            defender.add_effect("zeal_purge", duration=3, agility=-2, armor=-2)
            messages.append(f"{attacker.name} выжигает слабость {defender.name} пламенем веры.")
        elif ability_id == "dark_bolt":
            damage = 8 + attacker.stats.level + random.randint(1, 6)
            messages.append(f"{attacker.name} выпускает темный болт в {defender.name}.")
        elif ability_id == "soul_drain":
            damage = 10 + attacker.stats.level + random.randint(2, 6)
            attacker.stats.hp = min(attacker.stats.max_hp, attacker.stats.hp + max(4, damage // 3))
            messages.append(f"{attacker.name} вытягивает силы из {defender.name}.")
        elif ability_id == "death_pact":
            damage = 15 + attacker.stats.level + random.randint(3, 8)
            attacker.stats.hp = min(attacker.stats.max_hp, attacker.stats.hp + max(6, damage // 3))
            defender.add_effect("death_pact", duration=3, armor=-3)
            messages.append(f"{attacker.name} заключает кровавый пакт против {defender.name}.")
        elif ability_id == "blindness":
            damage = 4 + attacker.stats.level
            defender.add_effect("blindness", duration=4, agility=-4)
            messages.append(f"{attacker.name} лишает {defender.name} зрения вспышкой света.")
        elif ability_id == "curse":
            damage = 5 + attacker.stats.level
            defender.add_effect("curse", duration=4, agility=-2, armor=-2)
            messages.append(f"{attacker.name} накладывает проклятие на {defender.name}.")
        elif ability_id == "exorcism":
            damage = 11 + attacker.stats.level + random.randint(2, 7)
            defender.add_effect("exorcism", duration=3, agility=-2)
            messages.append(f"{attacker.name} изгоняет слабость из {defender.name} огнем веры.")
        elif ability_id == "fire_burst":
            damage = 8 + attacker.stats.level + random.randint(2, 6)
            messages.append(f"{attacker.name} обжигает {defender.name} огненным всполохом.")
        elif ability_id == "fireball":
            damage = 10 + attacker.stats.level + random.randint(2, 8)
            messages.append(f"{attacker.name} швыряет огненный шар в {defender.name}.")
        elif ability_id == "flame_storm":
            damage = 15 + attacker.stats.level + random.randint(3, 9)
            defender.add_effect("flame_storm", duration=3, armor=-3)
            messages.append(f"{attacker.name} накрывает {defender.name} огненным штормом.")
        elif ability_id == "ice_shard":
            damage = 7 + attacker.stats.level + random.randint(1, 5)
            defender.add_effect("chill", duration=3, agility=-1)
            messages.append(f"{attacker.name} пронзает {defender.name} ледяным осколком.")
        elif ability_id == "ice_strike":
            damage = 8 + attacker.stats.level + random.randint(1, 6)
            defender.add_effect("chill", duration=4, agility=-2)
            messages.append(f"{attacker.name} обрушивает на {defender.name} ледяной удар.")
        elif ability_id == "tidal_wave":
            damage = 11 + attacker.stats.level + random.randint(2, 7)
            defender.add_effect("tidal_wave", duration=3, agility=-2, armor=-1)
            messages.append(f"{attacker.name} накрывает {defender.name} тяжелой волной.")
        elif ability_id == "tsunami":
            damage = 15 + attacker.stats.level + random.randint(3, 9)
            defender.add_effect("tsunami", duration=3, agility=-3, armor=-2)
            messages.append(f"{attacker.name} сокрушает {defender.name} цунами.")
        elif ability_id == "stone_fist":
            damage = 8 + attacker.stats.level + random.randint(1, 5)
            if random.randint(1, 100) <= 35:
                defender.add_effect("stun", duration=1)
            messages.append(f"{attacker.name} поражает {defender.name} каменным кулаком.")
        elif ability_id == "earth_shatter":
            damage = 12 + attacker.stats.level + random.randint(2, 7)
            defender.add_effect("earth_shatter", duration=3, armor=-3)
            messages.append(f"{attacker.name} раскалывает землю под {defender.name}.")
        elif ability_id == "air_burst":
            damage = 7 + attacker.stats.level + random.randint(2, 6)
            defender.add_effect("air_burst", duration=3, agility=-2)
            messages.append(f"{attacker.name} срывает на {defender.name} взрыв воздуха.")
        elif ability_id == "lightning":
            damage = 9 + attacker.stats.level + random.randint(1, 7)
            if random.randint(1, 100) <= 35:
                defender.add_effect("stun", duration=1)
            messages.append(f"{attacker.name} поражает {defender.name} молнией.")
        elif ability_id == "thunderstorm":
            damage = 15 + attacker.stats.level + random.randint(3, 9)
            if random.randint(1, 100) <= 50:
                defender.add_effect("stun", duration=1)
            defender.add_effect("thunderstorm", duration=3, agility=-2)
            messages.append(f"{attacker.name} обрушивает на {defender.name} яростную грозу.")
        elif ability_id == "shadow_flame":
            damage = 12 + attacker.stats.level + random.randint(2, 8)
            defender.add_effect("shadow_flame", duration=3, agility=-1, armor=-2)
            messages.append(f"{attacker.name} окутывает {defender.name} черным пламенем.")
        elif ability_id == "abyss_bolt":
            damage = 15 + attacker.stats.level + random.randint(3, 9)
            defender.add_effect("abyss_bolt", duration=3, armor=-3, agility=-1)
            messages.append(f"{attacker.name} пробивает {defender.name} болтом бездны.")
        elif ability_id == "backstab":
            damage = self.damage_roll(attacker, defender) + 8 + attacker.total_agility // 2
            messages.append(f"{attacker.name} наносит подлый удар в спину {defender.name}.")
        elif ability_id == "trip":
            damage = self.damage_roll(attacker, defender) + 3
            defender.add_effect("stun", duration=1)
            messages.append(f"{attacker.name} подсечкой валит {defender.name} с ног.")
        else:
            circle = max(1, ability.circle)
            damage = 4 + attacker.stats.level + circle * 2 + random.randint(1, 4 + circle)
            defender.add_effect(ability_id, duration=2 + min(3, circle // 2), armor=-min(5, circle), agility=-min(4, circle // 2 + 1))
            messages.append(f"{attacker.name} обрушивает {ability.name} на {defender.name}.")

        died = defender.receive_damage(damage)
        messages.append(f"{defender.name} получает {damage} урона.")
        attacker.engage(defender)
        if not defender.fighting and defender.alive:
            defender.engage(attacker)
        self.maybe_improve_skill(attacker, ability_id, success=True)
        if died:
            messages.extend(self._handle_kill_rewards(attacker, defender))
        return messages, died
