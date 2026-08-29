from pathlib import  Path
import json
from services.bot import db
from bson import ObjectId

province_map = []
cities = []

def init_map():
    global province_map, cities
    maps = Path("services/map")
    i = 0
    for file in maps.glob("*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for province, info in data.items():
                cities.extend([{"_id":ObjectId(), "name":city["name"], "population":0,"owner":None, "controller":None, "buildings":[], "province":province} for city in info["cities"]])
                province_map.append({"id":i, "name":province, "cities":[city["name"] for city in info["cities"]], "connected_with":info["connected_with"]})
                i += 1

def load_map(tg_id):
    db.players.update_one({"tg_id":tg_id},
                          {
                              "$set":{
                                  "province_map":province_map,
                                  "cities":cities
                              }
                          })

def city_exists_on_map(name):
    res = []
    for city in cities:
        if city["name"] == name:
            res.append(city)
    return res
