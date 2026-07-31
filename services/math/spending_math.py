from services.constants import ARMY_TYPES, get_modifier, get_is_pacifism
from services.math.territory_math import get_total_population

def get_army_spending(country):
    return sum(
        get_one_army_spending(country, army["type_id"])
        for army in country["armies"]
    )

def get_one_army_spending(country, type_id):
    return (ARMY_TYPES[type_id]["per_unit_spending"] *
            (get_modifier(country, "army_maintenance", 1) + country["national_spirits"][4]["army_maintenance"]) *
            country["national_spirits"][4]["army_maintenance"])

def get_army_buff_spending(country, modifier):
    return country["national_spirits"][4].get(modifier)

def get_pops_invest_spending(player, country):
    spending = get_total_population(player, country["id"]) * country["national_spirits"][3]["population_growth_invest"] /12
    return spending if spending > 0 else spending/6

def get_diplomacy_spending():
    return 0

def get_stability_invest_spending(player, country):
    stability = abs(get_modifier(country, "stability"))
    if stability >= 1:
        return 0
    else:
        invest = country["national_spirits"][5]["stability_invest"]
        return stability * invest * get_total_population(player, country["id"])

def get_stability_growth(country):
    return country["national_spirits"][5]["stability_invest"]

def get_militarization_invest_spending(player, country):
    militarization = abs(get_modifier(country, "militarization"))
    if militarization >= 1:
        return 0
    else:
        invest = country["national_spirits"][6]["militarization_invest"]
        return militarization * invest * get_total_population(player, country["id"]) * (0.1 if get_is_pacifism(country) else 1)

def get_militarization_growth(country):
    return country["national_spirits"][6]["militarization_invest"]