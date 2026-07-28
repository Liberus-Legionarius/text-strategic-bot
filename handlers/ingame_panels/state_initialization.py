from services.bot import db
import services.ai as ai
from datetime import datetime
from bson import ObjectId
from services.constants import MOBILIZATION_LAWS

def init_state(user):
    player = db.players.find_one({"tg_id":user.id})
    data = ai.write_step_first(player)
    print(data["response"])
    print(data)
    capital = {
        "city_id":0,
        "name":player["capital"],
        "population":data["capital_population"],
        "buildings":[],
        "contacted_with":[],
        "is_capital":True
    }

    armies = []

    for i, army in enumerate(data["armies"]):
        armies.append(
            {
                "army_id":i,
                "name":army["name"],
                "city_id": 0,
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
        "tg_id":user.id},{
        "$set":{
            "polit_power": data["polit_power"],
            "armies":armies,
            "money": data["money"],
            "loans":0.0,
            "interest": 0.04,
            "population_growth_invest": 0.0,
            "cities":[capital],
            "date":datetime(3057, data["month"], 1),
            "step":1,
            "ai_plot":data["response"],
            "campaigns":[],
            "national_spirits":[data["national_spirit"], taxes_politic, mobilization_law, invest_in_pop_growth]
        }
    })