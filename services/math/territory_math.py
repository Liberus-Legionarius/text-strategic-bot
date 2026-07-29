from services.constants import BUILDINGS, get_modifier
from services.bot import db

def get_total_population(player, country_id):
    cities = db.cities.find({"player_id":player["tg_id"], "owner":country_id})
    return sum(
        city["population"]
        for city in cities
    ) + len(player["countries"][country_id]["armies"]) * 1000

def get_avg_population(player, country_id):
    return get_total_population(player, country_id)/len(get_cities(player, country_id))

def get_largest_city(player, country_id):
    city = db.cities.find_one({"player_id":player["tg_id"], "owner":country_id},
                       sort=[("population",-1)])
    return city["name"]

def get_next_step_growth(player, country):
    return get_total_population(player, country["id"]) * ((get_modifier(country, "population_growth") + get_modifier(country, "population_growth_invest")) * (1 + get_modifier(country, "stability") - 0.65))

def get_prod_city_income(country, city):
    return sum(
        BUILDINGS[building["id"]]["income_per_pop"] * city["population"] * get_modifier(country, "buildings_income_efficiency")
        for building in city["buildings"]
    )
def get_one_city_tax_income(country, city):
    return city["population"] * get_modifier(country, "tax_rate") * (1 + get_modifier(country, "stability") - 0.65) / 120

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

def get_percent_pop_growth(country):
    return get_modifier(country, "population_growth") + get_modifier(country, "population_growth_invest") * (1 + get_modifier(country, "stability") - 0.65)

def get_cities(player, country_id):
    return list(db.cities.find({"player_id": player["tg_id"], "owner": country_id}))