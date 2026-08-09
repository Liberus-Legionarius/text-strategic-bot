from services.bot import db
from services.constants import ARMY_TYPES
from bson import ObjectId

def reorganize_army(player, country_id, army_id, army_type):
    db.players.update_one({"tg_id": player["tg_id"]},
                          {
                              "$set": {
                                  "countries.$[country].armies.$[army].type_id": army_type
                              }
                          },
                          array_filters=[
                              {"country.id": country_id},
                              {"army.army_id": army_id}
                          ])