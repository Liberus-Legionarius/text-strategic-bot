import random
import services.ai as ai
from services.math.territory_math import get_cities
from services.bot import db
from services.constants import get_city_name

CAMPAIGN_RESULT = {
    0: lambda player, army, cost, campaign: zero_dice(player, army, cost, campaign),
    1: lambda player, army, cost, campaign: one_dice(player, army, cost, campaign),
    2: lambda player, army, cost, campaign: two_dice(player, army, cost, campaign),
    3: lambda player, army, cost, campaign: three_dice(player, army, cost, campaign),
    4: lambda player, army, cost, campaign: four_dice(player, army, cost, campaign),
    5: lambda player, army, cost, campaign: four_dice(player, army, cost, campaign),
    6: lambda player, army, cost, campaign: four_dice(player, army, cost, campaign),
}

def remove_campaign(player, campaign):
    db.players.update_one({"tg_id":player["tg_id"]},
                          {
                              "$pull":{"countries.0.campaigns":campaign}
                          })

def zero_dice(player, army, cost, campaign):
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$inc": {"countries.0.national_spirits.0.stability": -0.01},
                              "$push": {
                                  "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {army['name']} полностью погибла. На экспедицию было потрачено {cost} монет."}
                          })
    remove_campaign(player, campaign)

def one_dice(player, army, cost, campaign):
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$push": {
                                  "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {army['name']} с тяжёлыми потерями вернулась без каких-либо новостей. На экспедицию было потрачено {cost} монет.",
                                  "countries.0.armies": army.update(
                                      {"morale": army["morale"] * random.random(), "hp": army["hp"] * random.random()})}
                          })
    remove_campaign(player, campaign)

def two_dice(player, army, cost, campaign):
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$push": {
                                  "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {army['name']} вернулась без каких-либо новостей. На экспедицию было потрачено {cost} монет.",
                                  "countries.0.armies": army}
                          })
    remove_campaign(player, campaign)

def three_dice(player, army, cost, campaign):
    if random.random() <= 0.5:
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {
                                      "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {army['name']} вернулась с небольшим количеством трофеев. На экспедицию было потрачено {cost} монет.",
                                      "countries.0.armies": army},
                                  "$inc": {"countries.0.money": cost + cost * random.random()}
                              })
    else:
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {
                                      "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {army['name']} вернулась с некоторым количеством выживших, мы распределим их по городам. На экспедицию было потрачено {cost} монет.",
                                      "countries.0.armies": army}
                              })
        population = int(1000 * random.random()/len(list(get_cities(player, 0))))
        db.cities.update_many({"player_id":player["tg_id"], "owner":0},
                              {
                                  "$inc":{
                                      "population":population
                                  }
                              })
    remove_campaign(player, campaign)

def four_dice(player, army, cost, campaign):
    if random.random() <= 0.5:
        city = ai.generate_city(player, get_city_name(player["countries"][0]["capital"]), 0, [])
        db.players.update_one({"tg_id": player["tg_id"]},
                              {
                                  "$push": {
                                      "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {army['name']} вернулась с новостями: обнаружен пустой бункер, мы его заселим. На экспедицию было потрачено {cost} монет.",
                                      "countries.0.armies": army}
                              })

        to_dec = int(1000 / len(list(get_cities(player, 0))))
        db.cities.update_many({"player_id":player["tg_id"], "owner":0},
                              {
                                  "$inc":{"population": -to_dec}
                              })
        new_city = db.cities.insert_one({
            "player_id": player["tg_id"],
            "name": city["name"],
            "owner": 0,
            "controller": 0,
            "population": 1000,
            "buildings": [],
            "connected_with":[player["countries"][0]["capital"]]
        })

        db.cities.update_one({"_id":player["countries"][0]["capital"]},
                             {
                                 "$push":{"connected_with":new_city.inserted_id}
                             })
    else:
        if random.random() <= 0.5:
            city = ai.generate_city(player, get_city_name(player["countries"][0]["capital"]))
            db.players.update_one({"tg_id": player["tg_id"]},
                                  {
                                      "$push": {
                                          "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {army['name']} вернулась с новостями: обнаружен заселённый бункер, местное население приняло нашу власть. На экспедицию было потрачено {cost} монет.",
                                          "countries.0.armies": army}
                                  })
            new_city = db.cities.insert_one({
                "player_id": player["tg_id"],
                "name": city["name"],
                "owner": 0,
                "controller": 0,
                "population": city["population"],
                "buildings": city["buildings"],
                "connected_with": [player["countries"][0]["capital"]]
            })

            db.cities.update_one({"_id": player["countries"][0]["capital"]},
                                 {
                                     "$push": {"connected_with": new_city.inserted_id}
                                 })
        else:
            city = ai.generate_city(player, get_city_name(player["countries"][0]["capital"]))
            db.players.update_one({"tg_id": player["tg_id"]},
                                  {
                                      "$push": {
                                          "actions": f"{player['date']}: Исследовательская экспедиция в составе армейского подразделения {army['name']} вернулась с новостями: обнаружен заселённый бункер, к сожалению, местное население подчинилось нам только после боя. На экспедицию было потрачено {cost} монет.",
                                          "countries.0.armies": army.update(
                                      {"morale": army["morale"] * random.random(), "hp": army["hp"] * random.random()})}
                                  })
            new_city = db.cities.insert_one({
                "player_id": player["tg_id"],
                "name": city["name"],
                "owner": 0,
                "controller": 0,
                "population": city["population"] * random.uniform(0.45,0.9),
                "buildings": city["buildings"],
                "connected_with": [player["countries"][0]["capital"]]
            })

            db.cities.update_one({"_id": player["countries"][0]["capital"]},
                                 {
                                     "$push": {"connected_with": new_city.inserted_id}
                                 })
    remove_campaign(player, campaign)

def five_dice(player, army, cost, campaign): # Найдено государство (нейтральное или враждебное).
    pass

def six_dice(player, army, cost, campaign): # Найдено государство (дружественное, возможно, даже слишком).
    pass

CAMPAIGN_BONUS = {
    250: 0,
    500: 1,
    1000: 2,
    2500: 3
}