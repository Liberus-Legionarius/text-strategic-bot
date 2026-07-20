import services.ai
from bot import db
import random as rnd
from datetime import datetime

def init_state(user):
    player = db.players.find_one({"tg_id":user.id})
    capital = {
        "name":player["capital"],
        "population":rnd.randint(1000, 10000),
        "satisfaction":rnd.triangular(0.5,1,0.65),
        "is_capital":True
    }
    db.players.update_one({
        "tg_id":user.id},{
        "$set":{
            "polit_power":rnd.randint(50,200),
            "stability":rnd.triangular(0.5,0.75, 0.65),
            "militarization":rnd.triangular(-0.15,0.50,0.10),
            "money":rnd.randint(-15,100),
            "initiative_point":rnd.uniform(5,10),
            "cities":[capital],
            "date":datetime(3057, rnd.randint(1,12), 1),
            "step":1
        }
    })