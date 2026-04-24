from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RaceTemplate:
    id: str
    name: str
    description: str
    strength: int = 0
    agility: int = 0
    vitality: int = 0
    hp: int = 0
    mana: int = 0
    move: int = 0


@dataclass(frozen=True, slots=True)
class ClassTemplate:
    id: str
    name: str
    group: str
    description: str
    strength: int = 0
    agility: int = 0
    vitality: int = 0
    hp: int = 0
    mana: int = 0
    move: int = 0
    magic: bool = False
    abilities: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class AbilityTemplate:
    id: str
    name: str
    description: str
    mana_cost: int = 0
    move_cost: int = 0
    cooldown: int = 0
    target_required: bool = True
    base_percent: int = 45
    circle: int = 1
    required_level: int = 1
    trainer_cost: int = 0
    book_required: bool = False


RACE_TEMPLATES: tuple[RaceTemplate, ...] = (
    RaceTemplate("wood_elf", "лесные эльфы", "Ловкие лесные стрелки и разведчики.", agility=2, vitality=-1, mana=4, move=8),
    RaceTemplate("high_elf", "высшие эльфы", "Утонченные маги с высоким запасом маны.", agility=1, mana=8, hp=-2),
    RaceTemplate("half_elf", "полуэльфы", "Гибкие универсалы между миром людей и эльфов.", agility=1, mana=3, move=3),
    RaceTemplate("mountain_dwarf", "горные дварфы", "Крепкие бойцы в тяжелой броне.", strength=1, vitality=2, hp=6, move=-5),
    RaceTemplate("deep_dwarf", "глубинные дварфы", "Выносливые подземные жители с чуть большей магической стойкостью.", vitality=2, mana=2, hp=4, move=-6),
    RaceTemplate("human", "человек", "Сбалансированная раса без ярко выраженных слабостей.", hp=2, mana=2, move=2),
    RaceTemplate("orc", "орк", "Сильные и грубые фронтовики.", strength=2, vitality=1, hp=6, mana=-4),
    RaceTemplate("goblin", "гоблин", "Ловкие и хитрые, но не самые крепкие.", agility=2, vitality=-1, move=6),
    RaceTemplate("giant", "великан", "Медленные, но очень живучие и сильные.", strength=3, vitality=2, hp=10, move=-10, mana=-6),
    RaceTemplate("half_orc", "полуорк", "Универсальный рукопашный боец.", strength=2, hp=4, mana=-2),
)

ABILITY_TEMPLATES: tuple[AbilityTemplate, ...] = (
    AbilityTemplate("bash", "bash", "Сильный щитовой/силовой удар с шансом оглушить цель.", move_cost=8, cooldown=2, base_percent=55, circle=1, required_level=1, trainer_cost=0),
    AbilityTemplate("rage", "rage", "Впасть в ярость и временно поднять урон.", move_cost=6, cooldown=5, target_required=False, base_percent=60, circle=1, required_level=1, trainer_cost=0),
    AbilityTemplate("fortify", "fortify", "Укрепить стойку и поднять броню.", move_cost=5, cooldown=5, target_required=False, base_percent=55, circle=1, required_level=1, trainer_cost=0),
    AbilityTemplate("smite", "smite", "Священный удар светом.", mana_cost=8, cooldown=2, base_percent=50, circle=1, required_level=1, trainer_cost=0),
    AbilityTemplate("heal", "heal", "Быстрое исцеление своих ран.", mana_cost=10, cooldown=3, target_required=False, base_percent=55, circle=1, required_level=1, trainer_cost=0),
    AbilityTemplate("holy_wrath", "holywrath", "Вспышка священного гнева поражает нечистых и еретиков.", mana_cost=14, cooldown=4, base_percent=44, circle=3, required_level=10, trainer_cost=85, book_required=True),
    AbilityTemplate("sacred_shield", "sacredshield", "Священный щит резко укрепляет паладина.", mana_cost=18, cooldown=6, target_required=False, base_percent=42, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("dark_bolt", "darkbolt", "Темный болт, пробивающий защиту.", mana_cost=9, cooldown=2, base_percent=48, circle=1, required_level=1, trainer_cost=0),
    AbilityTemplate("soul_drain", "souldrain", "Вытянуть часть жизни цели темной волей.", mana_cost=14, cooldown=4, base_percent=43, circle=3, required_level=10, trainer_cost=85, book_required=True),
    AbilityTemplate("death_pact", "deathpact", "Кровавый пакт усиливает удар и крадет жизнь у врага.", mana_cost=18, cooldown=5, base_percent=41, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("blindness", "blindness", "Ослепить цель и сбить ее точность.", mana_cost=11, cooldown=4, base_percent=45, circle=2, required_level=5, trainer_cost=45, book_required=True),
    AbilityTemplate("curse", "curse", "Ослабить врага проклятием.", mana_cost=10, cooldown=4, base_percent=45, circle=2, required_level=5, trainer_cost=35),
    AbilityTemplate("exorcism", "exorcism", "Карающая формула веры обжигает врага светом.", mana_cost=14, cooldown=4, base_percent=44, circle=3, required_level=10, trainer_cost=85, book_required=True),
    AbilityTemplate("zeal_purge", "zealpurge", "Пламя ревностной веры сжигает волю противника.", mana_cost=18, cooldown=5, base_percent=42, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("fire_burst", "fireburst", "Огненный всполох обжигает цель коротким взрывом.", mana_cost=11, cooldown=3, base_percent=48, circle=2, required_level=5, trainer_cost=45, book_required=True),
    AbilityTemplate("fireball", "fireball", "Огненный шар с большим уроном.", mana_cost=12, cooldown=3, base_percent=45, circle=3, required_level=10, trainer_cost=80, book_required=True),
    AbilityTemplate("flame_storm", "flamestorm", "Огненный шторм прожигает броню и плоть.", mana_cost=19, cooldown=5, base_percent=42, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("greater_heal", "greaterheal", "Глубокое исцеление закрывает тяжелые раны.", mana_cost=15, cooldown=4, target_required=False, base_percent=46, circle=3, required_level=10, trainer_cost=85, book_required=True),
    AbilityTemplate("salvation", "salvation", "Молитва спасения мгновенно исцеляет критические раны.", mana_cost=20, cooldown=6, target_required=False, base_percent=42, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("ice_shard", "iceshard", "Ледяной осколок, охлаждающий врага.", mana_cost=9, cooldown=2, base_percent=50, circle=2, required_level=5, trainer_cost=35),
    AbilityTemplate("ice_strike", "icestrike", "Ледяной удар замедляет и ранит врага.", mana_cost=11, cooldown=3, base_percent=48, circle=2, required_level=5, trainer_cost=45, book_required=True),
    AbilityTemplate("tidal_wave", "tidalwave", "Тяжелая волна сбивает врага и срывает его темп.", mana_cost=14, cooldown=4, base_percent=44, circle=3, required_level=10, trainer_cost=85, book_required=True),
    AbilityTemplate("tsunami", "tsunami", "Цунами сокрушает цель мощным потоком воды.", mana_cost=19, cooldown=5, base_percent=42, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("stone_fist", "stonefist", "Каменный кулак обрушивается на противника тяжёлым ударом.", mana_cost=10, cooldown=3, base_percent=48, circle=2, required_level=5, trainer_cost=45, book_required=True),
    AbilityTemplate("stone_skin", "stoneskin", "Каменная кожа на короткое время.", mana_cost=8, cooldown=5, target_required=False, base_percent=55, circle=2, required_level=5, trainer_cost=35),
    AbilityTemplate("earth_shatter", "earthshatter", "Разлом земли под ногами рвет строй и кости.", mana_cost=14, cooldown=4, base_percent=44, circle=3, required_level=10, trainer_cost=85, book_required=True),
    AbilityTemplate("mountain_guard", "mountainguard", "Печать гор дает мощную каменную защиту.", mana_cost=18, cooldown=6, target_required=False, base_percent=42, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("air_burst", "airburst", "Взрыв воздуха отбрасывает и дезориентирует цель.", mana_cost=10, cooldown=3, base_percent=48, circle=2, required_level=5, trainer_cost=45, book_required=True),
    AbilityTemplate("lightning", "lightning", "Молния с шансом оглушения.", mana_cost=11, cooldown=3, base_percent=47, circle=3, required_level=10, trainer_cost=80, book_required=True),
    AbilityTemplate("thunderstorm", "thunderstorm", "Грозовой разряд оглушает и сжигает врага.", mana_cost=19, cooldown=5, base_percent=42, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("restore_energy", "restoreenergy", "Восстановить запас сил и маны через зов духов.", mana_cost=9, cooldown=5, target_required=False, base_percent=50, circle=2, required_level=5, trainer_cost=45, book_required=True),
    AbilityTemplate("spirit_link", "spiritlink", "Духи восстанавливают силы шамана и укрепляют его плоть.", mana_cost=14, cooldown=5, target_required=False, base_percent=45, circle=3, required_level=10, trainer_cost=85, book_required=True),
    AbilityTemplate("storm_totem", "stormtotem", "Тотем бури окружает шамана силой духов и молний.", mana_cost=18, cooldown=6, target_required=False, base_percent=42, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("shadow_flame", "shadowflame", "Черное пламя обжигает тело и душу врага.", mana_cost=14, cooldown=4, base_percent=44, circle=3, required_level=10, trainer_cost=85, book_required=True),
    AbilityTemplate("abyss_bolt", "abyssbolt", "Болт бездны пробивает защиту и волю цели.", mana_cost=19, cooldown=5, base_percent=41, circle=4, required_level=15, trainer_cost=120, book_required=True),
    AbilityTemplate("backstab", "backstab", "Подлый удар с высоким стартовым уроном.", move_cost=10, cooldown=3, base_percent=42, circle=2, required_level=5, trainer_cost=45),
    AbilityTemplate("trip", "trip", "Подсечь врага и сбить темп боя.", move_cost=7, cooldown=3, base_percent=50, circle=1, required_level=1, trainer_cost=0),
    AbilityTemplate("bless", "bless", "Наложить благословение на себя.", mana_cost=8, cooldown=5, target_required=False, base_percent=55, circle=2, required_level=5, trainer_cost=40),
)

CLASS_TEMPLATES: tuple[ClassTemplate, ...] = (
    ClassTemplate("berserker", "берсерк", "воины без магии", "Атакующий рукопашный боец с высоким уроном.", strength=2, hp=8, move=2, abilities=("bash", "rage")),
    ClassTemplate("shield_warrior", "воин щита", "воины без магии", "Башер: контроль боя, оглушения и пробитие строя врага.", vitality=2, hp=10, abilities=("bash", "fortify")),
    ClassTemplate("vanguard", "авангард", "воины без магии", "Атакующий воин с упором в давление и прорыв.", strength=1, agility=1, hp=7, move=3, abilities=("bash", "rage")),
    ClassTemplate("guardian", "защитник", "воины без магии", "Танк с упором на живучесть, броню и удержание линии.", vitality=3, hp=12, move=-2, abilities=("bash", "fortify")),
    ClassTemplate("paladin", "паладин", "воины с магией", "Тяжелый боец света с лечением и защитой.", strength=1, vitality=1, hp=8, mana=8, magic=True, abilities=("smite", "heal", "bless", "holy_wrath", "sacred_shield")),
    ClassTemplate("black_knight", "черный рыцарь", "воины с магией", "Темный рыцарь с боевой магией и истощением.", strength=2, hp=8, mana=6, magic=True, abilities=("dark_bolt", "curse", "soul_drain", "death_pact")),
    ClassTemplate("inquisitor", "инквизитор", "священники", "Каратель веры с контролем и поддержкой.", vitality=1, mana=10, magic=True, abilities=("smite", "curse", "bless", "exorcism", "zeal_purge")),
    ClassTemplate("healer", "лекарь", "священники", "Сильный саппорт и лечение группы.", mana=12, hp=2, magic=True, abilities=("heal", "bless", "blindness", "greater_heal", "salvation")),
    ClassTemplate("shaman", "шаман", "священники", "Гибрид поддержки и стихийной магии духов.", mana=10, move=4, magic=True, abilities=("heal", "curse", "ice_shard", "restore_energy", "spirit_link", "storm_totem")),
    ClassTemplate("warlock", "варлок", "маги", "Темный маг с мощными проклятиями.", mana=14, hp=-2, magic=True, abilities=("dark_bolt", "curse", "shadow_flame", "abyss_bolt")),
    ClassTemplate("fire_mage", "маг огня", "маги", "Чистый урон по одной цели и по площади.", mana=14, hp=-2, magic=True, abilities=("fireball", "fire_burst", "flame_storm")),
    ClassTemplate("water_mage", "маг воды", "маги", "Контроль и восстановление ресурсов.", mana=14, move=2, magic=True, abilities=("ice_shard", "heal", "ice_strike", "tidal_wave", "tsunami")),
    ClassTemplate("earth_mage", "маг земли", "маги", "Защита и устойчивость в обмен на скорость.", vitality=1, mana=12, move=-2, magic=True, abilities=("stone_skin", "bash", "stone_fist", "earth_shatter", "mountain_guard")),
    ClassTemplate("air_mage", "маг воздуха", "маги", "Высокая мобильность и быстрые заклинания.", agility=1, mana=12, move=6, magic=True, abilities=("lightning", "air_burst", "thunderstorm")),
    ClassTemplate("rogue", "разбойник", "разведчики", "Гибкий боец с высокой мобильностью.", agility=2, move=5, abilities=("trip", "backstab")),
    ClassTemplate("assassin", "ассасин", "разведчики", "Убийца с критическим уроном и скрытностью.", agility=3, hp=2, move=4, abilities=("backstab", "trip")),
)

RACE_BY_NAME = {template.name: template for template in RACE_TEMPLATES}
CLASS_BY_NAME = {template.name: template for template in CLASS_TEMPLATES}
ABILITY_BY_ID = {template.id: template for template in ABILITY_TEMPLATES}
RACE_BY_INDEX = {index + 1: template for index, template in enumerate(RACE_TEMPLATES)}
CLASS_BY_INDEX = {index + 1: template for index, template in enumerate(CLASS_TEMPLATES)}

# Друид в текущем билде реализован как класс "шаман" с природной/духовной магией.
# Ниже — целевая дорожная карта на 9 кругов заклинаний для дальнейшего наполнения.
DRUID_SPELL_CIRCLES: dict[int, list[tuple[str, str, bool]]] = {
    1: [
        ("heal", "Быстрое исцеление ран.", True),
        ("nature_touch", "Легкий природный урон и метка цели.", False),
        ("thorn_whip", "Хлесткий удар лозой с шансом сбить темп.", False),
        ("seed_guard", "Короткий природный щит из семян и коры.", False),
        ("wild_instinct", "Повышает уклонение и чуть ускоряет восстановление.", False),
        ("druidic_sense", "Обостряет чувства и обнаруживает угрозы.", False),
    ],
    2: [
        ("curse", "Ослабляющее проклятие природы.", True),
        ("ice_shard", "Ледяной осколок, замедляющий врага.", True),
        ("restore_energy", "Восстанавливает ману и запас сил.", True),
        ("root_snare", "Опутывает корнями и режет мобильность.", False),
        ("swarm_bite", "Насекомые наносят периодический урон.", False),
        ("moss_armor", "Моховой панцирь усиливает броню.", False),
    ],
    3: [
        ("spirit_link", "Связь с духами: лечение и подпитка маны.", True),
        ("forest_roar", "Духовный клич пугает и ослабляет цель.", False),
        ("vine_prison", "Тяжелые лозы удерживают врага.", False),
        ("moonfire", "Лунное пламя прожигает защиту.", False),
        ("life_bloom", "Накладывает постепенное восстановление HP.", False),
        ("beast_aspect", "Временный боевой аспект зверя.", False),
    ],
    4: [
        ("storm_totem", "Тотем бури: бафы и магический импульс.", True),
        ("earth_circle", "Круг камней усиливает защиту группы.", False),
        ("spirit_howl", "Духовный вой снижает меткость врага.", False),
        ("rain_of_thorns", "Дождь шипов наносит рваный урон.", False),
        ("ancestral_bark", "Кора предков резко снижает входящий урон.", False),
        ("wild_pulse", "Импульс природы лечит союзников рядом.", False),
    ],
    5: [
        ("solar_flare", "Солнечная вспышка обжигает и ослепляет.", False),
        ("frost_grove", "Ледяная роща замедляет врагов в зоне.", False),
        ("spirit_barrier", "Сильный барьер духов для выживания.", False),
        ("predator_call", "Призыв хищников наносит серию ударов.", False),
        ("regen_aura", "Постоянная аура регенерации для группы.", False),
    ],
    # Пользователь не задал число для 6 круга явно; выбрано 5 как плавный переход 5→4.
    6: [
        ("ancient_growth", "Мощный само-баф выживаемости и силы.", False),
        ("tempest_roots", "Корни и ветер одновременно ломают строй.", False),
        ("spirit_mirror", "Часть входящего урона отражается обратно.", False),
        ("moon_tide", "Комбинированный урон водой и лунным светом.", False),
        ("earth_ward", "Долгая каменная защита против burst-урона.", False),
    ],
    7: [
        ("primal_avatar", "Слияние с первозданным духом зверя.", False),
        ("cataclysm_vines", "Катастрофический залп лоз и шипов.", False),
        ("storm_choir", "Хор духов бури оглушает и режет броню.", False),
        ("emerald_rebirth", "Сильное восстановление после критического урона.", False),
    ],
    8: [
        ("worldsap", "Истощает силу врага и передает ее друиду.", False),
        ("eclipse_crown", "Корона затмения усиливает магический урон.", False),
        ("gaia_command", "Кратковременный контроль поля боя природой.", False),
    ],
    9: [
        ("heart_of_wild", "Абсолютный пик формы друида: урон, защита, реген.", False),
        ("apocalypse_bloom", "Финальный природный катаклизм по цели.", False),
    ],
}

DRUID_SPELL_CIRCLE_SIZES = {circle: len(spells) for circle, spells in DRUID_SPELL_CIRCLES.items()}
DRUID_ALL_SPELL_IDS = tuple(
    spell_id for circle in sorted(DRUID_SPELL_CIRCLES) for spell_id, _, _ in DRUID_SPELL_CIRCLES[circle]
)

_DRUID_SELF_CAST = {
    "seed_guard",
    "wild_instinct",
    "druidic_sense",
    "moss_armor",
    "life_bloom",
    "beast_aspect",
    "earth_circle",
    "ancestral_bark",
    "wild_pulse",
    "spirit_barrier",
    "regen_aura",
    "ancient_growth",
    "spirit_mirror",
    "earth_ward",
    "primal_avatar",
    "emerald_rebirth",
    "eclipse_crown",
    "gaia_command",
    "heart_of_wild",
}

_DRUID_LEVEL_BY_CIRCLE = {1: 1, 2: 5, 3: 10, 4: 15, 5: 20, 6: 25, 7: 30, 8: 35, 9: 40}

for circle, spells in DRUID_SPELL_CIRCLES.items():
    for spell_id, description, _ in spells:
        if spell_id in ABILITY_BY_ID:
            continue
        ABILITY_BY_ID[spell_id] = AbilityTemplate(
            id=spell_id,
            name=spell_id.replace("_", ""),
            description=description,
            mana_cost=6 + circle * 3,
            cooldown=min(8, 2 + circle // 2),
            target_required=spell_id not in _DRUID_SELF_CAST,
            base_percent=max(35, 56 - circle * 2),
            circle=circle,
            required_level=_DRUID_LEVEL_BY_CIRCLE[circle],
            trainer_cost=20 + circle * 20,
            book_required=circle >= 2,
        )


def class_abilities(class_name: str) -> tuple[str, ...]:
    if class_name == "шаман":
        return DRUID_ALL_SPELL_IDS
    return CLASS_BY_NAME[class_name].abilities


def render_race_menu() -> str:
    lines = ["Выберите расу:"]
    for index, template in RACE_BY_INDEX.items():
        lines.append(f"  {index}. {template.name} — {template.description}")
    return "\n".join(lines)


def render_class_menu() -> str:
    lines = ["Выберите класс:"]
    current_group = None
    for index, template in CLASS_BY_INDEX.items():
        if template.group != current_group:
            current_group = template.group
            lines.append(f"[{current_group}]")
        lines.append(f"  {index}. {template.name} — {template.description}")
    return "\n".join(lines)


def render_abilities_for_class(class_name: str, skill_levels: dict[str, int] | None = None) -> str:
    template = CLASS_BY_NAME[class_name]
    abilities = class_abilities(class_name)
    if not abilities:
        return "У вашего класса пока нет активных умений."
    lines = [f"Умения класса {class_name}:"]
    for ability_id in abilities:
        ability = ABILITY_BY_ID[ability_id]
        costs = []
        if ability.mana_cost:
            costs.append(f"{ability.mana_cost} mana")
        if ability.move_cost:
            costs.append(f"{ability.move_cost} move")
        cost_text = ", ".join(costs) if costs else "без стоимости"
        percent = ""
        if skill_levels is not None:
            if ability_id in skill_levels:
                percent = f" {skill_levels[ability_id]}%"
            else:
                percent = " не изучено"
        lines.append(
            f"- {ability.name}{percent}: круг {ability.circle}, ур. {ability.required_level}, "
            f"{ability.description} ({cost_text}, cd {ability.cooldown})"
        )
    return "\n".join(lines)
