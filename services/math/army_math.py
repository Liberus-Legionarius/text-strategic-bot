from services.constants import ARMY_TYPES, MOBILIZATION_LAWS, get_modifier
from services.math.territory_math import get_total_population
from services.math.economy_math import get_prod_units_consumption, get_prod_units
from bson import ObjectId

def get_army_power(country):
    return sum(
        ARMY_TYPES[army["type_id"]]["power"]
        for army in country["armies"]
    )

def get_total_army(country):
    return len(country["armies"])

def get_manpower(player, country):
    return get_total_population(player, country["id"]) / (1 if country["national_spirits"][2]['women_at_war'] else 2) * get_modifier(country, "mobilization_percent")

def get_manpower_percent(country):
    return  get_modifier(country, "mobilization_percent") * 100

def get_women_at_war(country):
    f = country["national_spirits"][2]["women_at_war"]
    return 'разрешена' if f else 'запрещена'

def get_army_type(army):
    key = (ObjectId(army["type_id"]) if isinstance(army["type_id"], str) else army["type_id"])
    return ARMY_TYPES[key]

def get_is_armour(type):
    return "Да" if type["is_armour"] else "Нет"

def get_army_counteracts(type):
    if len(type["counteracts"]) > 0:
        return ", ".join([ARMY_TYPES[army_id]["title"] for army_id in type["counteracts"]])
    return "Никому."

def get_prod_units_debuff(player, country):
    balance = get_prod_units(player, country["id"]) - get_prod_units_consumption(country)
    if balance >= 0:
        return 0
    else:
        return balance/get_prod_units_consumption(country)

def get_army(country, army_id):
    return next((a for a in country["armies"] if str(a["army_id"]) == army_id), None)

def get_reorganization_cost(army, new_type):
    return (new_type["cost"] - new_type["cost"] * (get_army_type(army)["cost"]/new_type["cost"]/2)) * army["size"]