SUPPORTED_EXCEL_FORMATS = {"*.xlsx", "*.xls"}

EXPANSIONS_SHORT = [
    {"name": "A1_genetic-apex", "code": "A1"},
    {"name": "A2_space-time-smackdown", "code": "A2"},
    {"name": "A3_celestial-guardians", "code": "A3"},
    {"name": "A4_wisdom-of-sea-and-sky", "code": "A4"},
    {"name": "B1_mega-brave", "code": "B1"},
    {"name": "promo-a", "code": "promo-a"},
    {"name": "promo-b", "code": "promo-b"},
]

EXPANSIONS = [
    {"name": "A1_genetic-apex", "code": "A1"},
    {"name": "A1a_mythical-island", "code": "A1a"},
    {"name": "A2_space-time-smackdown", "code": "A2"},
    {"name": "A2a_triumphant-light", "code": "A2a"},
    {"name": "A2b_shining-rivalry", "code": "A2b"},
    {"name": "A3_celestial-guardians", "code": "A3"},
    {"name": "A3a_extradimensional-crisis", "code": "A3a"},
    {"name": "A3b_eevee-groove", "code": "A3b"},
    {"name": "A4_wisdom-of-sea-and-sky", "code": "A4"},
    {"name": "A4a_secluded-springs", "code": "A4a"},
    {"name": "A4b_deluxe-pack-ex", "code": "A4b"},
    {"name": "B1_mega-brave", "code": "B1"},
    {"name": "B1a_crimson-blaze", "code": "B1a"},
    {"name": "promo-a", "code": "promo-a"},
    {"name": "promo-b", "code": "promo-b"},
]

BOOSTER_PACKS = [
    {"name": "Mew", "code": "A1a"},
    {"name": "Arceus", "code": "A2a"},
    {"name": "Shining-Revelry", "code": "A2b"},
    {"name": "Extradimensional-Crisis", "code": "A3a"},
    {"name": "Eevee-Grove", "code": "A3b"},
    {"name": "Secluded-Springs", "code": "A4a"},
    {"name": "Deluxe-Pack-ex", "code": "A4b"},
    {"name": "Crimson-Blaze", "code": "B1a"},
]

PACK_KEYS = [
    {"name": "Charizard", "code": "AN001_0020_00_000"},
    {"name": "Mewtwo", "code": "AN001_0010_00_000"},
    {"name": "Pikachu", "code": "AN001_0030_00_000"},
    {"name": "Mew", "code": "AN002_0010_00_000"},
    {"name": "Dialga", "code": "AN003_0010_00_000"},
    {"name": "Palkia", "code": "AN003_0020_00_000"},
    {"name": "Arceus", "code": "AN004_0010_00_000"},
    {"name": "Shining Revelry", "code": "AN005_0010_00_000"},
    {"name": "Lunala", "code": "AN006_0020_00_000"},
    {"name": "Solgaleo", "code": "AN006_0010_00_000"},
    {"name": "Extradimensional Crisis", "code": "AN007_0010_00_000"},
    {"name": "Eevee Grove", "code": "AN008_0010_00_000"},
    {"name": "Ho-oh", "code": "AN009_0010_00_000"},
    {"name": "Lugia", "code": "AN009_0020_00_000"},
    {"name": "Secluded Springs", "code": "AN010_0010_00_000"},
    {"name": "Deluxe Pack ex", "code": "AN011_0010_00_000"},
    {"name": "Mega Altaria", "code": "BN001_0030_00_000"},
    {"name": "Mega Blaziken", "code": "BN001_0010_00_000"},
    {"name": "Mega Gyarados", "code": "BN001_0020_00_000"},
    {"name": "Crimson Blaze", "code": "BN002_0010_00_000"},
]

MATCH_EXP_AND_PACK = {
    "A1": ["AN001_0010_00_000", "AN001_0020_00_000", "AN001_0030_00_000"],
    "A1a": "AN002_0010_00_000",
    "A2": ["AN003_0010_00_000", "AN003_0020_00_000"],
    "A2a": "AN004_0010_00_000",
    "A2b": "AN005_0010_00_000",
    "A3": ["AN006_0010_00_000", "AN006_0020_00_000"],
    "A3a": "AN007_0010_00_000",
    "A3b": "AN008_0010_00_000",
    "A4": ["AN009_0010_00_000", "AN009_0020_00_000"],
    "A4a": "AN010_0010_00_000",
    "A4b": "AN011_0010_00_000",
    "B1": ["BN001_0010_00_000", "BN001_0020_00_000", "BN001_0030_00_000"],
    "B1a": ["BN002_0010_00_000"],
}

WEAKNESS_MAP = {
    "grass": "fire",
    "fire": "water",
    "water": "lightning",
    "lightning": "fighting",
    "psychic": "darkness",
    "fighting": "grass",
    "darkness": "fighting",
    "metal": "fire",
    "colorless": "fighting",
    "dragon": "none",
}

CARD_REGIONS = {
    "type": {"top": 0.03, "bottom": 0.09, "left": 0.88, "right": 0.95},
    "weakness": {"top": 0.86, "bottom": 0.89, "left": 0.28, "right": 0.33},
    "attack": {"top": 0.55, "bottom": 0.80, "left": 0.05, "right": 0.30},
    "trainer": {"top": 0.03, "bottom": 0.06, "left": 0.05, "right": 0.15},
    "name": {"top": 0.037, "bottom": 0.13, "left": 0.04, "right": 0.65},
}

LANGUAGES = {
    "en_US": "English",
    "zh_TW": "Chinese",
    "ja_JP": "Japanese",
}
