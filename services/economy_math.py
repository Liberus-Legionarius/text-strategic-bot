from bot import db
from services.territory_math import get_total_population
from constants import BUILDINGS, ARMY_TYPES

def get_tax_income(player):
    return sum(
        city["population"] * player["taxes"] / 120
        for city in player["cities"]
    )

def get_buildings_income(player):
    sum = 0
    for city in player["cities"]:
        for building in city["buildings"]:
            sum += BUILDINGS[building["id"]]["income_per_pop"] * city["population"]
    return sum

def get_prod_units(player):
    sum = 0
    for city in player["cities"]:
        for building in city["buildings"]:
            if BUILDINGS[building["id"]].get("prod_unit_inc"): sum += BUILDINGS[building["id"]]["prod_unit_inc"]
    return sum

def get_prod_units_consumption(player):
    return sum(
        get_one_prod_units_consumption(army["type"])
        for army in player["armies"]
    )

def get_one_prod_units_consumption(type_id):
    return ARMY_TYPES[type_id]["prod_units_consumption"]

def get_army_spending(player):
    return sum(
        get_one_army_spending(army["type"])
        for army in player["armies"]
    )

def get_one_army_spending(type_id):
    return ARMY_TYPES[type_id]["per_unit_spending"]

def get_loan_spending(player):
    return player['loans']*player['interest']/12

def get_pops_invest_spending(player):
    return get_total_population(player) * player["pops_invest"] /12