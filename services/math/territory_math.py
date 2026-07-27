from services.constants import BUILDINGS

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
    return get_total_population(player) * ((player["population_growth"] + player["population_growth_invest"]) * (1 + player["stability"] - 0.65))

def get_prod_city_income(city, player):
    return sum(
        BUILDINGS[building["id"]]["income_per_pop"] * city["population"] * player["buildings_income_efficiency"]
        for building in city["buildings"]
    )
def get_one_city_tax_income(player, city):
    return city["population"] * player["tax_rate"] * (1 + player["stability"] - 0.65) / 120

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

def get_percent_pop_growth(player):
    return (player["population_growth"] + player["population_growth_invest"]) * (1 + player["stability"] - 0.65)