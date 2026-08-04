from services.constants import get_is_pacifism
from services.math.territory_math import get_total_population, get_one_city_tax_income, get_cities
from services.constants import BUILDINGS, ARMY_TYPES, get_modifier
from services.math.spending_math import *


def get_tax_income(player, country):
    cities = get_cities(player, country["id"])
    return sum(
        get_one_city_tax_income(country, city)
        for city in cities
    )

def get_buildings_income(player, country):
    sum = 0
    cities = get_cities(player, country["id"])
    buildings_income_efficiency = get_modifier(country, "buildings_income_efficiency")
    for city in cities:
        for building in city["buildings"]:
            sum += BUILDINGS[building["id"]]["income_per_pop"] * city["population"] * buildings_income_efficiency * building["amount"]
    return sum

def get_prod_units(player, country_id):
    sum = 0
    cities = get_cities(player, country_id)
    for city in cities:
        for building in city["buildings"]:
            if BUILDINGS[building["id"]].get("prod_unit_inc"): sum += BUILDINGS[building["id"]]["prod_unit_inc"]
    return sum

def get_prod_units_consumption(country):
    return sum(
        get_one_prod_units_consumption(army["type_id"])
        for army in country["armies"]
    )

def get_one_prod_units_consumption(type_id):
    return ARMY_TYPES[type_id]["prod_units_consumption"]

def get_loan_spending(country):
    return country['loans']*country['interest']/12

def get_total_income(player, country):
    return get_buildings_income(player, country) + get_tax_income(player, country)

def get_total_spending(player, country):
    return (get_army_spending(country) + get_loan_spending(country) + get_pops_invest_spending(player, country) +
            get_stability_invest_spending(player, country) + get_militarization_invest_spending(player, country))