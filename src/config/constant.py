SUPPORTED_EXCEL_FORMATS = {"*.xlsx", "*.xls"}

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
    {"name": "B1_mega-brave", "code": "B1"},
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
    {"name": "Deluxe Pack: ex", "code": "AN011_0010_00_000"},
    {"name": "Mega Altaria", "code": "BN001_0030_00_000"},
    {"name": "Mega Blaziken", "code": "BN001_0010_00_000"},
    {"name": "Mega Gyarados", "code": "BN001_0020_00_000"},
]

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
}
