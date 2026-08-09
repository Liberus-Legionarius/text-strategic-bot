from services.bot import db
from services.constants import ARMY_TYPES
from bson import ObjectId
from services.math.territory_math import get_cities, change_population


def conscript_army(player, country, army_type):
    i = max(country["armies"], key=lambda a: a["army_id"])["army_id"] + 1
    a_type = ARMY_TYPES[ObjectId(army_type)]
    change_pops = 100 / len(get_cities(player, country["id"]))
    change_population(player, 0, -change_pops)
    db.players.update_one({"tg_id": player["tg_id"], "countries.id": country["id"]},
                          {
                              "$push": {
                                  "countries.$.armies": {
                                      "army_id": i,
                                      "name": f"Армия №{i}",
                                      "size": 1,
                                      "hp": a_type["hp"],
                                      "morale": a_type["morale"],
                                      "type_id": ObjectId(army_type)
                                  }
                              },
                              "$inc": {
                                  "countries.$.money": -a_type["cost"]
                              }
                          })