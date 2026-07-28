from services.constants import ARMY_TYPES, MOBILIZATION_LAWS
from services.math.territory_math import get_total_population
from services.math.economy_math import get_prod_units_consumption, get_prod_units

def get_army_power(player):
    return sum(
        ARMY_TYPES[army["type_id"]]["power"]
        for army in player["armies"]
    )

def get_total_army(player):
    return len(player["armies"])

def get_manpower(player):
    return get_total_population(player) / (1 if MOBILIZATION_LAWS[player["mobilization_law"]]['women_at_war'] else 2) * MOBILIZATION_LAWS[player["mobilization_law"]]['percent']

def get_manpower_percent(player):
    return  MOBILIZATION_LAWS[player["mobilization_law"]]["percent"] * 100

def get_women_at_war(player):
    f = MOBILIZATION_LAWS[player["mobilization_law"]]["women_at_war"]
    return 'разрешена' if f else 'запрещена'

def get_army_type(army):
    return ARMY_TYPES[army["type_id"]]

def get_is_armour(army):
    return "Да" if get_army_type(army)["is_armour"] else "Нет"

def get_army_counteracts(army):
    a_type = get_army_type(army)
    if len(a_type["counteracts"]) > 0:
        return ", ".join([ARMY_TYPES[army_id]["title"] for army_id in a_type["counteracts"]])
    return "Никому."

def get_prod_units_debuff(player):
    balance = get_prod_units(player) - get_prod_units_consumption(player)
    if balance >= 0:
        return 0
    else:
        return balance/get_prod_units_consumption(player)