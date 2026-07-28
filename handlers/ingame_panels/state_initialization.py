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

    db.players.update_one({
        "tg_id":user.id},{
        "$set":{
            "polit_power_gain_flat":data["polit_power_gain_flat"],
            "polit_power_gain_modifier": data["polit_power_gain_modifier"],
            "polit_power": data["polit_power"],
            "stability":data["stability"],
            "militarization": data["militarization"],
            "armies":armies,
            "mobilization_law": ObjectId(data["mobilization_law"]),
            "money": data["money"],
            "tax_rate": data["tax_rate"],
            "buildings_income_efficiency": data["buildings_income_efficiency"],
            "loans":0.0,
            "interest": 0.04,
            "population_growth_invest": 0.0,
            "population_growth": data["population_growth"],
            "cities":[capital],
            "date":datetime(3057, data["month"], 1),
            "step":1,
            "ai_plot":data["response"],
            "campaigns":[]
        }
    })