from services.bot import db
import services.ai as ai
from datetime import datetime
from bson import ObjectId
from services.constants import MOBILIZATION_LAWS
from services.math.army_math import get_army_type


def init_state(user):
    player = db.players.find_one({"tg_id":user.id})
    data = ai.write_step_first(player)
    capital = {
        "player_id":player["tg_id"],
        "name":player["countries"][0]["capital"],
        "owner":0,
        "controller":0,
        "population":data["capital_population"],
        "buildings":[],
        "contacted_with":[]
    }
    city = db.cities.insert_one(capital)

    armies = []

    for i, army in enumerate(data["armies"]):
        armies.append(
            {
                "army_id":i,
                "name":army["name"],
                "size":1,
                "hp":get_army_type(army)["hp"],
                "morale":get_army_type(army)["morale"],
                "city_id": city.inserted_id,
                "type_id": ObjectId(army["type_id"])
            }
        )
    taxes_politic = {
        "id":1,
        "name": "Налоговая ставка",
        "tax_rate":0.0,
        "stability":0.0
    }

    mobilization_law = {
        "id":2,
        "name": "Политика призыва"
    }

    for key, value in MOBILIZATION_LAWS[ObjectId(data["mobilization_law"])].items():
        mobilization_law.update({key:value})

    invest_in_pop_growth = {
        "id": 3,
        "name": "Дополнительные вложения в рост населения",
        "population_growth_invest": 0.0,
        "polit_power_gain_modifier": 0.0
    }

    db.players.update_one({
        "tg_id":user.id, "countries.id":0},{
        "$set":{
            "countries.$.capital": city.inserted_id,
            "countries.$.armies": armies,
            "countries.$.polit_power": data["polit_power"],
            "countries.$.money": data["money"],
            "countries.$.loans": 0.0,
            "countries.$.interest": 0.04,
            "countries.$.campaigns": [],
            "countries.$.national_spirits": [data["national_spirit"], taxes_politic, mobilization_law, invest_in_pop_growth],
            "countries.$.is_player": True,
            "date":datetime(3057, data["month"], 1),
            "step":1,
            "ai_plot":data["response"],
            "actions":[],
            "history":[]
        }
    })

