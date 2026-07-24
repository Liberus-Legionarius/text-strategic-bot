from services.bot import db
import random as rnd
from datetime import datetime
from bson import ObjectId
from services.constants import MOBILIZATION_LAWS

def init_state(user):
    player = db.players.find_one({"tg_id":user.id})
    capital = {
        "city_id":0,
        "name":player["capital"],
        "population":rnd.randint(1000, 10000),
        "buildings":[],
        "contacted_with":[],
        "is_capital":True
    }
    army = {
        "army_id": 0,
        "name": "1-ый полк ополчения",
        "city_id":capital["city_id"],
        "type": ObjectId("6a60997f381180f7fb494521")
    }
    db.players.update_one({
        "tg_id":user.id},{
        "$set":{
            "polit_power":rnd.randint(50,200),
            "stability":rnd.triangular(0.5,0.75, 0.65),
            "militarization":rnd.triangular(-0.15,0.50,0.10),
            "armies":[army],
            "mobilization_laws": list(MOBILIZATION_LAWS.keys())[0],
            "money":rnd.uniform(-15,100),
            "taxes": 0.15,
            "loans":0.0,
            "interest": 0.04,
            "pops_invest": 0.0,
            "cities":[capital],
            "date":datetime(3057, rnd.randint(1,12), 1),
            "step":1,
            "ai_plot":None
        }
    })