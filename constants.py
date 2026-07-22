from bot import db
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton

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

def get_build_kb(city_id):
    buildings_kb = InlineKeyboardMarkup()
    for building in BUILDINGS.values():
        buildings_kb.add(InlineKeyboardButton(f"{building['title']} ({building['cost']} монет)",
                                              callback_data=f"territory:build:{building['_id']}"))
    buildings_kb.add(InlineKeyboardButton("Вернуться", callback_data=f"territory:cities:{city_id}"))
    return  buildings_kb