import random
import services.ai as ai
from services.math.territory_math import get_cities, change_population
from services.bot import db

CAMPAIGN_RESULT = {
    0: lambda player, campaign: zero_dice(player, campaign),
    1: lambda player, campaign: one_dice(player, campaign),
    2: lambda player, campaign: two_dice(player, campaign),
    3: lambda player, campaign: three_dice(player, campaign),
    4: lambda player, campaign: four_dice(player, campaign),
    5: lambda player, campaign: four_dice(player, campaign),
    6: lambda player, campaign: four_dice(player, campaign),
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
            print(army)
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
    pass

def six_dice(player, campaign): # Найдено государство (дружественное, возможно, даже слишком).
    pass

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