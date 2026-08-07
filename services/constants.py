from services.bot import db
from services.modifiers import modifiers_from_zero_to_one, modifiers_from_one_to_one

NUMBER_TO_MONTH = {
    1:"Январь",
    2:"Февраль",
    3:"Март",
    4:"Апрель",
    5:"Май",
    6:"Июнь",
    7:"Июль",
    8:"Август",
    9:"Сентябрь",
    10:"Октябрь",
    11:"Ноябрь",
    12:"Декабрь"
}

BASE_INCOME = 2.5

BUILDINGS = dict()
ARMY_TYPES = dict()
MOBILIZATION_LAWS = dict()

def get_player(user):
    return db.players.find_one({"tg_id": user.id})

def get_country(player, country_id):
    return player["countries"][country_id]

def get_date_move(player):
    return f"{NUMBER_TO_MONTH[player['date'].month]}, год {player['date'].year}, шаг {player['step']}"

def set_buildings():
    global  BUILDINGS
    BUILDINGS.update({
        str(b["_id"]): b
        for b in db.buildings.find()
    })

def set_army_types():
    global ARMY_TYPES
    ARMY_TYPES.update({
        army["_id"]: army
        for army in db.army_types.find()
    })

def set_mobilization():
    global MOBILIZATION_LAWS
    MOBILIZATION_LAWS.update({
        law["_id"]: law
        for law in db.mobilization_laws.find()
    })

def get_buildings_info():
    text = ""
    for building in BUILDINGS.values():
        text += f"\n{building['title']} - {building['income_per_pop']*1000} монет за 1000 населения в ход"
    return text

def get_modifier(country, modifier, addition = 0):
    result = sum(
        spirit[modifier]
        for spirit in country["national_spirits"] if spirit.get(modifier)
    ) + addition
    if modifier in modifiers_from_zero_to_one:
        result = min(1 + addition, max(0, result))
    elif modifier in modifiers_from_one_to_one:
        result = min(1 + addition, max(-1, result))
    return result

def get_is_pacifism(country):
    return country["national_spirits"][2].get("is_pacifism")