entrance = "Welcome( again)? to \\w+'s (.*)!"
price = "[^(only)] (a|\\d+) (.*) \\(unpaid, (\\d+) zorkmids\\)\\."
offer = "offers (\\d+) gold pieces for your (.*)"

types = {
    "general":                         "random",
    "used armor dealership":           "90/10 arm/weap",
    "second-hand bookstore":           "90/10 scroll/books",
    "liquor emporium":                 "potions",
    "antique weapons outlet" :         "90/10 weap/armor",
    "delicatessen":                    "83/14/3 food/drink/icebox",
    "jewelers":                        "85/10/5 ring/gems/amu",
    "quality apparel and accessories": "90/10 wand/misc",
    "hardware store":                  "tools",
    "rare books":                      "90/10 books/scrolls",
    "lighting store":                  "97/3 light/m.lamp" 
}

amulets = set([
    ("change", 150, 130, None),
    ("ESP", 150, 175, None),
    ("life saving", 150, 75, None),
    ("magical breathing", 150, 65, None),
    ("reflection", 150, 75, None),
    ("restful sleep", 150, 135, None),
    ("strangulation", 150, 135, None),
    ("unchanging", 150, 45, None),
    ("versus poison", 150, 165, None),
    ("imitation AoY", 0, 0, None),
    ("Yendor", 30000, 0, None),
])

weapons = { 
    "dagger": set([
        ("orcish dagger", 4, 12, "crude dagger"),
        ("dagger", 4, 30, None),
        ("silver dagger", 40, 3, None),
        ("athame", 4, 0, None),
        ("elven dagger", 4, 10, "runed dagger"),
    ]),
    "knife": set([
        ("worm tooth", 2, 0, None),
        ("knife", 4, 20, None),
        ("shito", 4, 20, None),
        ("stiletto", 4, 5, None),
        ("scalpel", 6, 0, None),
        ("crysknife", 100, 0, None),
    ]),
    "axe": set([
        ("axe", 8, 40, None),
        ("battle-axe", 40, 10, "double-headed axe"),
    ]),
    "short sword": set([
        ("orcish short sword", 10, 3, "crude short sword"),
        ("short sword", 10, 8, None),
        ("wakizashi", 10, 8, None),
        ("dwarvish short sword", 10, 2, "broad short sword"),
        ("elvish short sword", 10, 2, "runed short sword"),
    ]),
    "broadsword": set([
        ("broadsword", 10, 8, None),
        ("ninja-to", 10, 8, None),
        ("runesword", 300, 0, "runed broadsword"),
        ("elven broadsword", 10, 4, "runed broadsword"),
    ]),
    "long sword": set([
        ("long sword", 15, 50, None),
        ("katana", 80, 4, "samurai sword"),
    ]),
    "two-handed sword": set([
        ("two-handed sword", 50, 22, None),
        ("tsurugi", 500, 0, "long samurai sword"),
    ]),
    "club": set([
        ("club", 3, 12, None),
        ("aklys", 3, 8, "thonged club"),
    ]),
    "flail": set([
        ("flail", 4, 40, None),
        ("nunchaku", 4, 40, None),
        ("grappling hook", 50, 0, "iron hook"),
    ]),
    "polearm": set([
        ("partisan", 10, 5, "vulgar polearm"),
        ("fauchard", 5, 6, "pole sickle"),
        ("glaive", 6, 8, "single-edged polearm"),
        ("naginata", 6, 8, "single-edged polearm"),
        ("bec-de-corbin", 8, 4, "beaked polearm"),
        ("spetum", 5, 5, "forked polearm"),
        ("lucern hammer", 7, 5, "pronged polearm"),
        ("guisarme", 5, 6, "pruning hook"),
        ("ranseur", 6, 5, "hilted polearm"),
        ("voulge", 5, 4, "pole cleaver"),
        ("bill-guisarme", 7, 4, "hooked polearm"),
        ("bardiche", 7, 4, "long poleaxe"),
        ("halberd", 10, 8, "angled poleaxe"),
    ]),
    "spear": set([
        ("orcish", 3, 13, "crude spear"),
        ("spear", 3, 50, None),
        ("silver", 40, 2, None),
        ("elven", 3, 10, "runed spear"),
        ("dwarvish", 3, 12, "stout spear"),
    ]),
    "bow": set([
        ("orcish", 60, 12, "crude bow"),
        ("bow", 60, 24, None),
        ("elven", 60, 12, "runed bow"),
        ("yumi", 60, 0, "long bow"),
    ]),
    "whip": set([
        ("bullwhip", 4, 2, None),
        ("rubber hose", 3, 0, None),
    ]),
}

spellbooks = set([
    ("blank paper", 0, 18, None),
    ("Book of the Dead", 10000, 0, None),
    ("force bolt", 100, 35, None),
    ("drain life", 200, 10, None),
    ("magic missile", 200, 45, None),
    ("cone of cold", 400, 10, None),
    ("fireball", 400, 20, None),
    ("finger of death", 700, 5, None),
    ("healing", 100, 40, None),
    ("cure blindness", 200, 25, None),
    ("cure sickness", 300, 32, None),
    ("extra healing", 300, 27, None),
    ("stone to flesh", 300, 15, None),
    ("restore ability", 400, 25, None),
    ("detect monsters", 100, 43, None),
    ("light", 100, 45, None),
    ("detect food", 200, 30, None),
    ("clairvoyance", 300, 15, None),
    ("detect unseen", 300, 20, None),
    ("identify", 300, 20, None),
    ("detect treasure", 400, 20, None),
    ("magic mapping", 500, 18, None),
    ("sleep", 100, 50, None),
    ("confuse monster", 200, 30, None),
    ("slow monster", 200, 30, None),
    ("cause fear", 300, 25, None),
    ("charm monster", 300, 20, None),
    ("protection", 100, 18, None),
    ("create monster", 200, 35, None),
    ("remove curse", 300, 25, None),
    ("create familiar", 600, 10, None),
    ("turn undead", 600, 16, None),
    ("jumping", 100, 20, None),
    ("haste self", 300, 33, None),
    ("invisibility", 400, 25, None),
    ("levitation", 400, 20, None),
    ("teleport away", 600, 15, None),
    ("knock", 100, 35, None),
    ("wizard lock", 200, 30, None),
    ("dig", 500, 20, None),
    ("polymorph", 600, 10, None),
    ("cancellation", 700, 15, None),
])

scrolls = set([
    ("mail", 0, 0, "stamped"),
    ("identify", 20, 180, None),
    ("light", 50, 90, None),
    ("blank paper", 60, 28, "unlabeled"),
    ("enchant weapon", 60, 80, None),
    ("enchant armor", 80, 63, None),
    ("remove curse", 80, 65, None),
    ("confuse monster", 100, 53, None),
    ("destroy armor", 100, 45, None),
    ("fire", 100, 30, None),
    ("food detection", 100, 25, None),
    ("gold detection", 100, 33, None),
    ("magic mapping", 100, 45, None),
    ("scare monster", 100, 35, None),
    ("teleportation", 100, 55, None),
    ("amnesia", 200, 35, None),
    ("create monster", 200, 45, None),
    ("earth", 200, 18, None),
    ("taming", 200, 15, None),
    ("charging", 300, 15, None),
    ("genocide", 300, 15, None),
    ("punishment", 300, 15, None),
    ("stinking cloud", 300, 15, None),
])

potions = set([
    ("booze", 50, 42, None),
    ("fruit juice", 50, 42, None),
    ("see invisible", 50, 42, None),
    ("sickness", 50, 42, None),
    ("confusion", 100, 42, None),
    ("extra healing", 100, 47, None),
    ("hallucination", 100, 40, None),
    ("healing", 100, 57, None),
    ("restore ability", 100, 40, None),
    ("sleeping", 100, 42, None),
    ("water", 100, 92, "clear"),
    ("blindness", 150, 40, None),
    ("gain energy", 150, 42, None),
    ("invisibility", 150, 40, None),
    ("monster detection", 150, 40, None),
    ("object detection", 150, 42, None),
    ("enlightenment", 200, 20, None),
    ("full healing", 200, 10, None),
    ("levitation", 200, 42, None),
    ("polymorph", 200, 10, None),
    ("speed", 200, 42, None),
    ("acid", 250, 10, None),
    ("oil", 250, 30, None),
    ("gain ability", 300, 42, None),
    ("gain level", 300, 20, None),
    ("paralysis", 300, 42, None),
])

rings = set([
    ("meat ring", 5, 0, None), 
    ("adornment",100, 1, None),
    ("hunger",100, 1, None),
    ("protection",100, 1, None),
    ("protection from shape changers", 100, 1, None),
    ("stealth", 100, 1, None),
    ("sustain ability", 100, 1, None),
    ("warning", 100, 1, None),
    ("aggravate monster", 150, 1, None),
    ("cold resistance", 150, 1, None),
    ("gain constitution",150, 1, None),
    ("gain strength",150, 1, None),
    ("increase accuracy",150, 1, None),
    ("increase damage",150, 1, None),
    ("invisibility", 150, 1, None),
    ("poison resistance", 150, 1, None),
    ("see invisible", 150, 1, None),
    ("shock resistance", 150, 1, None),
    ("fire resistance", 200, 1, None),
    ("free action", 200, 1, None),
    ("levitation", 200, 1, None),
    ("regeneration", 200, 1, None),
    ("searching", 200, 1, None),
    ("slow digestion", 200, 1, None),
    ("teleportation", 200, 1, None),
    ("conflict", 300, 1, None),
    ("polymorph", 300, 1, None),
    ("polymorph control", 300, 1, None),
    ("teleport control", 300, 1, None),
])

wands = set([
    ("light", 100, 95, None),
    ("nothing", 100, 25, None),
    ("digging", 150, 55, None),
    ("enlightenment", 150, 15, None),
    ("locking", 150, 25, None),
    ("magic missile", 150, 50, None),
    ("make invisible", 150, 45, None),
    ("opening", 150, 25, None),
    ("probing", 150, 30, None),
    ("secret door detection", 150, 50, None),
    ("slow monster", 150, 50, None),
    ("speed monster", 150, 50, None),
    ("striking", 150, 75, None),
    ("undead turning", 150, 50, None),
    ("cold", 175, 40, None),
    ("fire", 175, 40, None),
    ("lightning", 175, 40, None),
    ("sleep", 175, 50, None),
    ("cancellation", 200, 45, None),
    ("create monster", 200, 45, None),
    ("polymorph", 200, 45, None),
    ("teleportation", 200, 45, None),
    ("death", 500, 5, None),
    ("wishing", 500, 5, None),
])

armor = {
    "shirts": set([
        ("hawaiian shirt", 3, 8, None),
        ("t-shirt", 2, 2, None),
    ]),
    "suits": set([
        ("leather jacket", 10, 12, None),
        ("leather armor", 5, 82, None),
        ("orcish ring mail", 80, 20, "crude ring mail"),
        ("studded leather armor", 15, 72, None),
        ("ring mail", 100, 72, None),
        ("scale mail", 45, 72, None),
        ("orcish chain mail", 75, 20, "crude chain mail"),
        ("chain mail", 75, 72, None),
        ("elven mithril coat", 240, 15, None),
        ("splint mail", 80, 62, None),
        ("banded mail", 90, 72, None),
        ("dwarvish mithril coat", 240, 10, None),
        ("bronze plate mail", 400, 25, None),
        ("plate mail", 600, 44, None),
        ("tanko", 600, 44, None),
        ("crystal plate mail", 820, 10, None),
    ]),
    "cloaks": set([
        ("orcish cloak", 40, 8, "coarse mantelet"),
        ("dwarvish cloak", 50, 8, "hooded cloak"),
        ("leather cloak", 40, 8, None),
        ("cloak of displacement", 50, 10, "piece of cloth"),
        ("oilskin cloak", 50, 10, "slippery cloak"),
        ("alchemy smock", 50, 9, "apron"),
        ("cloak of invisibility", 60, 10, "opera cloak"),
        ("cloak of magic resistance", 60, 2, "ornamental cape"),
        ("elven cloak", 60, 8, "faded pall"),
        ("robe", 50, 3, None),
        ("cloak of protection", 50, 9, "tattered cape"),
    ]),
    "helmets": set([
        ("fedora", 1, 0, None),
        ("dunce cap", 1, 3, "conical hat"),
        ("cornuthaum", 80, 3, "conical hat"),
        ("dented pot", 8, 2, None),
        ("elven leather helm", 8, 6, "leather hat"),
        ("helmet", 10, 10, "plumed helmet"),
        ("kabuto", 10, 10, "plumed helmet"),
        ("orcish helm", 10, 6, "iron skull cap"),
        ("helm of billiance", 50, 6, "etched helmet"),
        ("helm of opposite alignment", 50, 6, "crested helmet"),
        ("helm of telepathy", 50, 2, "visored helmet"),
        ("dwarvish iron helm", 20, 6, "hard hat"),
    ]),
    "gloves": set([
        ("leather gloves", 8, 16, "old gloves"),
        ("yugake", 8, 16, "old gloves"),
        ("gauntlets of dexterity", 50, 8, "padded gloves"),
        ("gauntlets of fumbling", 50, 8, "riding gloves"),
        ("gauntlets of power", 50, 8, "fencing gloves"),
    ]),
    "shields": set([
        ("small shield", 3, 6, None),
        ("orcish shield", 7, 2, "red-eyed shield"),
        ("Uruk-hai shield", 7, 2, "white-handed shield"),
        ("elven shield", 7, 2, "blue and green shield"),
        ("dwarvish roundshield", 10, 4, "large round shield"),
        ("large shield", 10, 7, None),
        ("shield of reflection", 50, 3, "polished silver shield"),
    ]),
    "boots": set([
        ("low boots", 8, 25, "walking shoes"),
        ("elven boots", 8, 12, "mud boots"),
        ("kicking boots", 8, 12, "buckled boots"),
        ("fumble boots", 30, 12, "riding boots"),
        ("levitation boots", 30, 12, "snow boots"),
        ("jumping boots", 50, 12, "hiking boots"),
        ("speed boots", 50, 12, "combat boots"),
        ("water walking boots", 50, 12, "jungle boots"),
        ("high boots", 12, 15, "jackboots"),
        ("iron shoes", 16, 7, "hard shoes"),
    ]),
}

def buy_price_markup(charisma):
    if charisma < 6:
        return 1
    elif charisma == 6 or charisma == 7:
        return 0.50
    elif 8 <= charisma <= 10:
        return 0.333
    elif 11 <= charisma <= 15:
        return 0
    elif charisma == 16 or charisma == 17:
        return -0.25
    elif charisma == 18:
        return -0.333
    elif charisma > 18:
        return -0.50

def get_item_set(name):
    if "amulet" in name:
        return amulets
    elif "spellbook" in name:
        return spellbooks
    elif "scroll" in name:
        return scrolls
    elif "potion" in name:
        return potions
    elif "ring" in name:
        return rings
    elif "wand" in name:
        return wands
    elif "dagger" in name:
        return weapons["dagger"]
    elif "knife" in name:
        return weapons["knife"]
    elif "axe" in name:
        return weapons["axe"]
    elif "short sword" in name:
        return weapons["short sword"]
    elif "broadsword" in name:
        return weapons["broadsword"]
    elif "two-handed sword" in name or "long samurai sword" in name:
        return weapons["two-handed sword"]
    elif "long sword" in name or "samurai sword" in name:
        return weapons["long sword"]
    elif "club" in name:
        return weapons["club"]
    elif "flail" in name or "nanchaku" in name or "iron hook" in name:
        return weapons["flail"]
    elif "polearm" in name or "poleaxe" in name or "sickle" in name or "pruning hook" in name:
        return weapons["polearm"]
    elif "spear" in name:
        return weapons["spear"]
    elif "box" in name:
        return weapons["bow"]
    elif "whip" in name:
        return weapons["whip"]
    elif "shirt" in name:
        return armor["shirts"]
    elif "jacket" in name or \
            "armor" in name or \
            "mail" in name or \
            "coat" in name or \
            "tanko" in name:
        return armor["suits"]
    elif "cloak" in name or \
            "smock" in name or \
            "mantelet" in name or \
            "cape" in name or \
            "pall" in name or \
            "apron" in name or \
            "cloth" in name:
        return armor["cloaks"]
    elif "hat" in name or "helm" in name:
        return armor["helmets"]
    elif "gloves" in name:
        return armor["gloves"]
    elif "shield" in name:
        return armor["shields"]
    elif "shoes" in name or "boots" in name:
        return armor["boots"]

def buy_identify(charisma, item, price, sucker=False):
    possibles = get_item_set(item)
    if possibles is None:
        return set() 

    markup = buy_price_markup(charisma)
    price_adjusted = [(p[0], p[1] + int(p[1] * markup)) + p[2:] for p in possibles]
    random_markup = [(p[0], p[1] + int(p[1] * 0.333)) + p[2:] for p in price_adjusted]
    real_possibles = price_adjusted + random_markup

    if sucker:
        real_possibles = [(p[0], p[1] + int(p[1] * 0.333)) + p[2:] for p in real_possibles]
    
    appearance_ids = set([p for p in real_possibles if p[3] == item and p[1] == price])
    if len(appearance_ids) > 0:
        return appearance_ids 

    price_ids = set([p for p in real_possibles if p[3] is None and p[1] == price])

    return price_ids

def sell_identify(item, price, sucker=False):
    possibles = get_item_set(item)
    if possibles is None:
        return set()

    if sucker:
        real_possibles = [(p[0], int(p[1] * 0.333)) + p[2:] for p in possibles]
    else:
        real_possibles = [(p[0], int(p[1] * 0.5)) + p[2:] for p in possibles]

    random_markdown = [(p[0], int(p[1] * 0.25)) + p[2:] for p in possibles]
    real_possibles += random_markdown

    appearance_ids = set([p for p in real_possibles if p[3] == item and p[1] == price])
    if len(appearance_ids) > 0:
        return appearance_ids

    price_ids = set([p for p in real_possibles if p[3] is None and p[1] == price])

    return price_ids

