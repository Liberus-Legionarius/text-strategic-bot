from services.math.territory_math import get_total_population, get_one_city_tax_income
from services.constants import BUILDINGS, ARMY_TYPES, get_modifier


def get_tax_income(player):
    return sum(
        get_one_city_tax_income(player, city)
        for city in player["cities"]
    )

def get_buildings_income(player):
    sum = 0
    for city in player["cities"]:
        for building in city["buildings"]:
            sum += BUILDINGS[building["id"]]["income_per_pop"] * city["population"] * player["buildings_income_efficiency"]
    return sum

def get_prod_units(player):
    sum = 0
    for city in player["cities"]:
        for building in city["buildings"]:
            if BUILDINGS[building["id"]].get("prod_unit_inc"): sum += BUILDINGS[building["id"]]["prod_unit_inc"]
    return sum

def get_prod_units_consumption(player):
    return sum(
        get_one_prod_units_consumption(army["type_id"])
        for army in player["armies"]
    )

def get_one_prod_units_consumption(type_id):
    return ARMY_TYPES[type_id]["prod_units_consumption"]

def get_army_spending(player):
    return sum(
        get_one_army_spending(army["type_id"])
        for army in player["armies"]
    )

def get_one_army_spending(type_id):
    return ARMY_TYPES[type_id]["per_unit_spending"]

def get_loan_spending(player):
    return player['loans']*player['interest']/12

def get_pops_invest_spending(player):
    return get_total_population(player) * player["national_spirits"][3]["population_growth_invest"] /12

def get_total_income(player):
    return get_buildings_income(player) + get_tax_income(player)

def get_total_spending(player):
    return get_army_spending(player) + get_loan_spending(player) + get_pops_invest_spending(player)