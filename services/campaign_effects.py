import random
import services.ai as ai
from services.constants import MOBILIZATION_LAWS
from services.math.army_math import get_army_type
from services.math.territory_math import get_cities, change_population, get_free_cities
from services.bot import db
from bson import ObjectId

CAMPAIGN_RESULT = {
    0: lambda player, campaign: zero_dice(player, campaign),
    1: lambda player, campaign: one_dice(player, campaign),
    2: lambda player, campaign: two_dice(player, campaign),
    3: lambda player, campaign: three_dice(player, campaign),
    4: lambda player, campaign: four_dice(player, campaign),
    5: lambda player, campaign: five_dice(player, campaign),
    6: lambda player, campaign: six_dice(player, campaign),
}

def remove_campaign(player, campaign):
    db.players.update_one({"tg_id":player["tg_id"]},
                          {
                              "$pull":{"countries.0.campaigns":campaign}
                          })

def zero_dice(player, campaign):
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$inc": {"countries.0.national_spirits.0.stability": -0.01},
                              "$push": {
                                  "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} полностью погибла. На экспедицию было потрачено {campaign['cost']} монет."}
                          })
    change_population(player, 0, -100)
    remove_campaign(player, campaign)

def one_dice(player, campaign):
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$push": {
                                  "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} с тяжёлыми потерями вернулась без каких-либо новостей. На экспедицию было потрачено {campaign['cost']} монет.",
                                  "countries.0.armies": campaign['army'].update(
                                      {"morale": campaign['army']["morale"] * random.random(), "hp": campaign['army']["hp"] * random.random()})}
                          })
    remove_campaign(player, campaign)

def two_dice(player, campaign):
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$push": {
                                  "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} вернулась без каких-либо новостей. На экспедицию было потрачено {campaign['cost']} монет.",
                                  "countries.0.armies": campaign['army']}
                          })
    remove_campaign(player, campaign)

def three_dice(player, campaign):
    if random.random() <= 0.5:
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {
                                      "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} вернулась с небольшим количеством трофеев. На экспедицию было потрачено {campaign['cost']} монет.",
                                      "countries.0.armies": campaign['army']},
                                  "$inc": {"countries.0.money": campaign['cost'] + campaign['cost'] * random.random()}
                              })
    else:
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {
                                      "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} вернулась с некоторым количеством выживших, мы распределим их по городам. На экспедицию было потрачено {campaign['cost']} монет.",
                                      "countries.0.armies": campaign['army']}
                              })
        population = int(1000 * random.random()/len(list(get_cities(player, 0))))
        change_population(player, 0, population)
    remove_campaign(player, campaign)

def four_dice(player, campaign):
    if random.random() <= 0.5:
        city_name = get_unknown_city(player, campaign["province"])["name"]
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {
                                      "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} вернулась с новостями: обнаружен пустой бункер, мы его заселим. На экспедицию было потрачено {campaign['cost']} монет.",
                                      "countries.0.armies": campaign['army']}
                              })

        to_dec = int(1000 / len(list(get_cities(player, 0))))
        change_population(player, 0, -to_dec)

        db.players.update_one({"tg_id":player["tg_id"], "cities.name":city_name},
                             {
                                 "$set":{
                                     "cities.$.owner": 0,
                                     "cities.$.controller": 0,
                                     "cities.$.population":1000
                                 }
                             })
    else:
        if random.random() <= 0.5:
            city_name = get_unknown_city(player, campaign["province"])["name"]
            city = ai.generate_city(player, city_name)
            db.players.update_one({"tg_id": player["tg_id"]},
                                  {
                                      "$push": {
                                          "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} вернулась с новостями: обнаружен заселённый бункер, местное население приняло нашу власть. На экспедицию было потрачено {campaign['cost']} монет.",
                                          "countries.0.armies": campaign["army"]}
                                  })

            db.players.update_one({"tg_id": player["tg_id"], "cities.name": city_name},
                                  {
                                      "$set": {
                                          "cities.$.owner": 0,
                                          "cities.$.controller": 0,
                                          "cities.$.population": city["population"],
                                          "cities.$.buildings": city["buildings"]
                                      }
                                  })
        else:
            city_name = get_unknown_city(player, campaign["province"])["name"]
            city = ai.generate_city(player, city_name)
            army = campaign["army"]
            army.update({"morale": army["morale"] * random.random(), "hp": army["hp"] * random.random()})
            db.players.update_one({"tg_id": player["tg_id"]},
                                  {
                                      "$push": {
                                          "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} вернулась с новостями: обнаружен заселённый бункер, к сожалению, местное население подчинилось нам только после боя. На экспедицию было потрачено {campaign['cost']} монет.",
                                          "countries.0.armies": army}
                                  })
            db.players.update_one({"tg_id": player["tg_id"], "cities.name": city_name},
                                  {
                                      "$set": {
                                          "cities.$.owner": 0,
                                          "cities.$.controller": 0,
                                          "cities.$.population": city["population"] * random.uniform(0.45,0.9),
                                          "cities.$.buildings": city["buildings"]
                                      }
                                  })
    remove_campaign(player, campaign)

def five_dice(player, campaign): # Найдено государство (нейтральное или враждебное).
    city = get_unknown_city(player, campaign["province"])["name"]
    print(city)
    relation = "Враждебны" if random.random() < 0.45 else "Нейтральны"
    new_country = ai.generate_country(player, city, get_max_country_size(player), relation)
    print(new_country)
    paste_country(player, new_country)

    db.players.update_one({"tg_id":player["tg_id"]},
                          {
                              "$push":{
                                  "countries.0.armies": campaign["army"],
                                  "actions":f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} вернулась с новостями: они встретили государство. Они к нам {relation}. Их держава называется {new_country['full_countryname']} со столицей в городе {new_country['capital_name']}, а их идеология это {new_country['ideology']}. Подробности об их идеологии: {new_country['ideology_desc']}. Суть их страны: {new_country['country_characteristics']}."
                              }
                          })
    remove_campaign(player, campaign)

def six_dice(player, campaign): # Найдено государство (дружественное, возможно, даже слишком).
    city = get_unknown_city(player, campaign["province"])["name"]
    print(city)
    new_country = ai.generate_country(player, city, get_max_country_size(player), "Дружественны")
    print(new_country)
    paste_country(player, new_country)

    db.players.update_one({"tg_id":player["tg_id"]},
                          {
                              "$push":{
                                  "countries.0.armies": campaign["army"],
                                  "actions":f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {campaign['army']['name']} вернулась с новостями: они встретили дружественное нам государство. Их держава называется {new_country['full_countryname']} со столицей в городе {new_country['capital_name']}, а их идеология это {new_country['ideology']}. Подробности об их идеологии: {new_country['ideology_desc']}. Суть их страны: {new_country['country_characteristics']}."
                              }
                          })
    remove_campaign(player, campaign)

CAMPAIGN_BONUS = {
    250: -1,
    500: 0,
    1000: 1,
    2500: 2
}

def get_unknown_city(player, province):
    cities = [city for city in player["cities"] if city["name"] in province["cities"] and city["owner"] is None]
    percent =  len(cities) / (len(province["cities"]))
    if len(cities) < 1 or random.random() > percent:
        provinces = [p for p in player["province_map"] if p["name"] in province["connected_with"]]
        cities = []
        for prov in provinces:
            cs = [city for city in player["cities"] if city["name"] in prov["cities"] and city["owner"] is None]
            if len(cs) < 1: break
            cities.extend(cs)
        return  random.choice(cities)
    else:
        return random.choice(cities)

def get_max_country_size(player):
    player_size = len(get_cities(player, 0))
    free_cities = len(get_free_cities(player))
    if free_cities < player_size:
        size = int(free_cities/5*random.uniform(0.25,5))
    elif player_size < 5:
        size = random.randint(1,int(player_size*random.uniform(1,2)))
    elif player_size < free_cities/20:
        size = int(player_size*random.uniform(0.25,3.5))
    else:
        size = int(player_size*random.uniform(0.75,1.5))
    return  size

def paste_country(player, new_country):
    armies = []
    for i, army in enumerate(new_country["armies"]):
        a_type = get_army_type(army)
        armies.append({
            "army_id": i,
            "name": army["name"],
            "size": 1,
            "hp": a_type["hp"],
            "morale": a_type["morale"],
            "type_id": ObjectId(army["type_id"])
        })

    taxes_politic = {
        "id": 1,
        "name": "Налоговая ставка",
        "tax_rate": 0.0,
        "stability": 0.0
    }

    mobilization_law = {
        "id": 2,
        "name": "Политика призыва"
    }

    for key, value in MOBILIZATION_LAWS[ObjectId(new_country["mobilization_law"])].items():
        mobilization_law.update({key: value})

    invest_in_pop_growth = {
        "id": 3,
        "name": "Дополнительные вложения в рост населения",
        "population_growth_invest": 0.0,
        "polit_power_gain_modifier": 0.0
    }

    invest_in_army = {
        "id": 4,
        "name": "Обеспечение армии",
        "army_maintenance": 1.0,
        "attack_modifier": 0.0,
        "defense_modifier": 0.0,
        "hp_modifier": 0.0,
        "morale_modifier": 0.0
    }

    invest_in_stability = {
        "id": 5,
        "name": "Дополнительные вложения в рост стабильности",
        "stability_invest": 0.0
    }

    invest_in_militarization = {
        "id": 6,
        "name": "Дополнительные вложения в рост милитаризации общества",
        "militarization_invest": 0.0
    }
    country_id = ObjectId()
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$push": {
                                  "countries": {
                                      "id": country_id,
                                      "countryname": new_country["countryname"],
                                      "full_countryname": new_country["full_countryname"],
                                      "capital": new_country["capital_name"],
                                      "ideology": new_country["ideology"],
                                      "ideology_desc": new_country["ideology_desc"],
                                      "country_characteristics": new_country["country_characteristics"],
                                      "ai_logic": new_country["ai_logic"],
                                      'territorial_ambitions': new_country["ambitions"],
                                      "money": new_country["money"],
                                      "polit_power": new_country["polit_power"],
                                      "armies": armies,
                                      "loans": 0,
                                      "interest": 0.04,
                                      "national_spirits": [new_country["national_spirit"], taxes_politic,
                                                           mobilization_law, invest_in_pop_growth, invest_in_army,
                                                           invest_in_stability, invest_in_militarization]
                                  }
                              }
                          })
    for city in new_country["cities"]:
        city_data = ai.generate_city(player, city)
        db.players.update_one({"tg_id":player["tg_id"], "cities.name":city},
                              {
                                  "$set":{
                                      "cities.$.owner": country_id,
                                      "cities.$.controller": country_id,
                                      "cities.$.population":city_data["population"],
                                      "cities.$.buildings": city_data["buildings"]
                                  }
                              })