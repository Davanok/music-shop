import json

from .models import *
from .services import DEFAULT_IMAGE, hash_password

SEED_CATEGORIES = [
    # (slug, name, description, image_url, parent_slug)
    # ── Root categories ──────────────────────────────────────────────────────
    ("guitars",           "Гитары",                  "Электрогитары, акустические и бас-гитары для сцены и студии.",              "https://images.unsplash.com/photo-1516924962500-2b4b3b99ea02?auto=format&fit=crop&w=900&q=80", None),
    ("drums",             "Барабаны",                "Ударные установки, малые барабаны, тарелки и перкуссия.",                   "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80", None),
    ("keyboards",         "Клавишные",               "Сценические пианино, синтезаторы, MIDI-контроллеры и рабочие станции.",     "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80", None),
    ("wind-instruments",  "Духовые инструменты",     "Саксофоны, трубы, флейты, кларнеты и другие духовые инструменты.",         "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80", None),
    ("parts-accessories", "Запчасти и аксессуары",   "Струны, палочки, чехлы, кабели, педали, трости и стойки.",                 "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", None),

    # ── Guitars ──────────────────────────────────────────────────────────────
    ("electric-guitars",  "Электрогитары",           "Solid-body, полуакустика и арchtop для любого стиля.",                     "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f?auto=format&fit=crop&w=900&q=80", "guitars"),
    ("acoustic-guitars",  "Акустические гитары",     "Дредноуты, концертные и джамбо для живого звука без усилителя.",           "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "guitars"),
    ("bass-guitars",      "Бас-гитары",              "4- и 5-струнные бас-гитары для сцены и студии.",                           "https://images.unsplash.com/photo-1558098329-a11cff621064?auto=format&fit=crop&w=900&q=80", "guitars"),
    ("guitar-amps",       "Усилители для гитары",    "Ламповые, транзисторные и моделирующие комбо и головы.",                   "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?auto=format&fit=crop&w=900&q=80", "guitars"),

    # ── Drums ─────────────────────────────────────────────────────────────────
    ("acoustic-drums",    "Акустические ударные",    "Кленовые, берёзовые и дубовые установки для студии и сцены.",              "https://images.unsplash.com/photo-1524230659092-07f99a75c013?auto=format&fit=crop&w=900&q=80", "drums"),
    ("electronic-drums",  "Электронные ударные",     "Компактные пэд-установки и модули для тихой практики и записи.",           "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80", "drums"),
    ("cymbals",           "Тарелки",                 "Хай-хэты, крэши, райды и сплэши ведущих брендов.",                        "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80", "drums"),
    ("percussion",        "Перкуссия",               "Кахоны, конги, бонго, шейкеры и маракасы.",                               "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7?auto=format&fit=crop&w=900&q=80", "drums"),

    # ── Keyboards ────────────────────────────────────────────────────────────
    ("synthesizers",      "Синтезаторы",             "Аналоговые, цифровые и виртуально-аналоговые синтезаторы.",               "https://images.unsplash.com/photo-1552422535-c45813c61732?auto=format&fit=crop&w=900&q=80", "keyboards"),
    ("digital-pianos",    "Цифровые пианино",        "Взвешенные клавиатуры с молоточковой механикой для дома и сцены.",         "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80", "keyboards"),
    ("midi-controllers",  "MIDI-контроллеры",        "Клавишные, пэд- и смешанные контроллеры для DAW и живых выступлений.",     "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?auto=format&fit=crop&w=900&q=80", "keyboards"),

    # ── Wind instruments ─────────────────────────────────────────────────────
    ("brass",             "Медные духовые",          "Трубы, тромбоны, валторны и тубы.",                                       "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80", "wind-instruments"),
    ("woodwinds",         "Деревянные духовые",      "Саксофоны, кларнеты, флейты и гобои.",                                    "https://images.unsplash.com/photo-1511192336575-5a79af67a629?auto=format&fit=crop&w=900&q=80", "wind-instruments"),

    # ── Parts & accessories ───────────────────────────────────────────────────
    ("strings-picks",     "Струны и медиаторы",      "Никелевые, стальные и нейлоновые струны, медиаторы всех форм и толщин.",   "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
    ("cases-bags",        "Чехлы и кейсы",           "Гигбэги, твёрдые кейсы и рэковые сумки для любых инструментов.",          "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
    ("cables-connectors", "Кабели и коннекторы",     "Инструментальные, балансные, MIDI и патч-кабели.",                        "https://images.unsplash.com/photo-1556379118-7034d926d258?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
    ("stands-mounts",     "Стойки и крепления",      "Стойки для гитар, микрофонов, клавишных и ударных.",                      "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
    ("effects-pedals",    "Эффекты и педали",        "Дисторшн, хорус, дилэй, лупер и мультиэффекты.",                          "https://images.unsplash.com/photo-1510915361894-db8b60106cb1?auto=format&fit=crop&w=900&q=80", "parts-accessories"),
]

SEED_PRODUCTS = [
    # ───────────────────────── ЭЛЕКТРОГИТАРЫ ─────────────────────────

    (
        "aurora-strat-black",
        "Электрогитара Aurora Strat Black",
        "electric-guitars",
        "Универсальная электрогитара с тремя синглами, удобным кленовым грифом и классическим звучанием для рока, блюза и поп-музыки.",
        Decimal("45990.00"),
        12,
        True,
        "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f"
    ),
    (
        "aurora-strat-red",
        "Электрогитара Aurora Strat Red",
        "electric-guitars",
        "Яркий инструмент для начинающих и продвинутых музыкантов с насыщенным чистым звуком.",
        Decimal("48990.00"),
        8,
        True,
        "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f"
    ),
    (
        "storm-les-paul",
        "Электрогитара Storm LP Standard",
        "electric-guitars",
        "Мощный звук хамбакеров, корпус из красного дерева и отличное сустейн-звучание.",
        Decimal("72990.00"),
        5,
        False,
        "https://images.unsplash.com/photo-1564186763535-ebb21ef5277f"
    ),

    # ───────────────────────── АКУСТИЧЕСКИЕ ─────────────────────────

    (
        "forest-dreadnought",
        "Акустическая гитара Forest Dreadnought",
        "acoustic-guitars",
        "Полноразмерная акустическая гитара с громким и насыщенным звучанием.",
        Decimal("24990.00"),
        15,
        True,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),
    (
        "forest-jumbo",
        "Акустическая гитара Forest Jumbo",
        "acoustic-guitars",
        "Большой корпус обеспечивает объемный звук и мощный бас.",
        Decimal("31990.00"),
        7,
        False,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),

    # ───────────────────────── БАС-ГИТАРЫ ─────────────────────────

    (
        "bassline-j4",
        "Бас-гитара BassLine J4",
        "bass-guitars",
        "Классическая четырехструнная бас-гитара для репетиций и выступлений.",
        Decimal("39990.00"),
        9,
        True,
        "https://images.unsplash.com/photo-1558098329-a11cff621064"
    ),
    (
        "bassline-j5",
        "Бас-гитара BassLine J5",
        "bass-guitars",
        "Пятиструнная модель для расширенного диапазона и современного звучания.",
        Decimal("55990.00"),
        4,
        False,
        "https://images.unsplash.com/photo-1558098329-a11cff621064"
    ),

    # ───────────────────────── УСИЛИТЕЛИ ─────────────────────────

    (
        "rockcube-20",
        "Комбоусилитель RockCube 20",
        "guitar-amps",
        "Компактный усилитель для домашних занятий мощностью 20 Вт.",
        Decimal("14990.00"),
        20,
        True,
        "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae"
    ),
    (
        "rockcube-50",
        "Комбоусилитель RockCube 50",
        "guitar-amps",
        "Мощный усилитель для репетиций и небольших концертов.",
        Decimal("26990.00"),
        10,
        False,
        "https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae"
    ),

    # ───────────────────────── УДАРНЫЕ ─────────────────────────

    (
        "studio-maple-5",
        "Ударная установка Studio Maple 5",
        "acoustic-drums",
        "Пятибарабанная установка из клена с глубоким и теплым звучанием.",
        Decimal("119990.00"),
        4,
        True,
        "https://images.unsplash.com/photo-1524230659092-07f99a75c013"
    ),
    (
        "stage-birch-kit",
        "Ударная установка Stage Birch",
        "acoustic-drums",
        "Березовые корпуса обеспечивают яркую атаку и отличную читаемость.",
        Decimal("139990.00"),
        3,
        False,
        "https://images.unsplash.com/photo-1524230659092-07f99a75c013"
    ),

    # ───────────────────────── ЭЛЕКТРОННЫЕ БАРАБАНЫ ─────────────────────────

    (
        "silent-drum-pro",
        "Электронная установка Silent Drum Pro",
        "electronic-drums",
        "Компактная установка для квартиры и домашней студии.",
        Decimal("89990.00"),
        6,
        True,
        "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7"
    ),
    (
        "silent-drum-max",
        "Электронная установка Silent Drum Max",
        "electronic-drums",
        "Продвинутая модель с сетчатыми пластиками и большим модулем звуков.",
        Decimal("149990.00"),
        2,
        True,
        "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7"
    ),

    # ───────────────────────── ТАРЕЛКИ ─────────────────────────

    (
        "bronze-crash-16",
        "Тарелка Bronze Crash 16",
        "cymbals",
        "Яркая крэш-тарелка для рок- и поп-музыки.",
        Decimal("10990.00"),
        15,
        False,
        "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7"
    ),
    (
        "bronze-ride-20",
        "Тарелка Bronze Ride 20",
        "cymbals",
        "Универсальный райд с четким пингом и насыщенным сустейном.",
        Decimal("15990.00"),
        9,
        False,
        "https://images.unsplash.com/photo-1519892300165-cb5542fb47c7"
    ),

    # ───────────────────────── СИНТЕЗАТОРЫ ─────────────────────────

    (
        "nova-synth-49",
        "Синтезатор Nova Synth 49",
        "synthesizers",
        "Современный синтезатор с большим количеством тембров и эффектов.",
        Decimal("54990.00"),
        11,
        True,
        "https://images.unsplash.com/photo-1552422535-c45813c61732"
    ),
    (
        "nova-synth-61",
        "Синтезатор Nova Synth 61",
        "synthesizers",
        "61 клавиша, арпеджиатор и профессиональные возможности редактирования.",
        Decimal("74990.00"),
        5,
        True,
        "https://images.unsplash.com/photo-1552422535-c45813c61732"
    ),

    # ───────────────────────── ЦИФРОВЫЕ ПИАНИНО ─────────────────────────

    (
        "nova-stage-88",
        "Цифровое пианино Nova Stage 88",
        "digital-pianos",
        "Взвешенная клавиатура с молоточковой механикой и реалистичным звучанием.",
        Decimal("99990.00"),
        6,
        True,
        "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0"
    ),
    (
        "home-piano-88",
        "Цифровое пианино Home Piano 88",
        "digital-pianos",
        "Домашняя модель в классическом корпусе с тремя педалями.",
        Decimal("124990.00"),
        3,
        False,
        "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0"
    ),

    # ───────────────────────── MIDI ─────────────────────────

    (
        "midi-key49",
        "MIDI-контроллер KeyControl 49",
        "midi-controllers",
        "49 чувствительных клавиш для работы в любой DAW.",
        Decimal("17990.00"),
        18,
        True,
        "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0"
    ),
    (
        "midi-key61",
        "MIDI-контроллер KeyControl 61",
        "midi-controllers",
        "61 клавиша и набор назначаемых фейдеров.",
        Decimal("24990.00"),
        10,
        False,
        "https://images.unsplash.com/photo-1520523839897-bd0b52f945a0"
    ),

    # ───────────────────────── ДУХОВЫЕ ─────────────────────────

    (
        "brassline-trumpet",
        "Труба BrassLine Bb",
        "brass",
        "Классическая труба для музыкальных школ и оркестров.",
        Decimal("44990.00"),
        5,
        False,
        "https://images.unsplash.com/photo-1511192336575-5a79af67a629"
    ),
    (
        "alto-sax-pro",
        "Альт-саксофон Sax Pro",
        "woodwinds",
        "Надежный инструмент с богатым тембром и качественной механикой.",
        Decimal("89990.00"),
        3,
        True,
        "https://images.unsplash.com/photo-1511192336575-5a79af67a629"
    ),

    # ───────────────────────── СТРУНЫ ─────────────────────────

    (
        "electric-strings-09",
        "Струны для электрогитары 09-42",
        "strings-picks",
        "Комплект никелированных струн для электрогитары.",
        Decimal("790.00"),
        150,
        False,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),
    (
        "electric-strings-10",
        "Струны для электрогитары 10-46",
        "strings-picks",
        "Популярный комплект для универсального звучания.",
        Decimal("890.00"),
        140,
        False,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),

    # ───────────────────────── КЕЙСЫ ─────────────────────────

    (
        "gigbag-electric",
        "Чехол для электрогитары Premium",
        "cases-bags",
        "Утепленный чехол с толстыми стенками и карманами.",
        Decimal("4990.00"),
        25,
        False,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),
    (
        "hardcase-electric",
        "Жесткий кейс для электрогитары",
        "cases-bags",
        "Максимальная защита инструмента во время перевозки.",
        Decimal("10990.00"),
        8,
        False,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),

    # ───────────────────────── КАБЕЛИ ─────────────────────────

    (
        "instrument-cable-3m",
        "Инструментальный кабель 3 м",
        "cables-connectors",
        "Надежный кабель с низким уровнем шума.",
        Decimal("990.00"),
        80,
        False,
        "https://images.unsplash.com/photo-1556379118-7034d926d258"
    ),
    (
        "instrument-cable-6m",
        "Инструментальный кабель 6 м",
        "cables-connectors",
        "Профессиональный кабель для сцены и студии.",
        Decimal("1490.00"),
        65,
        False,
        "https://images.unsplash.com/photo-1556379118-7034d926d258"
    ),

    # ───────────────────────── СТОЙКИ ─────────────────────────

    (
        "guitar-stand-a",
        "Стойка для гитары складная",
        "stands-mounts",
        "Легкая и прочная стойка для хранения инструмента.",
        Decimal("1990.00"),
        40,
        False,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),
    (
        "keyboard-stand-x",
        "Стойка для клавишных X-Type",
        "stands-mounts",
        "Регулируемая стойка для синтезаторов и пианино.",
        Decimal("3990.00"),
        20,
        False,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),

    # ───────────────────────── ПЕДАЛИ ─────────────────────────

    (
        "drive-pedal",
        "Педаль перегруза DriveBox",
        "effects-pedals",
        "Классический овердрайв для блюза и рока.",
        Decimal("6990.00"),
        14,
        True,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),
    (
        "delay-pedal",
        "Педаль Delay Echo",
        "effects-pedals",
        "Цифровой дилэй с несколькими режимами повторов.",
        Decimal("8990.00"),
        10,
        True,
        "https://images.unsplash.com/photo-1510915361894-db8b60106cb1"
    ),
]

SEED_USERS = [
    ("ivan.petrov@mail.ru", "Иван Петров"),
    ("sergey.volkov@mail.ru", "Сергей Волков"),
    ("alexey.ivanov@mail.ru", "Алексей Иванов"),
    ("dmitry.sokolov@mail.ru", "Дмитрий Соколов"),
    ("nikita.kozlov@mail.ru", "Никита Козлов"),
    ("artem.popov@mail.ru", "Артем Попов"),
    ("maksim.egorov@mail.ru", "Максим Егоров"),
    ("roman.fedorov@mail.ru", "Роман Федоров"),
    ("vladislav.orlov@mail.ru", "Владислав Орлов"),
    ("anton.belyaev@mail.ru", "Антон Беляев"),
    ("anna.smirnova@mail.ru", "Анна Смирнова"),
    ("maria.kuznetsova@mail.ru", "Мария Кузнецова"),
    ("elena.romanova@mail.ru", "Елена Романова"),
    ("ekaterina.sokolova@mail.ru", "Екатерина Соколова"),
    ("olga.morozova@mail.ru", "Ольга Морозова"),
]

SEED_REVIEWS = [
    # Aurora Strat
    ("aurora-strat-black", "Иван Петров", 5, "Отличная гитара. Очень удобный гриф и приятное звучание."),
    ("aurora-strat-black", "Сергей Волков", 4, "За свои деньги отличный инструмент."),
    ("aurora-strat-black", "Анна Смирнова", 5, "Качественная сборка и красивый внешний вид."),
    ("aurora-strat-black", "Максим Егоров", 5, "Подошла для репетиций и записи дома."),

    # LP
    ("storm-les-paul", "Алексей Иванов", 5, "Мощный звук, идеально для тяжелой музыки."),
    ("storm-les-paul", "Роман Федоров", 5, "Очень понравился сустейн и качество электроники."),
    ("storm-les-paul", "Дмитрий Соколов", 4, "Тяжеловата, но звук шикарный."),

    # Acoustic
    ("forest-dreadnought", "Мария Кузнецова", 5, "Громкая и насыщенная акустика."),
    ("forest-dreadnought", "Ольга Морозова", 4, "Хороший вариант для начинающих."),
    ("forest-dreadnought", "Елена Романова", 5, "Красивый тембр и удобный корпус."),

    # Bass
    ("bassline-j4", "Антон Беляев", 5, "Отличный бас за свою цену."),
    ("bassline-j4", "Никита Козлов", 4, "Удобный инструмент для концертов."),
    ("bassline-j4", "Владислав Орлов", 5, "Хорошо сидит в миксе."),

    # Piano
    ("nova-stage-88", "Мария Кузнецова", 5, "Клавиатура очень приятная."),
    ("nova-stage-88", "Екатерина Соколова", 5, "Похоже на настоящее пианино."),
    ("nova-stage-88", "Анна Смирнова", 4, "Большой набор звуков и функций."),

    # Electronic drums
    ("silent-drum-pro", "Артем Попов", 5, "Соседи довольны, играю даже ночью."),
    ("silent-drum-pro", "Сергей Волков", 4, "Отличный вариант для квартиры."),
    ("silent-drum-pro", "Максим Егоров", 5, "Очень понравились сетчатые пэды."),

    # Trumpet
    ("brassline-trumpet", "Дмитрий Соколов", 5, "Хорошая труба для обучения."),
    ("brassline-trumpet", "Роман Федоров", 4, "Интонация точная, играть приятно."),

    # Sax
    ("alto-sax-pro", "Елена Романова", 5, "Богатый и насыщенный звук."),
    ("alto-sax-pro", "Ольга Морозова", 5, "Отличный инструмент для выступлений."),
    ("alto-sax-pro", "Антон Беляев", 4, "Качественная механика."),

    # Drive pedal
    ("drive-pedal", "Алексей Иванов", 5, "Классический перегруз."),
    ("drive-pedal", "Никита Козлов", 5, "Хорошо работает с ламповым усилителем."),
    ("drive-pedal", "Владислав Орлов", 4, "Звук плотный и читаемый."),

    # Delay
    ("delay-pedal", "Максим Егоров", 5, "Красивые повторы и много настроек."),
    ("delay-pedal", "Сергей Волков", 4, "Удобная и понятная педаль."),
]

SEED_ADDRESSES = [
    ("Иван Петров", "Россия", "Москва", "ул. Тверская, д. 15", "125009"),
    ("Сергей Волков", "Россия", "Санкт-Петербург", "Невский проспект, д. 48", "191025"),
    ("Алексей Иванов", "Россия", "Казань", "ул. Баумана, д. 22", "420111"),
    ("Дмитрий Соколов", "Россия", "Екатеринбург", "ул. Малышева, д. 74", "620014"),
    ("Никита Козлов", "Россия", "Новосибирск", "Красный проспект, д. 88", "630091"),
    ("Артем Попов", "Россия", "Самара", "ул. Ленинградская, д. 45", "443099"),
    ("Максим Егоров", "Россия", "Краснодар", "ул. Красная, д. 101", "350000"),
    ("Роман Федоров", "Россия", "Челябинск", "ул. Кирова, д. 12", "454091"),
    ("Владислав Орлов", "Россия", "Уфа", "ул. Ленина, д. 55", "450077"),
    ("Антон Беляев", "Россия", "Ростов-на-Дону", "пр. Буденновский, д. 60", "344000"),
    ("Анна Смирнова", "Россия", "Москва", "ул. Арбат, д. 18", "119002"),
    ("Мария Кузнецова", "Россия", "Сочи", "ул. Навагинская, д. 11", "354000"),
    ("Елена Романова", "Россия", "Пермь", "ул. Ленина, д. 39", "614000"),
    ("Екатерина Соколова", "Россия", "Воронеж", "пр. Революции, д. 34", "394036"),
    ("Ольга Морозова", "Россия", "Тюмень", "ул. Республики, д. 86", "625000"),
]

SEED_ORDERS = [
    ("ORD-100001", "Иван Петров", OrderStatus.COMPLETED, "aurora-strat-black", 1),
    ("ORD-100002", "Сергей Волков", OrderStatus.COMPLETED, "silent-drum-pro", 1),
    ("ORD-100003", "Анна Смирнова", OrderStatus.SHIPPED, "nova-stage-88", 1),
    ("ORD-100004", "Алексей Иванов", OrderStatus.COMPLETED, "storm-les-paul", 1),
    ("ORD-100005", "Максим Егоров", OrderStatus.PROCESSING, "drive-pedal", 2),
    ("ORD-100006", "Мария Кузнецова", OrderStatus.COMPLETED, "forest-dreadnought", 1),
    ("ORD-100007", "Дмитрий Соколов", OrderStatus.CANCELLED, "brassline-trumpet", 1),
    ("ORD-100008", "Никита Козлов", OrderStatus.COMPLETED, "bassline-j4", 1),
    ("ORD-100009", "Владислав Орлов", OrderStatus.SHIPPED, "delay-pedal", 1),
    ("ORD-100010", "Антон Беляев", OrderStatus.PROCESSING, "alto-sax-pro", 1),
    ("ORD-100011", "Елена Романова", OrderStatus.COMPLETED, "nova-synth-61", 1),
    ("ORD-100012", "Роман Федоров", OrderStatus.COMPLETED, "rockcube-50", 1),
    ("ORD-100013", "Ольга Морозова", OrderStatus.SHIPPED, "electric-strings-09", 3),
    ("ORD-100014", "Екатерина Соколова", OrderStatus.COMPLETED, "midi-key49", 1),
    ("ORD-100015", "Артем Попов", OrderStatus.PROCESSING, "studio-maple-5", 1),
]


def seed_data():
    # ── 1. Categories (two-pass: roots first, then children) ─────────────────
    categories: dict[str, Category] = {}

    for pass_no in range(2):
        for slug, name, description, image_url, parent_slug in SEED_CATEGORIES:
            is_root = parent_slug is None
            if (pass_no == 0) != is_root:   # pass 0 → roots; pass 1 → children
                continue

            category = Category.query.filter_by(slug=slug).one_or_none() or Category(slug=slug)
            category.name        = name
            category.description = description
            category.image_url   = image_url or DEFAULT_IMAGE
            category.parent      = categories[parent_slug] if parent_slug else None
            db.session.add(category)
            categories[slug] = category

        db.session.flush()   # assigns IDs after each pass so children can reference parents

    # ── 2. Products ───────────────────────────────────────────────────────────
    for slug, name, category_slug, description, price, stock, featured, image_url in SEED_PRODUCTS:
        product = Product.query.filter_by(slug=slug).one_or_none() or Product(slug=slug)
        product.name         = name
        product.category     = categories[category_slug]
        product.description  = description
        product.price        = price
        product.stock        = stock
        product.featured     = featured
        product.image_url    = image_url
        product.gallery_json = json.dumps([image_url])
        db.session.add(product)

    for email, name in SEED_USERS:
        if not User.query.filter_by(email=email).first():
            db.session.add(User(
                email=email,
                name=name,
                password_hash=hash_password("12345678"),
                role="user"
            ))

    for product_slug, user_name, rating, comment in SEED_REVIEWS:
        product = Product.query.filter_by(slug=product_slug).first()
        user = User.query.filter_by(name=user_name).first()

        if product and user:
            exists = Review.query.filter_by(
                product_id=product.id,
                user_id=user.id,
                comment=comment
            ).first()

            if not exists:
                db.session.add(Review(
                    product_id=product.id,
                    user_id=user.id,
                    rating=rating,
                    comment=comment
                ))

    for name, country, city, street, postal_code in SEED_ADDRESSES:
        user = User.query.filter_by(name=name).first()

        if user and not Address.query.filter_by(user_id=user.id).first():
            db.session.add(Address(
                user_id=user.id,
                country=country,
                city=city,
                street=street,
                postal_code=postal_code
            ))

    for order_number, user_name, status, product_slug, quantity in SEED_ORDERS:
        user = User.query.filter_by(name=user_name).first()
        product = Product.query.filter_by(slug=product_slug).first()

        if not user or not product:
            continue

        address = Address.query.filter_by(user_id=user.id).first()

        if Order.query.filter_by(order_number=order_number).first():
            continue

        order = Order(
            order_number=order_number,
            user_id=user.id,
            address_id=address.id if address else None,
            status=status,
            delivery_method=DeliveryMethod.DELIVERY,
            assembly_option=AssemblyOption.NOT_REQUIRED,
            shipping=Decimal("500.00"),
            assembly_cost=Decimal("0.00")
        )

        db.session.add(order)
        db.session.flush()

        db.session.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=product.price
        ))

    # ── 3. Settings & admin user ──────────────────────────────────────────────
    delivery_setting = AppSetting.query.filter_by(key="delivery_price").one_or_none() or AppSetting(key="delivery_price")
    delivery_setting.value = "500.00"
    db.session.add(delivery_setting)

    assembly_setting = AppSetting.query.filter_by(key="assembly_price").one_or_none() or AppSetting(key="assembly_price")
    assembly_setting.value = "1000.00"
    db.session.add(assembly_setting)

    if not User.query.filter_by(email="admin@music-shop.local").one_or_none():
        db.session.add(User(
            email="admin@music-shop.local",
            name="Главный администратор",
            password_hash=hash_password("admin12345"),
            role="admin",
        ))

    if not User.query.filter_by(email="manager@music-shop.local").one_or_none():
        db.session.add(User(
            email="manager@music-shop.local",
            name="Менеджер магазина",
            password_hash=hash_password("manager12345"),
            role="manager",
        ))

    if not User.query.filter_by(email="user@music-shop.local").one_or_none():
        db.session.add(User(
            email="user@music-shop.local",
            name="Обычный пользователь",
            password_hash=hash_password("user12345"),
            role="user",
        ))

    db.session.commit()
