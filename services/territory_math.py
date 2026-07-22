from bot import db
from constants import BUILDINGS

def get_total_population(player):
    return sum(
        city["population"]
        for city in player["cities"]
    ) + len(player["armies"]) * 1000

def get_avg_population(player):
    return get_total_population(player)/len(player["cities"])

def get_largest_city(player):
    largest = 0
    name = ""
    for city in player["cities"]:
        if city["population"] > largest:
            largest = city["population"]
            name = city["name"]
    return name

def get_next_step_growth(player):
    return get_total_population(player) * player["pops_invest"]

def get_prod_city_income(city):
    return sum(
        BUILDINGS[building["id"]]["income_per_pop"] * city["population"]
        for building in city["buildings"]
    )

def get_buildings(city):
    if len(city["buildings"]) < 1:
        return "Нет зданий"
    else:
        text = ""
        for building in city["buildings"]:
            b = BUILDINGS[building["id"]]
            text += (f"\n{b['title']}:"
                     f"\n\t{b['income_per_pop'] * city['population']:.2f} монет в ход"
                     f"\n\t{b['prod_unit_inc'] + ' единиц производства' if b.get('prog_unit_inc') else ''}")
        return text