from services.constants import BUILDINGS, get_modifier
from services.bot import db

def get_total_population(player, country_id):
    cities = get_cities(player, country_id)
    return int(sum(
        city["population"]
        for city in cities
    ))

def get_avg_population(player, country_id):
    return int(get_total_population(player, country_id)/len(get_cities(player, country_id)))

def get_largest_city(player, country_id):
    city = max(get_cities(player, country_id), key=lambda c:c["population"])
    return city["name"]

def get_next_step_growth(player, country):
    return int(get_total_population(player, country["id"]) * ((get_modifier(country, "population_growth") + get_modifier(country, "population_growth_invest")) * get_modifier(country, "stability", 0.35)))

def get_prod_city_income(country, city):
    return sum(
        BUILDINGS[building["id"]]["income_per_pop"] * city["population"] * get_modifier(country, "buildings_income_efficiency")
        for building in city["buildings"]
    )
def get_one_city_tax_income(country, city):
    return city["population"] * get_modifier(country, "tax_rate") * get_modifier(country, "stability", 0.35) / 120

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
    return get_modifier(country, "population_growth") + get_modifier(country, "population_growth_invest") * get_modifier(country, "stability", 0.35)

def get_cities(player, country_id):
    return [city for city in player["cities"] if city["owner"] == country_id]

def get_city_by_name(player, name):
    return next((city for city in player["cities"] if city["name"] == name), None)

def build_in_city(player, city, building_id, country_id = 0, is_free = False):
    b = next((b for b in city["buildings"] if b["id"] == building_id), None)
    buildings = city["buildings"]
    if b:
        buildings = [building.update({"amount": building["amount"] + 1}) if building["id"] == building_id else building for building in city["buildings"]]
    else:
        buildings.append({"id": building_id, "amount": 1})

    db.players.update_one({"tg_id":player["tg_id"], "cities.name":city["name"]},
                          {
                              "$set":{
                                  "cities.$.buildings":buildings
                              }
                          })
    if not is_free:
        db.players.update_one({"tg_id":player["tg_id"], "countries.id":country_id},
                              {
                                  "$inc":{
                                      "countries.$.money":-BUILDINGS[building_id]["cost"]
                                  }
                              })

def change_population(player, country_id, change_on):
    db.players.update_one({"tg_id": player["tg_id"]},
                          [
                              {
                                  "$set": {
                                      "cities": {
                                          "$map": {
                                              "input": "$cities",
                                              "as": "city",
                                              "in": {
                                                  "$cond": [
                                                      {"$eq": ["$$city.owner", country_id]},
                                                      {
                                                          "$mergeObjects": [
                                                              "$$city",
                                                              {
                                                                  "population": {
                                                                      "$add": ["$$city.population", change_on]
                                                                  }
                                                              }
                                                          ]
                                                      },
                                                      "$$city"
                                                  ]
                                              }
                                          }
                                      }
                                  }
                              }
                          ])

def get_free_cities(player):
    return [city for city in player["cities"] if city["owner"] is None]